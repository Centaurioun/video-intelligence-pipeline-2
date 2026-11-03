# Rejected Alternatives and Reconsideration Triggers

**Information state:** `FROZEN_DECISION` + `INFERRED_DESIGN` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`  
**Authority parent:** ADR-0002

## Purpose

Preserve alternatives already considered so future ChatGPT/Codex sessions do not repeatedly reopen settled questions without new evidence.

A rejected alternative may be reconsidered only when its stated trigger becomes true.

## A1 — Migrate the Active V1 Project to SigLIP2 Before V1 Completion

**Decision:** Rejected.

**Why:** The current V1 effort already has an active implementation, provenance, tests, and execution frontier. Changing the representation before V1 is complete would reopen established work and destroy the clean V1 baseline needed for the later benchmark.

**Reconsider only if:** the V1 implementation becomes impossible to complete because the current SigLIP1 Base dependency itself becomes unusable and no bounded repair exists.

## A2 — Maintain Three Permanent Duplicated Repositories

**Decision:** Rejected as the default architecture.

**Why:** The benchmark needs three reproducible candidates, not three permanently diverging applications.

Preferred mechanism:

- immutable candidate SHAs/tags;
- isolated branches/worktrees during development;
- model/profile separation where the final code naturally supports it.

**Reconsider only if:** V2 Base and V2 So400m genuinely require incompatible application architectures that cannot share one implementation without unsafe conditionals or broad complexity.

## A3 — Add SigLIP1 So400m as a Mandatory Fourth Benchmark Arm

**Decision:** Rejected for the required practical benchmark.

**Why:** ADR-0002 asks the operational question:

`V1 Base vs V2 Base vs V2 So400m`

SigLIP1 So400m would mainly help isolate “generation effect” from “scale effect.” That is scientifically useful but not required for the first practical representation decision.

**Reconsider only if:** benchmark results are ambiguous and the project specifically needs to determine whether gains arise from SigLIP2 training changes or model scale.

## A4 — Fully Index the ~400-Hour Archive With Every Candidate

**Decision:** Rejected for model selection.

**Why:** It spends the dominant compute cost before the project knows which representation merits archive-scale use.

**Required approach:** small frozen representative benchmark first.

**Reconsider only if:** full-scale behavior itself becomes the experimental question under Gate 2 and separate authorization exists.

## A5 — Reuse V1 768-D Embeddings for V2 Base Because the Width Matches

**Decision:** Rejected absolutely.

**Why:** Equal dimension does not create semantic-space compatibility. Model weights, processor, preprocessing, and learned coordinates differ.

**Reconsideration trigger:** none under current architecture. A future separately validated cross-model mapping would be a new research project, not an exception to this rule.

## A6 — Compare Candidates by Raw Cosine Scores

**Decision:** Rejected.

**Why:** Score magnitudes across different semantic spaces are not directly calibrated quality measures.

**Required approach:** shared relevance/ranking outcomes and operational metrics.

**Reconsider only if:** an independently validated cross-model calibration method is designed and tested.

## A7 — Pick the Largest/Newest Model Without a Project Benchmark

**Decision:** Rejected.

**Why:** Public results and model scale justify testing but do not establish utility for ballet/dance/performing-arts retrieval on the target archive.

**Reconsideration trigger:** none for production selection. Local evidence remains required.

## A8 — Build a General Multi-Provider / Arbitrary-Model Plugin Framework

**Decision:** Rejected as YAGNI.

**Why:** The accepted candidate set is known. A broad framework would increase migration risk and review surface without current evidence that it is needed.

**Reconsider only if:** the project formally adds multiple unrelated model families/providers whose integration cannot be expressed through the bounded model-profile design.

## A9 — Use Provider/Cloud Inference for the Migration by Default

**Decision:** Rejected as the default direction.

**Why:** The project is local-first/selectively hybrid and current preparation does not authorize provider calls or network egress.

**Reconsider only if:** a later Gate-1 capability study explicitly authorizes a provider arm with privacy, provenance, cost, and timestamp limitations documented.

## A10 — Rewrite Historical Gate-0 Evidence to Reflect the New Model Architecture

**Decision:** Rejected.

**Why:** Historical audits and run evidence are part of project provenance. They should remain accurate to the state that produced them.

**Required approach:** add successor decisions, designs, and evidence.

**Reconsideration trigger:** factual correction of an actual historical error, documented as such; not convenience.

## A11 — Modify the Historical V1 Gate-0 Adapter in Place by Default

**Decision:** Not selected as the default.

**Why:** A successor representation adapter may preserve V1 reproducibility more cleanly.

**Reconsider only if:** final V1 architecture shows that the historical adapter is already the deliberate current abstraction and a narrowly compatible extension is safer than a successor boundary.

## A12 — Make Sampling Density a Variable in the Three-Way Model Benchmark

**Decision:** Rejected for the primary comparison.

**Why:** Changing sampling and representation simultaneously confounds the result.

**Required approach:** freeze equivalent source-native sample positions across candidate arms.

**Reconsider only if:** a separate experiment is explicitly designed to study representation × sampling interaction.

## A13 — Let the Benchmark Adapt Queries After Seeing Model Outputs

**Decision:** Rejected.

**Why:** It creates post-hoc goalpost drift and model-specific tuning.

**Required approach:** freeze query/relevance/metric/winner rules before final comparison.

**Reconsideration trigger:** none within the same benchmark. A revised query set requires a new benchmark version and all affected arms rerun.

## A14 — Treat Better Retrieval as Stronger Temporal Evidence

**Decision:** Rejected.

**Why:** Retrieval representation and exact temporal authority are different layers.

**Reconsideration trigger:** none under current project evidence architecture.

## A15 — Implement the Synthetic Rehearsal During Preparation

**Decision:** Deferred, not required now.

**Why:** The current objective is to reduce later workload without touching product/test code. A code-free rehearsal specification captures the test shape while avoiding drift against an unfinished V1.

**Reconsider only if:** a future pre-completion decision explicitly authorizes a disposable non-production prototype and accepts its staleness cost.

## Reconsideration Discipline

When reopening any item:

1. cite the trigger that became true;
2. present new evidence;
3. compare the reopened alternative with the currently accepted path;
4. preserve the original rejection in history;
5. obtain the appropriate design/authorization before implementation.
