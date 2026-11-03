# Owner adoption — H3-C05 read-only query-multi successor v1.0.2

**Decision date:** 2026-10-26  
**Authority:** Repository Owner, explicit in-conversation scoped authorization  
**Status:** ADOPTED — GOVERNING CONTRACT INTERPRETATION ONLY; SOURCE EXECUTION NOT_AUTHORIZED

The Owner explicitly adopted the versioned v1.0.2 consumed-contract successor in the signed and reviewed [PR #220](https://github.com/Centaurioun/video-intelligence-pipeline/pull/220), with permission **only** to prepare new versioned governing contract/Core files, matching Atlas/prompt references, synthetic contract tests and independent verification. Existing frozen versions and historical receipts must remain preserved.

**Controlling predecessor proposal:** `.orchestration/remaining-work/runs/controller-wave-20261027/c05-v1.0.2-consumed-contract-successor-proposal-20261027.md` (at `main@a9b6240cd10ae6acd8c6a014bd598ffb6307800c`; Git blob `b94302925298c9c184efec9d36b156013d42205d`).

**Adopted interpretation:** The C05 multi-source query uses already-existing generation query-only `SemanticIndexEngine.build_generation_spec` and `.query` through `retrieve_multi_source`; not `retrieval_adapter.retrieve` because the latter indexes source content. It preserves exact manifest locator+digest matching, distinct duplicate-content occurrences, source native locator PTS/timebase without exact cut inference, `MATCHED` / nonbinding evidence, stable rank/order/provenance, and no media opening or index mutation. A separate `query_local_index` coordinator API is additive and nonrequired. Do not add live token revalidation or generation-snapshot cryptographic claim without a new governing decision.

**Updated consumed producer Git blobs:**
- `src/vip_fvs/retrieval_adapter.py@main`: `0f0268d83da4ff6c06c45ad54d85070071d6e155`
- `src/vip_fvs/coordinator.py@main`: `1696b31afc58d83269389f025759b2ef7dba7670`
- `src/vip_fvs/semantic_index.py`: `e81fd15ee243b59b02bace14131c9d6b39b66701`
- `docs/architecture/CANONICAL_CONTRACTS.md`: `c0b665d70b311dd98b7ff9f4f564b2d5750ed17b`

**Not adopted / expressly forbidden:** C05 source implementation, inferred hard-dependency completion, authentic runtime testing, real or protected media read/probe/hash/scan, model downloads/loads, provider/cloud, production editing/export, Gate promotion, historical core rewrite or canonical-main direct source write. The new Core is adopted for specification only; launch eligibility requires a separate current owner grant and controller dependency/lease preflight.

**Versioned artifact:** `.orchestration/remaining-work/prompts/H3-C05/v1.0.2/core.md` + `core.json`. The original v1.0.1 remains immutable.
