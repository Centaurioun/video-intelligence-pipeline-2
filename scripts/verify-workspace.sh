#!/usr/bin/env bash
# Workspace verification through post-architecture audit. No repository, source,
# media, or remote mutation occurs.
set -uo pipefail

workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
require_pushed=0
verification_mode="canonical-main"
expected_head="${EXPECTED_HEAD:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --require-pushed)
      require_pushed=1
      shift
      ;;
    --feature-worktree)
      verification_mode="feature-worktree"
      shift
      ;;
    --mode)
      if [[ $# -lt 2 || -z "$2" ]]; then
        printf 'usage: %s [--require-pushed] [--feature-worktree] [--expected-head <commit>] [--mode canonical-main|feature-worktree]\n' "$0" >&2
        exit 2
      fi
      case "$2" in
        canonical-main|feature-worktree)
          verification_mode="$2"
          ;;
        *)
          printf 'usage: %s [--require-pushed] [--feature-worktree] [--expected-head <commit>] [--mode canonical-main|feature-worktree]\n' "$0" >&2
          exit 2
          ;;
      esac
      shift 2
      ;;
    --expected-head)
      if [[ $# -lt 2 || -z "$2" ]]; then
        printf 'usage: %s [--require-pushed] [--feature-worktree] [--expected-head <commit>] [--mode canonical-main|feature-worktree]\n' "$0" >&2
        exit 2
      fi
      expected_head="$2"
      shift 2
      ;;
    *)
      printf 'usage: %s [--require-pushed] [--feature-worktree] [--expected-head <commit>] [--mode canonical-main|feature-worktree]\n' "$0" >&2
      exit 2
      ;;
  esac
done
cd "$workspace_root"

failures=0
skipped=0

pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1" >&2; failures=$((failures + 1)); }
skip() { printf 'SKIPPED  %s\n' "$1"; skipped=$((skipped + 1)); }

pass "verification mode: $verification_mode"

check_file() {
  local check_path="$1"
  [[ -e "$check_path" ]] && pass "present: $check_path" || fail "missing: $check_path"
}

for required_path in \
  README.md AGENTS.md .gitignore .env.example Video_Intelligence_Pipeline_Raporu_v1.0.md \
  docs/INDEX.md docs/audits/ASTRA_ARCHITECTURE_REVIEW_BRIEF.md \
  docs/audits/PRE_ASTRA_EVIDENCE_SYNTHESIS.md \
  docs/audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md docs/audits/ASTRA_SIX_CYCLE_LEDGER.md \
  docs/audits/POST_ASTRA_SIX_CYCLE_REFINEMENT.md \
  docs/architecture/ASTRA_DECISION_REGISTER.md docs/architecture/CANONICAL_CONTRACTS.md \
  docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md \
  docs/implementation-spec-v1.1.md docs/audits/AUTHORITATIVE_REPORT_INTEGRITY.sha256 \
  docs/audits/SECRET_SCAN.md docs/audits/PHASE_0_REQUIREMENT_TRACEABILITY.md \
  docs/audits/PHASE_0_SIX_CYCLE_LEDGER.md \
  reference-pack/README.md reference-pack/manifest.yaml reference-pack/selection-manifest.json \
  scripts/bootstrap-references.py scripts/build-reference-pack.py scripts/verify-workspace.sh \
  src/README.md prototypes/google-video-analyzer/PHASE_0_RESEARCH_NOTE.md; do
  check_file "$required_path"
done

pre_astra_memo_count="$(find docs/research/pre-astra -maxdepth 1 -type f -name '[0-9][0-9]-*.md' | wc -l | tr -d ' ')"
if [[ "$pre_astra_memo_count" == "12" ]]; then
  pass 'Phase-0.5 has all 12 first-wave evidence memos'
else
  fail "Phase-0.5 first-wave memo count is ${pre_astra_memo_count}, expected 12"
fi

pre_astra_critique_count="$(find docs/research/pre-astra/cross-critiques -maxdepth 1 -type f -name '[0-9][0-9]-*.md' | wc -l | tr -d ' ')"
if [[ "$pre_astra_critique_count" == "6" ]]; then
  pass 'Phase-0.5 has all 6 cross-critiques'
else
  fail "Phase-0.5 cross-critique count is ${pre_astra_critique_count}, expected 6"
fi

astra_memo_count="$(find docs/research/astra -maxdepth 1 -type f -name '[0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$astra_memo_count" -ge 4 ]]; then
  pass "architecture audit retains ${astra_memo_count} persisted reviewer memos"
else
  fail "architecture reviewer memo count is ${astra_memo_count}, expected at least 4 persisted memos"
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  pass 'valid local Git repository'
else
  fail 'not a valid local Git repository'
fi

if [[ "$verification_mode" == "canonical-main" ]]; then
  [[ "$(git branch --show-current 2>/dev/null)" == "main" ]] && pass 'local branch is main' || fail 'local branch is not main'
  if [[ -n "$expected_head" ]]; then
    if [[ ! "$expected_head" =~ ^[0-9a-f]{40}$ ]]; then
      fail "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA: $expected_head"
    elif ! git cat-file -e "${expected_head}^{commit}" 2>/dev/null; then
      fail "expected HEAD commit does not exist: $expected_head"
    else
      actual_head="$(git rev-parse --verify HEAD 2>/dev/null || true)"
      if [[ "$actual_head" != "$expected_head" ]]; then
        fail "canonical main HEAD ($actual_head) does not match expected-head ($expected_head)"
      else
        pass "canonical main HEAD matches expected: $expected_head"
      fi
    fi
  fi
else
  git_dir="$(git rev-parse --git-dir 2>/dev/null || true)"
  git_common_dir="$(git rev-parse --git-common-dir 2>/dev/null || true)"
  is_inside="$(git rev-parse --is-inside-work-tree 2>/dev/null || true)"

  if [[ "$is_inside" != "true" || -z "$git_dir" || -z "$git_common_dir" ]]; then
    fail 'current directory is not a valid Git worktree'
  else
    abs_git_dir="$(cd "$git_dir" 2>/dev/null && pwd -P)"
    abs_common_dir="$(cd "$git_common_dir" 2>/dev/null && pwd -P)"

    if [[ "$abs_git_dir" == "$abs_common_dir" ]]; then
      fail 'feature-worktree mode requires an isolated feature worktree, but current directory is the canonical main worktree'
    elif [[ "$abs_git_dir" != "$abs_common_dir"/worktrees/* ]]; then
      fail 'current directory is not a registered linked Git worktree'
    elif [[ ! -f "$abs_git_dir/gitdir" ]]; then
      fail 'worktree gitdir metadata is missing or corrupted'
    else
      canonical_gitfile="$(pwd -P)/.git"
      if [[ -f "$canonical_gitfile" ]]; then
        recorded_gitdir="$(sed -n 's/^gitdir: //p' "$canonical_gitfile" | tr -d '\r\n')"
        if [[ "$recorded_gitdir" = /* ]]; then
          abs_recorded_gitdir="$(cd "$recorded_gitdir" 2>/dev/null && pwd -P)"
        else
          abs_recorded_gitdir="$(cd "$(dirname "$canonical_gitfile")" 2>/dev/null && cd "$recorded_gitdir" 2>/dev/null && pwd -P)"
        fi
      else
        abs_recorded_gitdir=""
      fi

      recorded_backlink="$(cat "$abs_git_dir/gitdir" 2>/dev/null | tr -d '\r\n')"
      if [[ "$recorded_backlink" = /* ]]; then
        abs_backlink="$(cd "$(dirname "$recorded_backlink")" 2>/dev/null && pwd -P)/$(basename "$recorded_backlink")"
      else
        abs_backlink="$(cd "$abs_git_dir" 2>/dev/null && cd "$(dirname "$recorded_backlink")" 2>/dev/null && pwd -P)/$(basename "$recorded_backlink")"
      fi

      if [[ -z "$abs_recorded_gitdir" || "$abs_recorded_gitdir" != "$abs_git_dir" ]]; then
        fail 'bidirectional worktree link verification failed (worktree gitdir pointer mismatch)'
      elif [[ -z "$recorded_backlink" || ("$abs_backlink" != "$canonical_gitfile" && "$abs_backlink" != "$(pwd -P)") ]]; then
        fail 'bidirectional worktree link verification failed (common gitdir backlink mismatch)'
      else
        actual_head="$(git rev-parse --verify HEAD 2>/dev/null || true)"
        if [[ -z "$actual_head" ]] || ! git cat-file -e "${actual_head}^{commit}" 2>/dev/null; then
          fail "worktree HEAD commit object is missing or corrupted: ${actual_head:-<empty>}"
        else
          current_branch="$(git branch --show-current 2>/dev/null || true)"
          if [[ -n "$current_branch" ]]; then
            if [[ "$current_branch" == "main" ]]; then
              fail 'feature-worktree mode cannot be used on branch main; use canonical-main mode'
            elif ! git show-ref --verify --quiet "refs/heads/$current_branch"; then
              fail "worktree branch ref is invalid: refs/heads/$current_branch"
            elif [[ -n "$expected_head" ]]; then
              if [[ ! "$expected_head" =~ ^[0-9a-f]{40}$ ]]; then
                fail "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA: $expected_head"
              elif ! git cat-file -e "${expected_head}^{commit}" 2>/dev/null; then
                fail "expected HEAD commit does not exist: $expected_head"
              elif [[ "$actual_head" != "$expected_head" ]]; then
                fail "feature branch HEAD ($actual_head) does not match expected-head ($expected_head)"
              else
                pass 'isolated feature worktree context and HEAD verified'
                pass "feature worktree branch is $current_branch (HEAD matches expected: $expected_head)"
              fi
            else
              pass 'isolated feature worktree context and HEAD verified'
              pass "feature worktree branch is $current_branch"
            fi
          else
            if git symbolic-ref -q HEAD >/dev/null 2>&1; then
              fail 'worktree branch state is inconsistent'
            elif [[ -z "$expected_head" ]]; then
              fail 'detached HEAD in feature worktree lacks required identity evidence (supply --expected-head <commit>)'
            elif [[ ! "$expected_head" =~ ^[0-9a-f]{40}$ ]]; then
              fail "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA: $expected_head"
            elif ! git cat-file -e "${expected_head}^{commit}" 2>/dev/null; then
              fail "expected HEAD commit does not exist: $expected_head"
            elif [[ "$actual_head" != "$expected_head" ]]; then
              fail "detached HEAD ($actual_head) does not match expected identity evidence ($expected_head)"
            else
              pass 'isolated feature worktree context and HEAD verified'
              pass "isolated feature worktree has verified detached HEAD: $actual_head"
            fi
          fi
        fi
      fi
    fi
  fi
fi

origin_url="$(git remote get-url origin 2>/dev/null || true)"
case "$origin_url" in
  git@github.com:Centaurioun/video-intelligence-pipeline.git|https://github.com/Centaurioun/video-intelligence-pipeline.git)
    pass 'origin targets Centaurioun/video-intelligence-pipeline'
    ;;
  *) fail "origin is unexpected or missing: ${origin_url:-<none>}" ;;
esac

if (cd "$workspace_root" && shasum -a 256 -c docs/audits/AUTHORITATIVE_REPORT_INTEGRITY.sha256 >/dev/null 2>&1); then
  pass 'authoritative v1.0 report matches pre-bootstrap SHA-256'
else
  fail 'authoritative v1.0 report hash mismatch'
fi

if rg -q '^\*\*STATUS: GATE0_SPEC_DRAFT — REVIEW REQUIRED; IMPLEMENTATION NOT APPROVED\*\*$' docs/implementation-spec-v1.1.md; then
  pass 'implementation spec is a bounded Gate-0 draft and remains review-only'
else
  fail 'implementation spec lifecycle status is missing or implementation-approved'
fi

if rg -q 'AUDIO_OBSERVED' AGENTS.md \
  && rg -q 'MEASURED.*MATCHED' AGENTS.md \
  && rg -q -U 'NOT_OBSERVED[[:space:][:print:]]{0,160}not[[:space:][:print:]]{0,80}evidence class' AGENTS.md; then
  pass 'workspace guidance reflects the approved assertion-level evidence taxonomy'
else
  fail 'workspace guidance evidence taxonomy is stale or incomplete'
fi

if rg -q '0\.0, 0\.5, 1\.0' docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md \
  && ! rg -q '0\.25-second steps.*2 FPS|0\.25 \+ 0\.5k.*2 FPS' docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md docs/research/astra/05-benchmark.md; then
  pass 'Gate-0 2 FPS schedule is internally consistent at 0.5-second intervals'
else
  fail 'Gate-0 sampling schedule contains a 2-FPS arithmetic inconsistency'
fi

if rg -q 'deepseek-v4-flash-vision-exp' docs/audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md \
  && rg -q 'deepseek-v4-flash-vision-exp' docs/research/astra/03-provider.md \
  && rg -q 'retired|compatibility|V4\.1-Flash' docs/audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md docs/research/astra/03-provider.md; then
  pass 'current DeepSeek model retirement and compatibility-route correction is reflected in architecture artifacts'
else
  fail 'DeepSeek model retirement/compatibility provenance correction is missing'
fi

if rg -q 'Architecture audit complete' README.md \
  && rg -q 'GATE-0 IMPLEMENTATION SPECIFICATION' README.md; then
  pass 'README points to Gate-0 specification drafting as the next planning step'
else
  fail 'README lifecycle state is stale'
fi

if rg -q '\| D28 \|.*\| `REVERSIBLE` \|' docs/architecture/ASTRA_DECISION_REGISTER.md; then
  pass 'Gate-0 diagnostic thresholds are reversible across protocol versions and frozen per run'
else
  fail 'D28 threshold lifecycle is inconsistent with the Gate-0 contract'
fi

if ruby -ryaml -e 'd=YAML.load_file(ARGV[0]); abort unless d.is_a?(Hash) && d.fetch("references").length == 15' reference-pack/manifest.yaml >/dev/null 2>&1; then
  pass 'manifest.yaml parses and records 15 references'
else
  fail 'manifest.yaml does not parse or lacks 15 references'
fi

if python3 -m json.tool scripts/reference-sources.json >/dev/null 2>&1 \
  && python3 -m json.tool reference-pack/selection-manifest.json >/dev/null 2>&1; then
  pass 'reference configuration JSON parses'
else
  fail 'reference configuration JSON does not parse'
fi

if python3 -m py_compile scripts/bootstrap-references.py scripts/build-reference-pack.py >/dev/null 2>&1; then
  pass 'Python bootstrap and curation scripts compile'
else
  fail 'Python bootstrap or curation script does not compile'
fi

if python3 scripts/bootstrap-references.py --dry-run >/dev/null 2>&1; then
  pass 'reference bootstrap safely re-verifies all pinned sparse checkouts'
else
  fail 'reference bootstrap re-verification failed'
fi

ref_stats="$(python3 -c '
import json, sys
from pathlib import Path

root = Path(".")
selection_file = root / "reference-pack" / "selection-manifest.json"
if not selection_file.is_file():
    print("NO_MANIFEST")
    sys.exit(0)

try:
    selection = json.loads(selection_file.read_text(encoding="utf-8"))
    references = selection.get("references")
    if not isinstance(references, list):
        print("CORRUPT_MANIFEST")
        sys.exit(0)
except Exception:
    print("CORRUPT_MANIFEST")
    sys.exit(0)

external_root = root / "external"
total = 0
found = 0

for ref in references:
    if not isinstance(ref, dict):
        print("CORRUPT_MANIFEST")
        sys.exit(0)
    ref_id = ref.get("id")
    files = ref.get("files")
    if not isinstance(ref_id, str) or not isinstance(files, list):
        print("CORRUPT_MANIFEST")
        sys.exit(0)
    ref_dir = external_root / ref_id
    for f in files:
        if not isinstance(f, dict):
            print("CORRUPT_MANIFEST")
            sys.exit(0)
        source_path = f.get("source_path")
        if not isinstance(source_path, str) or not source_path or source_path.startswith("/"):
            print("CORRUPT_MANIFEST")
            sys.exit(0)
        total += 1
        try:
            cand = (ref_dir / source_path).resolve()
            cand.relative_to(ref_dir.resolve())
        except (ValueError, RuntimeError):
            print("CORRUPT_MANIFEST")
            sys.exit(0)
        if cand.is_file():
            found += 1

has_extraneous = False
if external_root.exists():
    allowed_ignored = {".phase0-ignore-sentinel", ".DS_Store"}
    for item in external_root.iterdir():
        if item.name not in allowed_ignored:
            has_extraneous = True
            break

if total == 0:
    print("EMPTY_MANIFEST")
elif has_extraneous and found == 0:
    print("INCONSISTENT_EXTERNAL")
else:
    print(f"{found}/{total}")
' 2>/dev/null || echo "ERROR")"

ref_found="$(cut -d'/' -f1 <<<"$ref_stats" 2>/dev/null || true)"
ref_total="$(cut -d'/' -f2 <<<"$ref_stats" 2>/dev/null || true)"

if [[ "$ref_stats" == "NO_MANIFEST" || "$ref_stats" == "CORRUPT_MANIFEST" || "$ref_stats" == "ERROR" ]]; then
  fail 'reference-pack selection manifest could not be read or is corrupt'
elif [[ "$ref_stats" == "EMPTY_MANIFEST" ]]; then
  fail 'reference-pack selection manifest contains no files'
elif [[ "$ref_stats" == "INCONSISTENT_EXTERNAL" ]]; then
  fail 'external directory contains files or directories, but no reference sources were found; external reference set is inconsistent'
elif [[ ! "$ref_found" =~ ^[0-9]+$ || ! "$ref_total" =~ ^[0-9]+$ ]]; then
  fail 'reference-pack source statistics could not be parsed'
elif [[ "$ref_total" -eq 0 ]]; then
  fail 'reference-pack selection manifest contains no files'
elif [[ "$ref_found" -eq 0 ]]; then
  if [[ "$verification_mode" == "feature-worktree" ]]; then
    skip 'reference-pack source/map integrity: SKIPPED / NOT_OBSERVED (external reference sources unavailable in isolated worktree)'
  else
    fail 'reference-pack source/map integrity check failed (external reference sources are absent in canonical main)'
  fi
elif [[ "$ref_found" -gt 0 && "$ref_found" -lt "$ref_total" ]]; then
  fail "reference sources partially available (${ref_found}/${ref_total}); external reference set is incomplete or inconsistent"
else
  if python3 scripts/build-reference-pack.py --check >/dev/null 2>&1; then
    pass 'reference-pack source/map integrity check passes'
  else
    fail 'reference-pack source/map integrity check failed'
  fi
fi

if git check-ignore -q external/.phase0-ignore-sentinel; then
  pass 'external/ is ignored'
else
  fail 'external/ is not ignored'
fi

if [[ -z "$(git ls-files external)" ]]; then
  pass 'no external checkout is tracked'
else
  fail 'an external checkout is tracked'
fi

if python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('reference-pack/selection-manifest.json').read_text())
required_headings = {
    'Source identity', 'Exact analyzed revision', 'Purpose',
    'Why it matters to this project', 'Relevant architecture', 'Data flow',
    'Relevant interfaces', 'Reuse hypothesis', 'Key files',
    'What was intentionally omitted from the curated pack',
    'Known limitations / outdated assumptions', 'Open architecture questions',
    'Verification state',
}
for ref in data['references']:
    note = Path('reference-pack') / ref['id'] / 'NOTES.md'
    if not note.is_file():
        raise SystemExit(f'missing note: {note}')
    headings = {
        line[2:].strip() for line in note.read_text(encoding='utf-8').splitlines()
        if line.startswith('# ')
    }
    if headings != required_headings:
        raise SystemExit(f'NOTES heading contract mismatch: {note}')
    if not ref.get('copy_source', True) and (Path('reference-pack') / ref['id'] / 'source').exists():
        raise SystemExit(f'prohibited raw source snapshot present: {ref["id"]}')
PY
then
  pass 'all reference notes satisfy the 13-heading contract and copy-policy boundaries hold'
else
  fail 'reference note heading or copy-policy boundary check failed'
fi

if [[ ! -e video-analyzer && -d prototypes/google-video-analyzer ]]; then
  pass 'Google Video Analyzer has one canonical prototype location'
else
  fail 'Google Video Analyzer source is duplicated or missing'
fi

prototype_env="prototypes/google-video-analyzer/.env.local"
if git ls-files --error-unmatch "$prototype_env" >/dev/null 2>&1; then
  fail 'prototype .env.local is tracked in Git'
elif ! git check-ignore -q "$prototype_env"; then
  fail 'prototype .env.local is not covered by gitignore'
elif [[ -L "$prototype_env" ]]; then
  fail 'prototype .env.local must not be a symbolic link'
elif [[ -d "$prototype_env" ]]; then
  fail 'prototype .env.local is a directory, expected regular file'
elif [[ -f "$prototype_env" ]]; then
  pass 'prototype .env.local remains local and ignored'
elif [[ ! -e "$prototype_env" ]]; then
  pass 'prototype .env.local is absent and properly ignored'
else
  fail 'prototype .env.local exists but is not a regular file'
fi

if rg -q "gemini-2\.5-flash" prototypes/google-video-analyzer/api.ts \
  && rg -q 'KNOWN SECURITY/ARCHITECTURE ISSUE' prototypes/google-video-analyzer/PHASE_0_RESEARCH_NOTE.md; then
  pass 'prototype model state and client-key issue are documented'
else
  fail 'prototype model state or client-key issue is undocumented'
fi

tracked_env_paths="$(git ls-files | rg '(^|/)\.env($|\.)' | rg -v '^\.env\.example$' || true)"
if [[ -z "$tracked_env_paths" ]]; then
  pass 'no tracked credential environment file is present'
else
  fail "tracked credential environment file(s): ${tracked_env_paths//$'\n'/, }"
fi

secret_matches="$(git grep --cached -IlE \
  -e 'AIza[0-9A-Za-z_-]{20,}' \
  -e 'AKIA[0-9A-Z]{16}' \
  -e 'ASIA[0-9A-Z]{16}' \
  -e 'gh[pousr]_[A-Za-z0-9_]{20,}' \
  -e 'github_pat_[A-Za-z0-9_]{20,}' \
  -e '(^|[^[:alnum:]])sk-[A-Za-z0-9_-]{20,}' \
  -e 'tlk_[A-Za-z0-9_-]{20,}' \
  -e 'xox[baprs]-[A-Za-z0-9-]{20,}' \
  -e '-----BEGIN( [A-Z]+)? PRIVATE KEY-----' 2>/dev/null || true)"
if [[ -z "$secret_matches" ]]; then
  pass 'high-confidence secret scan has no tracked-file matches'
else
  fail "high-confidence secret scan matched file(s): ${secret_matches//$'\n'/, }"
fi

# Development-time source-authorization enforcement was removed by explicit
# Owner decision on 2026-10-24. See
# docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md.
# A removed check is reported as DISABLED, never as a successful verification,
# and it contributes no failure to this verifier.
DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER
printf 'DISABLED  development source authorization: DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=%s\n' \
  "$DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT"

if command -v gh >/dev/null 2>&1; then
  github_meta="$(gh repo view Centaurioun/video-intelligence-pipeline --json isPrivate,visibility,defaultBranchRef,url 2>/dev/null || true)"
  if [[ -n "$github_meta" ]] && python3 -c 'import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if d.get("isPrivate") and d.get("visibility")=="PRIVATE" else 1)' <<<"$github_meta" 2>/dev/null; then
    pass 'GitHub repository visibility is private'
  else
    fail 'GitHub repository privacy could not be verified'
  fi
  if [[ $require_pushed -eq 1 ]]; then
    if [[ -n "$github_meta" ]] && python3 -c 'import json,sys; d=json.load(sys.stdin); b=d.get("defaultBranchRef") or {}; raise SystemExit(0 if b.get("name")=="main" else 1)' <<<"$github_meta" 2>/dev/null \
      && git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
      pass 'remote main exists and is the GitHub default branch'
    else
      fail 'remote main/default-branch verification failed'
    fi
  fi
else
  fail 'GitHub CLI is unavailable for privacy verification'
fi

if [[ $failures -gt 0 ]]; then
  if [[ $skipped -gt 0 ]]; then
    printf 'Verification failed with %d failure(s) (%d check(s) skipped).\n' "$failures" "$skipped" >&2
  else
    printf 'Verification failed with %d failure(s).\n' "$failures" >&2
  fi
  exit 1
fi

if [[ $skipped -gt 0 ]]; then
  printf 'Verification passed with %d check(s) SKIPPED / NOT_OBSERVED.\n' "$skipped"
else
  printf 'Verification passed.\n'
fi
