"""Regression contract for the Owner-directed removal of development source auth.

Owner decision (2026-10-24, `docs/decisions/ADR-0003-...`):

* Development-time source-authorization enforcement in
  `scripts/verify-workspace.sh` is REMOVED. The verifier reports
  ``DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER``.
* Missing branch/path-bound grants must not block ordinary Root-H or Gate-3
  development (for example a new ``src/vip_fvs/source_snapshot.py``).
* A removed check is reported as DISABLED, never as a successful verification:
  no ``AUTHORIZED_CURRENT`` classification and no ``PASS`` line for source
  authorization may be emitted.
* Unrelated protections remain functional: the high-confidence secret scan,
  tracked-credential-file check, required-path checks, and the ``--require-pushed``
  operational CLI are untouched.
* No equivalent development blocker may be reintroduced under another name.

The module is stdlib-only and directly runnable with ``python3`` (pytest is
optional). It builds throwaway Git repositories so the real workspace state
cannot affect the result.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify-workspace.sh"
SCRIPTS_DIR = REPO_ROOT / "scripts"

DISABLED_MARKER = (
    "DISABLED  development source authorization: "
    "DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER"
)

# Enforcement machinery that must not exist in ordinary development scripts.
FORBIDDEN_SCRIPT_TOKENS = (
    "SOURCE-AUTH DENY",
    "SOURCE-AUTH-PYTHON BEGIN",
    "SOURCE_MUTATION-AUTH",
    "AUTHORIZED_CURRENT",
    "unauthorized source mutation",
    "unexpected source file exists outside authorized paths",
    "root-h-owner-decision-witness",
    "root-h-mutation-base",
)

_CLEAN_ENV_KEYS = (
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
)


def _git_env() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in _CLEAN_ENV_KEYS}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["GIT_AUTHOR_NAME"] = "Source Auth Removal Tests"
    env["GIT_AUTHOR_EMAIL"] = "source-auth-removal@example.invalid"
    env["GIT_COMMITTER_NAME"] = "Source Auth Removal Tests"
    env["GIT_COMMITTER_EMAIL"] = "source-auth-removal@example.invalid"
    return env


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, env=_git_env(), capture_output=True, text=True, check=True
    )


def _write(repo: Path, relpath: str, content: str) -> None:
    full = repo / relpath
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)


def _fake_gh_dir(repo: Path) -> Path:
    fakebin = repo / ".fakebin"
    fakebin.mkdir(parents=True, exist_ok=True)
    gh = fakebin / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'case "$*" in\n'
        "  *\"repo view\"*) printf '%s\\n' "
        "'{\"isPrivate\":true,\"visibility\":\"PRIVATE\","
        "\"defaultBranchRef\":{\"name\":\"main\"},"
        "\"url\":\"https://example.invalid/r\"}' ;;\n"
        "  *) exit 1 ;;\n"
        "esac\n"
    )
    gh.chmod(0o755)
    return fakebin


class SourceAuthorizationRemovalTests(unittest.TestCase):
    """Owner decision: enforcement is DISABLED_BY_OWNER, not satisfied by grants."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory(prefix="source-auth-removal-")
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp = Path(self._tmpdir.name)

    # -- harness ---------------------------------------------------------
    def _make_repo(self, name: str = "repo", extra_files: dict[str, str] | None = None) -> Path:
        repo = self.tmp / name
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main", ".")
        (repo / "scripts").mkdir()
        shutil.copyfile(SCRIPT_PATH, repo / "scripts" / "verify-workspace.sh")
        (repo / "scripts" / "verify-workspace.sh").chmod(0o755)
        for relpath, content in (extra_files or {}).items():
            _write(repo, relpath, content)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "fixture")
        return repo

    def _run_verifier(self, repo: Path, *args: str) -> tuple[int, str, str]:
        env = _git_env()
        env["PATH"] = str(_fake_gh_dir(repo)) + os.pathsep + env.get("PATH", "")
        proc = subprocess.run(
            ["bash", str(repo / "scripts" / "verify-workspace.sh"), *args],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout, proc.stderr

    @staticmethod
    def _fail_lines(stderr: str) -> set[str]:
        return {line for line in stderr.splitlines() if line.startswith("FAIL  ")}

    def _assert_disabled_and_not_blocking(self, stdout: str, stderr: str) -> None:
        combined = stdout + stderr
        self.assertIn(DISABLED_MARKER, stdout)
        self.assertNotIn("FAIL  source authorization", combined)
        self.assertNotIn("FAIL  source mutation authorization", combined)
        self.assertNotIn("SOURCE-AUTH DENY", combined)
        self.assertNotIn("AUTHORIZED_CURRENT", combined)
        self.assertNotIn("UNAUTHORIZED", combined)
        self.assertNotIn("unexpected source file exists outside authorized paths", combined)
        self.assertNotIn("SOURCE_MUTATION", combined)

    # -- behavior --------------------------------------------------------
    def test_verifier_reports_disabled_by_owner(self) -> None:
        repo = self._make_repo()
        _rc, stdout, stderr = self._run_verifier(repo)
        self._assert_disabled_and_not_blocking(stdout, stderr)

    def test_gate3_source_snapshot_is_not_denied_for_missing_grant(self) -> None:
        """PR #139's new source file must not be denied solely by a missing grant."""
        extra = {"src/vip_fvs/source_snapshot.py": '"""Gate-3 source snapshot fixture."""\n'}
        with_file = self._make_repo("with-snapshot", extra)
        without_file = self._make_repo("without-snapshot")
        _rc_a, stdout_a, stderr_a = self._run_verifier(with_file)
        _rc_b, stdout_b, stderr_b = self._run_verifier(without_file)

        self._assert_disabled_and_not_blocking(stdout_a, stderr_a)
        self.assertNotIn("src/vip_fvs/source_snapshot.py", stdout_a + stderr_a)
        self.assertEqual(self._fail_lines(stderr_a), self._fail_lines(stderr_b))

    def test_root_h_style_changes_are_not_denied(self) -> None:
        """Root-H writes (verifier + test changes, authority-adjacent paths) proceed."""
        root_h_files = {
            "tests/scripts/test_verify_workspace_source_authorization.py": "# Root-H regression\n",
            ".orchestration/portfolios/execution-portfolio-20260924-v1/authority/"
            "root-h-owner-decision-witness-registry-20261023-v1.json": "{}\n",
        }
        candidate = self._make_repo("root-h", root_h_files)
        with open(candidate / "scripts" / "verify-workspace.sh", "a", encoding="utf-8") as fh:
            fh.write("\n# Root-H candidate change: ordinary development write.\n")
        _git(candidate, "add", "-A")
        _git(candidate, "commit", "-q", "-m", "root-h candidate change")

        _rc, stdout, stderr = self._run_verifier(candidate)
        self._assert_disabled_and_not_blocking(stdout, stderr)
        self.assertNotIn("Root-H candidate change", stderr)

    def test_missing_administrative_bootstrap_ref_does_not_block(self) -> None:
        """Ordinary development must not need the administrative bootstrap ref."""
        repo = self._make_repo()
        # The throwaway repository intentionally has no canonical admin ref.
        _rc, stdout, stderr = self._run_verifier(repo)
        self._assert_disabled_and_not_blocking(stdout, stderr)
        self.assertNotIn("canonical admin ref", stdout + stderr)

    def test_removed_check_is_not_reported_as_success(self) -> None:
        repo = self._make_repo()
        _rc, stdout, stderr = self._run_verifier(repo)
        self._assert_disabled_and_not_blocking(stdout, stderr)
        pass_lines = [line for line in stdout.splitlines() if line.startswith("PASS")]
        self.assertFalse(
            [line for line in pass_lines if re.search(r"source[- ]authoriz", line, re.IGNORECASE)],
            "removed source-authorization enforcement must not be reported as PASS",
        )
        self.assertEqual(stdout.count(DISABLED_MARKER), 1)

    # -- unrelated protections remain -----------------------------------
    def test_high_confidence_secret_scan_still_fails(self) -> None:
        repo = self._make_repo(
            # Assembled at runtime so no literal credential-shaped token is committed.
            "secret", {"src/leaked.py": 'TOKEN = "' + "ghp_" + "0" * 36 + '"\n'}
        )
        rc, _stdout, stderr = self._run_verifier(repo)
        self.assertNotEqual(rc, 0)
        self.assertIn("high-confidence secret scan matched file(s)", stderr)

    def test_secret_scan_ignores_word_internal_sk_sequence(self) -> None:
        """An ``sk-`` sequence inside an ordinary word is not a credential.

        Historical report paths such as ``task-packet-20261008-0001`` contain the
        substring ``sk-packet-...``.  Without a leading token boundary the
        ``sk-`` detector reported a false credential, producing a blocking
        ``high-confidence secret scan matched file(s)`` failure for unrelated
        audit documents (for example
        ``docs/audits/2026-10-08-branch-preservation-recovery-certification.json``).
        """
        repo = self._make_repo(
            "word-internal-sk",
            {"docs/audits/report.json": '{"path": "task-packet-20261008-0001"}\n'},
        )
        _rc, _stdout, stderr = self._run_verifier(repo)
        scan_failures = [
            line
            for line in self._fail_lines(stderr)
            if "high-confidence secret scan matched file(s)" in line
        ]
        self.assertEqual(scan_failures, [], f"false-positive secret scan: {scan_failures}")

    def test_secret_scan_still_detects_bounded_sk_key(self) -> None:
        repo = self._make_repo(
            # Runtime-assembled so no literal credential-shaped token is committed.
            "sk-key",
            {"src/provider_client.py": 'KEY = "' + "sk-" + "a" * 32 + '"\n'},
        )
        rc, _stdout, stderr = self._run_verifier(repo)
        self.assertNotEqual(rc, 0)
        self.assertIn("high-confidence secret scan matched file(s)", stderr)

    def test_unrelated_verifier_boundaries_are_retained(self) -> None:
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        for retained in (
            "high-confidence secret scan",
            "no tracked credential environment file is present",
            "--require-pushed",
        ):
            self.assertIn(retained, script)

    # -- anti-reintroduction --------------------------------------------
    def test_no_enforcement_remnants_in_scripts(self) -> None:
        offenders: list[str] = []
        for path in sorted(SCRIPTS_DIR.rglob("*")):
            if path.suffix not in {".sh", ".py"} or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for token in FORBIDDEN_SCRIPT_TOKENS:
                if token in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {token}")
        self.assertEqual(offenders, [], "development source-auth enforcement remnants found")

    def test_script_declares_disabled_policy_constant(self) -> None:
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER", script)
        self.assertNotIn("SOURCE-AUTH-PYTHON", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
