"""Reconcile the Gate-2 narrative report against the digest-bound carriers (G-12).

The Gate-2 execution report once reported a timing/RSS/throughput profile that did
not come from the committed evidence bundle: the numbers were transcribed from an
invocation whose bundle was never committed.  G-12 records that defect and its
correction.  This test makes the correction durable and machine-checkable:

* the committed evidence still verifies against ``BUNDLE_MANIFEST.json``;
* the carrier-authoritative values in ``report-values.json`` can be recomputed
  from the receipts and raw carriers;
* the report's **corrected** §3B and §4 tables match those recomputed values;
* the preserved "original (superseded) values" tables are still present, so the
  historical audit trail cannot be silently erased;
* the report no longer contains the stale headline claims;
* the check fails when a corrected value is reverted or when evidence is edited.

This test is documentation/evidence integrity only.  It executes no product code
and promotes no measurement: every value remains a local synthetic observation.
"""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
import statistics
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[3]
RUN_ROOT = (
    REPO_ROOT / "docs" / "agent-runs" / "2026-10-25-gate2-reliability-execution"
)
BUNDLE_ROOT = RUN_ROOT / "evidence"
REPORT_PATH = RUN_ROOT / "gate2-reliability-execution-report.md"
RECON_ROOT = (
    REPO_ROOT / "docs" / "agent-runs" / "2026-10-25-g2-12-receipt-report-reconciliation"
)
VALUES_PATH = RECON_ROOT / "report-values.json"
RECONCILIATION_PATH = RECON_ROOT / "G2_12_RECEIPT_REPORT_RECONCILIATION.md"
RUN_NAMES = ("run-v2", "run-v2-confirmation")
PAYLOAD_BYTES = 1_572_864
ARTIFACT_BYTES = 65_536
ARTIFACT_WRITES = 72
STAGES_PER_REPETITION = 24


# --------------------------------------------------------------------------- #
# formatting conventions (must match the report exactly)
# --------------------------------------------------------------------------- #
def fmt_raw(value: float) -> str:
    """Carrier precision: up to 10 decimals, trailing zeros stripped."""
    return f"{value:.10f}".rstrip("0").rstrip(".")


def fmt2(value: float) -> str:
    return f"{value:.2f}"


def fmt_int(value: int) -> str:
    return f"{value:,}"


def fmt_thr(value: float) -> str:
    return f"{value:,.2f}"


def fmt_mb(value: float) -> str:
    """MB = 10^6 bytes (stated in the report)."""
    return f"{value / 1_000_000:,.2f}"


# --------------------------------------------------------------------------- #
# evidence verification and independent recomputation
# --------------------------------------------------------------------------- #
def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_manifest(bundle_root: Path) -> dict:
    """Fail closed unless every manifest file matches its committed bytes/hash."""
    manifest = json.loads((bundle_root / "BUNDLE_MANIFEST.json").read_text())
    assert manifest["schema"] == "gate2.synthetic-run-evidence-manifest.v1"
    assert manifest["scope"] == "synthetic_generated_only"
    checked = 0
    for name, bundle in manifest["bundles"].items():
        for relative, expected in bundle["files"].items():
            path = bundle_root / name / relative
            assert path.is_file(), f"missing evidence file {name}/{relative}"
            actual_bytes = path.stat().st_size
            assert actual_bytes == expected["bytes"], (
                f"byte count drift for {name}/{relative}: "
                f"{actual_bytes} != {expected['bytes']}"
            )
            actual_sha = _sha256(path)
            assert actual_sha == expected["sha256"], (
                f"sha256 drift for {name}/{relative}: "
                f"{actual_sha} != {expected['sha256']}"
            )
            checked += 1
    return manifest, checked


def _recompute() -> dict:
    """Recompute the derived observations straight from receipts/carriers."""
    runs: dict[str, dict] = {}
    for name in RUN_NAMES:
        receipt = json.loads((BUNDLE_ROOT / name / "receipt.json").read_text())
        repetitions = receipt["repetitions"]
        derived = receipt["derived_observations"]

        def carrier(metric: str) -> list[float]:
            """Read one metric's raw carrier rows for this run."""
            path = BUNDLE_ROOT / name / "evidence" / f"{metric}.raw.json"
            rows = json.loads(path.read_text())
            assert [row["repetition"] for row in rows] == list(
                range(1, len(rows) + 1)
            ), f"{path} repetition order drift"
            return [row["value"] for row in rows]

        fixture_ms = carrier("fixture_generation_wall_time")
        stage_ms = carrier("stage_execution_wall_time")
        restart_ms = carrier("restart_recovery_wall_time")
        peak = carrier("peak_rss_bytes")[0]
        disk_apparent = carrier("disk_space_growth_bytes")
        latency_runs = [row["stage_latency_ms"] for row in repetitions]
        latency = {
            "n": sum(item["n"] for item in latency_runs),
            "min": min(item["min"] for item in latency_runs),
            "median": statistics.median([item["median"] for item in latency_runs]),
            "max": max(item["max"] for item in latency_runs),
        }
        stage_throughput = [
            STAGES_PER_REPETITION / (value / 1000.0) for value in stage_ms
        ]
        write_throughput = [PAYLOAD_BYTES / (value / 1000.0) for value in stage_ms]
        before = derived["rss_before_bytes"]
        disk = repetitions[0]["disk"]

        # the receipt's own derived block must agree with the carrier recompute
        assert derived["peak_rss_bytes"] == peak
        assert derived["stage_latency_ms_all"] == latency
        assert derived["stage_throughput_stages_per_second"] == stage_throughput
        assert (
            derived["artifact_write_throughput_bytes_per_second"]
            == write_throughput
        )
        assert [row["stage_busy_wall_time_ms"] for row in repetitions] == stage_ms
        assert [row["fixture_generation_wall_time_ms"] for row in repetitions] == (
            fixture_ms
        )
        assert [row["resume_wall_time_ms"] for row in repetitions] == restart_ms

        def column(values: list[float]) -> dict:
            return {"repetitions": values, "median": statistics.median(values)}
        runs[name] = {
            "fixture_generation_wall_time_ms": column(fixture_ms),
            "stage_execution_wall_time_ms": column(stage_ms),
            "restart_recovery_wall_time_ms": column(restart_ms),
            "peak_rss_bytes": peak,
            "rss_before_bytes": before,
            "rss_growth_bytes": peak - before,
            "disk_space_growth_bytes": disk_apparent[0],
            "disk_allocated_bytes": disk["allocated_bytes"],
            "disk_files": disk["files"],
            "journal_bytes": disk_apparent[0] - PAYLOAD_BYTES,
            "stage_throughput_stages_per_second": stage_throughput,
            "artifact_write_throughput_bytes_per_second": write_throughput,
            "artifact_write_throughput_megabytes_per_second": [
                value / 1_000_000 for value in write_throughput
            ],
            "stage_latency_ms_all": {
                "n": latency["n"],
                "min": latency["min"],
                "median": latency["median"],
                "max": latency["max"],
            },
            "integrity": {
                "artifacts_verified": receipt["integrity"]["artifacts_verified"],
                "journal_records": receipt["integrity"]["journal_records"],
                "mismatches": receipt["integrity"]["mismatches"],
                "duplicate_writes_total": receipt["integrity"][
                    "duplicate_writes_total"
                ],
                "idempotent_replays_total": receipt["integrity"][
                    "idempotent_replays_total"
                ],
            },
            "receipt_digest": receipt["receipt_digest"],
        }

    derived_block = {
        "historical_payload_bytes": 768,
        "executed_payload_bytes_per_repetition": PAYLOAD_BYTES,
        "payload_ratio": PAYLOAD_BYTES / 768,
        "artifact_writes_total": ARTIFACT_WRITES,
        "bytes_per_artifact": ARTIFACT_BYTES,
        "artifact_payload_total_bytes": ARTIFACT_WRITES * ARTIFACT_BYTES,
        "artifact_payload_total_mib": ARTIFACT_WRITES * ARTIFACT_BYTES / (1024 * 1024),
        "stage_applications_per_repetition": STAGES_PER_REPETITION,
        "bound_margin_fixture": 30_000 / runs["run-v2"]["fixture_generation_wall_time_ms"]["repetitions"][0],
    }
    return {"runs": runs, "derived": derived_block}


def _test_function_count(path: Path) -> int:
    tree = ast.parse(path.read_text())
    return sum(
        1
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


# --------------------------------------------------------------------------- #
# report parsing
# --------------------------------------------------------------------------- #
def _table_rows(
    text: str, header: str, end_marker: str, start_marker: str | None = None
) -> list[list[str]]:
    start = text.index(start_marker) if start_marker else text.index(header)
    stop = text.index(end_marker, start)
    rows: list[list[str]] = []
    for line in text[start:stop].splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    assert len(rows) >= 2, f"table starting {header!r} has no body"
    assert set(rows[1][0]) <= {"-", ":", " "}, f"missing separator row after {header!r}"
    return rows[2:]


def _by_first_cell(rows: list[list[str]]) -> dict[str, list[str]]:
    """Index rows by their first cell, normalising backticked metric names."""
    indexed: dict[str, list[str]] = {}
    for row in rows:
        key = row[0].replace("`", "").strip()
        indexed[key] = [key, *row[1:]]
    return indexed


# --------------------------------------------------------------------------- #
# the complete reconciliation check (also used by the negative validations)
# --------------------------------------------------------------------------- #
def _check_report(report_text: str, values: dict) -> list[str]:
    problems: list[str] = []
    runs = values["runs"]
    run_v2 = runs["run-v2"]
    confirmation = runs["run-v2-confirmation"]

    # --- corrected §3B table -------------------------------------------------
    timing_rows = {
        "fixture_generation_wall_time": "fixture_generation_wall_time_ms",
        "stage_execution_wall_time": "stage_execution_wall_time_ms",
        "restart_recovery_wall_time": "restart_recovery_wall_time_ms",
    }
    table_3b = _by_first_cell(
        _table_rows(
            report_text,
            "| Metric | Unit | run-v2 values (median) | confirmation values (median) | Bound |",
            "\nOriginal (superseded) §3B values",
        )
    )
    for row_key, field in timing_rows.items():
        row = table_3b.get(row_key)
        if row is None:
            problems.append(f"§3B corrected table missing row {row_key}")
            continue

        def timing_cell(run: dict) -> str:
            rep = run[field]
            return (
                f"{fmt_raw(rep['repetitions'][0])}, "
                f"{fmt_raw(rep['repetitions'][1])}, "
                f"{fmt_raw(rep['repetitions'][2])} ({fmt2(rep['median'])})"
            )

        expected = [row_key, "ms", timing_cell(run_v2), timing_cell(confirmation), "30000"]
        if row != expected:
            problems.append(f"§3B row {row_key}: {row} != {expected}")

    expected_3b = {
        "peak_rss_bytes": [
            "peak_rss_bytes",
            "bytes",
            fmt_int(run_v2["peak_rss_bytes"]),
            fmt_int(confirmation["peak_rss_bytes"]),
            "200,000,000",
        ],
        "disk_space_growth_bytes": [
            "disk_space_growth_bytes",
            "bytes (apparent)",
            f"{fmt_int(run_v2['disk_space_growth_bytes'])} ×3 "
            f"({fmt_int(run_v2['disk_allocated_bytes'])} allocated; "
            f"{run_v2['disk_files']} files)",
            f"{fmt_int(confirmation['disk_space_growth_bytes'])} ×3 (same)",
            "8,000,000",
        ],
        "artifact_integrity_mismatches": [
            "artifact_integrity_mismatches",
            "artifacts",
            "0, 0, 0",
            "0, 0, 0",
            "0",
        ],
        "restart_duplicate_writes": ["restart_duplicate_writes", "writes", "0, 0, 0", "0, 0, 0", "0"],
        "restart_idempotent_replays": [
            "restart_idempotent_replays",
            "applications",
            "1, 1, 1",
            "1, 1, 1",
            "24",
        ],
        "repeatability_digest_mismatches": [
            "repeatability_digest_mismatches",
            "digests",
            "0",
            "0",
            "0",
        ],
    }
    for row_key, expected in expected_3b.items():
        row = table_3b.get(row_key)
        if row != expected:
            problems.append(f"§3B row {row_key}: {row} != {expected}")

    # --- corrected §4 table --------------------------------------------------
    table_4 = _by_first_cell(
        _table_rows(
            report_text,
            "| Observation | historical `metrics-003` @ `17edacbe` | "
            "baseline @ `fe2e5352` (2 invocations) | "
            "final @ `4453430a9` (2 invocations) |",
            "\nOriginal (superseded) §4 values",
        )
    )
    throughput_v2 = run_v2["stage_throughput_stages_per_second"]
    writes_v2 = run_v2["artifact_write_throughput_bytes_per_second"]
    throughput_c = confirmation["stage_throughput_stages_per_second"]
    writes_c = confirmation["artifact_write_throughput_bytes_per_second"]
    expected_4 = {
        "fixture generation (ms)": [
            "fixture generation (ms)",
            "0.135, 0.101041 (median 0.1180)",
            "0.1328 / 0.1238",
            f"{fmt2(run_v2['fixture_generation_wall_time_ms']['median'])} / "
            f"{fmt2(confirmation['fixture_generation_wall_time_ms']['median'])} (medians)",
        ],
        "restart recovery (ms)": [
            "restart recovery (ms)",
            "1.097417, 1.026208 (median 1.0618)",
            "1.2985 / 1.1369",
            f"{fmt2(run_v2['restart_recovery_wall_time_ms']['median'])} / "
            f"{fmt2(confirmation['restart_recovery_wall_time_ms']['median'])} (medians)",
        ],
        "duplicate applications": ["duplicate applications", "1.0, 1.0", "1.0, 1.0", "1.0, 1.0"],
        "peak RSS (bytes)": [
            "peak RSS (bytes)",
            "NOT_OBSERVED",
            "27,066,368",
            f"{fmt_int(run_v2['peak_rss_bytes'])} / {fmt_int(confirmation['peak_rss_bytes'])}",
        ],
        "disk growth": [
            "disk growth",
            "NOT_OBSERVED",
            "NOT_OBSERVED",
            f"{fmt_int(run_v2['disk_space_growth_bytes'])} B (apparent; "
            f"{fmt_int(run_v2['disk_allocated_bytes'])} B allocated)",
        ],
        "throughput": [
            "throughput",
            "NOT_OBSERVED",
            "NOT_OBSERVED",
            f"{fmt_thr(min(throughput_v2))}–{fmt_thr(max(throughput_v2))} stages·s⁻¹; "
            f"{fmt_mb(min(writes_v2))}–{fmt_mb(max(writes_v2))} MB·s⁻¹ (run-v2); "
            f"{fmt_thr(min(throughput_c))}–{fmt_thr(max(throughput_c))} stages·s⁻¹; "
            f"{fmt_mb(min(writes_c))}–{fmt_mb(max(writes_c))} MB·s⁻¹ (confirmation)",
        ],
        "decision": ["decision", "BR-7 (missing carrier)", "BR-7", "BR-1"],
    }
    for row_key, expected in expected_4.items():
        row = table_4.get(row_key)
        if row != expected:
            problems.append(f"§4 row {row_key}: {row} != {expected}")

    # --- preserved superseded tables ----------------------------------------
    preserved_3b = _by_first_cell(
        _table_rows(
            report_text,
            "| Metric | Unit | run-v2 values (median) | "
            "confirmation values (median) | Bound |",
            "\nDerived run observations",
            start_marker="\nOriginal (superseded) §3B values",
        )
    )
    expected_preserved_3b = {
        "fixture_generation_wall_time": [
            "fixture_generation_wall_time",
            "ms",
            "187.3550, 185.3045, 186.3842 (186.38)",
            "181.5020, 181.5604, 177.8449 (181.50)",
            "30000",
        ],
        "stage_execution_wall_time": [
            "stage_execution_wall_time",
            "ms",
            "8.0790, 6.2807, 7.0960 (7.096)",
            "6.7047, 6.0439, 6.0935 (6.094)",
            "30000",
        ],
        "restart_recovery_wall_time": [
            "restart_recovery_wall_time",
            "ms",
            "9.3874, 6.0862, 11.3645 (9.387)",
            "8.5380, 6.0218, 10.9440 (8.538)",
            "30000",
        ],
        "peak_rss_bytes": [
            "peak_rss_bytes",
            "bytes",
            "42,762,240",
            "42,352,640",
            "200,000,000",
        ],
        "disk_space_growth_bytes": [
            "disk_space_growth_bytes",
            "bytes",
            "1,579,263 ×3",
            "1,579,263 ×3",
            "8,000,000",
        ],
        "artifact_integrity_mismatches": [
            "artifact_integrity_mismatches",
            "artifacts",
            "0, 0, 0",
            "0, 0, 0",
            "0",
        ],
        "restart_duplicate_writes": [
            "restart_duplicate_writes",
            "writes",
            "0, 0, 0",
            "0, 0, 0",
            "0",
        ],
        "restart_idempotent_replays": [
            "restart_idempotent_replays",
            "applications",
            "1, 1, 1",
            "1, 1, 1",
            "24",
        ],
        "repeatability_digest_mismatches": [
            "repeatability_digest_mismatches",
            "digests",
            "0",
            "0",
            "0",
        ],
    }
    assert len(preserved_3b) == 9, f"expected 9 preserved §3B rows, found {len(preserved_3b)}"
    for row_key, expected in expected_preserved_3b.items():
        row = preserved_3b.get(row_key)
        if row != expected:
            problems.append(f"preserved §3B row {row_key}: {row} != {expected}")

    preserved_4 = _by_first_cell(
        _table_rows(
            report_text,
            "| Observation | historical `metrics-003` @ `17edacbe` | "
            "baseline @ `fe2e5352` | "
            "final @ `4453430a9` (as originally reported) |",
            "\nInterpretation: the historical numbers",
        )
    )
    expected_preserved_4 = {
        "fixture generation (ms)": ["fixture generation (ms)", "0.135, 0.101041 (median 0.1180)", "0.1328 / 0.1238", "186.38 / 181.50"],
        "restart recovery (ms)": ["restart recovery (ms)", "1.097417, 1.026208 (median 1.0618)", "1.2985 / 1.1369", "9.387 / 8.538"],
        "peak RSS (bytes)": ["peak RSS (bytes)", "NOT_OBSERVED", "27,066,368", "42,762,240 / 42,352,640"],
        "throughput": ["throughput", "NOT_OBSERVED", "NOT_OBSERVED", "3.0–3.8 k stages/s; 195–250 MB/s"],
    }
    for row_key, expected in expected_preserved_4.items():
        row = preserved_4.get(row_key)
        if row != expected:
            problems.append(f"preserved §4 row {row_key}: {row} != {expected}")

    # --- headline claims -----------------------------------------------------
    fixture_first = run_v2["fixture_generation_wall_time_ms"]["repetitions"][0]
    stage_first = run_v2["stage_execution_wall_time_ms"]["repetitions"][0]
    restart_first = run_v2["restart_recovery_wall_time_ms"]["repetitions"][0]
    for required in (
        "ERRATUM — G-12 (2026-10-25)",
        "2,048× more payload",
        "829 passed (815 pre-existing + 14 new",
        "837 passed",
        "4.5 MiB",
        "4,718,592 B ≈ 4.5 MiB",
        "1.5 MiB",
        "128 KiB",
        "112 KiB",
        ">168× margin",
        f"{30_000 / fixture_first:.1f}×",  # 168.5×
        f"{30_000 / stage_first:,.0f}×",  # 3,463×
        f"{30_000 / restart_first:,.0f}×",  # 2,615×
        "pooled 75-sample median",
    ):
        if required not in report_text:
            problems.append(f"report is missing required corrected claim: {required!r}")
    for forbidden in (
        "≈ 819×",
        "828 passed",
        "13 new)",
        "3 × 48 fsynced records",
        "194.7 / 250.4",
        "2,971 / 3,821",
        "42,647,552",
        "min ≈ 0.46",
    ):
        if forbidden in report_text:
            problems.append(f"report still contains stale claim: {forbidden!r}")

    return problems


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def test_evidence_manifest_still_verifies() -> None:
    manifest, checked = _verify_manifest(BUNDLE_ROOT)
    assert checked == 28, f"expected 28 manifest files, checked {checked}"
    assert set(manifest["bundles"]) == set(RUN_NAMES)


def test_report_values_match_receipts_and_carriers() -> None:
    values = json.loads(VALUES_PATH.read_text())
    assert values["schema"] == "gate2.report-reconciliation-values.v1"
    assert values["scope"] == "synthetic_generated_only"
    recomputed = _recompute()
    assert values["runs"] == recomputed["runs"]
    assert values["derived"] == recomputed["derived"]
    # frozen report facts recorded alongside the numbers
    assert values["tests"] == {
        "prior_gate2_passed": 829,
        "current_gate2_passed": 837,
        "pre_existing": 815,
        "new_report_related": 14,
        "new_reconciliation_tests": 8,
        "synthetic_run_execution": 7,
        "synthetic_run_evidence_bundle": 7,
    }
    assert values["tests"]["current_gate2_passed"] == (
        values["tests"]["prior_gate2_passed"]
        + values["tests"]["new_reconciliation_tests"]
    )


def test_receipts_are_the_committed_ones() -> None:
    values = json.loads(VALUES_PATH.read_text())
    for name in RUN_NAMES:
        receipt_path = BUNDLE_ROOT / name / "receipt.json"
        manifest = json.loads((BUNDLE_ROOT / "BUNDLE_MANIFEST.json").read_text())
        expected = manifest["bundles"][name]["files"]["receipt.json"]["sha256"]
        assert _sha256(receipt_path) == expected
        assert values["runs"][name]["receipt_digest"] == json.loads(
            receipt_path.read_text()
        )["receipt_digest"]


def test_report_tables_match_carriers() -> None:
    report_text = REPORT_PATH.read_text()
    values = json.loads(VALUES_PATH.read_text())
    assert _check_report(report_text, values) == []


def test_reconciliation_record_is_complete() -> None:
    record = RECONCILIATION_PATH.read_text()
    assert "G12_CORRECTED_AND_VERIFIED" in record
    assert "NOT_A_PROMOTION" in record
    matrix = [
        line
        for line in record.splitlines()
        if line.startswith("| M-")
    ]
    assert len(matrix) == 35, f"expected 35 matrix rows, found {len(matrix)}"
    for index in range(1, 36):
        assert any(line.startswith(f"| M-{index:02d} |") for line in matrix), (
            f"matrix row M-{index:02d} missing"
        )
    for pair in (
        "187.3550, 185.3045, 186.3842",
        "2,048×",
        "829 passed",
        "4.5 MiB",
        "NOT_OBSERVED",
    ):
        assert pair in record


def test_new_report_related_test_count_matches_report() -> None:
    integration = Path(__file__).parent
    execution = _test_function_count(integration / "test_synthetic_run_execution.py")
    bundle = _test_function_count(integration / "test_synthetic_run_evidence_bundle.py")
    assert (execution, bundle) == (7, 7)
    values = json.loads(VALUES_PATH.read_text())
    assert values["tests"]["new_report_related"] == execution + bundle
    report_text = REPORT_PATH.read_text()
    assert "829 passed (815 pre-existing + 14 new" in report_text


def test_check_rejects_reverted_report_value() -> None:
    report_text = REPORT_PATH.read_text()
    values = json.loads(VALUES_PATH.read_text())
    assert _check_report(report_text, values) == []
    stale_cell = "| 178.02525, 173.118959, 174.831208 (174.83) |"
    assert report_text.count(stale_cell) == 1
    reverted = report_text.replace(
        stale_cell, "| 187.3550, 185.3045, 186.3842 (186.38) |"
    )
    problems = _check_report(reverted, values)
    assert any("fixture_generation_wall_time" in problem for problem in problems)


def test_check_rejects_mutated_carrier_copy(tmp_path: Path) -> None:
    copy_root = tmp_path / "evidence"
    shutil.copytree(BUNDLE_ROOT, copy_root)
    _verify_manifest(copy_root)  # the pristine copy verifies
    tampered = copy_root / "run-v2" / "evidence" / "peak_rss_bytes.raw.json"
    tampered.write_text(tampered.read_text() + " ")
    with pytest.raises(AssertionError, match="byte count drift"):
        _verify_manifest(copy_root)
