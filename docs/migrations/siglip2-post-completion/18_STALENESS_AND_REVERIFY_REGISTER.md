# Staleness and Reverification Register

**Information state:** `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Purpose

Prevent a future agent from treating pre-completion preparation as final implementation truth.

The current V1 project is still evolving. Therefore every mutable fact is assigned a refresh rule.

## Categories

### FROZEN_DECISION

Reverify only if a newer explicit user decision or governing repository decision supersedes it.

Examples:

- ADR-0002 candidate sequence;
- source-media immutability;
- semantic timestamps are candidate evidence only;
- source-native PTS/timebase authority;
- three-way benchmark before full-archive winner-driven indexing.

### STRUCTURAL_EXPECTATION

Likely durable architecture but still inspect after V1 completion.

Examples:

- semantic-space identity should bind model/provenance fields;
- incompatible spaces fail closed;
- model migration should remain isolated from temporal/edit/QC semantics.

### SNAPSHOT

Observed at a specific repository SHA and expected to drift.

Examples:

- file paths;
- symbol names;
- constants;
- dependency versions;
- test file locations;
- duplicate runtime-construction call sites.

### OFFICIAL_EXTERNAL

True of the referenced upstream source when captured, but must be checked again before operational use.

Examples:

- Hugging Face repository file inventory;
- Transformers SigLIP2 preprocessing docs;
- model config fields;
- PyTorch MPS behavior/documentation.

## Reverification Table

| Item | Current state | Source | Refresh trigger | Future action |
|---|---|---|---|---|
| ADR-0002 sequence | FROZEN_DECISION | ADR-0002 | explicit superseding decision only | preserve |
| V1 completion SHA | NOT_OBSERVED | future repo | V1 completion | freeze exact SHA/tag |
| V1 model/revision/digests | SNAPSHOT | current V1 evidence | V1 completion | compare to final candidate |
| `EMBEDDING_DIM = 768` | SNAPSHOT | current code | V1 completion | search final code |
| `768 * 4` write-side constants | SNAPSHOT | current indexer/storage/tests | V1 completion | search final code |
| `SiglipModel/SiglipProcessor` loader | SNAPSHOT | V1 adapter | V1 completion | inspect final runtime |
| V1 `PROCESSOR_ASSETS` list | SNAPSHOT | model_space.py | V1 completion | inspect final list |
| V1 text contract shorthand | SNAPSHOT | model_space.py | V1 completion | inspect final contract |
| query search dimension-aware behavior | SNAPSHOT | search.py | V1 completion | rerun code audit/tests |
| V2 Base exact revision/hash | NOT_OBSERVED | future acquisition | authorized acquisition | freeze exact values |
| V2 So400m exact revision/hash | NOT_OBSERVED | future acquisition | authorized acquisition | freeze exact values |
| SigLIP2 Base upstream file inventory | OFFICIAL_EXTERNAL | HF repo | before acquisition | re-fetch |
| SigLIP2 text preprocessing defaults | OFFICIAL_EXTERNAL | Transformers docs | before implementation | re-fetch exact docs/version |
| So400m config geometry | OFFICIAL_EXTERNAL | HF config | before acquisition | re-fetch exact revision/config |
| PyTorch MPS API/behavior | OFFICIAL_EXTERNAL | PyTorch docs | runtime freeze | verify selected torch version |
| exact future Python version | NOT_OBSERVED | future runtime | migration activation | freeze receipt |
| exact future Transformers version | NOT_OBSERVED | future runtime | migration activation | freeze receipt |
| exact future PyTorch version | NOT_OBSERVED | future runtime | migration activation | freeze receipt |
| full 400h indexing duration | NOT_OBSERVED | future measurement | separately authorized run | measure, do not infer |
| candidate winner | NOT_OBSERVED | three-way benchmark | benchmark completion | decide using frozen rules |

## Automatic Stale Conditions

Treat a preparation artifact as stale if any of these occur after it was captured:

- canonical V1 code path renamed/moved;
- model/runtime abstraction introduced;
- embedding dimension handling changes;
- processor digest implementation changes;
- dependency management changes;
- authorization boundary changes;
- benchmark decision is superseded;
- official model repository changes materially.

Stale does not mean incorrect history. It means not safe as current execution input until refreshed.

## Refresh Priority

At V1 completion refresh in this order:

1. authority decisions;
2. completion SHA and V1 reproducibility identity;
3. code/symbol migration surface;
4. hard-coded assumptions;
5. dependency/runtime state;
6. external model contracts;
7. test/acceptance mapping;
8. runbooks/handoffs;
9. benchmark preparation.

This ordering prevents later documents from being refreshed against already-stale lower-level facts.

## Provenance Rule

When updating a snapshot, retain the previous capture in Git history.

Do not rewrite old dates/SHAs to make an old snapshot appear current.

## 2026-10-11 Controlled Task 0 Reconciliation

| Artifact / claim | 2026-10-11 state | Evidence / remaining gate |
|---|---|---|
| V1 completion source identity | `VERIFIED_GIT_REF`; preserved V1 is an ancestor of canonical main. | `3586eeaa904fc5a2e6a2745078611886f482f3de`; canonical `748818e867ce08ccc2367bad21df7d83eaf51d70`. |
| Migration-relevant code/test surface | `REFRESHED_CURRENT`; relevant code/test paths are identical between preserved V1 and canonical main. | Task 0 report and Git path comparison at those exact SHAs. |
| Model-coupling/hard-code surface | `REFRESHED_CURRENT`; 768-wide session/writer/validator and V1 loader assumptions remain. | Append-only evidence in `07` and `08`; no code change. |
| Model-profile seam | `REFRESHED_CURRENT`; `SemanticSpace` and callable runtime seams exist; no closed `ModelProfile` exists. | Append-only evidence in `10`; current design remains applicable. |
| Test/acceptance mapping | `REFRESHED_CURRENT` for T001–T026. | `14_TEST_AND_ACCEPTANCE_MATRIX.md` and Task 0 `test-acceptance-matrix.json`; 811 distinct model-free synthetic passes. |
| Installed test environment | `OBSERVED_TEST_ENVIRONMENT_ONLY`; not the frozen final V1 runtime. | `13_DEPENDENCY_RUNTIME_COMPATIBILITY.md`; no model imports/assets opened. |
| Historical V1 model/runtime receipts | `HISTORICAL_PROVENANCE_ONLY`; applicability to preserved V1 is not freshly proven. | Pilot receipt plus Git-only preservation receipt; model bytes/runtime were not inspected. |
| External source receipts | `BLOCKED`; source receipts remain captured at 2026-10-05. | No external primary-source fetch was authorized in this refresh. |
| V2 Base/SO400M checkpoint identity and runtime | `BLOCKED / NOT_OBSERVED`. | Requires separate model acquisition/inspection authority; no local assets touched. |
| Plan/protocol step count | `RESOLVED`: the owner-accepted original plan blob `78127a9199a912531d5b2240eed66e93814d83f3` covers protocol Steps 1–13. | A prior refresh candidate recorded a 12-versus-13 discrepancy; that was a historical candidate observation, not current status. The plan text remains preserved. |
| Readiness and full refresh receipt | `NO_GO_BLOCKED`; full receipt remains blocked. | A versioned Task 0 progress receipt records exact verified fields and blockers; it does not replace template 30 or grant execution authority. |

Earlier preparation dates and source SHAs remain historical records. The appended state is a new observation and does not backdate or rewrite them.

## Post-adoption status reconciliation

PR #69 merged at `7f4a5ce1baf7de2aa580f1043502458336bf57fe` and records owner acceptance of plan blob `78127a9199a912531d5b2240eed66e93814d83f3` for planning. The accepted plan now names all 13 steps; its successor documentation blob is not the original accepted blob. The seven migration snapshot/test/runtime documents in this section are adopted by the current consolidation candidate, and E01–E10 source refresh documents 20/21 are reconciled from `229d08f564fb8c21a7a119fc900eaac82cb64cd0`. F07 retains `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; tokenizer semantic uncertainty and the overall `NO_GO_BLOCKED` disposition remain.
