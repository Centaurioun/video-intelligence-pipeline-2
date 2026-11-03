#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

BUILD_STATES = {'BUILD_GREEN', 'VERIFY_READY', 'VERIFYING', 'VERIFIED', 'REPAIRING'}
HARD_BUILD_STATES = {'BUILD_GREEN', 'VERIFY_READY', 'VERIFYING', 'VERIFIED'}
LANE_FOR_STATE = {'READY': 'BUILD', 'VERIFY_READY': 'VERIFY', 'REPAIRING': 'REPAIR'}
LANE_PRIORITY = {'REPAIR': 0, 'VERIFY': 1, 'BUILD': 2}
BOOTSTRAP_META_REF = '.orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.json'
BOOTSTRAP_SCHEMA = 'remaining-work-launch-bootstrap.v2'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_launch_bootstrap(root: Path) -> tuple[dict, str]:
    meta_path = root / BOOTSTRAP_META_REF
    meta = load_json(meta_path)
    if meta.get('schema_version') != BOOTSTRAP_SCHEMA:
        raise ValueError(f"unsupported launch bootstrap schema: {meta.get('schema_version')!r}")
    for key in ('version', 'sha256', 'ref', 'preflight_script_ref', 'verified_superpowers_skills'):
        if not meta.get(key):
            raise ValueError(f'launch bootstrap metadata missing {key}')
    text_path = root / meta['ref']
    text = text_path.read_text(encoding='utf-8')
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if digest != meta['sha256']:
        raise ValueError(f"launch bootstrap hash mismatch: {digest} != {meta['sha256']}")
    if not (root / meta['preflight_script_ref']).exists():
        raise ValueError(f"launch bootstrap preflight script missing: {meta['preflight_script_ref']}")
    return meta, text

def paths_overlap(a: str, b: str) -> bool:
    aa, bb = a.rstrip('/'), b.rstrip('/')
    return aa == bb or aa.startswith(bb + '/') or bb.startswith(aa + '/')


def dependency_satisfied(state: str, kind: str) -> bool:
    if kind == 'INDEPENDENT':
        return True
    if kind == 'SOFT_BUILD_DEPENDENCY':
        return state in BUILD_STATES
    if kind == 'HARD_BUILD_DEPENDENCY':
        return state in HARD_BUILD_STATES
    if kind == 'HARD_VERIFY_DEPENDENCY':
        return state == 'VERIFIED'
    return False


def _candidate_entry(node: dict) -> dict | None:
    lane = LANE_FOR_STATE.get(node.get('state'))
    if lane is None:
        return None
    if lane in {'VERIFY', 'REPAIR'} and not node.get('candidate_generation'):
        return None
    resource = 'LIGHTWEIGHT_CPU_TEST' if lane == 'VERIFY' else node.get('resource_class')
    executor = 'VERIFY_ONLY' if lane == 'VERIFY' else ('REPAIR_CELL' if lane == 'REPAIR' else node.get('executor_mode'))
    return {
        'task_id': node['id'],
        'label': node.get('title') or node['id'],
        'lane': lane,
        'state': node.get('state'),
        'write_mode': 'READ_ONLY' if lane == 'VERIFY' else 'WRITE',
        'executor_mode': executor,
        'resource_class': resource,
        'weight': float(node.get('weight') or 0),
        'write_domain': list(node.get('write_domain') or []),
        'prompt_core_ref': node.get('prompt_core_ref'),
        'prompt_core_sha256': node.get('prompt_core_sha256'),
        'overlay_ref': node.get('overlay_ref'),
    }


def select_entries(atlas: dict, *, exclude_task_ids: set[str] | None = None) -> list[dict]:
    excluded = exclude_task_ids or set()
    nodes = [n for n in atlas.get('nodes', []) if isinstance(n, dict) and n.get('level') == 'H3']
    by_id = {n.get('id'): n for n in nodes}
    candidates = []
    for node in nodes:
        if node.get('id') in excluded:
            continue
        entry = _candidate_entry(node)
        if entry is None:
            continue
        if entry['lane'] == 'BUILD':
            ok = True
            for dep in node.get('dependencies') or []:
                kind = dep.get('kind')
                if kind == 'INDEPENDENT':
                    continue
                up = by_id.get(dep.get('node_id'))
                if up is None or not dependency_satisfied(up.get('state'), kind):
                    ok = False
                    break
            if not ok:
                continue
        candidates.append(entry)

    candidates.sort(key=lambda e: (LANE_PRIORITY[e['lane']], -e['weight'], e['task_id']))
    leases = atlas.get('resource_leases') or {}
    counts = Counter()
    owned: list[tuple[str, str]] = []
    selected: list[dict] = []

    for entry in candidates:
        resource = entry['resource_class']
        limit = leases.get(resource)
        if isinstance(limit, int) and counts[resource] >= limit:
            continue
        if entry['write_mode'] == 'WRITE':
            conflict = False
            for path in entry['write_domain']:
                for _, other_path in owned:
                    if paths_overlap(path, other_path):
                        conflict = True
                        break
                if conflict:
                    break
            if conflict:
                continue
        selected.append(entry)
        counts[resource] += 1
        if entry['write_mode'] == 'WRITE':
            owned.extend((entry['task_id'], p) for p in entry['write_domain'])

    return selected


def _validate_overlay(overlay: dict, task_id: str) -> None:
    if overlay.get('task_id') != task_id:
        raise ValueError(f'overlay task_id mismatch for {task_id}')
    for key in ('version', 'base_sha', 'branch', 'resolved_model_identity', 'reconciled_at_head'):
        if not overlay.get(key):
            raise ValueError(f'overlay missing {key} for {task_id}')


def _render_build_prompt(entry: dict, overlay: dict, core_text: str, bootstrap_text: str) -> str:
    return (
        f"# {entry['task_id']} — {entry['label']}\n\n"
        "Open this as a **fresh top-level Codex** task. Repository/Git evidence is authoritative. "
        "Do not depend on remembering any prior Codex chat.\n\n"
        f"- Executor mode: `{entry['executor_mode']}`\n"
        f"- Resource class: `{entry['resource_class']}`\n"
        f"Resolved model: `{overlay['resolved_model_identity']}`\n\n"
        "## Launch Bootstrap v2\n\n" + bootstrap_text.rstrip() + "\n\n"
        "## Launch Overlay\n\n```json\n"
        + json.dumps(overlay, indent=2, sort_keys=True)
        + "\n```\n\n## Frozen Core\n\n"
        + core_text
    )


def _render_verify_prompt(entry: dict, overlay: dict, core_text: str, bootstrap_text: str) -> str:
    return (
        f"# {entry['task_id']} — feature verification/review\n\n"
        "Open this as a **fresh top-level Codex** VERIFY task. Use `requesting-code-review` against the exact candidate generation in repository state. "
        "Read the Frozen Core for acceptance criteria, remain read-only on product paths, and return a compact review/verification receipt.\n\n"
        f"Resolved model: `{overlay['resolved_model_identity']}`\n\n"
        "## Launch Bootstrap v2\n\n" + bootstrap_text.rstrip() + "\n\n"
        "## Launch Overlay\n\n```json\n" + json.dumps(overlay, indent=2, sort_keys=True) + "\n```\n\n"
        "## Governing Frozen Core\n\n" + core_text
    )


def _render_repair_prompt(entry: dict, overlay: dict, core_text: str, bootstrap_text: str) -> str:
    return (
        f"# {entry['task_id']} — bounded repair cell\n\n"
        "Open this as a **fresh top-level Codex** REPAIR task. Read the accepted review/problem evidence, use `receiving-code-review`, systematic debugging, and TDD. "
        "Repair only the authorized write domain and produce a new exact candidate generation.\n\n"
        f"Resolved model: `{overlay['resolved_model_identity']}`\n\n"
        "## Launch Bootstrap v2\n\n" + bootstrap_text.rstrip() + "\n\n"
        "## Launch Overlay\n\n```json\n" + json.dumps(overlay, indent=2, sort_keys=True) + "\n```\n\n"
        "## Governing Frozen Core\n\n" + core_text
    )


def render_pack(*, root: Path, batch_id: str, generated_at_head: str, output_dir: Path, exclude_task_ids: set[str] | None = None) -> dict:
    root = Path(root)
    output_dir = Path(output_dir)
    atlas = load_json(root / '.orchestration/remaining-work/atlas/atlas.json')
    bootstrap_meta, bootstrap_text = load_launch_bootstrap(root)
    excluded = sorted(exclude_task_ids or set())
    entries = select_entries(atlas, exclude_task_ids=set(excluded))
    if not entries:
        raise ValueError('no launchable work on current frontier')

    prompts_dir = output_dir / 'prompts'
    prompts_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries = []
    for i, entry in enumerate(entries, 1):
        core_ref = entry['prompt_core_ref']
        if not core_ref:
            raise ValueError(f"missing prompt core ref for {entry['task_id']}")
        core_path = root / core_ref
        core_text = core_path.read_text(encoding='utf-8')
        digest = hashlib.sha256(core_text.encode('utf-8')).hexdigest()
        if digest != entry['prompt_core_sha256']:
            raise ValueError(f"prompt core hash mismatch for {entry['task_id']}")
        overlay_path = root / entry['overlay_ref'] if entry.get('overlay_ref') else core_path.with_name('overlay.json')
        overlay = load_json(overlay_path)
        _validate_overlay(overlay, entry['task_id'])

        if entry['lane'] == 'VERIFY':
            text = _render_verify_prompt(entry, overlay, core_text, bootstrap_text)
        elif entry['lane'] == 'REPAIR':
            text = _render_repair_prompt(entry, overlay, core_text, bootstrap_text)
        else:
            text = _render_build_prompt(entry, overlay, core_text, bootstrap_text)

        prompt_rel = f"prompts/{i:02d}-{entry['task_id']}.md"
        (output_dir / prompt_rel).write_text(text, encoding='utf-8')
        manifest_entries.append({
            'task_id': entry['task_id'],
            'label': entry['label'],
            'lane': entry['lane'],
            'state': entry['state'],
            'write_mode': entry['write_mode'],
            'prompt_ref': prompt_rel,
            'core_ref': core_ref,
            'overlay_ref': str(overlay_path.relative_to(root)),
            'executor_mode': entry['executor_mode'],
            'resource_class': entry['resource_class'],
        })

    manifest = {
        'schema_version': 'remaining-work-launch-pack.v1',
        'batch_id': batch_id,
        'generated_at_head': generated_at_head,
        'fresh_codex_default': True,
        'excluded_in_flight_task_ids': excluded,
        'instruction': 'Open each numbered prompt in a fresh top-level Codex session unless its executor mode explicitly says otherwise.',
        'launch_bootstrap': {
            'version': bootstrap_meta['version'],
            'sha256': bootstrap_meta['sha256'],
            'ref': bootstrap_meta['ref'],
            'metadata_ref': BOOTSTRAP_META_REF,
            'preflight_script_ref': bootstrap_meta['preflight_script_ref'],
        },
        'entries': manifest_entries,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return manifest


def parse_args():
    p = argparse.ArgumentParser(description='Render the next Remaining Work Launch Pack')
    p.add_argument('--root', default=None)
    p.add_argument('--batch-id', required=True)
    p.add_argument('--generated-at-head', required=True)
    p.add_argument('--output-dir', default=None)
    p.add_argument('--exclude-task', action='append', default=[])
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    output_dir = Path(args.output_dir).resolve() if args.output_dir else root / '.orchestration/remaining-work/launch-packs' / args.batch_id
    manifest = render_pack(root=root, batch_id=args.batch_id, generated_at_head=args.generated_at_head, output_dir=output_dir, exclude_task_ids=set(args.exclude_task))
    print(json.dumps({'status':'PASS','batch_id':args.batch_id,'count':len(manifest['entries']),'manifest':str(output_dir/'manifest.json')}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
