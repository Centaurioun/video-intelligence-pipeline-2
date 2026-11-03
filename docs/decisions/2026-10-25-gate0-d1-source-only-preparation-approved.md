# Decision — Gate-0 D-1 source-only preparation authorization (2026-10-25)

**Decision status:** `OWNER_APPROVED_D1_IN_CHAT` · `D2_INPUTS_PENDING` · `D3_EXECUTION_NOT_AUTHORIZED` · `GATE0_EXPERIMENT_NOT_RUN`.

## Authority and audit trail

- The Owner answered **"Onaylıyorum."** to an explicit request to approve **only Gate-0 D-1 bounded source-code preparation and synthetic tests**. This is an **in-chat Owner decision**, recorded in the repository by the reconciliation assistant; it does not purport to be an Owner-authored GitHub comment.
- Source of D-1/D-2/D-3 definitions: **PR #182**, pinned packet commit `4a65bff0904c60163bf501014e07fbe5d4239cfc`, file `docs/gate0/OWNER_AUTHORIZATION_INPUT_PACKET_2026-10-25.md`. PR #182 remains OPEN until its own disposition; its presence does not authorize experiment execution. Decision also recorded in PR #182 comment `6396540654`.
- Planning/reconciliation base: `main@18a86820ccc78dbfa2dd571661ea9a6d3e813289`. Verify latest live `main` and file ownership before executing any lane.
- Governing constraints remain `AGENTS.md`, `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `docs/implementation-spec-v1.1.md`, `docs/implementation-spec-v1.1.1-erratum.md`, frozen schemas and `docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md`.

## Approved D-1 deliverables, and ONLY these

1. **P-08.1–P-08.7 source-only preparation:** a distinct, explicit `authorized_local` corpus declaration/entry path with a separate provenance and runtime gate; no spoofed generated-fixture provenance and no accidental fallback; guarded real-manifest assembly from declarations; editor-authored query and human-gold input loaders, never synthetic labels used as authentic truth; strict metadata-to-model boundary; model adapter/decoder integration seams that fail closed when weights, inputs, licences and operational authorization are missing; reproducible dependency-lock preparation where locally verifiable, without downloads.
2. **P-05 reviewer-envelope assembly tool:** build/validate a strictly blinded two-human input envelope compatible with existing `gate0.evaluation.load_reviewer_input` and frozen contract. Only generated/artificial reviewer fixtures in tests; no human labels fabricated as authentic evidence.
3. **P-09 digest/config-freeze tooling:** preflight checks and canonical digest calculation with synthetic inputs, explicit refusal on absent/unapproved values and no all-zero placeholder accepted as a real frozen configuration. Never invent model/processor, rights, policy, input-root or sandbox digests.
4. **Verification:** chronological RED→GREEN TDD in isolated exclusive-writer worktrees, preservation of all original synthetic paths and frozen thresholds, failure/negative cases, and GitHub PR-level checks. No source branch merge by an executor.

## Operational prohibitions and gates

- **D-2 has not been answered with real inputs.** Corpus sessions/revisions/rights/retention, source paths, relationships, editor's 40 genuine query texts, two human reviewers/adjudicator, authentic model asset licence/root, policy egress data and Linux `bwrap`/macOS Stage-B host have **NOT_OBSERVED** status.
- **D-3 has not been authorized.** Do not open, stat for content, hash, probe, decode, index or otherwise touch any real/protected archive source. Do not download/load/infer using actual model weights; no provider/cloud/network egress, no real input-root mounts, no scored run, no production export, no Gate-promotion decision. Tests may use repository fixtures and generated disposable MP4 only.
- A source-only preparation implementation must fail closed on a real `authorized_local` attempt without a separately attested D-2 input/rights package **and** explicit D-3 run authorization. Development test simulation is not an operational grant. No new manual development SOURCE-AUTH permission bureaucracy (ADR-0003).
- **Do not load or download `torch`, `transformers`, model weights, or other packages merely to make a D-1 test pass.** Dependency-lock work must use verified repository/local metadata; report a blocker if a compatible pinned lock cannot be established offline. PyPI calls are not implicitly authorized.
- Reviewer access to a real evaluation corpus **also requires explicit real-source access permission**: the PR #182 §6 critical-chain suggestion that reviewers start examining real media after D-1/D-2 is not itself that grant. Creating *text-only* review templates requires no media access.
- No alteration of the frozen 24-positive (6/family) + 8-absent evaluation set, 8 development queries, 2 reviewers, 4-second windows, 2-FPS targets, 13 required artifacts, 20/24 Hit@10, +5/24 paired lift, 3/6 family threshold, or `NOT_RUN` synthetic non-promotion.
- No scope expansion to Gate 1–3, production, credentials, or the Owner-frozen backup `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe@17edacbe64983ae284f09a8386377200bf538ec3`.

## Approved execution subdivision

Three independent owner-exclusive paths, separately reviewed and integrated through one controlled path:
- `G0-D1-A` P-08 execution/corpus/model-preflight core; sole writer for existing `src/gate0/{cli.py,execution.py,media_experiment.py}` and `requirements/gate0.lock` and its dedicated new tests.
- `G0-D1-B` P-05 reviewer-envelope assembler; owns new `src/gate0/reviewer_envelope.py` and new dedicated tests only.
- `G0-D1-C` P-09 freeze inspector; owns new `src/gate0/config_freeze.py` and new dedicated tests only. Existing `config.py` remains contract-frozen pending a separate cross-owner contract decision.

Exact tasks: `docs/superpowers/plans/2026-10-25-gate0-d1-source-only-preparation.md`. Separate agents may work simultaneously only with verified no-overlap and clean worktrees. The owner has approved this development scope, **not** the detailed downstream interface assumptions that would rewrite a frozen contract.

## Six-cycle acceptance discipline

1. Recheck governing and current source facts; 2. audit D-1/D-2/D-3 authority; 3. prefer additive isolated input/preflight seams over rewriting the generated-fixture pipeline; 4. execute bounded TDD lanes; 5. independent security/data-provenance review; 6. verify candidate SHAs/tests/CI before any source integration, preserving real Gate-0 as `NOT_RUN`.
