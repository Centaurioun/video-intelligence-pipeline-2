# Owner adoption — H3-A04 Option B primitive-producer interpretation v1.0.1

**Decision date:** 2026-10-26  
**Authority:** Repository Owner, explicit in-conversation scoped authorization  
**Status:** ADOPTED — GOVERNING CONTRACT INTERPRETATION ONLY; TASK-6 IMPLEMENTATION NOT_AUTHORIZED

The Owner explicitly selected **Option B** in the independently reviewed [PR #220](https://github.com/Centaurioun/video-intelligence-pipeline/pull/220), and permitted only new versioned governing Core/contract files, related prompt/Atlas references, synthetic contract tests, and independent verification. The historical v1.0.0 Core, all immutable Task-4/5/6 source/spec/plan objects, and declined alternatives remain preserved.

**Controlling predecessor proposal:** `.orchestration/remaining-work/runs/controller-wave-20261027/a04-owner-decision-instrument-v1.0.0-20261027.md` (at `main@a9b6240cd10ae6acd8c6a014bd598ffb6307800c`; Git blob `9c70be286b480939e0971db52408d3e49162fbcb`).

**Adopted interpretation:** `_run_codesign_entitlements(application)` is the sole one-shot signer-observation *subleaf* and returns exactly one successful `subprocess.CompletedProcess[bytes]` measurement. The boundary validates successful return code and byte stdout, then derives the five-field `N4ABoundaryPrimitive` **exactly once** from accepted S1 bytes and the observed signer bytes. The same primitive instance is forwarded, with identity `is` across registration, Task-4, Task-5, `N4ASealHandoff.measured_primitive` and `N4AProductionResult.primitive`; source/capability aliases, Task-3 descriptor-anchored write-free lifecycle, same-flow binding and refusals are unchanged. No alternate producer, second constructor, retry, manufactured measurement or optional handoff.

The earlier statement “fixed measurement leaf is sole primitive producer” is interpreted as a **single boundary measurement-and-primitive-production flow**, not that the signer observation helper returns the primitive. This is a versioned clarification, not a rewriting of the old Frozen Core.

**Not adopted / expressly forbidden:** Task-6 product source edits or active build/sign/codesign, protected media, provider/cloud, model loads/downloads, production export, Gate promotion, direct canonical-main writes, old source/contract destruction. Separate exact implementation authorization is still required after reference/hash/dependency reconciliation.

**Versioned artifact:** `.orchestration/remaining-work/prompts/H3-A04/v1.0.1/core.md` + `core.json`. Original `H3-A04/core.md` / `core.json` remain immutable.
