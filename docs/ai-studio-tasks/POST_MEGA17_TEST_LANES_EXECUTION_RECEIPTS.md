# Post-MEGA17 Test Lanes — Execution Receipts and Reconciliation

**Observed:** 2026-11-05 (GitHub and artifact observations made during this Task 5 run)

**Reconciliation disposition:** **PARTIAL — three test slices reconcile independently; project-wide acceptance remains pending.**
**Evidence classes:** hosted test results are `MEASURED` software test outcomes. They are not real-media measurements, Gate evidence, or approval to adopt/merge.

## A. Executive evidence summary

There are two ownership lanes and three separately reported test slices:

| Lane | Slice | Expected | Python 3.11 | Python 3.14 | Current slice disposition |
|---|---|---:|---:|---:|---|
| C — canonical | `CANONICAL_HISTORY_33` | 33 exact nodes | 33 pass, 0 fail/error/skip/deselect | 33 pass, 0 fail/error/skip/deselect | `TEST_EXECUTION_PASS` |
| C — canonical | `PR258_BOUNDED_ADMISSION` | 22 exact nodes | 22 pass, 0 fail/error/skip/deselect | 22 pass, 0 fail/error/skip/deselect | `TEST_EXECUTION_PASS` |
| L — LAB | `LAB_SYNTHETIC` | 37 exact nodes | 37 pass, 0 fail/error/skip/deselect | 37 pass, 0 fail/error/skip/deselect | `TEST_EXECUTION_PASS` |

Each interpreter's collected and executed node set equals the exact expected set for its own slice. Each JUnit population is unique and agrees with its JSON receipt's outcomes/counts. All six actual artifact ZIPs were downloaded; their SHA-256 values match GitHub's artifact metadata.

This is **not an overall cross-lane PASS**. The current PR #258 CodeScene Code Health Review is `QUEUED`, so `TASK3_CODE_HEALTH = PENDING`. PR review approvals are not observed for the exact current heads. The four existing PRs remain open and unmerged. Gate authorization and production adoption are not granted by these software test results.

Two receipt-level provenance fields are incomplete despite independently observable GitHub job identities: PR #258's JSON receipts have `github_job_id: null`; LAB's receipts contain `github_job_id: "NOT_OBSERVED"`. The live job API supplies the numeric IDs recorded below. These omissions remain visible and are not backfilled into the downloaded receipts.

## B. Repository identities and ownership

| Repository | Owner lane | Observed main SHA | GitHub repository identity |
|---|---|---|---|
| [`Centaurioun/video-intelligence-pipeline`](https://github.com/Centaurioun/video-intelligence-pipeline) | C — canonical | `bee314b92981b9ae7ea38d83fe2dbae120c474e4` | Canonical VIP; repository ID `1366495746` |
| [`Centaurioun/video-intelligence-pipeline-2`](https://github.com/Centaurioun/video-intelligence-pipeline-2) | L — LAB | `d512cfbfead4c02c137714a2203eee3d99348f79` | LAB; repository ID `1444908753` |

## C. Exact PR, source, merge-checkout and tree identities

| PR | Base SHA | Source head SHA | Workflow-tested merge/checkout SHA | Tested tree SHA | Current state |
|---|---|---|---|---|---|
| Canonical [#264](https://github.com/Centaurioun/video-intelligence-pipeline/pull/264) | `bee314b92981b9ae7ea38d83fe2dbae120c474e4` | `34f7854af967dc343893ba6e91128bde327d16c3` | not applicable to its manifest-only run evidence | PR head manifest/oracle | open, Draft, unmerged |
| Canonical [#265](https://github.com/Centaurioun/video-intelligence-pipeline/pull/265) | `34f7854af967dc343893ba6e91128bde327d16c3` | `2d9ab6affac9492fd9d89aabd81f0dad8d4a4bfd` | run checkout `089d8ae40dcbd6aaa5951e6d468bc1417a1f08f8` | `15db93acc2bce5113ef41a78fda0a0352e9a07fa` | open, Draft, unmerged |
| Canonical [#258](https://github.com/Centaurioun/video-intelligence-pipeline/pull/258) | `bee314b92981b9ae7ea38d83fe2dbae120c474e4` | `0a97f96c04510e57216f8b9e1d5d1cd21df81fdc` | `861b8c5a89c1b64ddc8e454bac1dd9ad85a00bb4` | `c0cd41407ba16c33fc209e8d4f749cd97a112bfd` | open, Draft, unmerged |
| LAB [#6](https://github.com/Centaurioun/video-intelligence-pipeline-2/pull/6) | `d512cfbfead4c02c137714a2203eee3d99348f79` | `894c67612ec5b5fa49abb9fe04755e0fc917839b` | `a853992412ca1f9124829c4f114666707560fa28` | `1ae07872c42fec255114e09bf1f2b305bbdf1a01` | open, **not Draft**, unmerged |

For PR #265, the run receipt binds the tested merge commit `089d8ae…`. At observation time GitHub's current `refs/pull/265/merge` pointed to `9206b6cb1c681ce8ff7b984669e194cf1a525906`. GitHub reports both merge commits have the same two parents (`34f7854…`, `2d9ab6a…`) and exact same tree `15db93e…`; they are distinct commit object IDs. The run evidence remains tied to `089d8ae…`, while `9206b6c…` is the current merge-ref observation.

PR #258's verified candidate tree contains all eight changed paths together: `src/vip_fvs/bounded_admission.py`, `src/vip_fvs/_bounded_admission_fs.py`, `tests/vip_fvs/unit/test_bounded_admission.py`, `tests/contracts/bounded_admission_expected_nodeids.json`, `scripts/bounded_admission_receipt.py`, `tests/scripts/test_bounded_admission_receipt.py`, `tests/scripts/test_bounded_admission_workflow_contract.py`, and `.github/workflows/python-synthetic-smoke.yml`. Their GitHub tree entries were read from the same merge candidate `861b8c5…` / tree `c0cd414…`.

## D. Ownership lanes and evidence slices

- **Lane C — canonical** owns `CANONICAL_HISTORY_33` and the distinct focused `PR258_BOUNDED_ADMISSION` slice. Neither result transfers to LAB.
- **Lane L — LAB** owns `LAB_SYNTHETIC`; its 37 nodes are only the six MEGA-17 suites from the pinned Task 4 baseline. They do not contain either canonical slice.
- All exact pytest IDs are printed in Appendix 1, grouped by the independent baseline that owns them.

## E–I. Interpreter results, node sets, and JUnit/JSON reconciliation

`EXPECTED = COLLECTED = EXECUTED = JUNIT`, compared as exact node identities separately for every interpreter:

| Slice / Python | Node count | Expected baseline match | Collected match | Executed match | JUnit IDs / receipt match | JUnit fail/error/skip | Receipt outcomes/counts |
|---|---:|---|---|---|---|---|---|
| C1 / 3.11.17 | 33 | yes | yes | yes | yes, 33 unique | 0 / 0 / 0 | 33 PASS; `pytest_exit_code=0`, `deselected=0` |
| C1 / 3.14.9 | 33 | yes | yes | yes | yes, 33 unique | 0 / 0 / 0 | 33 PASS; `pytest_exit_code=0`, `deselected=0` |
| C2 / 3.11.18 | 22 | yes | yes | yes | yes after JUnit `classname` + `name` normalization, 22 unique | 0 / 0 / 0 | collected/executed/passed 22; failed/errors/skipped/deselected 0 |
| C2 / 3.14.9 | 22 | yes | yes | yes | yes after JUnit `classname` + `name` normalization, 22 unique | 0 / 0 / 0 | collected/executed/passed 22; failed/errors/skipped/deselected 0 |
| L1 / 3.11.18 | 37 | yes | yes | yes | yes, 37 unique | 0 / 0 / 0 | collected/executed/passed 37; failed/errors/skipped/deselected 0 |
| L1 / 3.14.9 | 37 | yes | yes | yes | yes, 37 unique | 0 / 0 / 0 | collected/executed/passed 37; failed/errors/skipped/deselected 0 |

The C1 workflow reports exact patch versions and pytest `8.3.3`. The LAB receipts report exact patch versions and pytest `8.3.3`. PR #258 receipts report only Python `3.11` / `3.14` (major/minor), while the hosted job logs independently report CPython `3.11.18` and `3.14.9`; the receipt-level patch field remains `NOT_OBSERVED` and is not backfilled.

The LAB collection sidecar bytes hash to the exact `collection_sha256` in each JSON receipt. JUnit and JSON receipt SHA-256 values are also cross-checked by the receipt fields wherever present. JUnit outcome nodes are all pass and match exact expected identities. This confirms scoped test execution evidence; it is not formal acceptance of any PR.

## J. Artifact provenance and integrity

The ZIP files below were independently downloaded from their GitHub Actions artifact IDs. `Observed ZIP SHA-256` equals the `digest` in GitHub's artifact metadata for all six.

| Slice / Python | Run / numeric job ID | Artifact ID and name | ZIP SHA-256 (observed = GitHub digest) | Inner evidence |
|---|---|---|---|---|
| C1 / 3.11 | `41993418672` / `127130793260` | `13399401066` `canonical-history-py3.11` | `5c9b84dc66981cbab209fc1ffa8f0fa1b5855acd427a036a49a9657efd2d6e0b` | `canonical-history-junit.xml`; `canonical-history-receipt.json` |
| C1 / 3.14 | `41993418672` / `127130793747` | `13398144520` `canonical-history-py3.14` | `28536d1fe2e49ce972e19a41efbbd2cd31f692e37a836730cd12e1b0ab34d64b` | same filenames, interpreter-specific contents |
| C2 / 3.11 | `42015564467` / `127205120279` | `13408384188` `bounded-admission-python-3.11` | `fee8a5f846eee21a26b98b1c5d642ffdcc29fcf8cf6f3f0eea19143b950bd3ef` | `bounded-admission-junit.xml`; `bounded-admission-receipt.json` |
| C2 / 3.14 | `42015564467` / `127205120763` | `13408384199` `bounded-admission-python-3.14` | `71257269bd6f10947b5a3c05ed177b7927ee2259f45b6c71888d80acf51ffa90` | same filenames, interpreter-specific contents |
| L1 / 3.11 | `41998064852` / `127146066361` | `13400169562` `lab-synthetic-3.11` | `e63e614b4624bd650845dc304418cc78ceeb72ff7a1e2e93be331f113a25fb70` | `lab-synthetic-junit.xml`; `lab-synthetic-receipt.json`; `mega17-collection.txt` |
| L1 / 3.14 | `41998064852` / `127146066894` | `13401685754` `lab-synthetic-3.14` | `ecbca5b508a9c6d43d55bd8ba19d1e91412a0964f62c47f28f29d92820bba2b4` | same filenames, interpreter-specific contents |

For C1, the receipt's `job_id` string contains the numeric GitHub job ID; it matches the jobs API. For C2, the receipt's `logical_job_key` is `synthetic-smoke-python-3.11` / `...3.14`, while `github_job_id` is null; the live job API maps each logical interpreter job to the numeric ID above. For L1, receipt `job_key` is `gate1-synthetic-3.11` / `...3.14`, while `github_job_id` is literal `NOT_OBSERVED`; the live job API supplies the numeric ID above. These values are not conflated.

## K. Workflow, lock, manifest, and historical Git-object identity

| Slice | Workflow path / Git blob | Expected-node baseline | Dependency lock SHA-256 | Historical Git/dependency observation |
|---|---|---|---|---|
| C1 | `.github/workflows/canonical-history-regressions.yml` / `800be6f72980831d630c5dcd68dace72bb0218dc` | Task 1 manifest at PR #264 head `34f7854…`; oracle path `tests/contracts/canonical_history_expected_nodeids.json`, blob `be2f6feb38cb35b24fd023ccc6527ac8ccc59323`; 33 nodes; canonical sorted compact-LF node-set digest `8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016`; exact oracle file bytes SHA-256 `c3f058579f4cea557bdd2a7cd4cebec1fcdf84ec517910eba73de5ecba9f5cfa` | `bfe36fb15e17f245e9cd8f133e25d6939546c63d0ded7d11868b26bbd3c2e9ec` | full-history checkout and required refs/objects validated by the hosted Task 2 workflow; both receipts have empty blockers. Manifest's 33 historical `prior_status` values remain `UNRESOLVED`; this later run is separate observed execution evidence. |
| C2 | `.github/workflows/python-synthetic-smoke.yml` / `3996ede731b43678f17b75497ec86fb70edbbb5c` | `tests/contracts/bounded_admission_expected_nodeids.json` at PR #258 candidate, blob `aa5e6cd5145f36fc762f6c9d89e31c6b1980e7f3`; exactly 22 nodes; receipt node-baseline digest `4fd239a941011e352cd3e28d7f1413d36881f009a7bae9c3d6255e86ac7fec3f` | `bfe36fb15e17f245e9cd8f133e25d6939546c63d0ded7d11868b26bbd3c2e9ec` | source, test, expected-node file, receipt tooling, workflow and workflow contract tests coexist in PR #258 candidate tree `c0cd414…`. JUnit inner-file digests equal the receipt `junit_sha256` values. |
| L1 | `.github/workflows/vip-ai-studio-synthetic-ci.yml` / `ea63eaaaf39df98e65d8217f235bd2ebc0ca3444` | Task 4 `scripts/lab_synthetic_expected_nodes.txt` at PR #6 head, blob `c91d14d12e4bddac1ac866eabfdf02658f4300eb`; 37 exact dotted pytest IDs | `bfe36fb15e17f245e9cd8f133e25d6939546c63d0ded7d11868b26bbd3c2e9ec` | hosted merge checkout `a853992…`, tree `1ae0787…`; collection sidecar hash matches each receipt and contains the six-suite 37-node MEGA-17 population only. |

The common lock hash is receipt-reported in each slice. It identifies the lock input; the C1 receipt additionally records interpreter-specific installed-dependency inventories and their SHA-256 values. PR #258's checked-in expected-node file byte hash and both receipt set digest values were recomputed from the downloaded GitHub content. No Git objects, lockfiles, manifest fields, or historical `prior_status` values were edited.

## L. Current review and quality statuses

| PR | GitHub review submissions observed | Formal approval on current head | Merge/adoption state |
|---|---|---|---|
| Canonical #258 | Historical `COMMENTED` review submissions exist; the latest one is anchored to earlier head `5a60cd8…`, and is not an approval | `NOT_OBSERVED` for current head `0a97f96…` | open / Draft / unmerged |
| Canonical #264 | none returned | `NOT_OBSERVED` | open / Draft / unmerged |
| Canonical #265 | none returned | `NOT_OBSERVED` | open / Draft / unmerged |
| LAB #6 | none returned | `NOT_OBSERVED` | open / not Draft / unmerged |

At the current canonical PR #258 head, GitHub check `CodeScene Code Health Review (main)` is **`queued`** with no conclusion and no completion timestamp (`TASK3_CODE_HEALTH = PENDING`). GitGuardian and the functional hosted runs are successful; neither substitutes for CodeScene. No CodeScene success is claimed.

## M. Remaining `NOT_OBSERVED` / `PENDING` facts

- Exact patch versions for PR #258's matrix jobs: `NOT_OBSERVED` in the downloaded receipt; it reports `3.11` and `3.14` only.
- PR #258 and LAB JSON receipt numeric `github_job_id` fields: absent/`NOT_OBSERVED`; their live numeric GitHub job IDs were independently retrieved and reported in §J.
- Formal human review/approval for the current exact PR heads: `NOT_OBSERVED`.
- PR #258 CodeScene conclusion: `PENDING` (`queued` at this observation).
- Current protected-branch rules or human adoption/merge decisions: outside this reconciliation and `NOT_OBSERVED`.
- Current canonical merge ref for #265 has a different commit SHA from the tested run checkout but identical tree/parents as detailed in §C; run provenance remains the run's exact `089d8ae…` object.

## N. Synthetic evidence limits

`PR258_BOUNDED_ADMISSION` is explicitly `SYNTHETIC_ONLY`; its JSON receipt says `gate_acceptance: NOT_CLAIMED`, source authorization requires caller policy, source-native PTS is `NOT_MEASURED`, and `trusted_root_is_independent_source_authorization: false`. `LAB_SYNTHETIC` is a synthetic MEGA-17 test population. These are hosted software tests and receipts, not measurements of authentic media or successful real source access.

## O. Forbidden conclusions and Gate boundaries

- Do not combine 33 + 22 + 37 into a single acceptance percentage or overall PASS.
- A successful test slice is not formal PR approval, CodeScene approval, merge/adoption, Gate authorization, or production readiness.
- No test result authorizes protected archive access, real-media execution, model/provider calls, rendering/export, or Gate promotion.
- TrustedRoot is not general authorization to access a protected archive.
- LAB's 37-node MEGA-17 receipt excludes canonical history and the 22 bounded-admission tests; unrelated legacy LAB test steps are not part of that receipt.

## P. Owner-controlled next decisions

Any merge/adoption decision remains separate and owner controlled. A next safe project-wide step is a separately reviewed, evidence-dependent integration decision after PR #258 CodeScene reaches a terminal result and exact-head PR reviews are obtained. Do not merge PR #258, #264, #265, or LAB #6 automatically.

## Q. Final reconciliation disposition

**PARTIAL.** All six hosted interpreter-specific execution artifacts reconcile against their own expected populations, JUnit outcomes, receipt summaries, artifact digests, repository ownership, PR/run/job identities, workflow blobs and dependency-lock hashes. Cross-slice test execution succeeds independently. Full Task 5 acceptance is not claimed because CodeScene remains pending, current-head formal PR reviews remain unobserved, and the two receipt formats omit numeric job IDs even though GitHub job IDs were independently recovered. No Gate or production adoption is authorized.

## R. Method and verification record

- **TDD RED:** 56 focused contract cases were run against an intentionally fail-closed interface: 10 behavior/disposition assertions failed, while 46 adversarial rejection cases passed. This showed that the accepting and state-mapping behavior was not present.
- **TDD GREEN:** the completed minimal validator passed all 60 contract tests on Python 3.11.9 / pytest 8.3.3 and Python 3.14.9 / pytest 8.3.3. Added fail-closed cases explicitly cover receipt statuses `ERROR`, `SKIP`, and `NOT_OBSERVED`.
- A separate exact-head check also had a targeted RED: a stale successful CodeScene result incorrectly mapped to `PASS` before head binding; after requiring the observed SHA to equal the requested current SHA, it maps to `NOT_OBSERVED`. A contradictory `open + draft + merged` PR tuple likewise had a targeted RED and now stays `UNRESOLVED`.
- Existing six MEGA-17 test modules were also run without changing their selection: 37/37 passed locally on Python 3.11.9 and 37/37 on Python 3.14.9. The Python 3.14 task-local environment initially lacked NumPy and Pillow; after installing the routine prerequisites into that temporary environment (NumPy 2.5.4, Pillow 13.0.0), the same six-module command passed. An initial import attempt also required the repo's `src:experiments` paths in `PYTHONPATH`; no test expectation or workflow selection was changed.
- These validator fixtures are synthetic and live only in the contract tests. The six actual hosted ZIP artifacts were separately downloaded and reconciled as described above.
- The helper validates **normalized** evidence records. It does not download or parse raw artifact ZIPs, parse raw JUnit/JSON, or compute ZIP digests; those source-level checks were performed from the downloaded files and GitHub metadata and are recorded above. Re-running the helper alone is not equivalent to replaying all six external artifact checks.
- The Task 5 Draft PR's exact head `1ebeb2874e6877b014a54679762183b03771d290` ran LAB workflow [42021156237](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/42021156237) successfully. Python 3.11 job `127223969938` and Python 3.14 job `127223970060` completed with `success`. This existing workflow ran the LAB synthetic suites on the exact candidate, but did **not** select `tests/contracts/test_post_mega17_receipt_reconciliation.py`; the 60 Task 5 contract tests remain locally verified only.
- Exact-head read-only review of `958102d150acf71e74551fbf8c5fb578b31e33f0` found no material reconciliation defect and confirmed six digest and six node-set comparisons. It identified the normalized-input limitation above (P2) and the duplicate empty appendix heading, which this revision removes. The updated final candidate receives its own exact-head review before publication.
- `gitleaks git` over the Task 5 commit reported no leaks. `scripts/verify-workspace.sh --feature-worktree` completed its checks but returned 26 repository-surface failures: the LAB base lacks multiple canonical audit, reference-pack, and prototype files required by that repository-wide verifier. The Task 5 changed-file list does not include any of those paths; this is retained as an ambient LAB workspace limitation, not reported as PASS.

## Appendix 1 — Exact node populations

The lists below are transcribed from the independent owning baseline. C1's canonical historical manifest `prior_status` entries remain `UNRESOLVED`; their observed execution outcomes are in the downloaded Task 2 receipts, not written back into that manifest.

### CANONICAL_HISTORY_33 — 33 exact node IDs

```text
tests/gate0/unit/test_evidence_projection.py::test_capture_frozen_fixture_and_guarantee_limits
tests/gate0/unit/test_evidence_seal.py::test_task15_has_no_successor_behavior_delta
tests/gate0/unit/test_evidence_seal.py::test_tasks12_13_14_16_s9_inventory_is_exact
tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_old_frozen_core_remains_byte_identical
tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_option_b_core_integrity_and_exact_one_shot_semantics
tests/gate0/unit/test_h3_adopted_core_atlas_index.py::test_owner_adopted_cores_are_exactly_bound_in_atlas_and_prompt_index
tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_adopted_core_is_digest_bound_and_consistent_with_producers
tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_old_frozen_core_remains_byte_identical
tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_read_only_contract_and_restricted_authority
tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_mutated_carrier_copy
tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_reverted_report_value
tests/gate2/integration/test_report_receipt_reconciliation.py::test_evidence_manifest_still_verifies
tests/gate2/integration/test_report_receipt_reconciliation.py::test_new_report_related_test_count_matches_report
tests/gate2/integration/test_report_receipt_reconciliation.py::test_receipts_are_the_committed_ones
tests/gate2/integration/test_report_receipt_reconciliation.py::test_reconciliation_record_is_complete
tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_tables_match_carriers
tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_values_match_receipts_and_carriers
tests/gate2/integration/test_scale_restart_decision.py::test_only_carried_metrics_are_measured_and_unavailable_metrics_are_explicit
tests/gate2/integration/test_scale_restart_decision.py::test_rebuilt_metrics_003_binds_git_objects_frozen_preregistration_and_exact_carriers
tests/gate2/integration/test_scale_restart_decision.py::test_receipt_binds_exact_dependencies_and_synthetic_scope
tests/gate2/integration/test_scale_restart_decision.py::test_workload_bounds_and_freeze_are_recorded_before_measurements
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_both_runs_self_verified_at_execution_time
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_disposition_justifies_no_additional_mechanism
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_durable_journals_are_complete_and_ordered
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_every_preregistered_metric_has_a_matching_committed_carrier
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_fault_injection_evidence_was_derived_from_executed_observations
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_identity_is_reproducible_across_independent_invocations
tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_real_scale_evidence_remains_not_observed
tests/gate2/integration/test_synthetic_run_execution.py::test_bounded_run_measures_every_preregistered_metric
tests/gate2/integration/test_synthetic_run_execution.py::test_cli_run_executes_and_reports_disposition
tests/gate2/integration/test_synthetic_run_execution.py::test_integrity_verification_detects_tampered_artifacts
tests/gate2/integration/test_synthetic_run_execution.py::test_interruption_resumes_from_journal_without_duplicate_writes
tests/gate2/integration/test_synthetic_run_execution.py::test_repeated_runs_reproduce_identity_but_not_wall_clock
```

### PR258_BOUNDED_ADMISSION — 22 exact node IDs

```text
tests/vip_fvs/unit/test_bounded_admission.py::test_absolute_outside_root_and_dotdot_refuse
tests/vip_fvs/unit/test_bounded_admission.py::test_admits_regular_file_as_immutable_digest_bound_bytes
tests/vip_fvs/unit/test_bounded_admission.py::test_admitted_bytes_cannot_be_forged_with_self_declared_digest
tests/vip_fvs/unit/test_bounded_admission.py::test_admitted_bytes_replace_cannot_forge_digest
tests/vip_fvs/unit/test_bounded_admission.py::test_admitted_bytes_replace_cannot_introduce_mutable_data
tests/vip_fvs/unit/test_bounded_admission.py::test_descriptor_close_failure_is_a_typed_refusal
tests/vip_fvs/unit/test_bounded_admission.py::test_digest_mismatch_returns_no_buffer
tests/vip_fvs/unit/test_bounded_admission.py::test_digest_verified_requires_actual_authoritative_binding
tests/vip_fvs/unit/test_bounded_admission.py::test_fifo_refuses_without_blocking
tests/vip_fvs/unit/test_bounded_admission.py::test_final_and_parent_symlinks_refuse
tests/vip_fvs/unit/test_bounded_admission.py::test_growth_refuses_without_reading_beyond_initial_admitted_size
tests/vip_fvs/unit/test_bounded_admission.py::test_invalid_limits_are_a_typed_refusal_before_file_access
tests/vip_fvs/unit/test_bounded_admission.py::test_missing_nofollow_capability_refuses_without_fallback
tests/vip_fvs/unit/test_bounded_admission.py::test_oversize_refuses_before_read_or_allocation
tests/vip_fvs/unit/test_bounded_admission.py::test_path_replacement_refuses_after_descriptor_open
tests/vip_fvs/unit/test_bounded_admission.py::test_post_read_fstat_failure_is_a_typed_refusal
tests/vip_fvs/unit/test_bounded_admission.py::test_returned_buffer_has_no_mutable_alias
tests/vip_fvs/unit/test_bounded_admission.py::test_root_descriptor_open_failure_is_a_typed_refusal
tests/vip_fvs/unit/test_bounded_admission.py::test_truncation_refuses_without_partial_result
tests/vip_fvs/unit/test_bounded_admission.py::test_trusted_root_cannot_be_forged_without_validated_factory
tests/vip_fvs/unit/test_bounded_admission.py::test_trusted_root_refuses_symlink_in_any_ancestor_component
tests/vip_fvs/unit/test_bounded_admission.py::test_visible_same_inode_mutation_refuses
```

### LAB_SYNTHETIC — 37 exact node IDs

```text
tests.vip_lab.test_mega17_editorial_readiness::test_workstream_d_consumes_mega15_and_preserves_lineage_and_mandatory_flags
tests.vip_lab.test_mega17_editorial_readiness::test_workstream_d_refuses_a7_stream_ambiguity_and_it6_tail_mismatch_and_vfr_fps
tests.vip_lab.test_mega17_editorial_readiness::test_workstream_d_refuses_semantic_boundary_and_forged_editorial_authority
tests.vip_lab.test_mega17_editorial_readiness::test_workstream_d_tampered_packet_is_rejected
tests.vip_lab.test_mega17_end_to_end::test_mega17_end_to_end_three_arm_and_single_arm_deterministic_replay
tests.vip_lab.test_mega17_end_to_end::test_mega17_single_and_three_arm_keep_matching_upstream_scenario_lineage
tests.vip_lab.test_mega17_end_to_end::test_mega15_16_pipeline_preserves_custom_single_arm_membership
tests.vip_lab.test_mega17_end_to_end::test_mega17_rejects_upstream_occurrence_drop_even_when_membership_sets_match
tests.vip_lab.test_mega17_end_to_end::test_mega17_rejects_foreign_upstream_arm_labels
tests.vip_lab.test_mega17_end_to_end::test_mega17_eight_readiness_dimensions_and_maturity_model_ceilings
tests.vip_lab.test_mega17_end_to_end::test_mega17_cross_workstream_foreign_key_and_digest_continuity
tests.vip_lab.test_mega17_end_to_end::test_mega17_thirty_category_adversarial_and_invariant_matrix
tests.vip_lab.test_mega17_gate0_readiness::test_workstream_c_gate0_readiness_receipt_and_mandatory_flags
tests.vip_lab.test_mega17_gate0_readiness::test_workstream_c_deterministic_synthetic_scoring_thresholds_and_verdicts
tests.vip_lab.test_mega17_gate0_readiness::test_workstream_c_refuses_protocol_violations_and_synthetic_promotion
tests.vip_lab.test_mega17_gate0_readiness::test_workstream_c_tampered_receipt_is_rejected
tests.vip_lab.test_mega17_integration_readiness::test_workstream_a_inventory_covers_mega03_through_mega16_and_gate0_media
tests.vip_lab.test_mega17_integration_readiness::test_workstream_a_transplant_conflict_detector_catches_collisions_and_pr_overlaps
tests.vip_lab.test_mega17_integration_readiness::test_workstream_a_refuses_canonical_completion_or_main_mutation_claims
tests.vip_lab.test_mega17_integration_readiness::test_workstream_a_refuses_candidate_with_transplant_conflicts
tests.vip_lab.test_mega17_integration_readiness::test_workstream_a_tampered_digest_is_refused
tests.vip_lab.test_mega17_release_readiness::test_workstream_e_consumes_mega16_and_enforces_seven_stages_and_mandatory_flags
tests.vip_lab.test_mega17_release_readiness::test_workstream_e_all_twelve_e12_negative_refusal_checks_individually
tests.vip_lab.test_mega17_release_readiness::test_workstream_e_refuses_derived_receipt_provenance_upgrade_and_executable_ffmpeg
tests.vip_lab.test_mega17_release_readiness::test_workstream_e_tampered_packet_is_rejected
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_closed_synthetic_d2_fixture_and_invariants
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_synthetic_dev_eval_partitions_are_disjoint_on_all_identity_axes
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_identical_filename_as_byte_identity
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_duplicate_occurrence_collapse_or_auto_skip
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_forged_owner_attestation_and_d3_claims
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_discovery_granting_processing_or_model_or_export
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_dev_eval_partition_leakage
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_cross_partition_identity_overlap[development_session_ids-evaluation_session_ids]
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_cross_partition_identity_overlap[development_content_ids-evaluation_content_ids]
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_cross_partition_identity_overlap[development_query_ids-evaluation_query_ids]
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_refuses_cross_partition_identity_overlap[development_query_text_ids-evaluation_query_text_ids]
tests.vip_lab.test_mega17_source_readiness::test_workstream_b_tampered_packet_is_rejected
```
