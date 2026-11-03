import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'render-remaining-work-launch-pack.py'


def load_mod():
    spec = importlib.util.spec_from_file_location('render_launch_pack', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def node(task_id, *, state='READY', write=None, resource='LIGHTWEIGHT_CPU_TEST', deps=None, weight=1, candidate=None):
    return {
        'id': task_id,
        'level': 'H3',
        'title': f'Title {task_id}',
        'weight': weight,
        'state': state,
        'candidate_generation': candidate,
        'dependencies': deps or [],
        'write_domain': write or [f'src/{task_id}.py'],
        'resource_class': resource,
        'executor_mode': 'PARALLEL_PORTFOLIO',
        'prompt_core_ref': f'.orchestration/remaining-work/prompts/{task_id}/core.md',
        'prompt_core_sha256': 'a' * 64,
    }


def atlas(nodes, leases=None):
    return {'nodes': nodes, 'resource_leases': leases or {
        'LIGHTWEIGHT_CPU_TEST': 16, 'HEAVY_CPU': 2, 'FFMPEG_HEAVY': 2,
        'MODEL_MPS': 2, 'MIXED_HEAVY': 1, 'ENV_ADMIN': 1,
    }}


def ids(entries):
    return [(e['task_id'], e['lane']) for e in entries]


def test_six_independent_ready_builds_coexist_no_four_cap():
    m = load_mod()
    nodes = [node(f'H3-X0{i}') for i in range(1, 7)]
    got = m.select_entries(atlas(nodes))
    assert ids(got) == [(f'H3-X0{i}', 'BUILD') for i in range(1, 7)]


def test_overlapping_build_writers_do_not_coexist():
    m = load_mod()
    nodes = [node('H3-A', write=['src/shared.py'], weight=2), node('H3-B', write=['src/shared.py'], weight=1)]
    got = m.select_entries(atlas(nodes))
    assert ids(got) == [('H3-A', 'BUILD')]


def test_hard_dependency_blocks_even_if_node_was_marked_ready():
    m = load_mod()
    up = node('H3-UP', state='PLANNED')
    down = node('H3-DOWN', deps=[{'node_id':'H3-UP','kind':'HARD_BUILD_DEPENDENCY'}])
    assert ids(m.select_entries(atlas([up, down]))) == []


def test_soft_dependency_unlocks_after_upstream_build_green():
    m = load_mod()
    up = node('H3-UP', state='BUILD_GREEN', candidate={'sha':'b'*40})
    down = node('H3-DOWN', deps=[{'node_id':'H3-UP','kind':'SOFT_BUILD_DEPENDENCY'}])
    assert ids(m.select_entries(atlas([up, down]))) == [('H3-DOWN', 'BUILD')]


def test_verify_read_only_can_coexist_with_overlapping_build():
    m = load_mod()
    verify = node('H3-V', state='VERIFY_READY', write=['src/shared.py'], candidate={'sha':'c'*40})
    build = node('H3-B', write=['src/shared.py'])
    got = m.select_entries(atlas([verify, build]))
    assert set(ids(got)) == {('H3-V','VERIFY'), ('H3-B','BUILD')}
    v = next(e for e in got if e['task_id']=='H3-V')
    assert v['write_mode'] == 'READ_ONLY'
    assert v['executor_mode'] == 'VERIFY_ONLY'


def test_repair_blocks_overlapping_writer_but_unrelated_build_continues():
    m = load_mod()
    repair = node('H3-R', state='REPAIRING', write=['src/shared.py'], candidate={'sha':'d'*40})
    overlap = node('H3-B', write=['src/shared.py'])
    other = node('H3-C', write=['src/other.py'])
    got = m.select_entries(atlas([repair, overlap, other]))
    assert set(ids(got)) == {('H3-R','REPAIR'), ('H3-C','BUILD')}


def test_heavy_resource_lease_bounds_selection():
    m = load_mod()
    nodes = [node(f'H3-H{i}', resource='HEAVY_CPU') for i in range(1,4)]
    got = m.select_entries(atlas(nodes, {'LIGHTWEIGHT_CPU_TEST':16,'HEAVY_CPU':2,'FFMPEG_HEAVY':2,'MODEL_MPS':2,'MIXED_HEAVY':1,'ENV_ADMIN':1}))
    assert len(got) == 2


def test_dirty_or_parked_never_launches():
    m = load_mod()
    nodes = [node('H3-D', state='DIRTY_BY_CONTRACT_DELTA'), node('H3-P', state='PARKED')]
    assert m.select_entries(atlas(nodes)) == []


def test_active_batch_task_can_be_excluded_from_next_pack():
    m = load_mod()
    nodes = [node('H3-A03'), node('H3-NEW')]
    got = m.select_entries(atlas(nodes), exclude_task_ids={'H3-A03'})
    assert ids(got) == [('H3-NEW', 'BUILD')]


def test_render_pack_writes_copy_ready_prompt_and_manifest(tmp_path):
    m = load_mod()
    root = tmp_path
    n = node('H3-A')
    core = root / n['prompt_core_ref']
    core.parent.mkdir(parents=True)
    body = '# CORE\nDo the task.\n'
    core.write_text(body)
    import hashlib
    n['prompt_core_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    overlay = core.with_name('overlay.json')
    overlay.write_text(json.dumps({
        'schema_version':'remaining-work-launch-overlay.v1','task_id':'H3-A','version':'h3-a-overlay-v1',
        'base_sha':'e'*40,'dependency_heads':{},'branch':'execution/h3-a','worktree':None,
        'open_problem_ids':[],'contract_deltas':[],'resource_leases':{'LIGHTWEIGHT_CPU_TEST':16},
        'resolved_model_identity':'gpt-5.6-luna | reasoning=medium | family=LUNA','reconciled_at_head':'f'*40,
    }))
    (root/'.orchestration/remaining-work/atlas').mkdir(parents=True)
    (root/'.orchestration/remaining-work/atlas/atlas.json').write_text(json.dumps(atlas([n])))
    _write_launch_bootstrap_v2(root)
    out = root/'.orchestration/remaining-work/launch-packs/batch-001'
    manifest = m.render_pack(root=root, batch_id='batch-001', generated_at_head='f'*40, output_dir=out)
    assert manifest['schema_version'] == 'remaining-work-launch-pack.v1'
    assert manifest['fresh_codex_default'] is True
    assert manifest['entries'][0]['task_id'] == 'H3-A'
    prompt = (out/manifest['entries'][0]['prompt_ref']).read_text()
    assert 'fresh top-level Codex' in prompt
    assert 'gpt-5.6-luna' in prompt
    assert '# CORE' in prompt
    assert all(line == line.rstrip() for line in prompt.splitlines())


def test_render_pack_uses_atlas_overlay_ref_for_versioned_core(tmp_path):
    m = load_mod()
    root = tmp_path
    n = node('H3-A')
    n['prompt_core_ref'] = '.orchestration/remaining-work/prompts/H3-A/v1.0.1/core.md'
    n['overlay_ref'] = '.orchestration/remaining-work/prompts/H3-A/overlay-successor-001.json'
    core = root / n['prompt_core_ref']
    core.parent.mkdir(parents=True)
    body = '# Versioned CORE\n'
    core.write_text(body)
    import hashlib
    n['prompt_core_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    overlay = root / n['overlay_ref']
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.write_text(json.dumps({
        'schema_version':'remaining-work-launch-overlay.v1','task_id':'H3-A','version':'h3-a-overlay-v1.1',
        'base_sha':'e'*40,'dependency_heads':{},'branch':'execution/h3-a','worktree':None,
        'open_problem_ids':[],'contract_deltas':[],'resource_leases':{'LIGHTWEIGHT_CPU_TEST':16},
        'resolved_model_identity':'gpt-6-luna | reasoning=medium | family=LUNA','reconciled_at_head':'f'*40,
    }))
    (root/'.orchestration/remaining-work/atlas').mkdir(parents=True)
    (root/'.orchestration/remaining-work/atlas/atlas.json').write_text(json.dumps(atlas([n])))
    _write_launch_bootstrap_v2(root)
    out = root/'.orchestration/remaining-work/launch-packs/batch-001'
    manifest = m.render_pack(root=root, batch_id='batch-001', generated_at_head='f'*40, output_dir=out)
    assert manifest['entries'][0]['overlay_ref'] == n['overlay_ref']


def _write_launch_bootstrap_v2(root):
    import hashlib
    template = root / '.orchestration/remaining-work/prompts/_template'
    template.mkdir(parents=True, exist_ok=True)
    text = '# Launch Bootstrap v2\npacket preflight\nworkspace preflight\n'
    ref = '.orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.md'
    (root / ref).write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    script = root / 'scripts/preflight-remaining-work-launch.py'
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text('#!/usr/bin/env python3\n')
    (template / 'launch-bootstrap-v2.json').write_text(json.dumps({
        'schema_version': 'remaining-work-launch-bootstrap.v2',
        'version': 'launch-bootstrap-v2.0.3',
        'sha256': digest,
        'ref': ref,
        'preflight_script_ref': 'scripts/preflight-remaining-work-launch.py',
        'verified_superpowers_skills': ['using-superpowers'],
    }))
    return digest


def test_renderer_embeds_bootstrap_and_binds_manifest_metadata(tmp_path):
    m = load_mod()
    root = tmp_path
    n = node('H3-A')
    core = root / n['prompt_core_ref']
    core.parent.mkdir(parents=True)
    body = '# CORE\nDo the task.\n'
    core.write_text(body)
    import hashlib
    n['prompt_core_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    core.with_name('overlay.json').write_text(json.dumps({
        'schema_version':'remaining-work-launch-overlay.v1','task_id':'H3-A','version':'h3-a-overlay-v1',
        'base_sha':'e'*40,'dependency_heads':{},'branch':'execution/h3-a','worktree':None,
        'open_problem_ids':[],'contract_deltas':[],'resource_leases':{'LIGHTWEIGHT_CPU_TEST':16},
        'resolved_model_identity':'gpt-5.6-luna | reasoning=medium | family=LUNA','reconciled_at_head':'f'*40,
    }))
    (root/'.orchestration/remaining-work/atlas').mkdir(parents=True)
    (root/'.orchestration/remaining-work/atlas/atlas.json').write_text(json.dumps(atlas([n])))
    expected_hash = _write_launch_bootstrap_v2(root)
    out = root/'out'
    pack = m.render_pack(root=root, batch_id='batch', generated_at_head='f'*40, output_dir=out)
    assert pack['launch_bootstrap']['version'] == 'launch-bootstrap-v2.0.3'
    assert pack['launch_bootstrap']['sha256'] == expected_hash
    prompt = (out / pack['entries'][0]['prompt_ref']).read_text()
    assert '## Launch Bootstrap v2' in prompt
    assert 'packet preflight' in prompt
    assert prompt.index('## Launch Bootstrap v2') < prompt.index('## Launch Overlay')


def test_renderer_fails_closed_on_bootstrap_hash_mismatch(tmp_path):
    m = load_mod()
    root = tmp_path
    n = node('H3-A')
    core = root / n['prompt_core_ref']
    core.parent.mkdir(parents=True)
    body = '# CORE\nDo the task.\n'
    core.write_text(body)
    import hashlib
    n['prompt_core_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    core.with_name('overlay.json').write_text(json.dumps({
        'schema_version':'remaining-work-launch-overlay.v1','task_id':'H3-A','version':'h3-a-overlay-v1',
        'base_sha':'e'*40,'dependency_heads':{},'branch':'execution/h3-a','worktree':None,
        'open_problem_ids':[],'contract_deltas':[],'resource_leases':{'LIGHTWEIGHT_CPU_TEST':16},
        'resolved_model_identity':'gpt-5.6-luna | reasoning=medium | family=LUNA','reconciled_at_head':'f'*40,
    }))
    (root/'.orchestration/remaining-work/atlas').mkdir(parents=True)
    (root/'.orchestration/remaining-work/atlas/atlas.json').write_text(json.dumps(atlas([n])))
    _write_launch_bootstrap_v2(root)
    meta = root/'.orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.json'
    payload = json.loads(meta.read_text())
    payload['sha256'] = '0' * 64
    meta.write_text(json.dumps(payload))
    try:
        m.render_pack(root=root, batch_id='batch', generated_at_head='f'*40, output_dir=root/'out')
    except ValueError as exc:
        assert 'bootstrap hash mismatch' in str(exc)
    else:
        raise AssertionError('expected bootstrap hash mismatch to fail closed')
