"""Fail-closed consistency check for Task 5's exact pytest/JUnit population."""

import argparse
import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


EXPECTED_NODEIDS_SHA256 = "f729b01a4233a8a58d226104df724dea8f728e76201414e41c3ef9c59bf96664"
EXPECTED_CLASSNAME = "tests.contracts.test_post_mega17_receipt_reconciliation"


def _fail(message: str) -> int:
    print(f"::error::{message}", file=sys.stderr)
    return 1


def check_junit(junit_path: Path, expected_path: Path) -> int:
    try:
        expected_bytes = expected_path.read_bytes()
        expected_text = expected_bytes.decode("utf-8")
        expected = expected_text.splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return _fail(f"cannot read expected node population: {exc}")
    if hashlib.sha256(expected_bytes).hexdigest() != EXPECTED_NODEIDS_SHA256:
        return _fail("expected node population digest mismatch")
    if not expected or any(not item for item in expected) or len(expected) != len(set(expected)):
        return _fail("expected node population is empty or contains duplicate/blank identities")
    if not expected_text.endswith("\n"):
        return _fail("expected node population is not LF-terminated")

    try:
        root = ET.parse(junit_path).getroot()
    except (OSError, ET.ParseError) as exc:
        return _fail(f"missing or malformed JUnit XML: {exc}")
    if root.tag != "testsuites" or len(root) != 1 or root[0].tag != "testsuite":
        return _fail("JUnit root must contain exactly one pytest testsuite")

    suite = root[0]
    try:
        suite_tests = int(suite.attrib["tests"])
        suite_failures = int(suite.attrib["failures"])
        suite_errors = int(suite.attrib["errors"])
        suite_skipped = int(suite.attrib["skipped"])
    except (KeyError, ValueError) as exc:
        return _fail(f"JUnit suite summary is missing or malformed: {exc}")

    cases = list(suite)
    if any(case.tag != "testcase" for case in cases):
        return _fail("JUnit suite contains an unexpected non-testcase element")
    if suite_tests != len(cases) or suite_tests != len(expected):
        return _fail(f"JUnit case count mismatch: suite={suite_tests}, cases={len(cases)}, expected={len(expected)}")

    actual: list[str] = []
    failures = errors = skipped = 0
    for case in cases:
        classname = case.attrib.get("classname")
        name = case.attrib.get("name")
        if classname != EXPECTED_CLASSNAME or not name:
            return _fail("JUnit testcase identity is missing or outside the target module")
        if set(case.attrib) - {"classname", "name", "time", "file", "line"}:
            return _fail("JUnit testcase contains unexpected identity attributes")
        actual.append(f"tests/contracts/{classname.rsplit('.', 1)[-1]}.py::{name}")
        children = list(case)
        if any(child.tag not in {"failure", "error", "skipped", "system-out", "system-err"} for child in children):
            return _fail("JUnit testcase contains an unknown outcome element")
        failures += sum(child.tag == "failure" for child in children)
        errors += sum(child.tag == "error" for child in children)
        skipped += sum(child.tag == "skipped" for child in children)

    if len(actual) != len(set(actual)):
        return _fail("JUnit contains duplicate test identities")
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        return _fail(f"JUnit population mismatch: missing={missing}, extra={extra}")
    if failures != suite_failures or errors != suite_errors or skipped != suite_skipped:
        return _fail("JUnit suite outcome totals disagree with testcase elements")
    if failures or errors or skipped:
        return _fail(f"JUnit has non-passing cases: failures={failures}, errors={errors}, skipped={skipped}")
    print(f"Verified {len(expected)} exact JUnit cases; failures=0 errors=0 skipped=0")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", required=True, type=Path)
    parser.add_argument("--expected-nodeids", required=True, type=Path)
    args = parser.parse_args()
    return check_junit(args.junit, args.expected_nodeids)


if __name__ == "__main__":
    raise SystemExit(main())
