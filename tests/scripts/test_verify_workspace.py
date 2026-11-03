"""Regression and contract verification tests for scripts/verify-workspace.sh.

Covers V-1, V-2, and V-3 requirements:
1. Canonical main verification (default mode).
2. Valid isolated feature worktree (--feature-worktree mode).
3. Wrong repository / invalid worktree context.
4. Detached HEAD with and without required identity evidence.
5. Entire external reference set absent.
6. Partial external source availability.
7. Reference source/curated file mismatch.
8. .env.local absent and properly ignored.
9. .env.local present but tracked or not ignored.
10. Invalid-option rejection and preservation of --require-pushed behavior
    across focused tests 11–17.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-workspace.sh"


def run_git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def run_verifier(cwd: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    script = cwd / "scripts" / "verify-workspace.sh"
    if not script.is_file():
        script = VERIFY_SCRIPT
    run_env = os.environ.copy()
    if env is not None:
        run_env.update(env)
    return subprocess.run(
        [str(script), *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        env=run_env,
    )


@pytest.fixture
def mock_github_env(tmp_path: Path) -> dict[str, str]:
    """Provide a mock bin directory isolating gh and git ls-remote from network calls."""
    bin_dir = tmp_path / "mock-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    real_git = shutil.which("git")
    assert real_git, "Real git binary not found in PATH"

    gh_script = bin_dir / "gh"
    gh_script.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ -n \"${MOCK_GH_FAIL:-}\" ]]; then\n"
        "  exit 1\n"
        "fi\n"
        "if [[ -n \"${MOCK_GH_EMPTY:-}\" ]]; then\n"
        "  exit 0\n"
        "fi\n"
        "case \"$*\" in\n"
        "  *\"repo view\"*)\n"
        "    if [[ -n \"${MOCK_GH_JSON:-}\" ]]; then\n"
        "      printf '%s\\n' \"$MOCK_GH_JSON\"\n"
        "    else\n"
        "      printf '%s\\n' '{\"isPrivate\":true,\"visibility\":\"PRIVATE\",\"defaultBranchRef\":{\"name\":\"main\"},\"url\":\"https://github.com/Centaurioun/video-intelligence-pipeline\"}'\n"
        "    fi\n"
        "    exit 0\n"
        "    ;;\n"
        "  *)\n"
        "    exit 1\n"
        "    ;;\n"
        "esac\n"
    )
    gh_script.chmod(0o755)

    git_script = bin_dir / "git"
    git_script.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"ls-remote\" ]]; then\n"
        "  if [[ -n \"${MOCK_GIT_LS_REMOTE_FAIL:-}\" ]]; then\n"
        "    exit 2\n"
        "  fi\n"
        "  if [[ -n \"${MOCK_GIT_LS_REMOTE_OUT:-}\" ]]; then\n"
        "    printf '%s\\n' \"$MOCK_GIT_LS_REMOTE_OUT\"\n"
        "  else\n"
        "    printf '18e909dc99e8e229496485b8ab69dc71fa1db9df\\trefs/heads/main\\n'\n"
        "  fi\n"
        "  exit 0\n"
        "fi\n"
        f"exec \"{real_git}\" \"$@\"\n"
    )
    git_script.chmod(0o755)

    return {
        "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
    }


@pytest.fixture(scope="module")
def base_test_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a fast, isolated local clone of REPO_ROOT to serve as base repository."""
    base_dir = tmp_path_factory.mktemp("base-repo") / "repo"
    run_git(REPO_ROOT, "clone", "--shared", str(REPO_ROOT), str(base_dir))
    run_git(base_dir, "remote", "set-url", "origin", "https://github.com/Centaurioun/video-intelligence-pipeline.git")
    # Checkout branch 'main' in the clone
    run_git(base_dir, "checkout", "-B", "main")
    # Copy current candidate verify-workspace.sh into the clone
    shutil.copy2(VERIFY_SCRIPT, base_dir / "scripts" / "verify-workspace.sh")
    return base_dir


@pytest.fixture
def isolated_worktree(base_test_repo: Path, tmp_path: Path):
    """Create a fast, isolated temporary Git worktree from base_test_repo."""
    wt_dir = tmp_path / "wt-feature"
    branch_name = f"test-feature-{tmp_path.name}"
    run_git(base_test_repo, "worktree", "add", "-b", branch_name, str(wt_dir), "HEAD")
    # Ensure wt_dir has the current candidate verify-workspace.sh under test
    shutil.copy2(VERIFY_SCRIPT, wt_dir / "scripts" / "verify-workspace.sh")
    try:
        yield wt_dir, branch_name
    finally:
        run_git(base_test_repo, "worktree", "remove", "--force", str(wt_dir), check=False)
        run_git(base_test_repo, "branch", "-D", branch_name, check=False)


def test_01_canonical_main_verification(base_test_repo: Path, isolated_worktree):
    wt_dir, _ = isolated_worktree

    # Positive: on branch main in base_test_repo, check for 'local branch is main'
    proc_main = run_verifier(base_test_repo)
    assert "PASS  verification mode: canonical-main" in proc_main.stdout
    assert "PASS  local branch is main" in proc_main.stdout

    # Negative: running default mode on a feature branch must fail closed
    proc_feature = run_verifier(wt_dir)
    assert proc_feature.returncode != 0
    assert "FAIL  local branch is not main" in (proc_feature.stdout + proc_feature.stderr)

    # Expected-HEAD identity checks on canonical-main:
    main_head = run_git(base_test_repo, "rev-parse", "HEAD").stdout.strip()
    main_parent = run_git(base_test_repo, "rev-parse", "HEAD~1").stdout.strip()

    # 1. Matching exact SHA via flag passes
    proc_head_good = run_verifier(base_test_repo, "--expected-head", main_head)
    assert f"PASS  canonical main HEAD matches expected: {main_head}" in proc_head_good.stdout
    assert "does not match expected-head" not in (proc_head_good.stdout + proc_head_good.stderr)
    assert "expected HEAD must be an exact 40-character" not in (proc_head_good.stdout + proc_head_good.stderr)

    # 2. Matching exact SHA via explicit --mode canonical-main passes
    proc_mode_good = run_verifier(base_test_repo, "--mode", "canonical-main", "--expected-head", main_head)
    assert f"PASS  canonical main HEAD matches expected: {main_head}" in proc_mode_good.stdout
    assert "does not match expected-head" not in (proc_mode_good.stdout + proc_mode_good.stderr)
    assert "expected HEAD must be an exact 40-character" not in (proc_mode_good.stdout + proc_mode_good.stderr)

    # 3. Non-SHA or malformed revision expressions fail closed
    for bad_head in ("HEAD", "main", "HEAD~1", main_head[:7], main_head.upper(), main_head[:39], main_head + "0", main_head[:-1] + "g"):
        proc_bad = run_verifier(base_test_repo, "--expected-head", bad_head)
        assert proc_bad.returncode != 0
        assert "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA" in (proc_bad.stdout + proc_bad.stderr)

    # 4. Non-existent 40-character hexadecimal SHA fails closed
    proc_nonexist = run_verifier(base_test_repo, "--expected-head", "0" * 40)
    assert proc_nonexist.returncode != 0
    assert "expected HEAD commit does not exist" in (proc_nonexist.stdout + proc_nonexist.stderr)

    # 5. Mismatched commit SHA fails closed
    proc_mismatch = run_verifier(base_test_repo, "--expected-head", main_parent)
    assert proc_mismatch.returncode != 0
    assert "does not match expected-head" in (proc_mismatch.stdout + proc_mismatch.stderr)

    # 6. EXPECTED_HEAD environment variable in canonical-main mode
    env_good = os.environ.copy()
    env_good["EXPECTED_HEAD"] = main_head
    proc_env_good = run_verifier(base_test_repo, env=env_good)
    assert f"PASS  canonical main HEAD matches expected: {main_head}" in proc_env_good.stdout
    assert "does not match expected-head" not in (proc_env_good.stdout + proc_env_good.stderr)
    assert "expected HEAD must be an exact 40-character" not in (proc_env_good.stdout + proc_env_good.stderr)

    env_bad = os.environ.copy()
    env_bad["EXPECTED_HEAD"] = "HEAD"
    proc_env_bad = run_verifier(base_test_repo, env=env_bad)
    assert proc_env_bad.returncode != 0
    assert "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA" in (proc_env_bad.stdout + proc_env_bad.stderr)


def test_02_valid_isolated_feature_worktree(isolated_worktree):
    wt_dir, branch_name = isolated_worktree
    proc = run_verifier(wt_dir, "--feature-worktree")
    combined = proc.stdout + proc.stderr
    assert "PASS  verification mode: feature-worktree" in combined
    assert f"PASS  feature worktree branch is {branch_name}" in combined
    assert "PASS  isolated feature worktree context and HEAD verified" in combined
    assert proc.returncode == 0
    assert "Verification passed with 1 check(s) SKIPPED / NOT_OBSERVED" in proc.stdout


def test_03_wrong_repository_or_invalid_worktree_context(base_test_repo: Path, isolated_worktree, tmp_path: Path):
    wt_dir, branch_name = isolated_worktree

    # Negative 1: Wrong origin remote
    orig_url = run_git(wt_dir, "remote", "get-url", "origin").stdout.strip()
    try:
        run_git(wt_dir, "remote", "set-url", "origin", "https://github.com/adversary/unrelated-repo.git")
        proc = run_verifier(wt_dir, "--feature-worktree")
        assert proc.returncode != 0
        assert "FAIL  origin is unexpected or missing" in (proc.stdout + proc.stderr)
    finally:
        run_git(wt_dir, "remote", "set-url", "origin", orig_url)

    # Negative 2: Directory not registered as a git worktree
    fake_wt = tmp_path / "fake-repo"
    (fake_wt / "scripts").mkdir(parents=True)
    shutil.copy2(VERIFY_SCRIPT, fake_wt / "scripts" / "verify-workspace.sh")
    proc_fake = run_verifier(fake_wt, "--feature-worktree")
    assert proc_fake.returncode != 0
    assert "not a valid Git worktree" in (proc_fake.stdout + proc_fake.stderr)

    # Negative 3: Canonical main directory rejects --feature-worktree mode
    # Feature-worktree mode requires an isolated worktree, not canonical main
    proc_canonical = run_verifier(base_test_repo, "--feature-worktree")
    assert proc_canonical.returncode != 0
    assert "feature-worktree mode requires an isolated feature worktree" in (proc_canonical.stdout + proc_canonical.stderr)

    # Negative 4: Spoofed worktree (forward pointer to real worktree gitdir, but backlink mismatch)
    spoof_dir = tmp_path / "spoof-wt"
    spoof_dir.mkdir(parents=True)
    git_dir_out = run_git(wt_dir, "rev-parse", "--git-dir").stdout.strip()
    (spoof_dir / ".git").write_text(f"gitdir: {git_dir_out}\n")
    (spoof_dir / "scripts").mkdir(parents=True)
    shutil.copy2(VERIFY_SCRIPT, spoof_dir / "scripts" / "verify-workspace.sh")
    proc_spoof = run_verifier(spoof_dir, "--feature-worktree")
    assert proc_spoof.returncode != 0
    assert "bidirectional worktree link verification failed" in (proc_spoof.stdout + proc_spoof.stderr)

    # Negative 5: Worktree checking out branch 'main' rejects --feature-worktree mode
    # Feature-worktree mode is explicitly for feature branches, not main
    wt_main_dir = tmp_path / "wt-main"
    # Create temporary detached branch or switch base to allow checkout of main
    run_git(base_test_repo, "checkout", "-b", "temp-switch-branch")
    try:
        run_git(base_test_repo, "worktree", "add", str(wt_main_dir), "main")
        shutil.copy2(VERIFY_SCRIPT, wt_main_dir / "scripts" / "verify-workspace.sh")
        proc_main_wt = run_verifier(wt_main_dir, "--feature-worktree")
        assert proc_main_wt.returncode != 0
        assert "feature-worktree mode cannot be used on branch main" in (proc_main_wt.stdout + proc_main_wt.stderr)
    finally:
        run_git(base_test_repo, "worktree", "remove", "--force", str(wt_main_dir), check=False)
        run_git(base_test_repo, "checkout", "main")
        run_git(base_test_repo, "branch", "-D", "temp-switch-branch", check=False)


def test_04_detached_head_with_and_without_identity_evidence(isolated_worktree):
    wt_dir, branch_name = isolated_worktree
    head_sha = run_git(wt_dir, "rev-parse", "HEAD").stdout.strip()
    parent_sha = run_git(wt_dir, "rev-parse", "HEAD~1").stdout.strip()

    # Part A: Feature branch mode (attached branch)
    # Reject revision expressions, branch names, malformed SHAs
    for bad_expr in (
        "HEAD", "main", branch_name, "HEAD~1", "HEAD^0",
        head_sha[:7], head_sha.upper(), head_sha[:39], head_sha + "a",
        head_sha[:-1] + "g", "g" * 40, "not-a-sha",
    ):
        proc_bad = run_verifier(wt_dir, "--feature-worktree", "--expected-head", bad_expr)
        assert proc_bad.returncode != 0
        assert "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA" in (proc_bad.stdout + proc_bad.stderr)

    # Valid SHA on feature branch that matches HEAD: passes
    proc_branch_good = run_verifier(wt_dir, "--feature-worktree", "--expected-head", head_sha)
    assert proc_branch_good.returncode == 0
    assert f"PASS  feature worktree branch is {branch_name} (HEAD matches expected: {head_sha})" in proc_branch_good.stdout

    # Valid matching SHA via EXPECTED_HEAD environment variable in feature branch mode: passes
    env_branch = os.environ.copy()
    env_branch["EXPECTED_HEAD"] = head_sha
    proc_env_branch = run_verifier(wt_dir, "--feature-worktree", env=env_branch)
    assert proc_env_branch.returncode == 0
    assert f"PASS  feature worktree branch is {branch_name} (HEAD matches expected: {head_sha})" in proc_env_branch.stdout

    # Non-existent 40-character hexadecimal SHA on feature branch: fails closed
    proc_branch_nonexist = run_verifier(wt_dir, "--feature-worktree", "--expected-head", "0" * 40)
    assert proc_branch_nonexist.returncode != 0
    assert "expected HEAD commit does not exist" in (proc_branch_nonexist.stdout + proc_branch_nonexist.stderr)

    # Valid SHA on feature branch that exists but does not match HEAD: fails closed
    proc_branch_mismatch = run_verifier(wt_dir, "--feature-worktree", "--expected-head", parent_sha)
    assert proc_branch_mismatch.returncode != 0
    assert "does not match expected-head" in (proc_branch_mismatch.stdout + proc_branch_mismatch.stderr)

    # Part B: Detached HEAD mode
    # Detach HEAD in worktree
    run_git(wt_dir, "checkout", "--detach", head_sha)

    # Without identity evidence: MUST fail closed
    proc_no_id = run_verifier(wt_dir, "--feature-worktree")
    assert proc_no_id.returncode != 0
    assert "lacks required identity evidence" in (proc_no_id.stdout + proc_no_id.stderr)

    # Reject revision expressions and invalid SHAs in detached HEAD mode
    for bad_expr in (
        "HEAD", "main", branch_name, "HEAD~1", "HEAD^0",
        head_sha[:7], head_sha.upper(), head_sha[:39], head_sha + "a",
        head_sha[:-1] + "g", "g" * 40, "not-a-sha",
    ):
        proc_bad = run_verifier(wt_dir, "--feature-worktree", "--expected-head", bad_expr)
        assert proc_bad.returncode != 0
        assert "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA" in (proc_bad.stdout + proc_bad.stderr)

    # With non-existent commit sha (40 hex chars but non-existent): MUST fail closed
    proc_bad_id = run_verifier(wt_dir, "--feature-worktree", "--expected-head", "0" * 40)
    assert proc_bad_id.returncode != 0
    assert "expected HEAD commit does not exist" in (proc_bad_id.stdout + proc_bad_id.stderr)

    # With mismatched commit sha (exists in repo, but not HEAD): MUST fail closed
    proc_detached_mismatch = run_verifier(wt_dir, "--feature-worktree", "--expected-head", parent_sha)
    assert proc_detached_mismatch.returncode != 0
    assert "does not match expected identity evidence" in (proc_detached_mismatch.stdout + proc_detached_mismatch.stderr)

    # With correct identity evidence via CLI flag: MUST pass
    proc_good_id = run_verifier(wt_dir, "--feature-worktree", "--expected-head", head_sha)
    assert proc_good_id.returncode == 0
    assert f"PASS  isolated feature worktree has verified detached HEAD: {head_sha}" in proc_good_id.stdout

    # With correct identity evidence via EXPECTED_HEAD environment variable: MUST pass
    env_override = os.environ.copy()
    env_override["EXPECTED_HEAD"] = head_sha
    proc_env = run_verifier(wt_dir, "--feature-worktree", env=env_override)
    assert proc_env.returncode == 0
    assert f"PASS  isolated feature worktree has verified detached HEAD: {head_sha}" in proc_env.stdout

    # With invalid EXPECTED_HEAD environment variable (e.g. HEAD): MUST fail closed
    env_bad = os.environ.copy()
    env_bad["EXPECTED_HEAD"] = "HEAD"
    proc_bad_env = run_verifier(wt_dir, "--feature-worktree", env=env_bad)
    assert proc_bad_env.returncode != 0
    assert "expected HEAD must be an exact 40-character lowercase hexadecimal commit SHA" in (proc_bad_env.stdout + proc_bad_env.stderr)


def test_05_entire_external_reference_set_absent(isolated_worktree):
    wt_dir, _ = isolated_worktree
    # In isolated worktree, external/ is empty or absent.
    external_dir = wt_dir / "external"
    if external_dir.exists():
        shutil.rmtree(external_dir)

    # In canonical-main mode, missing external references must fail closed
    proc_canonical = run_verifier(wt_dir)
    assert proc_canonical.returncode != 0
    assert "FAIL  reference-pack source/map integrity check failed" in (proc_canonical.stdout + proc_canonical.stderr)

    # In feature-worktree mode, absent external references must report SKIPPED / NOT_OBSERVED, not PASS
    proc_feature = run_verifier(wt_dir, "--feature-worktree")
    combined = proc_feature.stdout + proc_feature.stderr
    assert "SKIPPED  reference-pack source/map integrity: SKIPPED / NOT_OBSERVED" in combined
    assert "PASS  reference-pack source/map integrity" not in combined
    assert "check(s) SKIPPED / NOT_OBSERVED" in proc_feature.stdout
    assert proc_feature.returncode == 0

    # Negative: Empty manifest (references: []) must fail closed, NOT skip
    selection_file = wt_dir / "reference-pack" / "selection-manifest.json"
    orig_text = selection_file.read_text(encoding="utf-8")
    try:
        selection_file.write_text(json.dumps({"version": 1, "references": []}))
        proc_empty = run_verifier(wt_dir, "--feature-worktree")
        assert proc_empty.returncode != 0
        assert "reference-pack selection manifest contains no files" in (proc_empty.stdout + proc_empty.stderr)
    finally:
        selection_file.write_text(orig_text)


def test_06_partial_external_source_availability(isolated_worktree):
    wt_dir, _ = isolated_worktree
    # Case A: Partial reference sources (1 out of 132 files)
    one_file = wt_dir / "external" / "videoduplicatefinder" / "README.md"
    one_file.parent.mkdir(parents=True, exist_ok=True)
    one_file.write_text("partial test content\n")

    proc = run_verifier(wt_dir, "--feature-worktree")
    assert proc.returncode != 0
    assert "partially available" in (proc.stdout + proc.stderr)

    # Clean up
    shutil.rmtree(wt_dir / "external")

    # Case B: Inconsistent external directory (contains files/dirs but 0 reference sources match)
    unrelated_file = wt_dir / "external" / "unrelated_pkg" / "dummy.txt"
    unrelated_file.parent.mkdir(parents=True, exist_ok=True)
    unrelated_file.write_text("unrelated file\n")

    proc_inconsistent = run_verifier(wt_dir, "--feature-worktree")
    assert proc_inconsistent.returncode != 0
    assert "external reference set is inconsistent" in (proc_inconsistent.stdout + proc_inconsistent.stderr)
    shutil.rmtree(wt_dir / "external")


def test_07_reference_source_curated_file_mismatch(isolated_worktree):
    wt_dir, _ = isolated_worktree
    # Populate all external reference sources matching curated files
    selection_file = wt_dir / "reference-pack" / "selection-manifest.json"
    manifest = json.loads(selection_file.read_text(encoding="utf-8"))

    # Populate external/ for all references
    for ref in manifest.get("references", []):
        ref_id = ref.get("id")
        for f in ref.get("files", []):
            rel_path = f["source_path"]
            curated_path = wt_dir / "reference-pack" / ref_id / "source" / rel_path
            target_path = wt_dir / "external" / ref_id / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if curated_path.is_file():
                shutil.copy2(curated_path, target_path)
            else:
                target_path.write_text(f"mapped source for {ref_id} {rel_path}\n")

    # Tamper with an existing curated file (twelve_labs_claude_plugin has copy_source: true)
    target_curated = wt_dir / "reference-pack" / "twelve_labs_claude_plugin" / "source" / "README.md"
    target_curated.write_text("tampered content that differs from external source\n")

    proc = run_verifier(wt_dir, "--feature-worktree")
    assert proc.returncode != 0
    assert "FAIL  reference-pack source/map integrity check failed" in (proc.stdout + proc.stderr)


def test_08_env_local_absent_and_properly_ignored(isolated_worktree):
    wt_dir, _ = isolated_worktree
    env_local = wt_dir / "prototypes" / "google-video-analyzer" / ".env.local"
    if env_local.exists():
        env_local.unlink()

    # Must pass when .env.local is absent and ignored
    proc = run_verifier(wt_dir, "--feature-worktree")
    assert proc.returncode == 0
    assert "PASS  prototype .env.local is absent and properly ignored" in proc.stdout


def test_09_env_local_present_but_tracked_or_not_ignored(isolated_worktree):
    wt_dir, _ = isolated_worktree
    env_local = wt_dir / "prototypes" / "google-video-analyzer" / ".env.local"
    env_local.write_text("GEMINI_API_KEY=fake-secret-key-123456789\n")

    # Case A: Tracked in Git
    run_git(wt_dir, "add", "-f", str(env_local))
    proc_tracked = run_verifier(wt_dir, "--feature-worktree")
    assert proc_tracked.returncode != 0
    assert "FAIL  prototype .env.local is tracked in Git" in (proc_tracked.stdout + proc_tracked.stderr)

    # Unstage
    run_git(wt_dir, "reset", "HEAD", str(env_local))

    # Case B: Not covered by gitignore
    proto_gitignore = wt_dir / "prototypes" / "google-video-analyzer" / ".gitignore"
    if proto_gitignore.exists():
        run_git(wt_dir, "rm", "-f", "prototypes/google-video-analyzer/.gitignore")
    gitignore = wt_dir / ".gitignore"
    gitignore_content = gitignore.read_text(encoding="utf-8")
    tampered_gitignore = "\n".join(
        line for line in gitignore_content.splitlines()
        if not line.startswith(".env")
    )
    gitignore.write_text(tampered_gitignore)

    proc_not_ignored = run_verifier(wt_dir, "--feature-worktree")
    assert proc_not_ignored.returncode != 0
    assert "FAIL  prototype .env.local is not covered by gitignore" in (proc_not_ignored.stdout + proc_not_ignored.stderr)

    # Restore gitignore
    gitignore.write_text(gitignore_content)
    run_git(wt_dir, "checkout", "HEAD", "--", ".gitignore", "prototypes/google-video-analyzer/.gitignore", check=False)

    # Case C: Symbolic link at .env.local must fail closed
    env_local.unlink()
    env_local.symlink_to("/nonexistent/target")
    proc_symlink = run_verifier(wt_dir, "--feature-worktree")
    assert proc_symlink.returncode != 0
    assert "must not be a symbolic link" in (proc_symlink.stdout + proc_symlink.stderr)
    env_local.unlink()

    # Case D: Directory at .env.local must fail closed
    env_local.mkdir()
    proc_dir = run_verifier(wt_dir, "--feature-worktree")
    assert proc_dir.returncode != 0
    assert "is a directory" in (proc_dir.stdout + proc_dir.stderr)
    env_local.rmdir()


def github_metadata_env(
    mock_github_env: dict[str, str], metadata: dict[str, object]
) -> dict[str, str]:
    env = dict(mock_github_env)
    env["MOCK_GH_JSON"] = json.dumps(metadata)
    return env


def verifier_output(proc: subprocess.CompletedProcess[str]) -> str:
    return proc.stdout + proc.stderr


def test_10_invalid_option_rejection_is_preserved(isolated_worktree):
    wt_dir, _ = isolated_worktree
    proc = run_verifier(wt_dir, "--bogus-flag")

    assert proc.returncode == 2
    assert "usage:" in verifier_output(proc)


def test_11_require_pushed_canonical_main_behavior(base_test_repo: Path, mock_github_env):
    proc_pushed = run_verifier(base_test_repo, "--require-pushed", env=mock_github_env)
    assert "PASS  remote main exists and is the GitHub default branch" in proc_pushed.stdout
    assert "PASS  GitHub repository visibility is private" in proc_pushed.stdout
    assert "FAIL  remote main/default-branch verification failed" not in verifier_output(proc_pushed)

    env_ls_fail = dict(mock_github_env)
    env_ls_fail["MOCK_GIT_LS_REMOTE_FAIL"] = "1"
    proc_remote_missing = run_verifier(base_test_repo, "--require-pushed", env=env_ls_fail)
    assert proc_remote_missing.returncode != 0
    assert "FAIL  remote main/default-branch verification failed" in verifier_output(proc_remote_missing)

    proc_without_requirement = run_verifier(base_test_repo, env=env_ls_fail)
    assert "remote main exists and is the GitHub default branch" not in proc_without_requirement.stdout
    assert "FAIL  remote main/default-branch verification failed" not in verifier_output(proc_without_requirement)


def test_12_require_pushed_succeeds_in_feature_worktree(isolated_worktree, mock_github_env):
    wt_dir, _ = isolated_worktree
    proc = run_verifier(wt_dir, "--feature-worktree", "--require-pushed", env=mock_github_env)

    assert proc.returncode == 0
    assert "PASS  remote main exists and is the GitHub default branch" in proc.stdout
    assert "PASS  GitHub repository visibility is private" in proc.stdout
    assert "Verification passed with 1 check(s) SKIPPED / NOT_OBSERVED" in proc.stdout


def test_13_require_pushed_rejects_non_main_or_missing_default_branch(
    isolated_worktree, mock_github_env
):
    wt_dir, _ = isolated_worktree
    default_branches = (
        {"name": "develop"},
        None,
    )

    for default_branch in default_branches:
        env = github_metadata_env(mock_github_env, {
            "isPrivate": True,
            "visibility": "PRIVATE",
            "defaultBranchRef": default_branch,
            "url": "https://github.com/Centaurioun/video-intelligence-pipeline",
        })
        proc = run_verifier(wt_dir, "--feature-worktree", "--require-pushed", env=env)

        assert proc.returncode != 0
        assert "FAIL  remote main/default-branch verification failed" in verifier_output(proc)


def test_14_require_pushed_rejects_unavailable_remote_main(isolated_worktree, mock_github_env):
    wt_dir, _ = isolated_worktree
    env = dict(mock_github_env)
    env["MOCK_GIT_LS_REMOTE_FAIL"] = "1"
    proc = run_verifier(wt_dir, "--feature-worktree", "--require-pushed", env=env)

    assert proc.returncode != 0
    assert "FAIL  remote main/default-branch verification failed" in verifier_output(proc)


def test_15_require_pushed_rejects_public_repository(isolated_worktree, mock_github_env):
    wt_dir, _ = isolated_worktree
    env = github_metadata_env(mock_github_env, {
        "isPrivate": False,
        "visibility": "PUBLIC",
        "defaultBranchRef": {"name": "main"},
        "url": "https://github.com/Centaurioun/video-intelligence-pipeline",
    })
    proc = run_verifier(wt_dir, "--feature-worktree", "--require-pushed", env=env)

    assert proc.returncode != 0
    assert "FAIL  GitHub repository privacy could not be verified" in verifier_output(proc)


@pytest.mark.parametrize("metadata_case", ("cli failure", "empty output", "malformed JSON", "invalid shape"))
def test_16_require_pushed_fails_closed_on_invalid_github_metadata(
    isolated_worktree, mock_github_env, metadata_case: str
):
    wt_dir, _ = isolated_worktree
    env = dict(mock_github_env)
    if metadata_case == "cli failure":
        env["MOCK_GH_FAIL"] = "1"
    elif metadata_case == "empty output":
        env["MOCK_GH_EMPTY"] = "1"
    elif metadata_case == "malformed JSON":
        env["MOCK_GH_JSON"] = "{invalid json content"
    else:
        env["MOCK_GH_JSON"] = "[]"

    proc = run_verifier(wt_dir, "--feature-worktree", "--require-pushed", env=env)
    output = verifier_output(proc)

    assert proc.returncode != 0
    assert "FAIL  GitHub repository privacy could not be verified" in output
    assert "FAIL  remote main/default-branch verification failed" in output
    assert "Traceback" not in output
    assert "JSONDecodeError" not in output
    assert "AttributeError" not in output


def test_17_require_pushed_is_optional_in_feature_worktree(isolated_worktree, mock_github_env):
    wt_dir, _ = isolated_worktree
    env = dict(mock_github_env)
    env["MOCK_GIT_LS_REMOTE_FAIL"] = "1"
    proc = run_verifier(wt_dir, "--feature-worktree", env=env)

    assert proc.returncode == 0
    assert "remote main exists and is the GitHub default branch" not in proc.stdout
