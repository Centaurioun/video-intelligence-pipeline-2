import subprocess
import sys


def test_verifier_repeatability_flags_are_supported():
    result = subprocess.run([sys.executable, "scripts/verify-gate0.py", "--repeatability",
                             "--repeat-comparison-closure", "--synthetic-only"],
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "repeatability=PASS" in result.stdout


def test_verifier_rejects_nonclosed_artifact_count():
    result = subprocess.run([sys.executable, "scripts/verify-gate0.py", "--artifact-count=12"],
                            text=True, capture_output=True)
    assert result.returncode == 30
