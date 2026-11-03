# Gate-0 Recovery **Evidence DAG** — Design Specification — **REVISION 18 — RR17 FINAL SPECIFICATION-CLOSURE SUCCESSOR**

**Run:** `run-20260923-gate0-rev18-remediation-v1`  
**Author:** ChatGPT Gate-0 Revision-18 final specification-closure author (GPT-5.6 Sol / High), sole writer on
`chatgpt/gate0-rev18-final-spec-closure-v1` under explicit owner architecture/specification-remediation
authority only.  
**Revision identity:** **REVISION 18 — RR17 FINAL SPECIFICATION-CLOSURE SUCCESSOR**. Revision 17 at
`dc861c25600335c5b23fc7b09ea4fec51ef34144`, spec blob
`6be127319148c38aa8ebcbeb07055eff932e96e4`, is the exact frozen review predecessor and remains
historical review evidence. Its later freeze-record commit
`a2e92a9d145eea700152eec980f36d1efa90b231` is metadata only and is not this branch base.  
**Revision-18 author base:** exactly `dc861c25600335c5b23fc7b09ea4fec51ef34144`; no Revision-17 freeze
commit, RR17 reviewer branch, moderator branch, canonical main, Gate-0 controller or future reviewer branch
is substituted as candidate ancestry.  
**Owner-approved dependency architecture:** `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`, from
`164bec97f720683504bc740c6b4a0abccc85def9` / blob
`0e4bfa5acb8791dbb9c032d7668fb3e2d6a6eada`.  
**Owner-approved A2R seed authority:** `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1`, from
`3f8f2fa98d97f8720c4a1a9687dcaab5a29225cd` / blob
`591c525ce8d517d8d44e2fa9f8803a19167c2102`.  
**Owner-approved M1R refinement:** `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`, decision
`GATE0-RR13-M1R-RUNTIME-CLOSURE-OWNER-DECISION-2026-09-22`, separately pinned at
`e7c3bb00fe6133d709506ab441ea1489bc20eaa8` /
`docs/agent-runs/run-20260922-gate0-rev13-independent-review-v1/owner-approved-m1r-runtime-closure-decision.md` /
blob `ccd39d7f31241514e50156a8a68a4d7765d079d2`.  
**Binding RR17 independent-review findings:** `RR17-2-F01` and `RR17-2-F02`, adjudicated as
specification-closure defects inside the existing approved architecture by moderator convergence
`159d36666bdd42b3bc02d299bf295b3840e67055` /
`docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/moderator-convergence-and-rev18-direction.md` /
blob `deac5f778d8e0b7afa26aec8e3093056378cf046`. RR17-1 and RR17-3 independently passed their
reviewed surfaces. No new owner architecture decision or C² amendment is required.  
**Self-identity:** eventual Revision-18 review-subject SHA/spec blob are deliberately absent and are
recorded forward-only after creation.  
**Current successor design-authority candidate:**
`docs/gates/gate0/rulings/2026-09-23-rr17-final-specification-closure-design-ruling.md`,
decision id `GATE0-RR17-FINAL-SPECIFICATION-CLOSURE-DESIGN-RULING-2026-09-23`.  
**Selected architecture:** `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`;
`G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1`;
`G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`; `OD_1_B_ONLY`;
future security baseline `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`.

**Current M1R availability:** `PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`.
`GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`.

**Status:** `GATE0_RECOVERY_EVIDENCE_DAG_SPEC_REVISION_DRAFT`. Design/specification review candidate
only. It is not implementation, an implementation plan, runtime policy, Gate promotion or independent
certification. No profile-freeze measurement, `otool`, `/usr/bin/file`, host dependency/runtime scan,
Homebrew query, pip operation, venv provisioning, dependency installation, build/sign, Generation B,
live Stage B, provider/model activity, dependency/model download or protected-media activity is claimed.

---

## 1. Authority, revision identity, and scope

| Item | Identity | State |
|---|---|---|
| Shared contracts | `docs/architecture/CANONICAL_CONTRACTS.md`, blob `c0b665d70b311dd98b7ff9f4f564b2d5750ed17b` | byte-unchanged |
| C² rev-6 | `docs/superpowers/specs/2026-09-13-gate0-stage-b-c2-hostname-resolver-evidence-design.md`, blob `f0d070f6e34ca107c03c8cfd35b79b246110f4a0` | byte-unchanged; amendment not required |
| Frozen recovery plan | `docs/superpowers/plans/2026-09-20-gate0-recovery-evidence-dag-implementation-plan.md`, blob `827ad4e19f56812562dc93376a36f33204800a8d` | byte-unchanged; stale lower-authority material; not approved/executable |
| Root ruling | `docs/gates/gate0/rulings/2026-09-20-recovery-evidence-dag-design-ruling.md`, blob `8259d48aac1bac40878a5288fc70e95f353431ac` | preserved except formal limited supersession |
| B+D1 ruling | `docs/gates/gate0/rulings/2026-09-22-n4a-boundary-primitive-design-ruling.md`, blob `82f035fbe45f4af99a72174b7af7bdb54609789e` | preserved |
| Revision-8 convergence ruling | `docs/gates/gate0/rulings/2026-09-22-rev8-review-convergence-design-ruling.md`, blob `9570052f5b3af5a180f13bbdcd1dc246566e2c1d` | preserved |
| **Revision-13 review subject** | `7360cfb98c619eb21850405c3da613906a595c0a`, spec blob `5c9749a591640bdbb7fe5966b1724621a25f883c` | immediate frozen predecessor; historical review evidence |
| Revision-13 ruling | `docs/gates/gate0/rulings/2026-09-22-rr12-a2r-seed-authority-remediation-design-ruling.md`, blob `96889dd8a309e5056dd8cdea7ebae9a867eae6f8` | preserved historical candidate record; not rewritten |
| **Revision-14 predecessor ruling** | `docs/gates/gate0/rulings/2026-09-22-rr13-m1r-runtime-closure-remediation-design-ruling.md`, blob `1d7ec387334edd8878aef887d75233bb7456586e` | preserved historical candidate record; not rewritten |
| **Revision-14 review subject** | `0d7e093d3651ed6d8ea1ac241291c5e964792d35`, spec blob `71f20ebc9a20992396cd508d1ae555d991096b55` | immediate frozen predecessor; historical review evidence |
| **Revision-15 predecessor ruling** | `docs/gates/gate0/rulings/2026-09-22-rr14-specification-closure-remediation-design-ruling.md`, id `GATE0-RR14-SPECIFICATION-CLOSURE-REMEDIATION-DESIGN-RULING-2026-09-22`, blob `a4f6eec5e315a7b377dd2f76edd6127e03a3a57b` | preserved historical candidate record; not rewritten |
| **Revision-15 review subject** | `55b3375c841820f0b5f88d35f7c9a184d1cd7635`, spec blob `78dbd0d5bd72a3bd1430c7fc52dec289b12dfe8f` | immediate frozen predecessor; historical review evidence |
| **Revision-15 pre-review blocker** | `9bda1d56d37f6596e6744dc85b50fdb17194e43a` / `docs/agent-runs/run-20260922-gate0-rev15-independent-review-v1/pre-review-mechanical-intake-blocker.md` / blob `0678e5b3ca3bdf8203e187eafb0acf6fdac08be0` | binding forward-correction evidence; no architecture decision |
| **Revision-16 predecessor ruling** | `docs/gates/gate0/rulings/2026-09-23-rev15-pre-review-mechanical-correction-design-ruling.md`, id `GATE0-REV15-PRE-REVIEW-MECHANICAL-CORRECTION-DESIGN-RULING-2026-09-23`, blob `b0a749b03cda474783d820fcfa26261378728fbd` | preserved historical candidate record; not rewritten |
| **Revision-16 review subject** | `948f726f144dc591eb7629ff417a199870b3bcbf`, spec blob `3f5afcee6fd001d692367cf75c4949efabf6af3a` | exact immediate frozen predecessor; historical review evidence |
| **Revision-16 freeze record** | `ff74daa9902553a569e93fc6b4274876ce5a823f` | later metadata only; not Revision-17 ancestry base |
| **RR16-1** | `review/gate0-rev16-r1-authority-c2-v1@ee13c979deb9f7a2a5d7e1ec8e4eda252886b980`, memo blob `60dc69c84a9964bf84ee91f065c3695f0bd99c0f` | PASS; authority/C²/mechanical/evidence lifecycle closures preserved |
| **RR16-2** | `review/gate0-rev16-r2-m1r-runtime-v1@5d91dabf820402e14f4a8a1a5c83a77816af0f45`, memo blob `a446bf497d75887ed36c36e1adf28e8c1901a377` | BLOCKED; `RR16-2-F01` and `RR16-2-F02` accepted for Revision-17 specification closure |
| **RR16-3** | `review/gate0-rev16-r3-macho-structure-v1@eebb158d463bf4e529e622177080c2da5d290c26`, memo blob `7bb51e7e18cef878413ecf5a020e10c90e9a5038` | BLOCKED; `RR16-3-F01` accepted for Revision-17 specification closure |
| **RR16 moderator convergence** | `f5655988c093db258006b98090da95fa55c85fd0` / `docs/agent-runs/run-20260923-gate0-rev16-independent-review-v1/moderator-convergence-and-rev17-direction.md` / blob `32f09a56678c6009d789d0d9590f33e5ee70268a` | binding Revision-17 remediation direction; no new architecture decision; C² amendment not required |
| **Revision-17 predecessor ruling** | `docs/gates/gate0/rulings/2026-09-23-rr16-independent-review-remediation-design-ruling.md`, id `GATE0-RR16-INDEPENDENT-REVIEW-REMEDIATION-DESIGN-RULING-2026-09-23`, blob `2aaa56f0e3fc911321a558c36c00787d0e280a6b` | preserved historical candidate record; not rewritten |
| **Revision-17 review subject** | `dc861c25600335c5b23fc7b09ea4fec51ef34144`, spec blob `6be127319148c38aa8ebcbeb07055eff932e96e4` | exact immediate frozen predecessor; historical review evidence |
| **Revision-17 freeze record** | `a2e92a9d145eea700152eec980f36d1efa90b231` | later metadata only; not Revision-18 ancestry base |
| **RR17-1** | `review/gate0-rev17-r1-authority-c2-v1@c4abb77e957de9fcedfb3f075d17a303fd63def9`, memo blob `8febd9b8c8aabc5e86f70e6803cd6a7ab677de70` | PASS; authority/C²/mechanical/evidence lifecycle surfaces preserved |
| **RR17-2** | `review/gate0-rev17-r2-stable-census-v1@970aed4566f291d3f4a5b4560af0d56f3b91b9b1`, memo blob `495050d1ac7f223322ebb0b82758f540f1dedd53` | BLOCKED; `RR17-2-F01` and `RR17-2-F02` accepted for Revision-18 specification closure |
| **RR17-3** | `review/gate0-rev17-r3-macho-header-v1@0e953d185a5550aa5e7a2787b6d24a1a9dee3fa0`, memo blob `b47f7a42fbc3fa5c2785aa01d3463539c8a16f78` | PASS; Header64/FAT/54-43-43/same-byte surfaces preserved |
| **RR17 moderator convergence** | `159d36666bdd42b3bc02d299bf295b3840e67055` / `docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/moderator-convergence-and-rev18-direction.md` / blob `deac5f778d8e0b7afa26aec8e3093056378cf046` | binding Revision-18 closure direction; no new architecture decision; C² amendment not required |
| **Revision-18 successor ruling** | `docs/gates/gate0/rulings/2026-09-23-rr17-final-specification-closure-design-ruling.md`, id `GATE0-RR17-FINAL-SPECIFICATION-CLOSURE-DESIGN-RULING-2026-09-23` | formal successor candidate |
| **Option-A owner decision** | `164bec97f720683504bc740c6b4a0abccc85def9` / `docs/agent-runs/run-20260922-gate0-rev11-independent-review-v1/owner-approved-architecture-decision.md` / blob `0e4bfa5acb8791dbb9c032d7668fb3e2d6a6eada` | separately pinned immutable owner decision; not candidate ancestry |
| **A2R owner decision** | `3f8f2fa98d97f8720c4a1a9687dcaab5a29225cd` / `docs/agent-runs/run-20260922-gate0-rev12-independent-review-v1/owner-approved-a2r-seed-authority-decision.md` / blob `591c525ce8d517d8d44e2fa9f8803a19167c2102` | separately pinned immutable owner decision; not candidate ancestry |
| **M1R owner decision** | `e7c3bb00fe6133d709506ab441ea1489bc20eaa8` / `docs/agent-runs/run-20260922-gate0-rev13-independent-review-v1/owner-approved-m1r-runtime-closure-decision.md` / blob `ccd39d7f31241514e50156a8a68a4d7765d079d2` | separately pinned immutable owner decision; closed architecture choice |
| RR13-1 | `review/gate0-rev13-r1-authority-c2-v1@135cc326bcf6c2d120f02888e41c940c6dddfa2b`, memo blob `d672952d36971419cd8ac8dd912bd966427fbed2` | PASS; authority/C²/mechanical surfaces preserved |
| RR13-2 | `review/gate0-rev13-r2-oracle-isolation-v1@55dcf0b37c95bd3d664e5a894a98b7f93e283028`, memo blob `8aa255c3c61279c020d0c188d374fb98ae4b3dde` | PASS; `RR13-2-N01` bookkeeping correction accepted |
| RR13-3 | `review/gate0-rev13-r3-a2r-seed-authority-v1@29d89a7cafcf651d737931eb71b87eb9a13b0531`, memo blob `1740e438a748874f84c75fb1e05d26de64899cbb` | AD-01/AD-02 owner-resolved by M1R; F01 specification repair required |
| RR13-4 | `review/gate0-rev13-r4-macho-closure-v1@5efb58a42c688437a8b2986fa22b403adb25a461`, memo blob `d805632fe981519819add28072a16275500fd1d5` | F01/F02 specification repairs required; other reviewed closure surfaces preserved |
| RR13 moderator convergence | `37dbf2761f4ebfd59f129371d3eb5567b3e21cfa` / `docs/agent-runs/run-20260922-gate0-rev13-independent-review-v1/moderator-convergence-and-a2r-runtime-closure-options.md` / blob `788e4e04a6c918b1fa48a44098254349bdfe950f` | historical adjudication evidence only; not candidate ancestry |
| RR14-1 | `9b0db9dd4915c995f0d1206fec6c1e001c5ed6af`, memo blob `7cbe0072de345e803bf3c62b8a5dc98b7123c2f2` | PASS; authority/C²/mechanical surfaces preserved |
| RR14-2 | `27b2e747b4a139fa85629089799346900956e029`, memo blob `90221126079a4bd6e9230696ca18e40ad5f0a4e0` | BLOCKED; F01–F04 accepted for Revision-15 specification closure |
| RR14-3 | `25c3679298f2a5dd8b48d560a70dba85e8c630b7`, memo blob `d414d9407265108ded38220628a6462677c4fd54` | BLOCKED; F01–F02 accepted for Revision-15 specification closure |
| RR14-4 | `40892cf0969349dfd1c751b4ffe79df433f57b03`, memo blob `8c0fc890ea441ff1fb52e2fc88a963142f6db0ad` | PASS; evidence/profile-freeze lifecycle preserved |
| RR14 moderator convergence | `0e44fa59022fd22c833539211f9dbaf63af8510d` / `docs/agent-runs/run-20260922-gate0-rev14-independent-review-v1/moderator-convergence-and-rev15-direction.md` / blob `3aa01a6aa09230962180770b58792feb9028530f` | binding remediation direction; no new architecture decision |

### 1.1 Revision identity and history policy

**Current revision:** **REVISION 18 — RR17 FINAL SPECIFICATION-CLOSURE SUCCESSOR**.

Revision 17 is preserved exactly as the immediate frozen review subject. RR17-1 and RR17-3 PASS surfaces
remain inherited and are not reopened. RR17-2's already-closed stable-census/path surfaces remain inherited.
Revision 18 repairs only the two moderator-accepted specification-closure defects:

- `RR17-2-F01`: total resolver termination under continually fresh externally observed symlink identities,
  by a project-owned hard 32-expansion ceiling;
- `RR17-2-F02`: explicit separation of arbitrary bounded-root ordinary-file native candidacy from the
  closed native-container parser entry contract.

The Revision-18 successor ruling preserves the root §6 supersession protocol by naming
`GATE0-RECOVERY-EVIDENCE-DAG-DESIGN-RULING-2026-09-20` in `supersedes`, while separately naming the
Revision-17 ruling as its immediate predecessor successor-record. Its normative formal field table and
labelled canonical JSON projection must have exact field-name and typed-value equality.

None of the three explicit owner decisions is claimed to have a cryptographic owner signature. Supported
authority remains limited to the repository-resolvable explicit owner acts at their immutable tuples, the
independent RR17 reviewer evidence, the binding RR17 moderator convergence above, and the current explicit
owner delegation for this bounded specification remediation.

### 1.2 Scope and explicit non-authorization

This specification authorizes no implementation or implementation-plan change/execution, profile-freeze
measurement, `otool`, `/usr/bin/file`, host dependency/runtime scan, Homebrew query, pip operation,
dependency install, build/sign, Generation B, live Stage B, provider/model call, network egress,
protected/archive-media processing, runtime-policy decision, Gate promotion, canonical-main mutation,
Gate-0-controller mutation or destructive cleanup.

Runtime policy remains a separate future pre-execution artifact under `CANONICAL_CONTRACTS.md` §5.
Nothing here is runtime `ALLOW`.

C² is not modified. M1R narrows/mechanizes legal A2R seed eligibility and deterministic S1 construction
only. Same-S1 renderer semantics and network-entitlement security remain unchanged.

## 2. Selected architecture, successor authority, and bounded RR14 remediation

### 2.1 Closed owner decisions

Three owner choices are binding and are not reopened:

1. `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`.
2. `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1`.
3. `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`.

M2/M3, original auto-drifting A2, A3, A4, Option B/C, runtime tracing as dependency authority,
open-ended host scanning, full Python runtime-tree attestation and wheel/RECORD reconstruction are not
selected. M1R remains a narrow permission-shaping runtime-closure refinement, not a full
software-supply-chain attestation system.

Revision 18 introduces exactly two bounded specification-closure refinements inside the already selected
architecture:

- **RD18-01:** `PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1 = 32` gives each
  `PATH_CANONICALIZATION_V1` invocation a project-owned finite progress bound. The exact hop-limit reason
  `CANONICALIZATION_FAILURE_HOP_LIMIT` belongs to the existing `CANONICALIZATION_FAILURE` terminal
  family and P25 failure semantics; no new DAG node, evidence class, predicate or global failure-code
  family is introduced.
- **RD18-02:** `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(bytes)` becomes the only Census-A/B ordinary-file
  native/non-native classifier, while `MACHO_NATIVE_CONTAINER_PARSE_V1(bytes)` remains the closed native
  parser entry. Unlisted ordinary-file prefixes are `NON_NATIVE`; unlisted encodings already entering the
  native parser fail `REJECT_UNSUPPORTED`. No external parser may promote future magic.

Revision 18 preserves Revision-17 **RD17-01** (closed canonicalization result families/cycle semantics),
**RD17-02** (project-writer quiescence + stable Census A/B protocol), and **RD17-03** (exact Header64
grammar), plus Revision-16 **RD16-01** and all Revision-15 closure decisions. In particular it preserves:

- generation-bound `RUN_SCOPED_VENV_ROOT_V1`;
- exhaustive two-root enumeration and unique symlink/cross-root scope law;
- exact active-state S4 key-set closure;
- complete FAT32/FAT64 outer structural grammar;
- complete project-owned `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`;
- deterministic Tier-1 falsifiers and accepted-policy↔structure-row bijection;
- all RR17-1 and RR17-3 PASS surfaces and all RR17-2 surfaces not challenged by its two findings.

No new DAG node, retained raw closure manifest or namespace census, primitive event field, runtime selector,
runtime nonce, cryptographic attestation, P19 class, P20 mode, predicate or global failure code is
introduced.

### 2.2 Design-authority chain and phase-correct resolution

The normative candidate lineage remains the historical root/B+D1/Revision-8/Revision-11/Revision-12/
Revision-13/Revision-14/Revision-15/Revision-16/Revision-17 design line plus this Revision-18 candidate. Option-A, A2R and M1R owner decisions, RR17 reviewer memos and moderator convergence are separately pinned immutable repository objects, not candidate ancestry.

Three resolution phases remain normative:

1. **candidate-lineage:** objects actually present in the Revision-18 candidate tree, including this specification and the new Revision-18 ruling;
2. **separately pinned immutable repository objects:** all three owner decisions and RR17
   review/adjudication evidence resolve only at their explicit immutable commit/path/blob tuples;
3. **future integrated controller:** only after independent review, later owner approval and integration
   may P19(d) bind the then-governing `base_controller_commit`; candidate/reviewer/moderator/sibling SHAs
   never substitute.

| Decision family | Revision-18 preserved application |
|---|---|
| historical DR-1/DR-2/DR-9 | historical B1 preserved; future universal-B1 role remains formally superseded |
| DR-3 / `OD-6` | Tier-1 must verify before Generation B |
| DR-5 / `OD-9` | privacy-reduced tracked projection only; complete app not retained |
| DR-10 / B+D1 | existing S9 primitive; P3a/P3b/P4 truth unchanged |
| AD-R8-01..03 | N5 subject, generation root and P19/P20 structure preserved |
| AD-R9-01 + RD11-03/04 | exact same production post-measurement core; fixed private leaf; single-use closure |
| Option A | dependency architecture remains verifier-derived static Mach-O closure |
| A2R | exact frozen Python/lock and FFmpeg/FFprobe identities remain prerequisites |
| M1R | permission-shaping Python native closure + canonical Homebrew formula/keg roots mechanize A2R without full supply-chain attestation |
| RR13-2 PASS | ordinary production package/import/module-search reachability of the test oracle remains mechanically excluded |
| RR13-4 closed surfaces | context-sensitive path resolution, fixed point, same-byte identity/parse/materialization, system exclusion, optional-registry emptiness, global de-dup/family/order and privacy/later-audit remain normative |

### 2.3 `OD_1_B_ONLY` is fixed design, not runtime branching

There are no S5/S6 nodes, A/B selector, `od_1_reading`, runtime authority election or OD-1(a) fallback.
Historical B1
`c6e5d05824bfd8a6f5d20ba6b24567bd741779d4ad8838d735116b596390a0e4`
remains historical evidence only, never a future pass condition. The future entitlement-policy baseline
remains `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`.

### 2.4 M1R baseline availability is a hard eligibility prerequisite

Repository evidence contains no measured authoritative
`PYTHON_NATIVE_RUNTIME_CLOSURE_V1` digest/member count. Therefore this revision normatively preserves:

`PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`

and:

`GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`.

A future narrow local profile-freeze measurement requires separate explicit owner authorization, yields
MEASURED evidence only if actually performed, and still requires a later narrow owner-approved seed-profile
record to pin its digest/count. This specification authorizes neither future act.

### 2.5 Provenance stated honestly

The explicit owner decisions are repository-resolvable only at their separately pinned tuples. No
cryptographic owner attestation is claimed. Design authority, independent review, later owner approval,
profile-freeze measurement, runtime policy, implementation authorization and execution authorization
remain separate acts.

## 3. Artifact model

### 3.1 Nodes

`S0`…`S13` are retained from the architecture authority, **minus the two `OD-1(b)`-only nodes `S5` and
`S6`, which this revision does not define.** Every node has exactly one creating stage and exactly one owner. Every node
names at least one consumer in its own `TABLE-NODES` row; for the terminal retention surface `S13` those
consumers are the tracked run ledger and later audits, resolved by path. Rank is the dependency position (§4.3).

| ID | Semantic name | Purpose | Created at | Owner | Identity / digest home | Rank | Named consumer(s) |
|---|---|---|---|---|---|---|---|
| `S0` | `HISTORICAL_HEAD` | pre-existing substantive head plus Generation A's sealed terminal record; ancestry anchor | by reference | repository history | its commit SHA | 0 | `S7` (parent), `S10` (named commit) |
| `S1` | `EFFECTIVE_RENDER_INPUT_SNAPSHOT` | verifier-produced deterministic canonical privacy-minimal projection of **exactly** renderer-effective inputs, including effective write root and verifier-derived dependency inventories; all paths obey §12.2 | `N2` | **verifier** | bytes pinned in `S7`; N5 anchor digest in `S11`; N4a renderer-handoff commitment in `S9` | 1 | `S2`, `S7`, `S9`, `S11`, `S12` |
| `S2` | `RENDERED_ENTITLEMENTS` | the exact rendered entitlement bytes intended for signing | `N2` | producer | bytes pinned in `S7`; N5 anchor digest recorded in `S11`; N4a signer-handoff commitment and sealed-payload binding retained in `S9` | 2 | `S7`, `S9`, `S11`, `S12` |
| `S3` | `RUN_CONFIG` | exact `argv`; the **declared** output root and its **closed-vocabulary provenance token**; `execution_mode`; `target_safety_validation_ref`; and the **echoed** verifier-derived authority tuple. `S3` carries **no** copy, digest, path reference or subtree of `S1` (§4.5) | `N2` | producer | bytes pinned in `S7`; digest recorded in `S11` | 1 | `S7`, `S11` |
| `S4` | `SOURCE_IDENTITY` | **pre-build, bundle-independent** tool/source blobs/version identity plus the exact required non-authoritative A2R/M1R echo object of `TABLE-S4-A2R-M1R-ECHO-SCHEMA`, and the **pre-build declared** signing-policy values. Missing/extra/wrong-type/conflicting A2R/M1R echo fields fail P25; **no post-build value may appear in `S4`** (§7.4, §12.4) | `N1` | producer | bytes pinned in `S7`; digest recorded in `S11` | 1 | `S7`, `S11` |
| `S7` | `PREBUILD_ANCHOR` — commit `A` | content-addressed commit of the immutable pre-build set | `N3` | producer (commit creation only; content is `S1`…`S4`) | its own commit SHA, assigned by the container; no path inside its tree records it | 3 | `S9` (parent), `S13` (parent and contains bytes), `S10` |
| `S9` | `SIGNED_BUILD_OUTPUT_EVIDENCE_SEAL` — commit `B` | the privacy-reduced projection of the build output `N4a` produced, plus the durable verifier-owned `n4a_boundary_primitive` event commitments; commit `B` is the **durable repository seal/projection and identity anchor**, not N5's operational `codesign` subject | `N4b` | **verifier** | its own commit SHA is recorded forward in `S10` (`TABLE-EDGES` row 23); `identity.json` carries the pre-`B` `SIGNING_TIME_STABLE_CODEDIRECTORY_IDENTITY` and verifier-owned `n4a_boundary_primitive`; `S10` remains the forward-only home for `B` commit/tree/member identities; §8.6 | 4 | `S11`, `S13` (parent), `S10` |
| `S8` | `S8_VERIFIER_EXTRACTION_BYTES` | **the exact verifier-derived operational entitlement extraction bytes captured at N5 from the transient sealed signed application produced by this generation's N4a**, retained byte-exact | `N5` | **verifier** | digest recorded in `S10`; bytes and digest retained in `S13`'s tree | 5 | `S11`, `S12`, `S13` |
| `S11` | `VERIFICATION_RECORD` | predicate results; anchored-set re-check; authority echo-coherence result; **`VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` application/result**; the gate record; the design-record record required by `P17` | `N6a` | producer | digest recorded in `S10` | 6 | `S10`, `S12`, `S13` |
| `S12` | `REPRODUCIBILITY_ATTESTATION` | deterministic re-render proof; non-vacuity controls | `N6b` | producer | digest recorded in `S10` | 7 | `S10`, `S13` |
| `S10` | `RESULT_MANIFEST` | **the post-seal identity home** — `B`'s commit SHA, `B`'s tree SHA and the member blob ids — created **last** among result artifacts; self-excluding | `N6c` | producer | self-excluding; integrity comes from `S13`'s tree | 8 | `S13` |
| `S13` | `EVIDENCE_PACKAGE` — commit `E` | pure-addition descendant of `S7`; the retention and audit surface | `N7` | producer | content-addressed commit SHA, recorded forward only in the tracked run ledger | 9 | the tracked run ledger and later audits (by path) |

**Canonical anchor-digest homes and N4a event commitments are distinct.** `S1`…`S4` are pinned by
the `S7` commit; the verifier's **N5 anchor-digest records** for those artifacts are recorded in `S11`,
and `S10` is not a second anchor-digest home for them. The `S12 ⟸ S2` `RECORDS_DIGEST` relation names
the canonical `S11` digest for reproducibility accounting. Revision 15 preserves the two
**contemporaneous N4a event commitments** in `S9.identity.json.n4a_boundary_primitive`:
`renderer_input_sha256` over the exact `S1` renderer handoff and `signer_entitlements_sha256` over the
exact `S2` signer handoff, each with its octet count. Those values are not duplicate N5 anchor-digest
fields; they exist to bind the historical handoff event and are consumed by `P3a`/`P3b`/`P4`.
Accordingly `S9 ⟸ S1` and `S9 ⟸ S2` are `RECORDS_IDENTITY` event-binding dependencies. The separate
`S8 ⟸ S2` `RECORDS_IDENTITY` relation continues to bind the sealed entitlement payload through the
parsed-equality rule of `P8`. `S8`, `S9` and `S11`/`S12` are recorded in `S10`.

**No path inside `S7`'s tree records `S7`'s own SHA**, and no path inside `B`'s tree records `B`'s own SHA
or `B`'s tree SHA: such an artifact would have to contain the hash of the commit or tree containing it,
which has no fixed point. Their identities are recorded forward only, in `S10` and — for the package commit — in
the tracked run ledger.

### 3.2 Conditional nodes, dropped nodes, counts

**This revision declares no conditional node.** Every row of `TABLE-NODES` is always present. The
historical runtime branch-selection nodes `S5` (`OWNER_RULING`) and `S6` (`OWNER_DELTA`) remain **not defined**. Revision 17 remains OD-1(b)-only by design authority, not by a runtime branch or selector; those historical nodes remain preserved by reference only (§2.3). `S7`'s Git tree **is** the anchor manifest, so no separate manifest artifact is defined.

### 3.3 Declared counts — derived echoes, not normative authority

**Every count in the table below is a non-normative *echo* of its declared authority, which is a table in
this document for every row except the two whose authority is a set declared in prose** — the
`Conditional nodes` set of §3.2 and the `Rank groups` set of the §4.3 rank assignment, both still checked
by their own `Checked by` row. The
normative content of each closure surface is that authority itself; the count exists only so a reader can
see the shape, and each declared value is independently re-derived from its authority by **the count-bearing
check named in its own `Checked by` cell** — not by a single blanket check. **No declared count may be treated as the authority for its own
table, and — as a general rule for every derived fact in this document — a value that can be derived from
a normative table must not be restated in prose unless a named mechanical check re-derives it from that
table.** If a later revision adds or removes a row, the table changes and the echo is corrected by
re-derivation — never the reverse. The stable table identities are defined in §17.

| Quantity | Declared echo | Authority for the echo | Checked by |
|---|---|---|---|
| Nodes | **12** | row count of `TABLE-NODES` (§3.1) | `V-1` |
| Conditional nodes | **0** | §3.2 | `V-2` |
| Stages | **9** (`N0`…`N8`) | row count of `TABLE-STAGES` (§4.1) | `V-2` |
| Sub-stages | **5** (`N4a`, `N4b`, `N6a`, `N6b`, `N6c`) | row count of the §4.2 sub-stage table | `V-2` |
| Rank groups | **10** (ranks `0`…`9`) | distinct ranks in §4.3 | `V-3` |
| Dependency edges | **28** | row count of `TABLE-EDGES` (§4.4) | `V-4` |
| Declared non-edges | **3** | row count of `TABLE-NONEDGES` (§4.5) | `V-6` |
| Predicates | **29** (`P1`…`P25`, with sub-identifiers `P3a`/`P3b`, `P5a`/`P5b` and `P18a`/`P18b`/`P18c`) | row count of `TABLE-PREDICATES` (§5.2) | `V-8` |
| Distinct failure codes | **29** | row count of `TABLE-CODES` (§13.1) | `V-11` |
| Verification checks | **21** (`V-1`…`V-21`) | row count of `TABLE-VERIFICATION-CHECKS` (§15) | `V-13` |
| Tier-1 gate rows | **21** | row count of `TABLE-TIER1-GATE` (§14.2) | `V-14` |
| Tier-1 adversarial-matrix data rows | **316** | data-row count of `TABLE-TIER1-ADVERSARIAL-MATRIX` (§14.2.1) | `V-14` |
| Load-bearing machine-readable tables | **14** | row count of the table directory in §17 (each row names one stable table id) | `V-15` |

---

## 4. Stage order, rank model, and the explicit edge table

### 4.1 The nine stages

| Stage | Action | Writes | Fails closed on |
|---|---|---|---|
| **N0** | Record `S0` (pre-existing head plus Generation A's sealed terminal record), by reference | nothing | — |
| **N1** | Freeze `S4`, then verify the **verifier-derived authority tuple** of §7.2 and record the generation's echo-coherence result | `S4` | `AUTHORITY_ECHO_MISMATCH` |
| **N2** | Under `VERIFIER_MATERIALIZED_CANONICAL_ROOT_V1` + `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1` + `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1` + `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`, verifier authorizes and resolves exact event-time seeds, derives dependency membership/cardinality/family/order by the closed Mach-O fixed-point contract, lawfully materializes fixed/indexed roles, constructs and freezes verifier-produced `S1`, renders `S2` from `S1` only, writes `S3`; producer-proposed dependency universes/lists are never authoritative | `S1`, `S2`, `S3` | `RENDER_INPUT_NOT_FROZEN`, `OUTPUT_ROOT_AMBIGUOUS`, `GENERATION_IDENTITY_COLLISION`, `DEPENDENCY_INVENTORY_DERIVATION_INVALID` |
| **N3** | Freeze `S7` (commit `A`, parent `S0`) adding **exactly** `{S1,S2,S3,S4}`; re-read every anchored path from the commit object | `S7` | `PREBUILD_ANCHOR_NOT_FROZEN` |
| **N4** | Build/sign through the verifier-owned immutable handoff boundary: measure the exact `S1` renderer handoff and exact `S2` signer-entitlement handoff (SHA-256 plus octet count), pass those same immutable byte objects onward, then seal in sub-order `N4a ≺ N4b` (§4.2) | `S9` (the destination is scratch, never a tracked path) | `RENDER_INPUT_NOT_FROZEN`, `SIGNING_ENTITLEMENTS_NOT_FROZEN`, `SIGNING_IDENTITY_DRIFT`, `BUILD_OUTPUT_SEAL_NOT_FROZEN`, `SEAL_PROJECTION_ELISION_INVALID` |
| **N5** | Verifier measurement on two explicit surfaces: operational `codesign -d --entitlements :-` extraction from the verifier-owned transient sealed signed application produced by this generation's N4a, plus repository-object re-reads from durable commit `B`; capture exact `S8`, retain its digest, evaluate exact signed-payload binding, `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`, and entitlement-key closure | `S8` | `SIGNED_BYTES_NOT_VERIFIER_DERIVED`, `FROZEN_EVIDENCE_MUTATED_BY_BUILD`, `ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE`, `ENTITLEMENT_ALLOWLIST_VIOLATION` |
| **N6** | Result artifacts in sub-order `N6a ≺ N6b ≺ N6c` (§4.2) | `S11`, `S12`, `S10` | `ANCHOR_DIGEST_NOT_RECORDED`, `POLICY_CLOSURE_RESULT_NOT_RECORDED`, `RENDER_NOT_BYTE_REPRODUCIBLE`, `REPRODUCIBILITY_PROOF_VACUOUS`, `RESULT_MANIFEST_NOT_FINAL`, `AUTHORITY_CONSUMPTION_NOT_RECORDED` |
| **N7** | Commit `S13` `EVIDENCE_PACKAGE`, parent `S9` | `S13` | `EVIDENCE_PACKAGE_NOT_ADDITIVE`, `EVIDENCE_NOT_RETAINED`, `EVIDENCE_REFERENCE_UNRESOLVED` |
| **N8** | Generation-B execution gate — the eligibility precondition of §14 | nothing | `GENERATION_B_TIER1_GATE_UNMET` |

**That table is `TABLE-STAGES`.** `N8` creates no artifact and produces no evidence; it is an explicit, named,
mechanically evaluated precondition, so that "Generation B must not execute" is a checkable statement
rather than a sentence in a document. It is evaluated **before entry** to any Generation-B lifecycle and
**re-asserted before `N7`**.

### 4.2 Sub-stages

| Sub-stage | Artifact | Constraint |
|---|---|---|
| `N4a` | (the verifier-owned transient sealed signed application) | **BUILD/SIGN + ORIGIN-PRESERVING MEASURE-AND-HANDOFF.** One production boundary entry point owns both governed handoffs; each S1/S2 handoff has exactly one governed call site to one fixed private internal measurement primitive. No production caller supplies/selects that primitive. Its return enters the same production post-return `measurement result => continuity state => capability` core in test and production. Tier-1 may substitute only that exact private leaf inside the test process; the oracle remains outside production. After return no branch may depend on test/oracle/measurer/environment/build/provider/runtime-adapter/config/helper discriminators, and no alternate scalar source/recomputation may exist. Same immutable object proceeds onward. Capability is opaque, invocation-bound, verifier-private, single-use, unretained and not a node. Failure closes under existing P3a/P4 codes and emits no S9. |
| `N4b` | `S9` `SIGNED_BUILD_OUTPUT_EVIDENCE_SEAL` | **SEAL.** Accept only the fresh capability from the immediately preceding production boundary and serialize its four values once. Copies share one consumption state: duplicate/current copy, second use after success and stale duplicate all fail. N4b has no oracle awareness, scalar/recompute/metadata channel or selectable measurer. Production surfaces expose no measurer selector through configuration/data or programmatic interfaces, and the test oracle is physically/logically absent from ordinary production package/import closure (§8.1); row 5 and `TABLE-TIER1-ADVERSARIAL-MATRIX` mechanically falsify selector plus package/import/re-export variants. Oracle is capability evidence only, never Generation-B config/retained/event evidence. |
| `N6a` | `S11` `VERIFICATION_RECORD` | may record `S1`…`S4`, `S7`, `S8`, `S9` and the design-record values required by `P17`; **must not** record `S10` or `S12` |
| `N6b` | `S12` `REPRODUCIBILITY_ATTESTATION` | may record `S1`, `S2`, `S8`, `S11`; **must not** record `S10` |
| `N6c` | `S10` `RESULT_MANIFEST` | may record `S0`, `S7`, `S8`, `S9` (commit SHA, tree SHA, member blob ids), `S11`, `S12` and the design-record values required by `P17`; **must exclude itself and `S13`'s commit SHA** |

`N2` creates three artifacts with an internal dependency (`S2 ⟸ S1`) but no sub-stage split: `S1` is
captured and frozen **before** `S2` is rendered, and `S3` is written from producer-authored values and
verifier-derived echoes only. This intra-stage order is stated because revision 1 created three artifacts
inside `N2` with an unmodelled dependency.

### 4.3 Notation law and rank assignment

Two relations are used, with disjoint symbols. The character `→` is **forbidden** in normative statements.

| Relation | Symbol | Reading | Law |
|---|---|---|---|
| **DEPENDENCY EDGE** | `C ⟸ P` | "`C` depends on `P`": `C`'s bytes depend on `P`'s identity or bytes | requires `rank(P) < rank(C)` |
| **EXECUTION ORDER** | `X ≺ Y` | "`X` is created or executed strictly before `Y`" | total over stages and sub-stages |

A dependency edge is **not** an execution-order statement, and an execution order does not by itself
create a dependency. **Ranks.** `0`: `S0`. `1`: `S1`, `S3`, `S4`. `2`: `S2`. `3`: `S7`. `4`: `S9`.
`5`: `S8`. `6`: `S11`. `7`: `S12`. `8`: `S10`. `9`: `S13`. That is the complete rank-group set; `V-3` re-derives its cardinality from this statement.

**Why the rank values survive the removal of `S5`/`S6` unchanged.** `S2` must outrank both of its
dependencies' positions, `S7` is `S0`'s child, and the seal/result chain is fixed by the architecture
authority's own topological order. Re-numbering the ranks would be a **cosmetic** change that would
falsify every rank value already verified by the architecture authority and by the revision-2 certifiers,
for no closure benefit. The rank values are therefore **retained as verified**; removing `S5` and `S6`
simply removes two members from rank `0` and rank `1` and leaves the ten distinct rank values `0`…`9`
intact and contiguous. `V-3` checks the declared group count against this complete rank-group statement, and `V-4`/`V-5` check
rank discipline per edge.

### 4.4 Dependency edge table (`TABLE-EDGES`) — the sole graph of record

No dependency may be inferred from prose: this table **is** the sole graph of record. Rows that existed
in revision 2 only for the `OD-1(b)` branch are removed; the surviving table is the complete graph.

| # | CONSUMER | CONSUMED | EDGE_TYPE | CONSUMER_RANK | CONSUMED_RANK | CHECK |
|---|---|---|---|---|---|---|
| 1 | `S2` | `S1` | `RENDERS_FROM` | 2 | 1 | PASS |
| 2 | `S7` | `S0` | `PARENT_OF` | 3 | 0 | PASS |
| 3 | `S7` | `S1` | `CONTAINS_BYTES` | 3 | 1 | PASS |
| 4 | `S7` | `S2` | `CONTAINS_BYTES` | 3 | 2 | PASS |
| 5 | `S7` | `S3` | `CONTAINS_BYTES` | 3 | 1 | PASS |
| 6 | `S7` | `S4` | `CONTAINS_BYTES` | 3 | 1 | PASS |
| 7 | `S9` | `S7` | `PARENT_OF` | 4 | 3 | PASS |
| 8 | `S9` | `S2` | `RECORDS_IDENTITY` | 4 | 2 | PASS |
| 9 | `S8` | `S2` | `RECORDS_IDENTITY` | 5 | 2 | PASS |
| 10 | `S11` | `S1` | `RECORDS_DIGEST` | 6 | 1 | PASS |
| 11 | `S11` | `S2` | `RECORDS_DIGEST` | 6 | 2 | PASS |
| 12 | `S11` | `S3` | `RECORDS_DIGEST` | 6 | 1 | PASS |
| 13 | `S11` | `S4` | `RECORDS_DIGEST` | 6 | 1 | PASS |
| 14 | `S11` | `S7` | `NAMES_COMMIT` | 6 | 3 | PASS |
| 15 | `S11` | `S8` | `RECORDS_DIGEST` | 6 | 5 | PASS |
| 16 | `S11` | `S9` | `NAMES_COMMIT` | 6 | 4 | PASS |
| 17 | `S12` | `S1` | `RENDERS_FROM` | 7 | 1 | PASS |
| 18 | `S12` | `S2` | `RECORDS_DIGEST` | 7 | 2 | PASS |
| 19 | `S12` | `S8` | `RECORDS_DIGEST` | 7 | 5 | PASS |
| 20 | `S12` | `S11` | `RECORDS_DIGEST` | 7 | 6 | PASS |
| 21 | `S10` | `S0` | `NAMES_COMMIT` | 8 | 0 | PASS |
| 22 | `S10` | `S7` | `NAMES_COMMIT` | 8 | 3 | PASS |
| 23 | `S10` | `S9` | `NAMES_COMMIT` | 8 | 4 | PASS |
| 24 | `S10` | `S8` | `RECORDS_DIGEST` | 8 | 5 | PASS |
| 25 | `S10` | `S11` | `RECORDS_DIGEST` | 8 | 6 | PASS |
| 26 | `S10` | `S12` | `RECORDS_DIGEST` | 8 | 7 | PASS |
| 27 | `S13` | `S7` | `CONTAINS_BYTES` | 9 | 3 | PASS |
| 28 | `S9` | `S1` | `RECORDS_IDENTITY` | 4 | 1 | PASS |

`S13` also stands in `PARENT_OF` and `CONTAINS_BYTES` relations to `S9`, and `CONTAINS_BYTES` to `S8`,
`S11`, `S12` and `S10`; those are **package-membership and history relations declared in §9.6**, not
additional dependency edges, and they are deliberately **not** rows of this table — the table records only
dependencies that constrain rank. Declaring them here would double-count the graph or imply rank
constraints that the packaging rule, not the dependency law, supplies.

### 4.5 Declared non-edges at shared ranks (`TABLE-NONEDGES`)

Two nodes of equal rank are **mutually independent by construction**: neither `X ⟸ Y` nor `Y ⟸ X` is
representable. Every equal-rank pair must therefore appear here with a basis.

| # | `X` | `Y` | RANK | INDEPENDENCE_BASIS |
|---|---|---|---|---|
| 1 | `S1` | `S3` | 1 | `S1` is the captured render input. `S3` carries producer-authored `argv`, the declared output root and provenance token, `execution_mode`, `target_safety_validation_ref`, and the echoed verifier-derived authority tuple; it embeds neither `S1`'s bytes nor its digest. Agreement of declared with effective root is a **predicate**, not a dependency. |
| 2 | `S1` | `S4` | 1 | `S4` is tool/source identity and declared signing-identity values; `S1` is render inputs. Disjoint field sets. |
| 3 | `S3` | `S4` | 1 | Run configuration vs tool/source and signing identity. Disjoint field sets. |

`S0` is alone at rank `0`, and ranks `2` through `9` each hold exactly one node, so there is no further
equal-rank pair. The declared non-edge set in `TABLE-NONEDGES` is therefore complete, and `V-6` checks that
the declared set equals the mechanically enumerated equal-rank pair set — including that the two cardinalities
agree.

### 4.6 Acyclicity consequence

Every dependency edge strictly decreases rank, and rank is a strict total order. A cycle would require a
strictly decreasing sequence returning to its start, which is impossible: the dependency graph is a DAG
**by construction**. This is what makes the historical mutual digest cycle unrepresentable.

---

## 5. Predicates

### 5.1 Tier vocabulary

Exactly four tier classes are declared, and no other tier label is admissible. `MACHINE_AVAILABLE_NOW`, `MACHINE_REQUIRES_TIER1` and `DOCUMENT_CHECK` label §5.2's predicate rows and `TABLE-VERIFICATION-CHECKS`'s rows; `NOT_OBSERVED` is an availability condition, not an evidence class.

| Class | Meaning |
|---|---|
| `MACHINE_AVAILABLE_NOW` | The deterministic check, **every tool it needs**, and **an instance of its subject** all exist in the repository at this base. At this base the class has **no members** among §5.2's predicates. |
| `MACHINE_REQUIRES_TIER1` | The check is deterministic in form, but at least one required implementation component does not exist at this base. **Such a predicate must never be described as enforced.** |
| `DOCUMENT_CHECK` | Checkable against this specification's own text by static inspection: counts, closure tables, vocabulary closure, key uniqueness, placeholder absence. |
| `NOT_OBSERVED` | An availability/status condition: the measurement was not taken. It is not an evidence class. |

A `DOCUMENT_CHECK` subject (§15) is this document's own text, which exists at this base. The
`MACHINE_AVAILABLE_NOW` emptiness claim above is scoped to **§5.2's predicate rows** only; §15's
`DOCUMENT_CHECK` rows are a different subject surface and are not predicates.

### 5.2 Predicate table

| # | Predicate | Stage | Class | Failure code |
|---|---|---|---|---|
| **P1** | **Verifier-derived authority binding and echo coherence.** The verifier derives the authority tuple of §7.2 from repository authority **before `N1`**, and `S3`'s echoed values equal the verifier-derived values exactly; `S3` never defines them | `N1`, re-asserted `N5` | `MACHINE_REQUIRES_TIER1` | `AUTHORITY_ECHO_MISMATCH` |
| **P2** | **Generation identity derivation and separation.** The generation identity is **verifier-derived**, never producer-chosen: `generation_identity = H(base_controller_commit ‖ applicable_spec_blob ‖ applicable_plan_blob ‖ generation_ordinal)`, where `generation_ordinal` is one plus the number of distinct generation identities already recorded in committed result manifests reachable from the current evaluation point. `S3` records it as an **echo**; a mismatch, or a reused identity, fails closed | `N2` | `MACHINE_REQUIRES_TIER1` | `GENERATION_IDENTITY_COLLISION` |
| **P3a** | **Capture-boundary coherence — render input.** **Truth condition unchanged:** the renderer consumed the frozen `S1` and nothing else. At `N4a` the verifier-owned boundary measures SHA-256 and octet count over the exact immutable `S1` object actually handed to the renderer and hands onward that same object; at `N4b` those values are retained in `S9.identity.json.n4a_boundary_primitive`. Later repository-only verification resolves governed `B`, reads the retained primitive, resolves parent `S7`, reads exact `S1`, recomputes SHA-256 + octet count and compares them. That later computation re-evaluates the durable binding; it does **not** physically re-observe historical `N4a`, and output equivalence alone is not evidence that the renderer consumed `S1` | `N2`, `N4a`, `N5` | `MACHINE_REQUIRES_TIER1` | `RENDER_INPUT_NOT_FROZEN` |
| **P3b** | **Capture-boundary coherence — exact canonical write role.** **Truth condition unchanged:** the effective write root from the actual frozen `S1` is exactly the verifier-assigned `roots.output` canonical role of §12.2, resolves uniquely, and agrees with `S3`'s declared root and provenance token. Later repository-only verification first establishes the `N4a` renderer-handoff binding to exact `S1` under `P3a`; then it parses that exact canonical write role from retained `S1`, reads `S3` from the **same parent `S7`**, and reruns the existing unique-resolution / declared-root / provenance-token comparison. No `S9 ⟸ S3` dependency and no root-specific duplicate primitive field is created | `N2`, `N4a`, `N5` | `MACHINE_REQUIRES_TIER1` | `OUTPUT_ROOT_AMBIGUOUS` |
| **P4** | **Sign-time byte binding.** **Truth condition unchanged:** the exact signer-handoff entitlement bytes equal frozen `S2` byte-for-byte, and the renderer consumed frozen `S1`. At `N4a` the verifier-owned boundary measures SHA-256 + octet count over the exact immutable `S2` object actually handed to the signer; `N4b` retains those values in the N4a primitive. Later repository-only verification compares `signer_entitlements_sha256` and `signer_entitlements_octets` against exact `S2` in parent `S7` and also requires the `P3a` renderer-input binding. It does not infer signer input from the final signed output | `N4a` | `MACHINE_REQUIRES_TIER1` | `SIGNING_ENTITLEMENTS_NOT_FROZEN` |
| **P5a** | **Seal freeze.** Commit `B` exists with `parent(B) = S7` and tree equal to `S7`'s tree plus exactly the projection paths, and every projection member re-read from the commit object equals the sealed bytes | `N4b` | `MACHINE_REQUIRES_TIER1` | `BUILD_OUTPUT_SEAL_NOT_FROZEN` |
| **P5b** | **Post-seal identity home.** `S10` records `B`'s commit SHA, `B`'s tree SHA and the member blob ids. **No member of `B`'s own tree carries `B`'s own SHA or tree SHA** (§8.6) | `N6c` | `MACHINE_REQUIRES_TIER1` | `SEAL_IDENTITY_HOME_INCOMPLETE` |
| **P6** | **Verifier-derived event-time extraction binding.** N5's operational `codesign -d --entitlements :-` subject is exactly the verifier-owned, generation-scoped, transient sealed signed application produced by this generation's N4a. No caller-supplied argument, producer-authored path, commit-B path reconstruction or alternate bundle may select it. Commit `B` remains the durable privacy-reduced seal/projection and identity anchor for repository-only checks; it is not the operational `codesign` subject | `N5` | `MACHINE_REQUIRES_TIER1` | `SIGNED_BYTES_NOT_VERIFIER_DERIVED` |
| **P7** | **Verifier-derived entitlement-policy closure.** Exact frozen S1 is a verifier-produced canonical projection whose dependency membership/cardinality/family/order was independently derived under `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1` from seeds authorized by `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1` as mechanically refined by `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`, including the required owner-pinned native-closure baseline, before freeze. Expected policy derives from canonical S1 roles + frozen renderer/schema semantics, never S2/S8/bundle/producer/config/discovery metadata. `parsed(exact S8)` must equal expected policy under **type-strict plist semantics**: Boolean is Boolean (`true` ≠ numeric `1`), arrays remain arrays with renderer-defined order, strings compare exactly after governed path normalization, no scalar/collection coercion, exact key/value sets. Path/key/type widening fails | `N5`; later retained S1+S8 audit | `MACHINE_REQUIRES_TIER1` | `ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE` |
| **P8** | **Exact `S8` retention.** The exact `S8_VERIFIER_EXTRACTION_BYTES` captured at `N5` from the lawful transient event-time subject are retained byte-exact in `S13`'s tree, and `parsed(S8) == parsed(EMBEDDED_ENTITLEMENT_PAYLOAD)`. The payload-to-`S8` **transformation** is optional/extra/non-load-bearing and is not a gate (§8.4) | `N5`, `N7` | `MACHINE_REQUIRES_TIER1` | `S8_NOT_RETAINED_EXACTLY` |
| **P9** | **Policy-closure result completeness.** `S11` records application/result of `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` for this generation, including predicate id/result and the governing successor design-record identity. The record is a **RESULT surface**, never primitive event evidence and never an expected-policy input | `N6a` | `MACHINE_REQUIRES_TIER1` | `POLICY_CLOSURE_RESULT_NOT_RECORDED` |
| **P10** | **Entitlement key closure.** Every key in the verifier-derived extraction is in `PERMITTED_ENTITLEMENT_KEYS`, and no `PROHIBITED_ENTITLEMENT_KEYS` key is present | `N5` | `MACHINE_REQUIRES_TIER1` | `ENTITLEMENT_ALLOWLIST_VIOLATION` |
| **P11** | **Signing-identity derived-value drift.** The **pre-build declared** values in `S4` (bundle identifier and signing policy) equal the verifier's own re-read of the sealed bundle, and the **post-build** derived values live only in the seal's `identity.json`, never in `S4`. The team identifier's status is fixed by the single normative privacy rule of §12.4 and is not restated here; no human-readable field participates | `N4a`, `N5` | `MACHINE_REQUIRES_TIER1` | `SIGNING_IDENTITY_DRIFT` |
| **P12** | **Seal projection integrity.** Every superblob member is retained byte-exact or elided-with-digest, and every elided member's recorded digest equals its slot or declared derived binding. **In the supported seal schema (`nSpecialSlots = 7`), the two unbound special slots −4 and −6 are additionally required to be all-zero entries carrying no object binding; a non-zero −4 or −6 is outside the supported projection contract and fails this predicate** (§8.3, §8.7) | `N4b`, `N5` | `MACHINE_REQUIRES_TIER1` | `SEAL_PROJECTION_ELISION_INVALID` |
| **P13** | **Privacy projection scan.** No **declared or textual** retained member — and no elided member's recorded name — contains a forbidden personal-data field class (§12.4). The opaque `CodeDirectory` byte blob is out of scope of this scan by construction, because it cannot be elided and is the identity pre-image | `N4b`, `N5` | `MACHINE_REQUIRES_TIER1` | `SEAL_PROJECTION_PRIVACY_VIOLATION` |
| **P14** | **Reproducibility byte equality.** A re-render from `S1` is byte-identical to `S2` | `N6b` | `MACHINE_REQUIRES_TIER1` | `RENDER_NOT_BYTE_REPRODUCIBLE` |
| **P15** | **Reproducibility non-vacuity.** An effective-field perturbation diverges; a non-effective perturbation does not | `N6b` | `MACHINE_REQUIRES_TIER1` | `REPRODUCIBILITY_PROOF_VACUOUS` |
| **P16** | **Result finalization order.** `S11 ≺ S12 ≺ S10`; `S10` excludes itself and `S13`'s commit SHA | `N6a`–`N6c` | `MACHINE_REQUIRES_TIER1` | `RESULT_MANIFEST_NOT_FINAL` |
| **P17** | **Design-record record.** S10/S11 record the current Revision-18 successor id and SHA-256 of exact authority bytes resolved at the future N1 controller evaluation through P19(d), plus provenance acknowledgement. The candidate-time chain distinguishes candidate-lineage records from separately pinned immutable owner/reviewer authority objects. Candidate/reviewer/moderator refs never substitute for future controller evaluation. P17 is record honesty, not runtime authority | `N1` pre-check, `N6c` | `MACHINE_REQUIRES_TIER1` | `AUTHORITY_CONSUMPTION_NOT_RECORDED` |
| **P18a** | **Anchor byte equality.** For every path in the closed anchor set, `sha256(worktree) == sha256(git cat-file -p S7:p)`; the anchor commit exists with the required parent and exact added set | `N3` | `MACHINE_REQUIRES_TIER1` | `PREBUILD_ANCHOR_NOT_FROZEN` |
| **P18b** | **Frozen-evidence immutability.** Every anchored path still equals its bytes in `S7` after the build | `N5` | `MACHINE_REQUIRES_TIER1` | `FROZEN_EVIDENCE_MUTATED_BY_BUILD` |
| **P18c** | **Anchor digest recording.** `S11` records each anchored input's digest | `N6a` | `MACHINE_REQUIRES_TIER1` | `ANCHOR_DIGEST_NOT_RECORDED` |
| **P19** | **Reference closure.** Every declared reference resolves to exactly one arm of §9.4, with the reference class tagged | `N5`, `N6c`, `N7` | `MACHINE_REQUIRES_TIER1` | `EVIDENCE_REFERENCE_UNRESOLVED` |
| **P20** | **Retention closure.** Every recorded evidence value — every digest, and every commit, tree or blob identity — recorded in this generation's own artifacts (`S8`, `S9`, `S11`, `S12`, `S10`) is assigned by the **verifier** to exactly one applicable retention mode declared by §9.5 and satisfies it: **A** `RETAINED_OBJECT` — the referenced object/pre-image resolves through the applicable §9.4 retained-object arm; or **B** `RETAINED_SEAL_TIME_MEASUREMENT_ONLY` — the measurement record itself resolves to the retained `S9`/`S13` evidence surface, while the underlying pre-image is explicitly and lawfully unretained. No artifact field, label or narrative selects a mode. **Recorded slot state is not a recorded evidence value:** the all-zero unbound special-slot entries −4 and −6 of the supported seal schema (§8.3) are recorded structural slot state, bind no referenced object and carry no pre-image identity, and are therefore **outside this predicate's domain** — neither a Mode A object nor a Mode B measurement, with no third mode created for them. `EVIDENCE_NOT_RETAINED` fires when a value satisfies neither mode | `N7` | `MACHINE_REQUIRES_TIER1` | `EVIDENCE_NOT_RETAINED` |
| **P21** | **Additive package.** `git diff --diff-filter=MDRT --name-only` is empty for `S7`..`S9`, `S9`..`S13` and `S7`..`S13`, and every `S7`/`S9` path is byte-identical in `S13`'s tree | `N7` | `MACHINE_REQUIRES_TIER1` | `EVIDENCE_PACKAGE_NOT_ADDITIVE` |
| **P22** | **Tier-1 gate (aggregate).** The truth condition remains the conjunction of prerequisite rows 1–18 of `TABLE-TIER1-GATE`. For **pre-entry eligibility**, rows 2 and 4 contribute their verifier-bound capability arms only; this proves the implementation can enforce the handoff laws and does **not** claim that a future `N4a` event occurred. For a generation-specific re-assertion before `N7`, and for later audit of retained generation evidence, rows 2 and 4 additionally satisfy their retained-event-evidence arms from `S9` + parent `S7`. A capability result and a generation-specific event result may never be substituted for or mixed with one another as though they were the same observation. Row 19 records this phase-aware conjunction | before entry, re-asserted before `N7` | `MACHINE_REQUIRES_TIER1` | `GENERATION_B_TIER1_GATE_UNMET` |
| **P23** | **Gate-coverage closure.** Every `MACHINE_REQUIRES_TIER1` predicate of `TABLE-PREDICATES` **other than the coverage predicate `P23` itself** is named by at least one `TABLE-TIER1-GATE` row. `P23`'s own coverage obligation is discharged by row 20 of that table, the single closure row, which names `P23`; the domain therefore excludes `P23` so that the coverage predicate is never its own coverage obligation | before entry, re-asserted before `N7` | `MACHINE_REQUIRES_TIER1` | `GATE_COVERAGE_INCOMPLETE` |
| **P24** | **Envelope-reference acceptance.** `S3`'s `execution_mode` and `target_safety_validation_ref` are present and are accepted by the governing C² rev-6 / rev-9 envelope checks; this design binds them to the governing contract, not to a branch of its own | `N2`, `N5` | `MACHINE_REQUIRES_TIER1` | `ENVELOPE_REFERENCE_NOT_ACCEPTED` |
| **P25** | **Verifier-derived S1 dependency provenance, A2R/M1R seed eligibility, closed parser policy, context-sensitive closure and privacy.** Before S1 freeze the verifier independently enforces the exact frozen A2R Python/lock and FFmpeg/FFprobe profiles; derives `PYTHON_BASE_RUNTIME_ROOT_V1`, eligible run-scoped venv and `HOMEBREW_FFMPEG_KEG_ROOT_V1`; requires a future owner-pinned exact `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` token/count/digest before Generation B; validates the exact typed `S4.a2r_m1r_echo` only as a non-authoritative echo; reads each admitted non-system source once into a transient immutable byte image; applies `MACHO_CONTAINER_SLICE_POLICY_V1`, exact numeric `MACHO_LOAD_COMMAND_POLICY_V1`, and the one-to-one project-owned `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`; expands `(canonical_source_identity, originating_governed_executable_context)` to fixed point; applies M1R Domain P/Domain H/system classification, empty optional registry, de-duplication, family/order, and same-byte materialization. Baseline absence, wrong root/lock/keg/profile, closure insertion/removal/relocation/mutation, malformed/unsupported container/subtype/command, unknown command, malformed accepted-command structure, S4 omission/undeclared-key/duplicate-key/alias/type/conflict, context divergence, second-read substitution, required optional seed, outside-domain target, arbitrary Cellar admission/scan, family ambiguity, unlawful materialization, producer population change or raw/private discovery retention fails closed. Later audit may verify retained S1/provenance results but may not claim historical host graph or native-closure re-observation. | `N2`–`N7`; later retained audit | `MACHINE_REQUIRES_TIER1` | `DEPENDENCY_INVENTORY_DERIVATION_INVALID` |

**Tier labelling is honest, not generous.** `MACHINE_AVAILABLE_NOW` requires the check, all its tools **and
an instance of its subject** to exist in the repository at this base. At this base **the class has no
members**: every governed subject is created by a generation that has never run, and `MEASURED` shows the
`O_EXCL` destination, the seal, the design-record consumption record, the generation-identity derivation
and the allowlist-closure code all absent. Every predicate in §5.2 is therefore
`MACHINE_REQUIRES_TIER1`, and none is described as enforced anywhere in this document.

**Target safety is not a predicate of this revision.** `TARGET_SAFETY_NOT_VALIDATED` is **removed**: the
existing verifier derivation `derive_target_safety_state` takes no inventory parameter and never compares
an inventory (`MEASURED`), so a `VALIDATED` state cannot be reached from a seal-derived inventory that
comes into existence during the same generation. Target safety remains governed by C² rev-6 §11.5 / `C15`,
and §14.4 states the re-entry trigger.

---

## 6. Structural invariants

The invariants below hold, each restating a rule already given above so that a reviewer can cite one name:

**I-1** dependency rank discipline (§4.4 is the complete edge set and every row satisfies
`CONSUMER_RANK > CONSUMED_RANK`); **I-2** same-rank independence (every equal-rank pair is a declared
non-edge, §4.5); **I-3** closed anchor set and per-hop additivity (the anchored set is **exactly**
`{S1,S2,S3,S4}`, and `git diff --diff-filter=MDRT --name-only` is empty for `S7`..`S9`, `S9`..`S13` **and**
`S7`..`S13`, so a modification in `S9` restored in `S13` is still caught); **I-4** additive chain (every
`S7` path is byte-identical in `S9`'s and `S13`'s trees; every `S9` path in `S13`'s); **I-5** no hybrid
artifact (no path is written at two stages); **I-6** **no runtime baseline selector** (OD-1(b) is fixed by successor design authority; no producer, owner-field, policy-field or generation artifact can select historical B1, OD-1(a), or another baseline; `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` is unconditional for future Generation-B eligibility);
**I-7** no future reference (no artifact's bytes depend on a later **rank** — ranks are finer than stages,
so this also governs the `S2 ⟸ S1` order inside `N2`); **I-8** verifier-derived security truth;
**I-9** two-surface measurement discipline: N5 operational `codesign` observes only the verifier-owned transient sealed signed application produced by the current N4a, while later repository-only checks use only the retained subjects that actually exist in `B`/`S13`; neither surface is substituted for the other; **I-10** byte/semantic discipline
(§11); **I-11** evidence minimization (§12.1); **I-12** no unbound normative field (every field of every
declared schema in this document is consumed by a named predicate or by a named stage obligation).

---


## 7. Authority model — verifier-derived values and producer echoes

### 7.1 Three distinct authority-resolution phases

**Phase A — candidate-lineage static objects.** Static review resolves objects actually present at the
Revision-18 candidate SHA from that exact candidate tree, including this specification and the new
Revision-18 ruling.

**Phase B — separately pinned immutable repository authority/review objects.** Option-A, A2R and M1R owner
decisions, all three RR17 reviewer memos and moderator convergence resolve only from their explicit
immutable commit/path/blob tuples. They are never candidate-lineage objects merely because this candidate
references them.

**Phase C — future integrated-controller evaluation.** Only after independent review, later owner approval
and integration may a future evaluator freeze the then-governing Gate-0 controller commit as
`base_controller_commit`. No candidate, reviewer, moderator, owner-decision commit, sibling, mutable
worktree or symbolic "latest" ref substitutes.

### 7.2 Future verifier-derived authority tuple

At the future post-integration evaluation point, before N1:

| Term | Source | Producer may |
|---|---|---|
| `base_controller_commit` | exact governing Gate-0 controller commit frozen at evaluation | echo only |
| `applicable_spec_blob` | exact spec blob at that commit | echo only |
| `applicable_plan_blob` | exact blob of `docs/superpowers/plans/2026-09-14-gate0-stage-b-c2-v3-implementation-plan.md` at the controller commit | echo only |
| `design_record_blob` | exact blob of `docs/gates/gate0/rulings/2026-09-23-rr17-final-specification-closure-design-ruling.md` at that commit | echo only |
| `generation_ordinal` | one plus distinct committed generation identities reachable from evaluation point | echo only |

P19 arm (d) remains exactly
`(authority_ref, repository_path, blob_id, commit_id, strict_ancestry, decision_record_id)`:

1. `repository_path` is the Revision-18 ruling path above;
2. `authority_ref` names that path;
3. `commit_id = base_controller_commit`, never candidate/reviewer/moderator/owner-decision/sibling/later ref;
4. `blob_id` resolves from exact `commit_id:repository_path`;
5. `strict_ancestry` requires one N1 controller resolution, equality to `commit_id`, successful
   ancestry test and re-confirmed equality;
6. parsed id equals
   `GATE0-RR17-FINAL-SPECIFICATION-CLOSURE-DESIGN-RULING-2026-09-23`;
7. candidate-time/static review separately resolves the three owner decisions and RR17
   review/adjudication evidence at their pinned tuples; P19(d) never pretends those objects were newly
   integrated.

The current pre-integration controller is not claimed to contain this ruling.

### 7.3 Candidate/review-time static check

Candidate-lineage verification resolves the exact Revision-18 specification and new ruling. The ruling's
normative formal table and labelled canonical JSON projection must have exactly the same complete key set
and typed values. Its `supersedes` value remains
`GATE0-RECOVERY-EVIDENCE-DAG-DESIGN-RULING-2026-09-20`, satisfying the root §6 protocol, while its
immediate-predecessor fields name the preserved Revision-17 ruling and exact frozen Revision-17 review
subject.

Separately pinned verification resolves:

- Option-A owner decision exactly at
  `164bec97f720683504bc740c6b4a0abccc85def9` /
  `docs/agent-runs/run-20260922-gate0-rev11-independent-review-v1/owner-approved-architecture-decision.md` /
  `0e4bfa5acb8791dbb9c032d7668fb3e2d6a6eada`;
- A2R owner decision exactly at
  `3f8f2fa98d97f8720c4a1a9687dcaab5a29225cd` /
  `docs/agent-runs/run-20260922-gate0-rev12-independent-review-v1/owner-approved-a2r-seed-authority-decision.md` /
  `591c525ce8d517d8d44e2fa9f8803a19167c2102`;
- M1R owner decision exactly at
  `e7c3bb00fe6133d709506ab441ea1489bc20eaa8` /
  `docs/agent-runs/run-20260922-gate0-rev13-independent-review-v1/owner-approved-m1r-runtime-closure-decision.md` /
  `ccd39d7f31241514e50156a8a68a4d7765d079d2`;
- RR17-1 exactly at
  `c4abb77e957de9fcedfb3f075d17a303fd63def9` /
  `docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/lanes/RR17-1-authority-c2-evidence.md` /
  `8febd9b8c8aabc5e86f70e6803cd6a7ab677de70`;
- RR17-2 exactly at
  `970aed4566f291d3f4a5b4560af0d56f3b91b9b1` /
  `docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/lanes/RR17-2-stable-census.md` /
  `495050d1ac7f223322ebb0b82758f540f1dedd53`;
- RR17-3 exactly at
  `0e953d185a5550aa5e7a2787b6d24a1a9dee3fa0` /
  `docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/lanes/RR17-3-macho-header.md` /
  `b47f7a42fbc3fa5c2785aa01d3463539c8a16f78`;
- binding RR17 moderator convergence exactly at
  `159d36666bdd42b3bc02d299bf295b3840e67055` /
  `docs/agent-runs/run-20260923-gate0-rev17-independent-review-v1/moderator-convergence-and-rev18-direction.md` /
  `deac5f778d8e0b7afa26aec8e3093056378cf046`.

The frozen recovery implementation plan remains
`827ad4e19f56812562dc93376a36f33204800a8d`.
Unavailable until future integration: a Generation-B `base_controller_commit` that contains the
Revision-18 ruling. No candidate/reviewer/moderator/owner-decision ref substitutes.

### 7.4 A2R/M1R seed eligibility; S3/S4 are coherence surfaces only

**Verifier resolution is not seed authorization.** S3/argv/operator path values may be locators only. S4
must carry the closed typed echo object below, but the echo never grants eligibility. The verifier derives
and validates every authoritative value independently.

The frozen Python authority remains CPython `3.14.7`, native `arm64`, Homebrew formula
`python@3.14`, executable SHA-256
`87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`, lock
`requirements/gate0-macos-stage-a.lock`, lock SHA-256
`d20752c0a55fa9552303bce6372fdb2172934bd95ec21e26463af997d77adfbc`, plus M1R root/closure
eligibility of §12.2.1.

The frozen tool authority remains FFmpeg `9.0.1` / native `arm64` /
`9f5ddd4f8b36eb07b0c5d60ab6ea1e618bedd70bc45feab82b4dc23be1596ad1` and FFprobe `9.0.1` /
native `arm64` /
`0ecd5e1affb1466b129b4f65bee261e9ab625c4d4a2e7c3e9089f63d44808605`, plus the coherent
`HOMEBREW_FFMPEG_KEG_ROOT_V1` rule of §12.2.1.

**Closed S4 A2R/M1R echo schema — `TABLE-S4-A2R-M1R-ECHO-SCHEMA`.** The echo object is exactly
`S4.a2r_m1r_echo`. Duplicate JSON/object member names fail before schema validation. Key spelling is
literal: no alias or synonym for a defined key is accepted. S4 remains non-authoritative.

The two and only two active-state key sets are:

`S4_NOT_OBSERVED_KEYS_V1` = {
`python_version`, `python_architecture`, `python_formula_lineage`, `python_executable_sha256`,
`python_lock_path`, `python_lock_sha256`, `python_base_runtime_root_identity`,
`python_base_runtime_root`, `python_native_runtime_closure_format`,
`python_native_closure_baseline_state`, `ffmpeg_version`, `ffmpeg_architecture`,
`ffmpeg_executable_sha256`, `ffprobe_version`, `ffprobe_architecture`,
`ffprobe_executable_sha256`, `ffmpeg_keg_root_identity`, `ffmpeg_keg_root`,
`native_execution_architecture`, `optional_tool_seed_registry_v1` }.

`S4_MEASURED_AND_OWNER_PINNED_KEYS_V1` is exactly `S4_NOT_OBSERVED_KEYS_V1` plus
`python_native_closure_baseline_sha256` and `python_native_closure_baseline_member_count`.

No other key set is valid. Every undeclared key fails, without any classifier for whether the key is
security-relevant. Missing required key, duplicate member name, alias/synonym, wrong type, forbidden
conditional key, or conflict with independently verifier-derived truth fails P25.

| Field | Type | Required value / law |
|---|---|---|
| `python_version` | string | exactly `3.14.7` |
| `python_architecture` | string | exactly `arm64` |
| `python_formula_lineage` | string | exactly `python@3.14` |
| `python_executable_sha256` | string | exact frozen lowercase digest |
| `python_lock_path` | string | exactly `requirements/gate0-macos-stage-a.lock` |
| `python_lock_sha256` | string | exact frozen lowercase digest |
| `python_base_runtime_root_identity` | string | exactly `PYTHON_BASE_RUNTIME_ROOT_V1` |
| `python_base_runtime_root` | string | verifier-observed canonical `/opt/homebrew/Cellar/python@3.14/<versioned-keg>`; echo only |
| `python_native_runtime_closure_format` | string | exactly `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` |
| `python_native_closure_baseline_state` | string | exactly `NOT_OBSERVED` now; only a future owner-pinned profile may change it to `MEASURED_AND_OWNER_PINNED` |
| `python_native_closure_baseline_sha256` | string | absent when state is `NOT_OBSERVED`; required exact future owner-pinned lowercase digest only when state is `MEASURED_AND_OWNER_PINNED` |
| `python_native_closure_baseline_member_count` | integer | absent when state is `NOT_OBSERVED`; required exact future owner-pinned non-negative count only when state is `MEASURED_AND_OWNER_PINNED` |
| `ffmpeg_version` | string | exactly `9.0.1` |
| `ffmpeg_architecture` | string | exactly `arm64` |
| `ffmpeg_executable_sha256` | string | exact frozen lowercase digest |
| `ffprobe_version` | string | exactly `9.0.1` |
| `ffprobe_architecture` | string | exactly `arm64` |
| `ffprobe_executable_sha256` | string | exact frozen lowercase digest |
| `ffmpeg_keg_root_identity` | string | exactly `HOMEBREW_FFMPEG_KEG_ROOT_V1` |
| `ffmpeg_keg_root` | string | verifier-observed canonical `/opt/homebrew/Cellar/ffmpeg/<keg-id>`; echo only |
| `native_execution_architecture` | string | exactly `arm64` |
| `optional_tool_seed_registry_v1` | array | exactly `[]` |

For `NOT_OBSERVED`, the digest/count keys are absent: null, empty, zero or synthetic placeholders fail.
For `MEASURED_AND_OWNER_PINNED`, both keys are required together. A producer cannot turn any echo into
authority.

The historical personal/run-scoped venv path is never reusable authority.The historical personal/run-scoped venv path is never reusable authority. This specification authorizes
no creation, installation or repair of a runtime. If no eligible existing runtime exists, or while the M1R
baseline is `NOT_OBSERVED`, Generation B is ineligible. Any profile change requires a narrow
owner-approved seed-profile revision.

Producer does not author S1, dependency membership/cardinality/order, seed eligibility/identity, family
assignment, optional-seed population, canonical-role assignment, authority tuple, expected policy,
retention mode, historical baseline, native-closure baseline, parser policy or oracle/measurer selection.

`OD_1_B_ONLY`, `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`,
`G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1`,
`G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1` and
`VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` are design/verifier constants, not artifact selectors.

## 8. The build-output seal


### 8.1 `N4a` — exact production post-measurement core and test-only leaf oracle

Exactly one production measure-and-handoff boundary entry point owns both handoffs; each exact S1/S2
handoff has one governed leaf measurement call site. The governed production boundary contains one fixed
**private internal leaf measurement primitive**. No production caller selects, replaces or supplies that
primitive. The primitive return enters one and only one production post-return core:

`measurement return => invocation-private continuity state => N4A_TO_N4B_SAME_INVOCATION_CONTINUITY`.

Test and production invoke the same boundary, call site and post-return code identity. Tier-1 may
instrument/monkeypatch **only that exact private leaf primitive and only inside the test process**. The
exact immutable handoff object, production boundary entry point, governed call site and post-return core
remain production objects/code; the test may not swap a handoff object, boundary, core or capability
constructor.

After the primitive returns, neither control flow nor data flow may branch on test mode, oracle identity,
measurer type, environment, build feature, provider type, runtime adapter, feature/config switch, strategy
or helper. No alternate scalar source, recomputation, metadata interception or second constructor exists.

**Production unreachability has three mandatory negative-inspection domains.**

**A — configuration/data surfaces:** production CLI; environment; artifact/schema; runtime-policy;
producer fields; build/runtime-adapter configuration; feature/config switches.

**B — programmatic production interface surfaces:** function/method signatures; constructor parameters;
callable/dependency-injection parameters; setters; mutators; factories; registries; plugin/provider maps;
callbacks/hooks; strategy objects; public or internal production APIs accepting a measurer/helper;
production module-loader/import hooks; production-accessible mutable globals containing a measurer/helper;
generic production configuration objects carrying callable/helper identity; dynamic production dispatch
tables; and any equivalent production-reachable selector.

**C — physical/logical ordinary production package/import surface:** the oracle implementation MUST exist
only in test-owned source/package roots. It MUST be absent from production source roots, production
package/install manifests, production dependency manifests/distributions, ordinary production
`sys.path`, production module-search closure and production import-graph re-export/alias surfaces. A
plain ordinary import attempt from the governed production environment MUST fail. Production source may
contain neither the oracle implementation nor a production-installed test-oracle helper package.

Tier-1 must mechanically inspect all three domains. In addition to all already-required selector
falsifiers, it must prove:

1. production packaging/install manifest excludes the oracle;
2. production source roots exclude the oracle module;
3. production `sys.path`/module search cannot resolve the oracle;
4. ordinary production import resolution fails;
5. no production module re-exports or aliases the oracle;
6. the test-owned oracle path is valid only while ordinary production import remains impossible.

Minimum selector mutations remain:

- `measure_and_handoff(..., measurer=...)`;
- `set_measurement_primitive(fn)`;
- `MEASURER_REGISTRY[...]`.

Every selector or package/import mutation must fail the negative inspection. This contract does not claim
arbitrary malicious source editing is impossible; it closes governed production interfaces and the
governed production package/import closure.

The four retained primitive values remain exactly renderer SHA/octet and signer-entitlement SHA/octet.
No new field, witness, node, nonce or cryptographic attestation is introduced. Sentinel success is
implementation-capability evidence only, never evidence that N4a/Generation B occurred.

### 8.2 `N4b` — one-shot seal act and closed primitive

Production N4b accepts only the fresh capability from the immediately preceding production boundary.
All references/copies share one consumption state; exactly one use may succeed. Duplicate/current copy,
second use after successful consumption, and stale duplicate after original consumption all fail before B.

N4b has no oracle awareness, public/production scalar constructor, recomputation path, cached/prior handle,
alternate helper or producer/build/runtime-adapter source. It serializes the four values once, builds the
privacy-reduced projection and commits B with `parent(B)=S7`.

`identity.json.n4a_boundary_primitive` remains closed:

| Field | Meaning |
|---|---|
| `format` | `N4A_BOUNDARY_PRIMITIVE_V1` |
| `renderer_input_sha256` | exact governed S1 measurement-call return |
| `renderer_input_octets` | matching octet return |
| `signer_entitlements_sha256` | exact governed S2 measurement-call return |
| `signer_entitlements_octets` | matching octet return |

No sixth field, oracle marker/sentinel, selector, path, capability token or self-dependent identity is
authorized. Test instrumentation changes only leaf returns; N4b has no test branch.

### 8.3 Retained projection (byte-exact)

`MEASURED` at this base against the preserved local Stage-B fixture `.stage-b-build/StageBSandboxRunner.app`
(3 regular files, 4 directories, 0 symlinks).

| # | Retained byte-exact | Bytes | Why |
|---|---|---|---|
| 1 | executable code region `[0, codeLimit)` | 259,392 | makes the 16 code-slot digests independently re-verifiable |
| 2 | `Contents/Info.plist` | 514 | bound by CodeDirectory special slot −1 |
| 3 | `Contents/_CodeSignature/CodeResources` | 2,200 | bound by CodeDirectory special slot −3 |
| 4 | superblob structural index (`12 + 5×8 = 52`) | 52 | makes the projection reconstructible and every elision auditable |
| 5 | `CodeDirectory` | 892 | `sha256(CodeDirectory)` **is** the signing-time-stable CodeDirectory identity (§8.5); it cannot be elided because it is the identity pre-image |
| 6 | `Entitlements` blob (8-byte blob header + the 803-byte payload) | 811 | the sealed entitlement payload; bound by special slot −5 |
| 7 | `DER-Entitlements` blob | 481 | bound by CodeDirectory special slot −7 |
| 8 | `identity.json` — a canonical, deterministic manifest whose field set **is** the enumeration of §8.2, including the closed five-field `n4a_boundary_primitive`. **No personal value.** | `NOT_OBSERVED` | declared projection manifest; it is the **only** lawful home for post-build derived values *that are computable before `B` exists*, including the already-measured N4a primitive |
| | **Total, byte-exact members 1–7** | **264,342** | ≈ 69 KB compressed at zlib level 6 |
| | **Total including the revised `identity.json`** | **`NOT_OBSERVED`** | no authorized canonical Revision-15 manifest instance exists from which to compute a lawful current byte total; no hypothetical manifest size or total is promoted to `MEASURED`. The zlib-level-6 figure for members 1–7 alone remains `NOT_OBSERVED` as a compression observation |

**Superblob structure, measured and stated exactly.** `MEASURED`: `LC_CODE_SIGNATURE` declares
`dataoff = 259,392`, `datasize = 20,464`, and that **region** ends at EOF. Inside it, the superblob
`0xfade0cc0` has length `7,248` and count `5`; the five blob headers begin at offsets `52`, `944`,
`1,164`, `1,975` and `2,456`, and the last blob ends at offset `7,248` — i.e. at `259,392 + 7,248`
absolute. The superblob therefore **does not** end at EOF: the remaining `20,464 − 7,248 = 13,216` bytes
of the region are **zero padding**, measured all-zero. This revision does not claim otherwise, and the
padding carries no evidence value.

**Superblob index format, measured and stated exactly.** The retained structural index is **`12 + 5×8`**
bytes: a 12-byte superblob header followed by five 8-byte entries. **Each index entry carries only
`(type, offset)`.** No index entry carries a length. Each blob's length is **derived** from its own
8-byte blob header, or equivalently from the next entry's offset, or — for the final entry — from the
superblob's declared length. Because the length is not in the index, an elided blob's **length** remains
recoverable from the surrounding offsets even though its own header bytes are not retained; an elided
blob's **internal magic** is not recoverable, and this revision does not claim it is.

**Projection path convention.** The projection is committed **flat** under a single generation-scoped
directory in commit `B`'s tree, one regular file per member above, with a declared, deterministic file
name per member and **no** captured directory hierarchy, symlink, xattr or ACL. `CodeResources` and
`Info.plist` are retained as bytes but are **not** re-materialised at their bundle-relative paths; the
mapping from member file name to bundle-relative path is recorded in `identity.json`.

`MEASURED` supporting figures: the `CodeDirectory` uses SHA-256 (`hashType = 2`, `hashSize = 32`),
`nCodeSlots = 16`, `nSpecialSlots = 7`, `codeLimit = 259392`, page size `2^14 = 16384`; the code slots
cover `[0, 259392)`, i.e. everything except the signature region.

**Special-slot disposition — all seven entries, for this supported seal schema.** The supported seal
schema of this design has `nSpecialSlots = 7`, and every one of the seven special-slot entries therefore
has an **explicit** disposition. This enumeration is exhaustive over the seven positions; it declares the
disposition of each, and it is not a table of evidence values:

- **−1 — `BOUND_RETAINED_OBJECT`.** `Contents/Info.plist`; slot digest equals `sha256(Info.plist)`; the
  pre-image is retained byte-exact (§8.3 row 2). Retention **Mode A**.
- **−2 — `BOUND_ELIDED_MEASUREMENT`.** The `Requirements` blob; the slot digest **is** the recorded
  `requirements_blob_sha256`; the pre-image is **lawfully elided** and its digest is bound by `P12`
  (§8.7). Retention **Mode B**.
- **−3 — `BOUND_RETAINED_OBJECT`.** `Contents/_CodeSignature/CodeResources`; slot digest equals
  `sha256(CodeResources)`; pre-image retained byte-exact (§8.3 row 3). Retention **Mode A**.
- **−4 — `UNBOUND_SPECIAL_SLOT`.** In this supported seal schema the entry **MUST** be **all-zero**. It
  binds **NO** referenced object. It is **NOT** a recorded evidence digest and **NOT** a pre-image
  identity. It is outside Mode A, outside Mode B, and outside `P20`'s evidence-value domain (§9.5). It is
  recorded only as structural slot state (§8.2).
- **−5 — `BOUND_RETAINED_OBJECT`.** The `Entitlements` blob; slot digest equals `sha256(Entitlements
  blob)`; pre-image retained byte-exact (§8.3 row 6). Retention **Mode A**.
- **−6 — `UNBOUND_SPECIAL_SLOT`.** In this supported seal schema the entry **MUST** be **all-zero**, with
  the same disposition as −4: no referenced object, not a recorded evidence digest, outside Mode A,
  outside Mode B, outside `P20`'s domain, recorded only as structural slot state.
- **−7 — `BOUND_RETAINED_OBJECT`.** The `DER-Entitlements` blob; slot digest equals `sha256(DER blob)`;
  pre-image retained byte-exact (§8.3 row 7). Retention **Mode A**.

`MEASURED` on the preserved local fixture, read-only: slot **−4 = `ALL_ZERO`** and slot **−6 =
`ALL_ZERO`**, while −1, −2, −3, −5 and −7 are non-zero and each equals the `sha256` of exactly the pre-image
named above. **No universal Apple-platform meaning is claimed for −4 or −6.** The normative statement is
scoped to **this** supported seal schema: for this schema, slots −4 and −6 are **required** to be all-zero
unbound entries. If either is **non-zero**, the seal is **outside the supported projection contract** and
**fails closed** under the existing seal/elision predicate: `P12` (§5.2) is the predicate, and
`SEAL_PROJECTION_ELISION_INVALID` (§13.1) is its failure code. No new predicate id and no new failure code
is introduced for this rule.


### 8.4 `S8` — exact retained verifier extraction and historical-B1 boundary

`EMBEDDED_ENTITLEMENT_PAYLOAD` is the payload of the retained Entitlements blob in B. The CodeDirectory
special slot −5 binds the complete Entitlements blob; the payload is transitively bound as its suffix.

The lawful N5 operational `codesign -d --entitlements :-` subject is the exact verifier-owned,
generation-scoped, transient sealed signed application produced by the current N4a lifecycle. It remains
under verifier control through N5, is never selected by a caller/producer, is not commit B and is not a
tracked complete-app evidence home.

`S8_VERIFIER_EXTRACTION_BYTES` is the exact byte slice captured at N5 under the already-frozen operational
extraction rule; those exact bytes are retained byte-for-byte in S13. P8 keeps two distinct duties:

1. exact S8 byte retention; and
2. `parsed(S8_VERIFIER_EXTRACTION_BYTES) == parsed(EMBEDDED_ENTITLEMENT_PAYLOAD)`.

Revision 15 does **not** infer exact S8 bytes from the payload and does not make a payload→S8 transform
load-bearing.

**Historical B1 evidence is preserved, but no longer a future predicate.** On the preserved historical
fixture, the historical S8 extraction was measured as 768 bytes with SHA-256

`c6e5d05824bfd8a6f5d20ba6b24567bd741779d4ad8838d735116b596390a0e4`.

That is truthful historical evidence and remains auditable wherever the historical retained bytes exist.
It is **not** the Revision-15 expected digest for every future generation and is not consumed by P7, P9,
N8 or a runtime selector.

Future anti-widening is instead §10.3's
`VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`: independently derive the expected semantic policy from
exact frozen S1 + closed canonical roles + frozen renderer/schema semantics, then compare the parsed exact
S8 policy against that expected policy. P8 separately proves the observed S8 is the policy embedded in the
signed subject.

The previously demonstrated payload-to-S8 exact transformation remains optional historical extra evidence
only. It is not a Generation-B gate, not a policy-closure satisfier and not a substitute for retaining
exact S8.

### 8.5 Signing-time-stable CodeDirectory identity

The retained CodeDirectory digest is **stable against CMS signing-time variation when all CodeDirectory
inputs remain identical**. It is **not** universally "re-sign invariant", and that phrase must not be used:
a changed `Requirements` blob, entitlement set, code page, or other CodeDirectory input **may change the
digest**. The precise term is **`SIGNING_TIME_STABLE_CODEDIRECTORY_IDENTITY`** — `sha256(CodeDirectory)`
together with `codeLimit`, the page size, and the code-slot and special-slot digest sets, as sealed.
`MEASURED`: the fixture's value is `7620baf7f1883f4778da1f1b4d99d7b54b5e11ccaf15c3c90102d29ef358b8bc`.
Byte-reproducibility of a signed bundle is unsatisfiable by construction, because the CMS `SignedData`
carries an authenticated `signingTime` attribute and there is no `SOURCE_DATE_EPOCH` equivalent for
`codesign`.

### 8.6 `S9` identity and event-evidence homes — no conflation

`S9` carries **two identity concepts and one distinct event-evidence concept**. They have different
homes and must never be conflated.

1. **Repository object identity — forward only.** Commit `B`'s SHA is the lawful durable **repository seal/identity subject** for checks over B's retained
   projection, resolved from the object database; it is **not** N5's operational `codesign` subject; because a commit SHA is not a pure content digest, `B`'s
   **tree** SHA and every member **blob id** are also recorded. **All three are recorded in `S10`** — an
   artifact created after `B` exists — and in the tracked run ledger. They are not fields of
   `S9/identity.json`.
2. **CodeDirectory structural identity.** The
   `SIGNING_TIME_STABLE_CODEDIRECTORY_IDENTITY` of §8.5 is retained in `S9/identity.json` because it is
   computable from the produced bundle **before** `B` exists and is re-derivable from `B`'s retained
   bytes.
3. **N4a event-binding commitments.** The verifier-measured
   `renderer_input_sha256` / `renderer_input_octets` and
   `signer_entitlements_sha256` / `signer_entitlements_octets`, together with fixed
   `format = N4A_BOUNDARY_PRIMITIVE_V1`, are retained at
   `S9.identity.json.n4a_boundary_primitive`. They are contemporaneous verifier-measured evidence about
   the N4a handoff. They are **not `B`'s identity**, are **not CodeDirectory structural identity**, and
   are **not predicate results**.

The CMS blob digest is **not** signing-time stable — it changes on every re-sign — so it remains a
retain-only seal-time measurement (`RETAINED_SEAL_TIME_MEASUREMENT_ONLY`, §8.7) and must never be used as
a stable identity term.

**Self-reference prohibition.** `B`'s identity is established by the commit object that *is* `B`.
`B` does not need to contain its own name, and no member of `B` may attempt to. No path inside commit
`B` may contain `B`'s own commit SHA, `B`'s own tree SHA, or a blob id that only becomes known after
`B` exists, where doing so requires a self-reference or fixed point. The N4a primitive does not weaken
that rule: all five of its fields are known before `B` exists.

### 8.7 Elided members, and the two-class re-verifiability statement

| Elided | Bytes | Binding retained | What a later auditor can and cannot do |
|---|---|---|---|
| `Requirements` blob | 220 | its `sha256` **is** CodeDirectory special slot −2 | The auditor can verify that the **recorded** digest equals the digest bound into the retained `CodeDirectory`. The elided bytes are gone: the auditor **cannot** recompute the digest from the object and **cannot** read the designated-requirement expression. |
| `CMS-Signature` blob | 4,792 | an exact digest recorded in the seal; the CMS signs the `CodeDirectory`, not vice versa, so it is not self-anchorable | The auditor can compare the **recorded** digest only. Later semantic inspection of the CMS blob — including the certificate chain, the leaf common name, and any email address — is **unavailable by design**. |

**A retained digest of an elided object is evidence of the digest recorded at seal time.** It is **not**
evidence that a later auditor can reconstruct or semantically inspect the elided bytes. That sentence is
normative and forbids the opposite claim; the retained projection's **members and recorded evidence values**
divide into exactly two re-verifiability classes, and those two classes are total over **that** subject.
They are **not** a classification of the seven CodeDirectory special-slot positions: the unbound all-zero
entries −4 and −6 (§8.3) are neither a retained object nor a recorded evidence digest, so they lie outside
this partition, while their all-zero **state** is itself re-derivable from the retained `CodeDirectory`.
**The special-slot disposition is exhaustive over all seven positions and is stated once, in §8.3.**

| Class | Members | Meaning |
|---|---|---|
| `INDEPENDENTLY_RE_VERIFIABLE_FROM_RETAINED_BYTES` | the CodeDirectory identity `sha256(CodeDirectory)`; the 16 code slots recomputed against the retained code region; special slots −1, −3, −5, −7 recomputed against retained members, plus the all-zero unbound-slot state of −4 and −6 read back from the retained `CodeDirectory`; every retained member digest; `parsed(S8) == parsed(EMBEDDED_ENTITLEMENT_PAYLOAD)`; the **retained exact `S8` bytes** and their `sha256`; the bundle identifier and the team identifier, both re-read from the retained `CodeDirectory`; `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`, re-evaluated from retained exact `S1` plus retained exact `S8` under §10.3; and the N4a `renderer_input_sha256` / `renderer_input_octets` commitment recomputed against exact `S1` in parent `S7`, plus the N4a `signer_entitlements_sha256` / `signer_entitlements_octets` commitment recomputed against exact `S2` in parent `S7` | Pure arithmetic over retained bytes and retained contemporaneous commitments. **No `codesign` re-execution and no certificate are required.** |
| `RETAINED_SEAL_TIME_MEASUREMENT_ONLY` | the two recorded elided-member digests of §12.4 — the `Requirements` blob digest, which **is** CodeDirectory special slot −2, and the `CMS-Signature` blob digest — these being the entire membership of `MEASUREMENT_ONLY_DIGEST_KEYS` (§9.5); the `CMS-Signature` elided bytes themselves; and the CMS `signingTime` and the certificate chain, neither of which is recorded as a digest value and both of which are therefore outside `P20`'s domain | Recorded at seal time and re-checkable **as recorded values** only. Reconstructing the underlying bytes, or inspecting them semantically, is impossible from the retained projection. **No `P20` obligation is created for the CMS `signingTime` or the certificate chain**, because neither is a recorded digest. |

**N4a evidentiary limit.** A later auditor may read the retained commitment from `S9`, read exact `S1` or
`S2` from parent `S7`, recompute SHA-256 and octet count, and compare those results to the primitive. That
is an independent re-evaluation of the binding against durable contemporaneous verifier evidence; it is
**not** a physical re-observation of the historical N4a event and must never be described as one. The two
N4a SHA-256 commitments therefore belong to the retained-preimage class above and **not** to
`MEASUREMENT_ONLY_DIGEST_KEYS`.

**The phrase "re-derivation of `S8` from the retained payload" is not used in this revision**, because it
would describe the optional transformation of §8.4 rather than the retained exact bytes. What is
re-verifiable is the **retained `S8`**; what is optional is the transformation.

---

## 9. Anchor, sign boundary, result order, package rule, references

### 9.1 Pre-build anchor `S7`

`S7` is **one commit** whose parent is `S0`'s commit, adding **exactly** the four paths `{S1, S2, S3, S4}`.
The anchor set is the **normative verifier constant** `{S1, S2, S3, S4}` — not "the set of paths the commit
happens to add" — and the mechanical check is bidirectional. No manifest lives inside that set, and no
member of it hashes itself. `S7`'s SHA is recorded **forward only**: its lawful in-graph home is `S10`
(rank 3 < 8) and the tracked run ledger, and it is also the package-parent rule. Immediately after creating
`S7`, every anchored path is re-read from the commit object and compared to the working tree; failure is
`PREBUILD_ANCHOR_NOT_FROZEN`.

### 9.2 Sign boundary

Build and sign operate **only** from a scratch build root, into the verifier-constructed sealed
destination. The bytes the signer consumes must equal `S2` byte-for-byte, and the render must have consumed
the frozen `S1` only — never a freshly re-run discovery. **N4a contemporaneously measures the exact
immutable `S1` and `S2` handoff subjects that it passes onward; N4b retains those commitments in
`S9.identity.json.n4a_boundary_primitive` before `B` exists.**

After build/sign, `N5` may re-read **all** anchored inputs from the commit object for mutation and
integrity checks. That later read is **not** retrospective observation of which bytes crossed the
historical N4a handoff. Later event-binding verification instead reads the contemporaneous commitment from
`S9`, reads the corresponding exact preimage from parent `S7`, recomputes SHA-256 and octet count, and
compares them. Final-output equality by itself is **not** proof of historical handoff identity.
**No pre-build artifact is rewritten.** The truth conditions of `P3a`, `P3b`, and `P4` are unchanged
by this evidence-source clarification.

### 9.3 Result order

The execution order inside the result boundary is `measurement (S8) ≺ S11 ≺ S12 ≺ S10 ≺ S13`. No result
artifact may name a later-ranked value (`I-7`), and `P16` enforces the governed result-order instances. `S10` is self-excluding and excludes `S13`'s commit SHA;
that SHA does not exist at `N6c`, so the rule is enforced structurally by `S10`'s field list and
mechanically by `P16`.


### 9.4 Reference classes and resolution arms (`P19`)

Every declared reference carries exactly one class tag; an untagged or multiply-resolved reference fails
P19.

| Class | Denotes | Resolution mechanism |
|---|---|---|
| `PATH_REFERENCE` | repository path expected in a commit tree | `git cat-file -e <commit>:<path>`, then blob comparison |
| `FILE_BLOB_REFERENCE` | blob identity independent of path | `git hash-object` on the artifact, compared with recorded blob id |
| `COMMIT_OBJECT_REFERENCE` | commit identity or such a commit's tree identity | object-database type check plus reachability from a durable ref; never `git ls-files` |
| `AUTHORITY_DESIGN_RECORD_REFERENCE` | current successor design record of §2.2 | resolve the **verifier-derived six-element tuple of §7.2**, read exact bytes at `commit_id:repository_path`, require their blob id to equal `blob_id`, require `strict_ancestry=true`, require embedded `decision_record_id` equality, and when P17 records the byte digest require `sha256(exact bytes)` equality |

The four resolution arms remain exactly: **(a)** path in S13; **(b)** tracked path that existed at S7 with
object comparison; **(c)** commit/tree object identity from the object database; **(d)** the authority
record through the deterministic tuple above.

For arm (d), `commit_id` is **exactly the frozen `base_controller_commit`** and not an introducing commit,
reviewer branch, mutable working-tree head or later ref. `strict_ancestry` has the single deterministic
meaning defined in §7.2. Independent implementers given the same frozen evaluation commit therefore derive
the same record bytes/blob and P17 preimage. No producer field selects tuple values.

No reference may resolve to untracked scratch, build output, a mutable current ref, or an unresolved
authority value.

### 9.5 Retention rule (`P20`)

**Two retention modes, exactly one assignment per recorded value.** **`P20` applies to RECORDED EVIDENCE
VALUES.** Every recorded evidence value — every digest, and every commit, tree or blob identity — recorded
in **this generation's own artifacts** (`S8`, `S9`, `S11`, `S12`, `S10`) is assigned by the **verifier** to
exactly one applicable mode below, and `P20` holds only if the assigned mode is satisfied. No artifact
field, label, flag or narrative selects, proposes or exempts a mode: the assignment is a total function of
the recorded value, the sealed superblob structure and the closed set declared below. A value satisfying
neither mode fails `EVIDENCE_NOT_RETAINED`.

**An all-zero unbound special-slot entry is recorded slot state, not a recorded evidence value.** In the
supported seal schema the two unbound special slots −4 and −6 are **required** to be all-zero and bind no
referenced object (§8.3). Their all-zero entry is recorded as structural slot **state** — not as a digest
of an evidence object and not as a pre-image identity — so it is **outside `P20`'s domain** and is neither
Mode A nor Mode B. This keeps the two-mode partition **total over recorded evidence values** without
inventing a third retention mode; the retained bytes at those two positions remain governed by `P12`.

**Mode A — `RETAINED_OBJECT` (attempted first for every value).** The referenced object/pre-image resolves
to a retained home by arm (a), (b), (c) or (d) of §9.4 under that object's own declared reference class.
`COMMIT_OBJECT_REFERENCE` values are exempt from path resolution by construction — they resolve under arm
(c). The ephemeral scratch directory, the build-products directory and the sealed destination are **never**
an acceptable home for retained evidence: the destination holds the transient build output, and the durable
home of the governed projection is commit `B`'s tree, inherited by `S13`.

**The authority design record and N4a boundary commitments use ordinary Mode A; no new mode or reference
class exists.** The immutable current Revision-18 successor design-record bytes are a retained repository authority
object resolved by existing arm (d). The P17 digest recorded in S10/S11 is therefore ordinary Mode-A
`RETAINED_OBJECT` evidence: arm (d) resolves the exact authority-record bytes and the verifier recomputes
and compares their SHA-256. There is no exemption and no mode-less authority-record value.

**N4a boundary commitments use ordinary Mode A.**
`renderer_input_sha256` is Mode-A retained-object evidence because its exact `S1` preimage is retained
in parent `S7`. `signer_entitlements_sha256` is Mode-A retained-object evidence because its exact
`S2` preimage is retained in parent `S7`. A later verifier reads the commitment from `S9`, resolves
the already-declared retained `S1` or `S2` bytes in `S7`, recomputes SHA-256 and octet count, and
compares the result. Neither digest is Mode B, neither is an orphan digest, and neither creates a new
`P19` reference class. The primitive `format` field and the two octet-count fields are ordinary
retained `S9` structured scalar fields; no digest-preimage or reference-class semantics are invented for
those scalar metadata fields.

**Mode B — `RETAINED_SEAL_TIME_MEASUREMENT_ONLY` (the closed exception).** The underlying elided bytes are
**intentionally not retained** and must not be required to resolve. A recorded digest is in mode B only if
**all three** conditions hold:

1. **Closed membership.** Its recorded key is a member of the closed, verifier-derived, **exhaustive** set
   `MEASUREMENT_ONLY_DIGEST_KEYS`, whose entire declared membership is exactly two members:
   `requirements_blob_sha256` — the elided `Requirements` blob digest, bound as CodeDirectory special slot
   −2 — and `cms_signature_blob_sha256` — the elided `CMS-Signature` blob digest. That constant is the sole
   authority for its own membership, and it is **not** a field of any artifact.
   **No artifact of this design carries a retention-mode, class or exemption field**, because `P20`'s mode
   assignment is **derived by the verifier** and is **never producer-selected**. The instrument that tests
   this schema-semantics prohibition is the `DOCUMENT_CHECK` `V-18` (§15), whose retention-mode selector
   class covers exactly this rule. The `I-12` and `V-12` instruments retain their own field-consumer
   purposes and are **not** relied on for it: a `retention_mode`-style field consumed by `P20` would
   satisfy `I-12` and would not contradict `V-12`, so neither of them proves this property, and this
   specification claims no such proof from them.
   The CMS `signingTime` and the certificate chain are **not** members: neither is recorded as a digest
   value in this generation's own artifacts, so neither is inside `P20`'s domain at all.
2. **Lawful elision.** `P12` holds for the corresponding superblob member: the member is
   elided-with-digest and the recorded digest equals its slot or declared derived binding (§8.7). A digest
   that is not the lawful elision digest of a superblob member is never admissible in mode B.
3. **Proven-absent pre-image.** The verifier demonstrates that no path in `S13`'s tree and no tracked
   repository path hashes to the recorded digest. If such a pre-image exists, the value resolves under mode
   A and mode B is **refused**; the two modes are therefore mutually exclusive by construction, and an
   ordinary retained-object digest cannot escape pre-image resolution by being labelled measurement-only.

What mode B retains is the **measurement record**, not the object. The measured subject, the measurement
class, the digest algorithm, the digest value, the reason the pre-image is intentionally elided and the
seal-subject identity are all recorded explicitly in the seal's `identity.json`, a member of commit `B`'s
tree inherited by `S13`; that record resolves by arm (a) and survives into `S13` via `S9`. The retained
measurement record is evidence of **what was measured at seal time**. It is **not** evidence that a later
auditor can recompute the digest. Mode B is a **measurement-record resolution**; wherever `P20`'s result is
recorded it is recorded as such, it is never reported as retained-object resolution, and the two are never
conflated.

**Git object identities.** `S10` records commit `B`'s commit SHA, commit `B`'s tree SHA and every member
blob id (`P5b`, §8.6). These are object-database identities, recorded under `P5b` and not declared as §9.4
references, so `P19`'s class-tag rule does not apply to them and no fifth reference class exists. Each
resolves by its own object type: a commit identity, and the tree identity of such a commit, as a
`COMMIT_OBJECT_REFERENCE` under arm (c); and a member blob identity through the projection path that
carries it, under arm (a) (§9.6). A tree identity is never resolved by pretending it is a path, a blob or a
commit.

**Authority-record Mode-A rule.** The `AUTHORITY_DESIGN_RECORD_REFERENCE` and the P17 digest of the
current successor design-record bytes are inside P20's total partition and use Mode A. Existing arm (d)
resolves the immutable authority-record preimage and its recorded byte digest. Neither value is exempt
from pre-image resolution; neither creates a third mode or fifth reference class.

### 9.6 Evidence package `S13`

`S13` is a pure-addition descendant with `parent(S9) = S7` and `parent(S13) = S9`. Mechanically,
`git diff --diff-filter=MDRT --name-only S7 S13` is **empty**, and so are `S7..S9` and `S9..S13`; every
path in `S7`'s tree and in `S9`'s tree exists in `S13`'s tree with an identical blob. No modification,
deletion, rename or type-change of a pre-build or sealed path is allowed at either hop. **Package
membership is declared, not implied:** `S8`, `S11`, `S12` and `S10` are committed into `S13`'s tree as new
paths, so §9.5 arm (a) can retain them; `S10` is created last among them and its tree entry therefore
post-dates the other three in execution order while remaining additive. `S13`'s own commit SHA is recorded
forward only, in the tracked run ledger — a commit cannot carry its own SHA.

### 9.7 Entitlement allowlist — declared constants

Two closed constants are declared. Their authority is the governing C² specification rev-6 and the
entitlement renderer it declares `MUST NOT CHANGE` (`scripts/stage-b-render-entitlements.py`); they are
**not** inferred from the measured bundle.

```
PERMITTED_ENTITLEMENT_KEYS = {
  "com.apple.security.app-sandbox",
  "com.apple.security.temporary-exception.files.absolute-path.read-only",
  "com.apple.security.temporary-exception.files.absolute-path.read-write",
}
PROHIBITED_ENTITLEMENT_KEYS = {          # must be absent or false
  "com.apple.security.network.client",
  "com.apple.security.network.server",
  "com.apple.security.temporary-exception.network.client",
  "com.apple.security.temporary-exception.network.server",
}
```

`MEASURED`: the unchanged renderer emits exactly the three permitted keys and no other, and the sealed
entitlement payload's parsed key set is exactly that set. The four prohibited keys are the closed
"documented network exception" set of the approved platform contract — C² rev-6 §7.1 items 3 and 4, and
its implementation in `src/gate0/feasibility/macos_stage_b_verdict.py`
(`DOCUMENTED_NETWORK_EXCEPTION_ENTITLEMENT_KEYS`, `PROHIBITED_NETWORK_ENTITLEMENT_KEYS`); C² §15.3's `N20`
row makes their presence a security failure. C² rev-6 §28 requires a byte-identical rendered entitlement
policy and forbids outgoing/incoming network entitlement widening. `P10` is unconditional and evaluated on
every generation. `P10` remains an independent exact-key closure defence. It neither substitutes for nor defines `P7`: `P7` independently derives the complete expected key/value policy from exact `S1` and frozen design semantics, while `P10` separately refuses any key outside `PERMITTED_ENTITLEMENT_KEYS` and every prohibited network key. The permit set and expected policy must **never** be defined from `S2`, `S8`, the measured bundle, or producer/build/runtime metadata.

---


## 10. Historical B1, successor policy closure, design record, and runtime-policy boundary

### 10.1 Future Generation-B runtime policy remains separate

Under `CANONICAL_CONTRACTS.md` §5, a runtime policy decision is a separate pre-execution artifact with its
own authority/lifecycle/processing/retention/egress fields and
`decision ∈ {ALLOW, DENY, EXPIRED, REVOKED}`. This specification creates none of those decisions and no
design record or S11 result may be consumed as runtime `ALLOW`.

### 10.2 Historical B1 — preserved evidence, superseded future role

Historical B1 is the truthful historical equality:

`sha256(historical S8_VERIFIER_EXTRACTION_BYTES) ==
c6e5d05824bfd8a6f5d20ba6b24567bd741779d4ad8838d735116b596390a0e4`.

Its historical extraction and measurements remain immutable evidence. Revision 15 does not erase,
relabel false or rewrite them.

The historical role that is now superseded is **universal future Generation-B exact-S8 pass condition**.
Repeated lawful generations have distinct generation identities; the verifier-owned canonical path values
therefore differ; the unchanged renderer serializes those absolute paths; exact S2→signer and signed
payload→S8 semantics therefore make one fixed cross-generation S8 byte literal unsatisfiable.

No predicate, failure code, Tier-1 row, S11 result, producer field, runtime policy field or fallback in
Revision 15 treats historical B1 as the current security baseline.

### 10.3 `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1`

Exact S1 entering policy closure is already the verifier-produced canonical projection from §12.2.
Dependency membership, cardinality, family assignment and ordering were derived under
`G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1` before S1 freeze, not selected by producer.

Verifier validates fixed roles, output role, both dependency lists, their exact event-time derived
membership/cardinality/family/order projection, indexed role values and global duplicate absence. Then
expected plist is constructed from canonical S1 roles plus frozen renderer/schema semantics:

- `com.apple.security.app-sandbox` = plist Boolean `true`;
- read-only = array of strings exactly equal to unchanged renderer
  `sorted(set(role_path + "/"))` over fixed read roles + verifier-derived dependency roles;
- read-write = array exactly `[canonical roots.output + "/"]`;
- no other key.

Equality is type-strict: Boolean `true` ≠ numeric `1`; array ≠ scalar; strings compare exactly after
governed normalization; renderer-defined array order is exact; no truthiness/numeric/scalar-collection
coercion. Expected policy cannot be seeded from S2, S8, bundle, producer/raw producer discovery,
build/runtime-adapter metadata, caller plist, baseline selector, configured tool locator, producer
dependency proposal, host-wide scan, optional-seed injection or traversal-order artifact.

P7 requires exact type-strict semantic equality with parsed exact retained S8. P10 independently closes
key/network vocabulary. P3a/P3b/P14/P15/P4/P8 retain the exact S1→S2→signer→payload→S8 chain.

**Later audit honesty:** read exact retained verifier-produced S1 and S8 and reconstruct expected policy.
Retained event-time P25/S11 provenance may establish that the event-time verifier reported PASS under the
governing algorithm. Later audit must not claim physical re-observation of the historical host dependency
graph, current-host recreation of that graph, or current `otool` output as proof of the historical event.
No raw host-discovery bytes/path/digest/fingerprint are retained for such a claim.

### 10.4 Supported owner-binding claim and P17 record

The supported authority claim is exactly `DURABLY_RECORDED_DESIGN_DECISION +
REPOSITORY_RESOLVABLE`. `TAMPER_PROOF_OWNER_SIGNATURE` and
`CRYPTOGRAPHIC_OWNER_ATTESTATION` are not claimed.

Each generation independently records in S10/S11 the current successor `decision_record_id`, the P17
SHA-256 of the exact authority-record bytes, and its own N1 authority-derivation acknowledgement. P19
arm (d) resolves those exact bytes at the deterministic `commit_id:repository_path` tuple of §7.2 and P20
treats the P17 digest as ordinary Mode-A retained-object evidence.

This is record honesty, never a baseline selector and never runtime authority.

### 10.5 Statements prohibited by this design

Until Tier-1 exists and verifies, Generation B must be described as not protected by the not-yet-landed
Revision-18 enforcement. Producer truth never substitutes for verifier truth. It is false to claim that:

- the complete signed application is retained;
- historical B1 is the future universal pass condition;
- a runtime field may select OD-1(a) versus OD-1(b);
- any arbitrary descendant of the generation root is an admissible entitlement path;
- key-only allowlisting substitutes for exact path/value closure;
- a fresh capability wrapper by itself proves measurement-result origin;
- the test-only sentinel oracle is generation event evidence;
- the repository cryptographically attests the owner's architecture act.


## 11. Byte and semantic discipline

| Relation | Lawful form | Forbidden substitution |
|---|---|---|
| Scratch signing bytes vs frozen render | **byte-exact:** signer handoff bytes equal exact S2 | parsed equality |
| Anchored path vs commit object | **byte-exact:** retained-object digest equality | parsed equality |
| Same-S1 re-render | **byte-exact:** `bytes(re-render(S1)) == S2` | comparing only parsed plists |
| Observed signed policy vs expected policy | **semantic exact key/value closure:** `parsed(S8) == verifier_derived_expected_policy(S1)` | historical fixed digest; key-only equality; broad-path acceptance |
| S8 vs embedded signed entitlement payload | **parsed equality** plus exact S8 byte retention | pretending serialization bytes must equal |
| Retained projection member vs B object | **byte-exact** re-read from B | reading mutable scratch destination |
| Historical B1 | preserved historical digest fact only | treating the historical literal as a future Generation-B predicate |
| Payload→S8 transformation | optional historical extra evidence only | using it instead of exact S8 retention/P8/P7 |

## 12. Privacy and retention

### 12.1 Admission rule (`I-11`)

A field may enter tracked evidence **only if** it is (1) consumed by a named governing predicate; (2)
consumed by the renderer, build or sign boundary; (3) required to reproduce a governed output; **or** (4)
required for provenance under frozen authority. Anything else is excluded, whatever a capture tool
happened to emit.


### 12.2 `S1` — verifier-produced canonical projection and dependency inventory

S1 contains only renderer-effective values: eight required fixed read roots, required
`tool_dependency_roots` and `python_dependency_roots` lists (possibly empty), and required output root.
S1 is verifier-produced; it contains no raw host discovery, host source locator or producer-selected
permission shape.

`GENERATION_ROOT = /private/tmp/vip-gate0/<generation_identity>/root`.

Before S1 freeze the verifier performs:

1. `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1` as refined by
   `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`: independently authorize exact existing
   Python/FFmpeg/FFprobe event-time seed subjects, M1R roots and the required owner-pinned Python native
   closure baseline; S3/S4 are locator/echo surfaces only;
2. `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`: derive one deterministic global dependency
   inventory using the exact native-slice/edge/context/same-byte/domain rules below;
3. `VERIFIER_MATERIALIZED_CANONICAL_ROOT_V1`: materialize fixed/indexed roles from the same verifier-held
   byte images, construct S1, and freeze it.

#### 12.2.1 A2R/M1R seed authorization before resolution-derived closure

**Python base-runtime authority.** The exact frozen interpreter remains CPython `3.14.7`, native
`arm64`, Homebrew formula lineage `python@3.14`, executable SHA-256
`87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`. After canonical realpath
resolution the exact authorized interpreter subject MUST reside beneath:

`/opt/homebrew/Cellar/python@3.14/<versioned-keg>/...`

on path-component boundaries. The unique canonical
`/opt/homebrew/Cellar/python@3.14/<versioned-keg>` directory containing that exact subject is
`PYTHON_BASE_RUNTIME_ROOT_V1`. The root is a coherence/provenance boundary, not an automatic version
selector; all frozen version/architecture/digest checks still apply. Exact-byte interpreter copies outside
this formula-domain root are ineligible. No historical `<versioned-keg>` value is fabricated.

**Run-scoped venv authority and exact generation binding.** P2 remains the sole
`generation_identity` derivation and is verifier-derived/producer-nonselectable. Define exactly:

`GENERATION_NAMESPACE_V1 = /private/tmp/vip-gate0/<generation_identity>`

and:

`RUN_SCOPED_VENV_ROOT_V1 = /private/tmp/vip-gate0/<generation_identity>/runtime/python-venv`.

The verifier derives both lexical locators from the P2 identity. No producer, S3, S4, runtime-policy field,
configuration surface, environment variable, operator path, or caller may nominate a different venv root.

Before a future generation may accept `RUN_SCOPED_VENV_ROOT_V1`, the generation namespace MUST be
exclusively reserved by the verifier for exactly that generation. The required capability is an atomic
create/acquire-if-absent reservation whose precondition is that the generation namespace did not already
exist. A pre-existing namespace entry, reservation collision, prior-generation reuse, same-generation
reuse, symlink/alias substitution of the namespace or any `runtime/python-venv` component, canonical
resolution different from the exact derived locator, namespace ownership attributable to another
generation, or inability to establish exclusive verifier ownership fails P25. The exact reservation
primitive is an implementation concern, but it MUST have these observable semantics; ordinary
open-existing-directory acceptance is insufficient.

This paragraph specifies future eligibility only. It performs and authorizes no `mkdir`, directory
creation, venv creation, provisioning, package installation or profile-freeze measurement.

An eligible root must additionally satisfy every existing A2R/M1R condition: its Python entrypoint
canonicalizes to the exact frozen A2R base-interpreter subject; it binds exact lock path
`requirements/gate0-macos-stage-a.lock` and SHA-256
`d20752c0a55fa9552303bce6372fdb2172934bd95ec21e26463af997d77adfbc`; and, once a baseline exists,
its native closure exactly equals the future owner-pinned M1R profile. The generation-derived path is a
locator/binding mechanism, not seed authority. A profile-correct runtime at any other root is ineligible.
If an eligible runtime cannot later be lawfully supplied at the exact root under separate authority,
Generation B remains ineligible.

**Permission-shaping native closure.** Define `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` over exactly two
canonical scan roots: `BASE_RUNTIME = PYTHON_BASE_RUNTIME_ROOT_V1` and
`RUN_SCOPED_VENV = RUN_SCOPED_VENV_ROOT_V1`. After canonicalization, the roots MUST be disjoint and
non-nested: equality, either root being a path-component ancestor of the other, or any canonical overlap
that makes ownership ambiguous fails P25.

**Total symlink resolver — `PATH_CANONICALIZATION_V1`.** This project-owned resolver applies only to
lstat-classified symlinks encountered inside the already authorized bounded traversal; it does not create
another scan root. Resolution begins from the symlink pathname itself without following it. Relative
targets are interpreted relative to the containing directory. Pathname identity uses the already-resolved
parent plus the encountered entry name, requires lossless UTF-8, performs no Unicode normalization or case
folding, and does not delegate cycle/termination semantics to host `realpath`, `ELOOP`,
`MAXSYMLINKS`, retry counts or library-specific policy.

Define the normative project constant exactly:

`PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1 = 32`.

For **each invocation** initialize exactly:

`symlink_hops = 0`

and a transient:

`visited_symlink_pathnames = {}`.

Immediately **before expanding an observed symlink target** apply this order:

1. if `symlink_hops == PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1`, terminate immediately with the
   exact result/reason `CANONICALIZATION_FAILURE_HOP_LIMIT` and fail P25;
2. otherwise increment `symlink_hops` by exactly one;
3. apply the existing repeated-pathname rule to the current exact symlink pathname identity;
4. if that pathname is already in `visited_symlink_pathnames`, terminate with exactly
   `SYMLINK_CYCLE`;
5. otherwise add the pathname to the set and continue deterministic target/component resolution.

Therefore at most **32** symlink-target expansions occur in one invocation. A repeated pathname observed
before the ceiling wins as `SYMLINK_CYCLE`. If resolving the next symlink would require expansion number
33, no 33rd expansion occurs: the exact result/reason is
`CANONICALIZATION_FAILURE_HOP_LIMIT`.

The terminal **family** remains exactly one member of this closed family partition:

- `SYMLINK_CYCLE`: a symlink pathname identity repeats during the same resolution;
- `DANGLING`: the target or any required intermediate component does not exist;
- `CANONICALIZATION_FAILURE`: permission failure, I/O failure, invalid component, non-lossless pathname,
  unstable/inconsistent observation, hop-limit exhaustion, or any other inability to produce exactly one
  canonical target;
- `RESOLVED_REGULAR_FILE`: exactly one canonical regular-file target;
- `RESOLVED_DIRECTORY`: exactly one canonical directory target;
- `RESOLVED_UNSUPPORTED_OBJECT`: exactly one canonical target whose filesystem-object kind is unsupported.

`CANONICALIZATION_FAILURE_HOP_LIMIT` is the exact hop-limit subtype/reason of the existing
`CANONICALIZATION_FAILURE` terminal family. It introduces no DAG node, evidence class, retained artifact,
predicate or global failure-code family. P25 still fails through its existing failure code. Family-level
consumers treat the hop-limit result as `CANONICALIZATION_FAILURE`; diagnostics may preserve the exact
reason token.

Every family except `RESOLVED_REGULAR_FILE` and `RESOLVED_DIRECTORY` fails P25 immediately. A
`RESOLVED_DIRECTORY` symlink also fails P25 under the existing directory-symlink rule and is never
traversed. Only `RESOLVED_REGULAR_FILE` continues to the file-symlink/cross-root scope law below.

The implementation may use platform primitives to observe components, but a host/library limit does not
become project authority: a stricter host may fail operationally before 32 and such an observation maps
fail-closed into the existing canonicalization-failure family; a looser host can never permit expansion
33. Even if an external/root actor continually mutates the observed graph so every newly seen symlink
pathname is distinct, the project resolver terminates at the hard project-owned ceiling. This contract
does not claim or require that the external actor is prevented from mutating.

**Stable population protocol — `PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1`.** The protocol remains bounded
to `BASE_RUNTIME` and `RUN_SCOPED_VENV`; it is not a host-wide scan, an atomic filesystem snapshot or
full Python software-supply-chain attestation.

**Project-writer quiescence.** From before Census A begins until Census B and all required stability
comparisons complete, the producer, build adapter and runtime/config surfaces have no project write
capability to either root, and the verifier itself does not mutate either root. If project execution cannot
establish that write-quiescent state, P25 fails before a successful capture exists. This is a future
execution invariant only. It authorizes no `chmod`, `chown`, mount operation, filesystem lock,
directory creation, venv creation, package installation or profile-freeze measurement, and it does not
claim that external/root host mutation is impossible. The two complete censuses below detect mutations
visible to their complete observations.

**Census A.** Perform one complete exhaustive traversal of both roots. For each canonical root
independently:

1. recursively enumerate every directory entry beneath every real directory, including hidden/dot and
   arbitrarily deep package subtrees;
2. classify each entry with lstat-equivalent semantics before following any symlink;
3. recurse only into a real directory;
4. for every symlink invoke `PATH_CANONICALIZATION_V1`; a resolved-directory symlink fails and is never
   traversed, a resolved-regular-file symlink continues only under the file-symlink law, and every other
   resolver result fails;
5. sockets, FIFOs, device nodes and every other unsupported encountered object type fail;
6. never prune using suffix/package allowlists, known-runtime-directory subsets, `site-packages`-only
   shortcuts, host-discovery results or a prior manifest;
7. enumeration order has no identity meaning.

Build a transient namespace census containing **every encountered pathname entry** beneath the roots. Each
namespace row contains exactly:

1. scope tag, exactly `BASE_RUNTIME` or `RUN_SCOPED_VENV`;
2. exact canonical root-relative lossless UTF-8 pathname bytes of the encountered entry without following
   a final symlink, with no leading slash, `.` or `..` component and no Unicode normalization/case fold;
3. entry kind, exactly one of `DIRECTORY`, `REGULAR_FILE`, `SYMLINK`;
4. only for `SYMLINK`: exact raw link-target bytes, exact `PATH_CANONICALIZATION_V1` result, and, when
   resolution succeeds, the exact canonical target identity.

An unsupported encountered entry type or a symlink resolving to an unsupported object fails before a
successful Census-A set exists.

For every ordinary regular file and every successfully resolved regular-file symlink target, Census A
invokes exactly `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(bytes)`. This wrapper is the **only**
native/non-native classification entry used by Census A and Census B.

**M1R ordinary-file entry — `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(bytes)`.** It applies only to arbitrary
regular-file bytes encountered by the two bounded Python-root censuses:

1. if byte length is less than four, return exactly `NON_NATIVE` and do not invoke the native parser;
2. if the first four bytes match no row of `TABLE-MACHO-CONTAINER-SLICE-POLICY`, return exactly
   `NON_NATIVE` and do not invoke the native parser;
3. if the first four bytes match a table row with disposition `REJECT_UNSUPPORTED`, return exactly
   `UNSUPPORTED_MACHO_CANDIDATE` and fail P25;
4. if the first four bytes match a table row with disposition `SUPPORTED`, invoke exactly
   `MACHO_NATIVE_CONTAINER_PARSE_V1(bytes)`. If the complete project grammar succeeds, return exactly
   `NATIVE_MEMBER`. If any supported container/FAT/Header64/load-command requirement fails, return exactly
   `UNSUPPORTED_MACHO_CANDIDATE` and fail P25.

A complete supported `MH_MAGIC_64` prefix with a truncated Header64 therefore fails and never degrades
to `NON_NATIVE`. Pure Python, JSON/data, ZIP-like or arbitrary non-Mach-O bytes whose first four bytes
match no project table row remain `NON_NATIVE`. The wrapper's unlisted-prefix treatment does **not**
authorize a future native encoding.

For each canonical pathname subject classified `NATIVE_MEMBER`, the verifier retains the **first
Census-A read** as its immutable byte image together with SHA-256; later aliases to that same canonical
pathname do not replace it. Hardlink pathnames remain distinct pathname subjects. The existing canonical
M1R native manifest is derived only from these Census-A native immutable byte images and is not accepted
until Census B succeeds.

**File-symlink and cross-root scope law after successful resolution.** A symlink entry itself never creates
a native-manifest row, although it remains a namespace-census row. For
`RESOLVED_REGULAR_FILE`:

- canonical target outside both Python roots: fail;
- canonical target inside exactly one authorized root: classify the canonical target under that
  target-owning root;
- manifest row scope = target-owning scope tag; manifest row path = canonical target path relative to that
  target-owning root;
- alias path contributes no native-manifest row;
- direct discovery plus one or more aliases to the same canonical target collapses to one canonical target
  subject for native-manifest serialization, while every alias remains independently visible in the
  namespace census;
- a target that appears to belong to both roots fails.

Thus a `RUN_SCOPED_VENV/bin/python` symlink resolving to the frozen base interpreter is classified under
`BASE_RUNTIME`, never falsely under `RUN_SCOPED_VENV`.

Distinct hardlink pathnames remain distinct pathname subjects under the existing path+digest model. No
inode-based identity is introduced.

**Census B.** After **all** Census-A native immutable byte images have been captured, but before closure
acceptance, perform a second complete traversal of both roots using exactly the same lstat-first
enumeration, `PATH_CANONICALIZATION_V1`, root-disjointness, symlink and unsupported-object laws, and invoke
exactly the same `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` for every ordinary regular file and every resolved
regular-file target. Census B independently reconstructs the complete namespace census. Require exact set
equality:

`CENSUS_A_NAMESPACE_ROWS == CENSUS_B_NAMESPACE_ROWS`.

Because a symlink row includes its raw target bytes, resolver result and resolved target identity, visible
insertion, removal, rename, regular↔directory change, regular↔symlink change, symlink-target-byte change,
canonical-target change and root-scope relocation all fail equality.

Additionally:

- every canonical pathname subject classified `NATIVE_MEMBER` in Census A must again classify
  `NATIVE_MEMBER` in Census B under the exact same wrapper, and one stability-only second read must have
  the same SHA-256 as the retained Census-A immutable byte image;
- every Census-A ordinary `REGULAR_FILE` classified `NON_NATIVE` must again classify `NON_NATIVE`;
  its ordinary non-native content is not required to be byte-identical;
- `NON_NATIVE → NATIVE_MEMBER`, `NATIVE_MEMBER → NON_NATIVE`, or `NATIVE_MEMBER → NATIVE_MEMBER`
  with a changed native digest fails;
- either Census A or Census B returning `UNSUPPORTED_MACHO_CANDIDATE` fails immediately;
- every resolved symlink row must reproduce the exact raw link-target bytes, exact
  `PATH_CANONICALIZATION_V1` result and exact canonical target identity;
- any Census-B canonicalization failure, unsupported object, namespace-set difference or required
  native-digest mismatch fails P25.

A pure-Python/data content mutation that keeps the same pathname, entry kind and `NON_NATIVE`
classification is intentionally outside M1R and may pass this stability protocol.

**Successful logical capture.** A successful capture is exactly namespace-set equality plus all required
native classification/digest equalities. This is the project-defined logical stable-census event, not a
claim of an atomic historical filesystem snapshot. A mutation that occurs and is completely restored
between the two complete observations is not claimed observed.

The accepted `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` manifest uses the following existing canonical rows,
derived only from Census-A native immutable images:

- scope tag exactly `BASE_RUNTIME` or `RUN_SCOPED_VENV`;
- non-empty canonical root-relative pathname exact lossless UTF-8 bytes, with no leading slash, `.` or
  `..` component after canonicalization;
- no Unicode normalization and no case folding;
- lowercase SHA-256 of the retained Census-A immutable bytes.

Canonical target subjects are de-duplicated before native rows are serialized. Distinct canonical
pathnames, including filesystem-permitted Unicode-normalization lookalikes or case variants, remain
distinct subjects. Rows sort by scope-tag UTF-8 bytes, then exact relative-path UTF-8 bytes, then lowercase
digest ASCII bytes. Any duplicate canonical row remaining after target de-duplication fails.

The exact canonical serialization is unchanged:

1. UTF-8 bytes of `PYTHON_NATIVE_RUNTIME_CLOSURE_V1`, then one NUL octet;
2. unsigned 64-bit big-endian member count;
3. for each sorted row: unsigned 16-bit big-endian scope-tag byte length, scope-tag UTF-8 bytes, unsigned
   32-bit big-endian relative-path byte length, path UTF-8 bytes, then the 32 raw SHA-256 digest bytes.

Length/count encoding overflow fails. No separator, normalization, host path or unspecified metadata is
added. Profile identity is exactly the format token, member count, and lowercase SHA-256 of these exact
serialization bytes.

The Census-A namespace rows, Census-B namespace rows, raw symlink-target bytes, absolute Python roots,
traversal state and ordinary non-native content are transient only. They are not a DAG node, retained
evidence artifact, P19 class or permission to retain personal paths. The existing durable M1R profile
remains only its authorized canonical projection. Census-A native byte images remain transient derivation
material only for the already-authorized dependency inventory/materialization step and are discarded
under the existing retention law after lawful materialization.

**Baseline availability.** Repository evidence contains no measured authoritative profile digest/count.
Thus `PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`. A lock digest does not imply installed-file
integrity, and no closure digest/count may be invented from the lock, historical Stage-A prose or an old
venv path. Until a future separately owner-authorized local profile-freeze measurement produces genuinely
`MEASURED` digest/count and a later narrow owner-approved seed-profile record pins them,
`GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`. This revision authorizes
neither future act.

Once such a profile is owner-pinned, event-time Domain-P native membership is valid only when **all** of
these existing/now-explicit conditions hold: (1) `PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1 = PASS`; (2) the
subject is classified exactly `NATIVE_MEMBER` by `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1`; (3) the subject is
present in the canonical native manifest; and (4) that manifest/profile exactly equals the future
owner-pinned baseline. A `NON_NATIVE` file inside an authorized root is never a native seed merely because
of lexical containment. The transient namespace census never grants membership by itself. Addition,
removal, relocation, replacement or byte mutation of a native member visible to the protocol fails.
Pure-Python/data content integrity remains outside this entitlement-authority contract. A future full
software-supply-chain requirement requires a separate architecture decision.

**FFmpeg/FFprobe coherent tool authority.** Define `HOMEBREW_FFMPEG_KEG_ROOT_V1`. After canonical
realpath resolution FFmpeg MUST structurally be
`/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg`, and FFprobe MUST be
`/opt/homebrew/Cellar/ffmpeg/<same-keg-id>/bin/ffprobe`. The shared canonical
`/opt/homebrew/Cellar/ffmpeg/<keg-id>` is the event-time coherent installation subject/root. Additionally:

- FFmpeg: version `9.0.1`, native `arm64`, SHA-256
  `9f5ddd4f8b36eb07b0c5d60ab6ea1e618bedd70bc45feab82b4dc23be1596ad1`;
- FFprobe: version `9.0.1`, native `arm64`, SHA-256
  `0ecd5e1affb1466b129b4f65bee261e9ab625c4d4a2e7c3e9089f63d44808605`.

Exact binaries copied elsewhere fail. Different keg roots fail. Mutable `/opt/homebrew/opt/ffmpeg`
paths are locators only; if used, their canonical resolution must satisfy the exact shared-root rule.
Upgrade/relink drift never updates authority automatically. No historical keg-id is fabricated.

**Lock versus closure semantics are distinct.** The frozen lock identifies authorized package-policy input.
The M1R profile identifies the measured installed permission-shaping native surface. Neither proves the
other, and neither is full Python software-supply-chain integrity.

If no eligible existing frozen-profile subjects exist, or the M1R baseline prerequisite is absent,
Generation B is ineligible. This specification does not authorize creating/installing one. A future profile
change requires a narrow owner-approved seed-profile revision.

For a Python Domain-P native seed, the authoritative source image for SHA-256 identity, container/slice
parsing, load-command extraction and canonical materialization is **exactly the retained Census-A immutable
native byte image** that survived Census-B stability validation. No post-Census-B host read may replace
those bytes. For frozen FFmpeg/FFprobe and later admitted non-system dependencies not already represented by
a Census-A image, canonicalize the source and perform one verifier-owned immutable first read at admission.
Define

`MACHO_SOURCE_ID_V1(canonical_absolute_event_time_path, sha256_transient_exact_bytes)`.

Every operation on one source subject uses its one governing immutable byte image. The Census-B
stability-only read is comparison evidence and never replaces the Census-A image. A later host mutation
cannot alter the already-derived dependency inventory or materialized bytes, but this protocol does not
claim full host immutability after capture. Transient bytes/paths remain derivation-only, are discarded
after lawful materialization, and are not retained evidence, a DAG node, a raw discovery object, or
authority to retain arbitrary host binaries.

The canonical source-identity comparison string remains the UTF-8 encoding of

`canonical_absolute_event_time_path + "\n" + lowercase_sha256_hex`.

#### 12.2.2 Closed native container/slice and load-command structural policy

Supported execution architecture is exactly native `arm64`. Parser/library preference functions never
choose architecture, FAT payload validity, numeric command semantics or command structural validity.

**Native-container parser entry — `MACHO_NATIVE_CONTAINER_PARSE_V1(bytes)`.** This is the project-owned
closed native-container parser entry. It is invoked only when either:

A. `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` has already matched a listed `SUPPORTED` magic; or  
B. the static dependency algorithm is parsing an already-governed native subject as native.

At this parser entry, fewer than four available bytes or any unlisted first-four-byte encoding fail exactly
`REJECT_UNSUPPORTED`; a listed `REJECT_UNSUPPORTED` row fails exactly `REJECT_UNSUPPORTED`; and a
listed `SUPPORTED` row proceeds through the complete project-owned container/FAT/Header64/numeric
load-command/structural grammar below. A supported row whose required grammar is malformed fails closed.
A generic parser/library may neither weaken this grammar nor create an additional supported encoding.

**Closed layering rule.** `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` answers: “is this arbitrary bounded-root
file ordinary non-native content, a known unsupported Mach-O candidate, or a supported native member?”
`MACHO_NATIVE_CONTAINER_PARSE_V1` answers: “given a subject already entering the native parser, is its
native container valid under the closed project grammar?” The sentence “unlisted encoding ⇒
`REJECT_UNSUPPORTED`” is normative **only at the native-parser entry**, not at the ordinary M1R wrapper.

An unlisted first-four-byte value treated as `NON_NATIVE` by the M1R wrapper does not authorize a future
Mach-O encoding. No parser library, OS update, Homebrew update, runtime policy or producer configuration may
promote it to `NATIVE_MEMBER`. Recognizing a new native magic requires a normal design-authority revision
of the closed project container table.

**Container/slice policy — `TABLE-MACHO-CONTAINER-SLICE-POLICY`.** At
`MACHO_NATIVE_CONTAINER_PARSE_V1` entry, the first four immutable source bytes are classified against
this closed table. Unlisted encodings fail `REJECT_UNSUPPORTED`; listed `REJECT_UNSUPPORTED` encodings
fail; only listed `SUPPORTED` encodings proceed through the complete grammar.

| Exact first four bytes | Symbolic magic | Encoding | V1 disposition |
|---|---|---|---|
| `cf fa ed fe` | `MH_MAGIC_64 = 0xfeedfacf` | thin 64-bit little-endian | `SUPPORTED` |
| `fe ed fa cf` | `MH_CIGAM_64 = 0xcffaedfe` | thin 64-bit big-endian/swapped | `REJECT_UNSUPPORTED` |
| `ce fa ed fe` | `MH_MAGIC = 0xfeedface` | thin 32-bit little-endian | `REJECT_UNSUPPORTED` |
| `fe ed fa ce` | `MH_CIGAM = 0xcefaedfe` | thin 32-bit big-endian/swapped | `REJECT_UNSUPPORTED` |
| `ca fe ba be` | `FAT_MAGIC = 0xcafebabe` | fat32 big-endian | `SUPPORTED` |
| `be ba fe ca` | `FAT_CIGAM = 0xbebafeca` | fat32 swapped/little-endian form | `REJECT_UNSUPPORTED` |
| `ca fe ba bf` | `FAT_MAGIC_64 = 0xcafebabf` | fat64 big-endian | `SUPPORTED` |
| `bf ba fe ca` | `FAT_CIGAM_64 = 0xbfbafeca` | fat64 swapped/little-endian form | `REJECT_UNSUPPORTED` |

For every supported standalone thin input and every FAT-selected ARM64 slice, the selected-thin header is
owned by the following project table.

**Selected thin header — `TABLE-MACHO-HEADER64-V1`.** The only supported thin encoding is
`MH_MAGIC_64`, little-endian. Header length is exactly
`MACHO_HEADER64_SIZE_V1 = 32` bytes. All offsets are relative to byte 0 of the selected thin slice.

| Offset | Width | Field | Normative V1 rule |
|---:|---:|---|---|
| 0 | 4 | `magic` | little-endian raw u32; must equal `0xfeedfacf` |
| 4 | 4 | `cputype` | little-endian raw u32; must equal `0x0100000c` |
| 8 | 4 | `cpusubtype` | little-endian raw u32; must equal exactly `0` or `1` |
| 12 | 4 | `filetype` | little-endian raw u32; decode only, no additional V1 rejection |
| 16 | 4 | `ncmds` | little-endian raw u32 |
| 20 | 4 | `sizeofcmds` | little-endian raw u32 |
| 24 | 4 | `flags` | little-endian raw u32; decode only, no additional V1 rejection |
| 28 | 4 | `reserved` | little-endian raw u32; decode only, no additional V1 rejection |

Define exactly:

`LOAD_COMMAND_REGION_START_V1 = 32`

`LOAD_COMMAND_REGION_END_V1 = 32 + sizeofcmds`.

All arithmetic after fixed-width decode uses mathematical non-negative integers. Require
`LOAD_COMMAND_REGION_END_V1 <= selected_slice_length`. For FAT input, selected-slice-local byte 0 is
the header origin. For standalone thin input, file byte 0 is the header origin. The command walker begins
**exactly** at selected-slice byte 32 and, under the already closed global command-region law, consumes
exactly `ncmds` commands and exactly `sizeofcmds` bytes.

`filetype`, `flags` and `reserved` are raw metadata fields in V1 and do not independently cause P25
rejection. A generic parser's stricter semantic validation of those fields is non-normative. No external
parser/header may select another header size, field order, byte offset, field width or command-region
start. A supported `MH_MAGIC_64` candidate with fewer than 32 bytes, a wrong required CPU field, an
unsupported subtype, or an invalid declared command region fails eligibility; it is not ordinary
`NON_NATIVE`.

**Complete supported FAT outer grammar.** FAT32 and FAT64 are big-endian. Decode every field at its
on-disk width, then perform all validation calculations in mathematical non-negative integers; native
machine-word overflow never defines validity.

- common FAT header: exactly 8 bytes, `u32 magic`, `u32 nfat_arch`; require `nfat_arch >= 1`;
- FAT32 entry: exactly 20 bytes: raw `u32 cputype`, raw `u32 cpusubtype`, `u32 offset`, `u32 size`,
  `u32 align`;
- FAT64 entry: exactly 32 bytes: raw `u32 cputype`, raw `u32 cpusubtype`, `u64 offset`, `u64 size`,
  `u32 align`, `u32 reserved`; require `reserved == 0`;
- `metadata_end = 8 + nfat_arch × entry_size`; the complete architecture table must satisfy
  `metadata_end <= file_length`;
- every declared slice requires `size > 0`, `offset >= metadata_end`, and mathematical
  `offset + size <= file_length`;
- every pair of half-open ranges `[offset, offset+size)` is disjoint;
- `align` is in `0..63`, alignment is mathematical `2^align`, and `offset mod 2^align == 0`.

Gaps between valid slice ranges are permitted. Trailing bytes after the final slice are permitted. Gap and
trailing bytes are ignored and are never parsed as hidden slices.

For every non-selected architecture entry, only the complete outer FAT metadata/range/alignment law above
is required; its payload is opaque, is not required to parse as Mach-O, and contributes no dependency
edge. This is normative and a stricter parser/library may not reject an otherwise valid container merely
because an unrelated payload is malformed.

For raw `CPU_TYPE_ARM64`, allowed subtype values are exactly `CPU_SUBTYPE_ARM64_ALL = 0` and
`CPU_SUBTYPE_ARM64_V8 = 1`; feature-bit variants, ARM64E = 2 and unknown ARM64 subtypes fail. Exactly
one allowed ARM64 slice is required. Its payload must be a complete supported thin
`MH_MAGIC_64` little-endian image contained in the declared slice, and its inner raw CPU type/subtype
must exactly equal its outer FAT entry. Zero or more than one allowed ARM64 slice fails.

**Selected-slice command envelope.** `TABLE-MACHO-HEADER64-V1` is the only source of the selected
slice's `ncmds`, `sizeofcmds`, 32-byte header extent and command-region start. The command walker starts
exactly at selected-slice offset 32; mathematical `32 + sizeofcmds` must fit wholly inside the selected
slice. It consumes exactly `ncmds` commands and exactly `sizeofcmds` bytes under the global law and
structural table below. Library-specific stricter/looser behavior is non-normative.

**Numeric load-command policy — `TABLE-MACHO-LOAD-COMMAND-POLICY`.** Numeric value is authoritative;
symbolic name is explanatory. Every enumerated value maps to exactly one disposition. Every numeric value
not in this table is automatically `REJECT_UNSUPPORTED` regardless of parser recognition, symbolic-name
availability, `LC_REQ_DYLD`, or guessed semantics. The `LC_REQ_DYLD` bit is never stripped before
lookup.

| Exact uint32 value | Symbolic name | V1 disposition | V1 role/rationale |
|---|---|---|---|
| `0x00000001` | `LC_SEGMENT` | `SUPPORTED_NONEDGE` | segment metadata |
| `0x00000002` | `LC_SYMTAB` | `SUPPORTED_NONEDGE` | symbol-table metadata |
| `0x00000003` | `LC_SYMSEG` | `SUPPORTED_NONEDGE` | obsolete symbol metadata; no dependency edge |
| `0x00000004` | `LC_THREAD` | `SUPPORTED_NONEDGE` | thread-state metadata |
| `0x00000005` | `LC_UNIXTHREAD` | `SUPPORTED_NONEDGE` | thread/entry metadata |
| `0x00000006` | `LC_LOADFVMLIB` | `REJECT_UNSUPPORTED` | historical path-loading form |
| `0x00000007` | `LC_IDFVMLIB` | `REJECT_UNSUPPORTED` | historical FVMLIB identity form outside V1 |
| `0x00000008` | `LC_IDENT` | `SUPPORTED_NONEDGE` | obsolete object-identification metadata |
| `0x00000009` | `LC_FVMFILE` | `REJECT_UNSUPPORTED` | historical fixed-VM file inclusion |
| `0x0000000a` | `LC_PREPAGE` | `REJECT_UNSUPPORTED` | historical/internal unsupported form |
| `0x0000000b` | `LC_DYSYMTAB` | `SUPPORTED_NONEDGE` | dynamic symbol-table metadata |
| `0x0000000c` | `LC_LOAD_DYLIB` | `DEPENDENCY_EDGE` | approved dylib dependency |
| `0x0000000d` | `LC_ID_DYLIB` | `SUPPORTED_NONEDGE` | dylib identity |
| `0x0000000e` | `LC_LOAD_DYLINKER` | `SUPPORTED_NONEDGE` | system dynamic-loader identity |
| `0x0000000f` | `LC_ID_DYLINKER` | `SUPPORTED_NONEDGE` | dynamic-loader identity |
| `0x00000010` | `LC_PREBOUND_DYLIB` | `REJECT_UNSUPPORTED` | historical prebound-library relationship outside V1 |
| `0x00000011` | `LC_ROUTINES` | `SUPPORTED_NONEDGE` | initialization routine metadata |
| `0x00000012` | `LC_SUB_FRAMEWORK` | `REJECT_UNSUPPORTED` | framework relationship semantics outside V1 |
| `0x00000013` | `LC_SUB_UMBRELLA` | `REJECT_UNSUPPORTED` | umbrella relationship semantics outside V1 |
| `0x00000014` | `LC_SUB_CLIENT` | `REJECT_UNSUPPORTED` | client relationship semantics outside V1 |
| `0x00000015` | `LC_SUB_LIBRARY` | `REJECT_UNSUPPORTED` | library relationship semantics outside V1 |
| `0x00000016` | `LC_TWOLEVEL_HINTS` | `SUPPORTED_NONEDGE` | namespace lookup metadata |
| `0x00000017` | `LC_PREBIND_CKSUM` | `SUPPORTED_NONEDGE` | prebind checksum metadata |
| `0x80000018` | `LC_LOAD_WEAK_DYLIB` | `DEPENDENCY_EDGE` | approved weak dylib dependency |
| `0x00000019` | `LC_SEGMENT_64` | `SUPPORTED_NONEDGE` | 64-bit segment metadata |
| `0x0000001a` | `LC_ROUTINES_64` | `SUPPORTED_NONEDGE` | 64-bit initialization routine metadata |
| `0x0000001b` | `LC_UUID` | `SUPPORTED_NONEDGE` | object UUID metadata |
| `0x8000001c` | `LC_RPATH` | `SUPPORTED_NONEDGE` | governed ordered search metadata; consumed by @rpath resolution |
| `0x0000001d` | `LC_CODE_SIGNATURE` | `SUPPORTED_NONEDGE` | code-signature location metadata |
| `0x0000001e` | `LC_SEGMENT_SPLIT_INFO` | `SUPPORTED_NONEDGE` | linkedit metadata |
| `0x8000001f` | `LC_REEXPORT_DYLIB` | `DEPENDENCY_EDGE` | approved re-export dependency |
| `0x00000020` | `LC_LAZY_LOAD_DYLIB` | `DEPENDENCY_EDGE` | approved lazy dylib dependency |
| `0x00000021` | `LC_ENCRYPTION_INFO` | `SUPPORTED_NONEDGE` | encryption metadata |
| `0x00000022` | `LC_DYLD_INFO` | `SUPPORTED_NONEDGE` | dyld linkedit metadata |
| `0x80000022` | `LC_DYLD_INFO_ONLY` | `SUPPORTED_NONEDGE` | dyld linkedit metadata |
| `0x80000023` | `LC_LOAD_UPWARD_DYLIB` | `DEPENDENCY_EDGE` | approved upward dylib dependency |
| `0x00000024` | `LC_VERSION_MIN_MACOSX` | `SUPPORTED_NONEDGE` | minimum-platform metadata |
| `0x00000025` | `LC_VERSION_MIN_IPHONEOS` | `SUPPORTED_NONEDGE` | minimum-platform metadata |
| `0x00000026` | `LC_FUNCTION_STARTS` | `SUPPORTED_NONEDGE` | function-start metadata |
| `0x00000027` | `LC_DYLD_ENVIRONMENT` | `REJECT_UNSUPPORTED` | can alter dynamic-loader environment/search semantics outside V1 |
| `0x80000028` | `LC_MAIN` | `SUPPORTED_NONEDGE` | entry-point metadata |
| `0x00000029` | `LC_DATA_IN_CODE` | `SUPPORTED_NONEDGE` | code-layout metadata |
| `0x0000002a` | `LC_SOURCE_VERSION` | `SUPPORTED_NONEDGE` | source-version metadata |
| `0x0000002b` | `LC_DYLIB_CODE_SIGN_DRS` | `SUPPORTED_NONEDGE` | linked-dylib code-signing requirement metadata |
| `0x0000002c` | `LC_ENCRYPTION_INFO_64` | `SUPPORTED_NONEDGE` | 64-bit encryption metadata |
| `0x0000002d` | `LC_LINKER_OPTION` | `SUPPORTED_NONEDGE` | linker-option metadata; no runtime dependency edge |
| `0x0000002e` | `LC_LINKER_OPTIMIZATION_HINT` | `SUPPORTED_NONEDGE` | linker optimization metadata |
| `0x0000002f` | `LC_VERSION_MIN_TVOS` | `SUPPORTED_NONEDGE` | minimum-platform metadata |
| `0x00000030` | `LC_VERSION_MIN_WATCHOS` | `SUPPORTED_NONEDGE` | minimum-platform metadata |
| `0x00000031` | `LC_NOTE` | `SUPPORTED_NONEDGE` | embedded note metadata |
| `0x00000032` | `LC_BUILD_VERSION` | `SUPPORTED_NONEDGE` | build/platform metadata |
| `0x80000033` | `LC_DYLD_EXPORTS_TRIE` | `SUPPORTED_NONEDGE` | export trie metadata |
| `0x80000034` | `LC_DYLD_CHAINED_FIXUPS` | `SUPPORTED_NONEDGE` | fixup metadata |
| `0x80000035` | `LC_FILESET_ENTRY` | `REJECT_UNSUPPORTED` | fileset-entry container semantics outside V1 |

Only the five `DEPENDENCY_EDGE` rows create dependency edges. `LC_RPATH` is a
`SUPPORTED_NONEDGE` consumed only as ordered search metadata by the existing `@rpath` rule.
`LC_ID_DYLIB` is identity metadata and `LC_LOAD_DYLINKER`/`LC_ID_DYLINKER` are dynamic-loader
identity, not dependency entitlement roles. `LC_LOADFVMLIB` is explicitly rejected. An unknown command
with or without `LC_REQ_DYLD` is rejected without stripping that bit or guessing semantics.

**Accepted-command structural policy — `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`.** This table is project-owned and normative. It has exactly one row for every numeric policy row whose disposition is `DEPENDENCY_EDGE` or `SUPPORTED_NONEDGE`, and no row for rejected/unknown values. The accepted numeric-value set and this table's numeric-value set MUST be equal.

For every row, all scalar integer fields are decoded at their declared unsigned width using the selected `MH_MAGIC_64` slice's little-endian byte order. Signed semantic typedefs such as VM protection words are structurally consumed as raw 32-bit fields; no host signed overflow participates. Every addition and count×size calculation is performed in mathematical non-negative integers after fixed-width decode.

`A` in the final column means **V1 command-local validation only**: the command's own fixed fields, in-command arrays/strings, counts, offsets into the command, reserved/pad bytes and exact `cmdsize` are validated, but file offsets/counts that refer to other immutable-image regions are deliberately not dereferenced or content-validated as part of V1 command structural validity. Those referenced external bytes therefore cannot make one parser accept while another rejects. `N/A` means the row contains no external file-range reference relevant to this choice.

Global selected-slice law: every command has an 8-byte `u32 cmd/u32 cmdsize` prefix; `cmdsize >= 8`; `cmdsize` is a multiple of 8; every command interval is wholly inside the declared load-command region; intervals are walked consecutively and do not overlap; exactly `ncmds` commands are consumed; total consumed bytes equal `sizeofcmds` exactly. Bytes designated as alignment padding by the row grammar MUST be zero. No parser/library default can add validity conditions or waive a project condition.

| Exact uint32 | Command | Disposition | Exact fixed structure / field widths | Exact `cmdsize` and in-command law | Reserved / padding law | External-reference policy |
|---|---|---|---|---|---|---|
| `0x00000001` | `LC_SEGMENT` | `SUPPORTED_NONEDGE` | SEGMENT32 fixed 56 bytes: u32 cmd, u32 cmdsize, bytes[16] segname, u32 vmaddr/vmsize/fileoff/filesize/maxprot/initprot/nsects/flags | cmdsize = 56 + nsects×68; each SECTION32 is bytes[16] sectname + bytes[16] segname + nine u32 fields; no trailing bytes | no project-reserved field; no padding beyond exact formula | A |
| `0x00000002` | `LC_SYMTAB` | `SUPPORTED_NONEDGE` | SYMTAB fixed 24 bytes: six u32 fields | cmdsize = 24 exactly | none | A |
| `0x00000003` | `LC_SYMSEG` | `SUPPORTED_NONEDGE` | SYMSEG fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | A |
| `0x00000004` | `LC_THREAD` | `SUPPORTED_NONEDGE` | THREAD fixed 8-byte header followed by zero or more blocks: u32 flavor, u32 count, then count×u32 state words | cmdsize = 8 + Σ(8 + count×4) exactly; block walk ends exactly at cmdsize | no separate padding; global 8-byte command alignment still applies | N/A |
| `0x00000005` | `LC_UNIXTHREAD` | `SUPPORTED_NONEDGE` | THREAD fixed 8-byte header followed by zero or more blocks: u32 flavor, u32 count, then count×u32 state words | cmdsize = 8 + Σ(8 + count×4) exactly; block walk ends exactly at cmdsize | no separate padding; global 8-byte command alignment still applies | N/A |
| `0x00000008` | `LC_IDENT` | `SUPPORTED_NONEDGE` | IDENT fixed 8-byte header plus optional bounded byte-string table | cmdsize >= 8; if payload exists it ends in NUL and is parsed as a complete sequence of NUL-terminated byte strings; no unparsed trailing bytes | global alignment only | N/A |
| `0x0000000b` | `LC_DYSYMTAB` | `SUPPORTED_NONEDGE` | DYSYMTAB fixed 80 bytes: twenty u32 fields total including cmd/cmdsize | cmdsize = 80 exactly | none | A |
| `0x0000000c` | `LC_LOAD_DYLIB` | `DEPENDENCY_EDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x0000000d` | `LC_ID_DYLIB` | `SUPPORTED_NONEDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x0000000e` | `LC_LOAD_DYLINKER` | `SUPPORTED_NONEDGE` | DYLINKER fixed 12 bytes: u32 cmd, u32 cmdsize, u32 name.offset | cmdsize >= 16; name.offset = 12 exactly; one lossless UTF-8 string begins at 12 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x0000000f` | `LC_ID_DYLINKER` | `SUPPORTED_NONEDGE` | DYLINKER fixed 12 bytes: u32 cmd, u32 cmdsize, u32 name.offset | cmdsize >= 16; name.offset = 12 exactly; one lossless UTF-8 string begins at 12 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x00000011` | `LC_ROUTINES` | `SUPPORTED_NONEDGE` | ROUTINES32 fixed 40 bytes: u32 cmd/cmdsize/init_address/init_module/reserved1..reserved6 | cmdsize = 40 exactly | reserved1..reserved6 = 0 | N/A |
| `0x00000016` | `LC_TWOLEVEL_HINTS` | `SUPPORTED_NONEDGE` | TWOLEVEL_HINTS fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | A |
| `0x00000017` | `LC_PREBIND_CKSUM` | `SUPPORTED_NONEDGE` | PREBIND_CKSUM fixed structure 12 bytes: three u32 fields | cmdsize = 16 exactly: 12-byte structure + 4 zero alignment bytes | bytes 12..15 = 0 | N/A |
| `0x80000018` | `LC_LOAD_WEAK_DYLIB` | `DEPENDENCY_EDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x00000019` | `LC_SEGMENT_64` | `SUPPORTED_NONEDGE` | SEGMENT64 fixed 72 bytes: u32 cmd/cmdsize, bytes[16] segname, u64 vmaddr/vmsize/fileoff/filesize, u32 maxprot/initprot/nsects/flags | cmdsize = 72 + nsects×80; each SECTION64 is bytes[16] sectname + bytes[16] segname + u64 addr/size + eight u32 fields; no trailing bytes | no project-reserved field; no padding beyond exact formula | A |
| `0x0000001a` | `LC_ROUTINES_64` | `SUPPORTED_NONEDGE` | ROUTINES64 fixed 72 bytes: u32 cmd/cmdsize, u64 init_address/init_module/reserved1..reserved6 | cmdsize = 72 exactly | reserved1..reserved6 = 0 | N/A |
| `0x0000001b` | `LC_UUID` | `SUPPORTED_NONEDGE` | UUID fixed 24 bytes: u32 cmd, u32 cmdsize, bytes[16] uuid | cmdsize = 24 exactly | none | N/A |
| `0x8000001c` | `LC_RPATH` | `SUPPORTED_NONEDGE` | RPATH fixed 12 bytes: u32 cmd, u32 cmdsize, u32 path.offset | cmdsize >= 16; path.offset = 12 exactly; one lossless UTF-8 string begins at 12 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x0000001d` | `LC_CODE_SIGNATURE` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x0000001e` | `LC_SEGMENT_SPLIT_INFO` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x8000001f` | `LC_REEXPORT_DYLIB` | `DEPENDENCY_EDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x00000020` | `LC_LAZY_LOAD_DYLIB` | `DEPENDENCY_EDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x00000021` | `LC_ENCRYPTION_INFO` | `SUPPORTED_NONEDGE` | ENCRYPTION32 fixed structure 20 bytes: five u32 fields | cmdsize = 24 exactly: 20-byte structure + 4 zero alignment bytes | bytes 20..23 = 0 | A |
| `0x00000022` | `LC_DYLD_INFO` | `SUPPORTED_NONEDGE` | DYLD_INFO fixed 48 bytes: twelve u32 fields | cmdsize = 48 exactly | none | A |
| `0x80000022` | `LC_DYLD_INFO_ONLY` | `SUPPORTED_NONEDGE` | DYLD_INFO fixed 48 bytes: twelve u32 fields | cmdsize = 48 exactly | none | A |
| `0x80000023` | `LC_LOAD_UPWARD_DYLIB` | `DEPENDENCY_EDGE` | DYLIB fixed 24 bytes: six u32 fields; lc_str name offset field is byte 8 | cmdsize >= 32; name.offset = 24 exactly; one lossless UTF-8 string begins at 24 and NUL-terminates before cmdsize; all bytes after first NUL are zero | terminal alignment padding zero | N/A |
| `0x00000024` | `LC_VERSION_MIN_MACOSX` | `SUPPORTED_NONEDGE` | VERSION_MIN fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | N/A |
| `0x00000025` | `LC_VERSION_MIN_IPHONEOS` | `SUPPORTED_NONEDGE` | VERSION_MIN fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | N/A |
| `0x00000026` | `LC_FUNCTION_STARTS` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x80000028` | `LC_MAIN` | `SUPPORTED_NONEDGE` | ENTRY_POINT fixed 24 bytes: u32 cmd/cmdsize, u64 entryoff/stacksize | cmdsize = 24 exactly | none | A |
| `0x00000029` | `LC_DATA_IN_CODE` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x0000002a` | `LC_SOURCE_VERSION` | `SUPPORTED_NONEDGE` | SOURCE_VERSION fixed 16 bytes: u32 cmd/cmdsize, u64 version | cmdsize = 16 exactly | none | N/A |
| `0x0000002b` | `LC_DYLIB_CODE_SIGN_DRS` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x0000002c` | `LC_ENCRYPTION_INFO_64` | `SUPPORTED_NONEDGE` | ENCRYPTION64 fixed 24 bytes: u32 cmd/cmdsize/cryptoff/cryptsize/cryptid/pad | cmdsize = 24 exactly | pad = 0 | A |
| `0x0000002d` | `LC_LINKER_OPTION` | `SUPPORTED_NONEDGE` | LINKER_OPTION fixed 12 bytes: u32 cmd/cmdsize/count, followed by exactly count NUL-terminated lossless UTF-8 strings | cmdsize >= 16; exactly count strings are consumed from byte 12; remaining bytes through cmdsize are zero alignment padding | terminal alignment padding zero; count×walk arithmetic mathematical | N/A |
| `0x0000002e` | `LC_LINKER_OPTIMIZATION_HINT` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x0000002f` | `LC_VERSION_MIN_TVOS` | `SUPPORTED_NONEDGE` | VERSION_MIN fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | N/A |
| `0x00000030` | `LC_VERSION_MIN_WATCHOS` | `SUPPORTED_NONEDGE` | VERSION_MIN fixed 16 bytes: four u32 fields | cmdsize = 16 exactly | none | N/A |
| `0x00000031` | `LC_NOTE` | `SUPPORTED_NONEDGE` | NOTE fixed 40 bytes: u32 cmd/cmdsize, bytes[16] data_owner, u64 offset/size | cmdsize = 40 exactly | none | A |
| `0x00000032` | `LC_BUILD_VERSION` | `SUPPORTED_NONEDGE` | BUILD_VERSION fixed 24 bytes: six u32 fields including ntools; each BUILD_TOOL_VERSION is two u32 = 8 bytes | cmdsize = 24 + ntools×8 exactly; no trailing bytes | no padding beyond exact formula | N/A |
| `0x80000033` | `LC_DYLD_EXPORTS_TRIE` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |
| `0x80000034` | `LC_DYLD_CHAINED_FIXUPS` | `SUPPORTED_NONEDGE` | LINKEDIT_DATA fixed 16 bytes: u32 cmd/cmdsize/dataoff/datasize | cmdsize = 16 exactly | none | A |

For all DYLIB/DYLINKER/RPATH rows, the declared `lc_str` offset is exact, not merely in-range. The NUL terminator is mandatory and all bytes after the first NUL through `cmdsize` are zero padding. This applies to `LC_ID_DYLIB` and `LC_ID_DYLINKER` as well as edge-producing commands. No parser-dependent string acceptance is permitted.

Fixed-size rows admit no unmodelled trailing bytes. Formula rows admit exactly the declared array/string/payload plus declared zero padding and nothing else. `LC_SEGMENT`/`LC_SEGMENT_64` validate their in-command section-array cardinality and byte extent only; section-referenced file ranges are policy A. `LC_BUILD_VERSION` validates the `ntools×8` in-command array exactly. `LC_LINKER_OPTION` validates exactly `count` strings and terminal zero alignment padding.

**Factual derivation provenance, not runtime authority.** The project-owned thin/load-command and FAT32 constants above were checked
against immutable public Apple XNU source blobs: `EXTERNAL_HEADERS/mach-o/loader.h`
`4d1b930c3dcee476538d4cb022e3cffb2d3a50e2`; `EXTERNAL_HEADERS/mach-o/fat.h`
`e2bcf433d518ee192244d31ce063611ec2f9d3fa`; and `osfmk/mach/machine.h`
`0169116b28174d5190b37efabbb2c90032099302`. FAT64 magic and `fat_arch_64` field widths/order were
independently checked against Apple cctools `include/mach-o/fat.h` blob
`03fca1644ce36180e71b6faa2575b9405544b5d3` at commit
`e0d56624eca2a76c2ace4c21850df9e666de4ca5`. Those sources are factual references only. Runtime
validity depends solely on this specification's copied project-owned tables/formulas and never on an
external header revision or parser library.

#### 12.2.3 Context-sensitive deterministic fixed point

Graph expansion state is exactly:

`(canonical_source_identity, originating_governed_executable_context)`.

The originating executable context is the canonical governed seed executable from which that traversal
state is reachable. Every reachable state is evaluated; a visited set keyed only by source identity is
insufficient.

For each state and every dependency-bearing command:

1. absolute install name: resolve that exact path;
2. `@loader_path`: anchor to the current object's canonical loader context;
3. `@executable_path`: anchor to the originating governed executable context carried in the state;
4. `@rpath`: expand only against the current governed object's applicable ordered `LC_RPATH` metadata
   under that originating context; tokens inside each RPATH obey the same loader/executable rules.
   Environment variables, CWD, `DYLD_*`, arbitrary prefixes and host-wide search paths do not extend it;
5. zero existing canonical targets is unresolved; more than one distinct canonical identity is ambiguous;
   syntactic candidates collapsing to one identity are one target;
6. classify system-domain targets under §12.2.5; for a non-system target require §12.2.4 domain admission,
   derive its source identity from its one-read image, enqueue every newly reachable
   `(identity, originating-context)` state, and continue to fixed point.

A fully resolved cycle is lawful. Traversal order cannot select the result. After state-level fixed-point
closure, compare all resolutions of every logical dependency edge reached under lawful originating
contexts. Global output may be de-duplicated by canonical source identity **only after** those
context-sensitive resolutions agree. If the same edge resolves to different canonical targets across
lawful contexts, Generation B fails closed rather than selecting first traversal.

For deterministic inspection, state edge records are normalized by
`(originating_context_identity, source_identity, load_command_class, raw_install_name_utf8_bytes, resolved_target_identity)`
before global projection.

#### 12.2.4 Permitted local non-system subject domain

After canonical event-time resolution, an admitted non-system dependency must be lawful under the
following closed rules.

**Domain P — M1R Python native authority.** `PYTHON_BASE_RUNTIME_ROOT_V1` and the eligible
`RUN_SCOPED_VENV` are bounded scan containers, not lexical grants. Python-family native seed membership
exists only after `PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1 = PASS` and, once a real baseline is later
authorized/measured/pinned, exact equality of the resulting canonical native manifest to the existing
owner-pinned `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` profile. The transient namespace census does not itself
grant membership. An insertion, removal, relocation, replacement, native-classification transition or
native-byte mutation visible to the protocol fails. While the baseline is `NOT_OBSERVED`, no
Generation-B Domain-P authority is claimed and Generation B remains blocked.

A native dependency reached from a lawful Python seed but canonically outside the two Python roots is not
made Domain P merely by reachability; it must satisfy Domain H or system-domain rules. Pure-Python/data
files are not native seeds under this contract, and ordinary non-native content mutation that remains
`NON_NATIVE` is outside M1R.

**Domain H — Homebrew dependency target.** A non-system target may be admitted under Domain H only when
its canonical event-time target is beneath `/opt/homebrew/Cellar` on a path-component boundary **and**
it is reached through a lawful closed dependency edge from frozen A2R FFmpeg/FFprobe, an already-admitted
dependency, or a future owner-approved optional seed.

Being readable, executable, arm64 or merely present under Cellar is insufficient. No enumeration of
Cellar grants permission. An arbitrary descendant is not admitted without deterministic graph reachability.
A non-system target outside verified M1R native membership and Domain H fails closed.

#### 12.2.5 Closed macOS system-domain exclusion

After canonical target resolution, exactly these domains are classified as macOS system dependencies:

- `/usr/lib` and descendants on a path-component boundary;
- `/System/Library` and descendants on a path-component boundary.

A target there is classified as observed system dependency and receives no dependency entitlement role;
traversal does not recurse through it. No producer field, mount, symlink, package root, environment
variable or host prefix adds another system domain. System exclusion is a role classification, not proof
of non-observation.

#### 12.2.6 Closed optional/dlopen seed registry

The production registry is exactly:

`OPTIONAL_TOOL_SEED_REGISTRY_V1 = []`

Historical `mpg123` and `zstd` special handling does not establish individual necessity and grants no
seed. Static Mach-O closure is not claimed to prove that no future dlopen-only dependency can exist.

If a future authorized generation requires an unmodelled optional/dlopen-only dependency, that generation
is **ineligible** until a new owner-approved design revision explicitly adds the semantic optional seed.
No runtime loader trace, host glob, "latest Cellar version", runtime/config insertion or runtime-selected
optional seed is authority.

A test-only synthetic registry fixture may exercise missing/ambiguous resolver mechanics but can never
create a production seed.

#### 12.2.7 Deterministic family assignment, global de-duplication and S1 projection

One canonical source identity appears at most once in the total dependency inventory.

Family assignment is:

1. if the identity is an exact member of the verifier-recomputed, owner-pinned
   `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` profile, assign `python_dependency_roots`;
2. otherwise, if lawfully reached from frozen A2R FFmpeg/FFprobe or a future owner-approved optional tool
   seed under Domain H, assign `tool_dependency_roots`;
3. otherwise fail closed.

If reachable from both families, Python precedence applies only for exact M1R native-profile membership.
A lexical venv/base-root prefix alone never creates Python-family membership. Traversal order never chooses
family.

After lawful closure, global de-duplication and family assignment, each family is ordered by **UTF-8
bytewise ascending canonical source-identity comparison string**. Zero-based unsigned base-10 indices are
assigned in that order.

| S1 role | Exact relative path beneath `GENERATION_ROOT` |
|---|---|
| `roots.worktree` | `roots/worktree` |
| `roots.worktree_src` | `roots/worktree-src` |
| `roots.python` | `roots/python` |
| `roots.python_runtime` | `roots/python-runtime` |
| `roots.model` | `roots/model` |
| `roots.synthetic` | `roots/synthetic` |
| `roots.ffmpeg` | `roots/ffmpeg` |
| `roots.ffprobe` | `roots/ffprobe` |
| `roots.output` | `roots/output` |
| `tool_dependency_roots[i]` | `dependency-roots/tool/<i>` |
| `python_dependency_roots[i]` | `dependency-roots/python/<i>` |

Materialize each admitted non-system dependency under its canonical generation-root role from the **same
transient immutable byte image** used for identity/parse. S1 stores only canonical generation-root role
paths, never host source paths, Cellar source paths, personal paths, raw parser output, closure-manifest
rows or raw graph bytes. After lawful materialization discard the transient image.

Producer/caller/runtime policy/configuration cannot add, remove, reorder, duplicate, choose cardinality,
choose family, choose optional seed, choose alternate frozen toolchain seed or substitute another
dependency universe. Both dependency lists are always present. Before freeze, aliases/symlinks/outside-root
indirection are rejected.

Renderer behavior remains unchanged: resolve canonical generation-root role paths, add trailing slash to
reads, `sorted(set(...))`, one output write value.

This contract authorizes no protected/archive copy, dependency download, egress or source mutation. If a
required dependency cannot be lawfully materialized at its exact role, the generation is ineligible.

### 12.3 Raw host discovery — including the tracked ledger

Raw host discovery output is **NOT** a tracked Generation-B evidence artifact and is **NOT** required as
byte-exact package content. Event-time verifier dependency derivation may transiently inspect exact governed
host/tool subjects under §12.2, but raw bytes/paths are not retained. **No raw-discovery bytes, digest, fingerprint, or personal field may appear in
ANY tracked artifact, including the tracked run ledger.** A diagnostic raw-discovery hash, if computed,
remains **local and untracked**; it is never copied into the ledger and is never a package reference. The
generation's renderer **MUST** consume the frozen `S1` directly and must not re-run discovery as its render
input. The historical privacy finding is recorded **by reference**; **no personal value is transcribed into
this specification or into any remediation-lane memo.** `P25` enforces this over the generation's tracked
artifacts (`TABLE-PREDICATES`).

### 12.4 Signing identity in tracked evidence

A signing identity participates in exactly one governed check (`P11`) and is admitted only in a
privacy-minimal derived form.

| Field class | Retention |
|---|---|
| bundle identifier | retained in `S4` (non-personal, pre-build declared; consumed by `P11`) |
| `SIGNING_TIME_STABLE_CODEDIRECTORY_IDENTITY` | retained in the seal's `identity.json` (consumed by `P5a`, `P11`); it is post-build and must not appear in `S4` |
| Requirements blob digest (special slot −2) and CMS blob digest | retained in the seal's `identity.json` as a **digest**, each under its own name (consumed by `P12`); post-build, never in `S4` |
| human-readable certificate common name | **NOT RETAINED** — in any artifact, in any generation, for any reason |
| email address | **NOT RETAINED** |
| personal name | **NOT RETAINED** |
| designated-requirement expression | **NOT RETAINED** — only its CodeDirectory slot digest |
| certificate-subject digest as a proxy for that expression | **NOT RETAINED** — the digest of the elided blob is recorded under its own name and never described as a subject digest; the CMS digest is also **not** signing-time stable and must not be used as a stable identity term |
| team identifier as a **declared, textual or convenience** field | **NOT RETAINED** — no standalone team-identifier field, and no declared or textual team-identifier value in any tracked artifact. This row states the **declared/textual/convenience** rule only; the **structural residual** is stated once, in the paragraph immediately below, and is **not** negated here |

**THE NORMATIVE PRIVACY RULE — stated once, here, and referenced elsewhere (`MEASURED`).** The team
identifier **is structurally embedded** inside the retained `CodeDirectory` blob: the 10-character value at
`teamOffset`, byte-equal to the value `codesign` reports. The `CodeDirectory` **is** the identity
pre-image, so it **cannot be elided**, and a team identifier inside it **cannot be erased** without
destroying the identity the whole architecture rests on. The privacy rule is therefore **minimization, not
fictional byte erasure**: what is prohibited is every **standalone, declared, textual or convenience**
team-identifier field; what is **disclosed as an unavoidable structural residual** is any team-identifier
byte structurally contained in the retained `CodeDirectory`. **This specification does not claim, and no
artifact of this design may claim, that the retained projection "carries no team identifier": that claim is
false and must never be written.** Every other statement of the signing-identity privacy rule in this
document, in the ledger and in the closeout is a **reference to this paragraph**, not a second statement of
it.

What this specification claims, and what `P13` enforces within its stated domain, is narrower and true.
**The normative privacy rule is stated once, in the paragraph above**; this list enumerates the classes
that rule prohibits and adds no second rule of its own:

1. there is **no separate human-readable or personal signing-identity record**;
2. there is **no certificate common name**;
3. there is **no email address**;
4. there is **no personal name**;
5. there is **no designated-requirement expression**;
6. there is **no redundant standalone team-identifier field** merely for convenience;
7. the team identifier is **not duplicated** into `identity.json`;
8. `P13`'s scan domain is the **declared and textual projection members plus the elided members' recorded
   names** — **not** the opaque `CodeDirectory` byte blob, which is precisely where the structural
   embedding lives.

The net-new-exposure argument is unaffected by that rule: the team identifier was already inside the signed
executable's signature in every historical artifact of this pipeline, and the projection introduces no new
occurrence of it.

`P13` evaluates the projection for the forbidden classes above, within that stated domain. `MEASURED`: the
repository's implemented secret scan matches credential patterns only and has **no** email or personal-name
pattern, so a leak of the personal-value class would be invisible to the existing audit; that is recorded
as a forward-compliance obligation, not a solved problem. **C² tension, resolved explicitly.** C² rev-6 §28
requires the designated-requirement *form* to be preserved across a bounded re-sign. This revision honours
that at the **code-signing layer** — the CodeDirectory special slot −2 binds the same Requirements blob, so
a byte-identical rendered entitlement policy and an unchanged designated-requirement binding both hold —
while **not** retaining the human-readable expression in tracked evidence. What is absent is only the
human-readable rendering, which no predicate needs.

**Structural vocabulary proof (`MB-7`).** The `GENERATION_SCOPED_ONLY` property is proved
**structurally**, never by a literal `grep`:

1. **Schema/domain inspection.** No declared field of §7.2, §7.3, §7.4, §9.7 or §12 has a `scope` field or
   a `STANDING` member; the closed vocabularies of this revision contain no such token, and there is no
   `scope` union in which one could live.
2. **Predicate inspection.** No predicate of §5.2 reads a `scope` value, a `STANDING` token, or a branch
   token; `P1` and `P2` compare only the §7.2 terms against verifier-derived values.
3. **Branch inspection.** This revision declares no branch selector, no ruling artifact, no supersession
   delta and no resolver; `I-6` states the property as an invariant, so there is no execution arm that
   could handle `STANDING`.

Occurrences of the token in historical or discussion prose are **irrelevant** to the property and are not
evidence about it. The revision-2 instrument — a literal `grep` whose declared result was 0 hits while its
own commit contained 14 — is **deleted**, and no replacement literal `grep` is used.

### 12.5 Honest statement of what is not retained

Raw discovery bytes, the Requirements blob, the CMS blob and its certificate chain, and the human-readable
signing identity are **not retained**, and later semantic inspection of those objects is **unavailable by
design**. Of that list only two have a retained digest form, and they are the **only** members of
`MEASUREMENT_ONLY_DIGEST_KEYS` (§9.5): the elided `Requirements` blob digest and the elided `CMS-Signature`
blob digest are retained seal-time measurements (§8.7), not reconstruction inputs. Raw discovery bytes,
the certificate chain and the human-readable signing identity are retained **neither as bytes nor in any
digest form**. The team identifier is **not** in that list: the normative privacy rule of §12.4 states its
structural residual once and governs here.

### 12.6 Scope of this privacy guarantee, and the historical residual (`MB-13`)

**The guarantee is a minimization guarantee, not a claim of byte erasure.** **Its scope is stated exactly
once, in this sentence:** the Generation-B evidence package and seal (`S13`, `S9`); this specification and
the C² rev-6 contract it defers to; the design-ruling record of §2.2 and the formal state surface; and the
operational run artifacts authored by this turn and by later turns, **including the tracked run ledger**.
No other sentence in this document states, narrows or widens that scope; every later scope reference points
back to this sentence. Within those surfaces the retained projection is the closed set of bytes and digests
required by a named predicate: no human-readable certificate common name,
email address, personal name, or designated-requirement expression is retained in any declared, textual or
structured field; no standalone team-identifier field is retained for convenience; and the two
personal-data-bearing signature components — the `Requirements` blob and the `CMS-Signature` blob — are
elided with digests retained only as seal-time measurements, so later semantic inspection of those objects
is unavailable by design. **The guarantee does not assert the absence of the team identifier from the
projection.** The single normative statement of that rule, and of the structural residual it discloses, is
§12.4; it is referenced here and not restated.

**The scope of this guarantee is the single statement made above; it is not restated here.**
**Historical review and audit documents are preserved evidence and are not silently rewritten.** Any
personal-value or local-user-path appearance inside a historical review/audit memo is recorded as
**`HISTORICAL_AUDIT_PRIVACY_RESIDUAL`**: disclosed, scoped out of the guarantee, and **not** repaired by
history rewriting.

**Forward rule, binding from the remediation turn onward:** new and modified tracked documents use
`<repo-root>` and `<user-home>` placeholders; no concrete local username, home-directory prefix, or
personal signing value is transcribed into any new tracked document. Every new or modified file of the
remediation turn is mechanically scanned for the local-user-path class **before** the candidate is
committed, and the scan result is recorded in the remediation run evidence. For future governed generation
artifacts, §12.2 is stronger: exact S1 path bytes are never redacted after use; instead the verifier makes
them non-personal by construction under `VERIFIER_MATERIALIZED_CANONICAL_ROOT_V1`, and P25 rejects a
concrete personal home prefix, outside-root path or producer/caller alias before tracked generation
evidence is committed.

**Why this closes the blocker.** `MB-13` is closed by **truthful scope**, **no new recurrence**, and
**durable residual disclosure** — not by rewriting history. The revision-2 finding was that the run's own
artifacts contained the class while the disclosure named only historical occurrences. This revision states
the scope correctly, admits no new occurrence, and records the existing ones in the run ledger.

---

## 13. Failure model

### 13.1 Failure vocabulary (`TABLE-CODES`) — one semantic condition per row

The **authority of this vocabulary is this table**. Its declared count in §3.3 is a derived echo, checked
by `V-11`, which counts its rows.

| Code | One semantic condition | Evaluated at | Reachable because | Resulting branch |
|---|---|---|---|---|
| `AUTHORITY_ECHO_MISMATCH` | an echoed authority value in `S3` differs from the verifier-derived value of §7.2 | `N1`, `N5` | a producer echo may disagree | fail closed |
| `AUTHORITY_CONSUMPTION_NOT_RECORDED` | `S10`/`S11` omit the current successor `decision_record_id`, P17 Mode-A digest of the exact arm-(d) authority-record bytes, or this generation's N1 authority-derivation acknowledgement | `N1` pre-check, `N6c` | a recording step may be omitted | fail closed on the record; policy closure unaffected |
| `GENERATION_IDENTITY_COLLISION` | the verifier-derived generation identity is reused by a committed generation | `N2` | an identity may be reused | fail closed |
| `RENDER_INPUT_NOT_FROZEN` | the render input is not the frozen `S1` | `N2`, `N4a`, `N5` | discovery may be re-run | fail closed |
| `OUTPUT_ROOT_AMBIGUOUS` | the effective write root has no unique recorded source, or disagrees with `S3` | `N2` | two sources may disagree | fail closed |
| `PREBUILD_ANCHOR_NOT_FROZEN` | `S7` was not created as specified, or an anchored digest read from it disagrees | `N3` | the commit may be absent or wrong | fail closed |
| `FROZEN_EVIDENCE_MUTATED_BY_BUILD` | an anchored path differs from its bytes in `S7` | `N5` | a build may write a tracked path | fail closed |
| `ANCHOR_DIGEST_NOT_RECORDED` | `S11` does not record each anchored input's digest | `N6a` | a recording step may be omitted | fail closed |
| `BUILD_OUTPUT_SEAL_NOT_FROZEN` | commit `B` was not created as specified, or a projection member re-read from it disagrees | `N4b` | the seal may be absent or divergent | fail closed |
| `SEAL_IDENTITY_HOME_INCOMPLETE` | `S10` omits `B`'s commit SHA, `B`'s tree SHA or a member blob id, or a member of `B`'s own tree carries `B`'s own SHA or tree SHA | `N6c` | a recording step may be omitted, or a self-reference may be attempted | fail closed |
| `SIGNING_ENTITLEMENTS_NOT_FROZEN` | the scratch signing bytes differ from `S2` | `N4a`, `N5` | a swapped render is constructible | fail closed |
| `SIGNING_IDENTITY_DRIFT` | the derived signing-identity values differ from the verifier's re-read of `B` | `N4a`, `N5` | a substituted identity is constructible | fail closed |
| `SIGNED_BYTES_NOT_VERIFIER_DERIVED` | N5 operational `codesign` extraction was not taken from this generation's verifier-owned transient sealed signed application, or a caller/producer/alternate path selected the subject | `N5` | a swapped or caller-selected bundle is constructible | fail closed |
| `ENTITLEMENT_ALLOWLIST_VIOLATION` | a key in the extraction is outside `PERMITTED_ENTITLEMENT_KEYS`, or a `PROHIBITED_ENTITLEMENT_KEYS` key is present | `N5` | a widened entitlement set is constructible | fail closed |
| `ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE` | independently verifier-derived expected policy from exact S1/closed roles/frozen renderer semantics differs from parsed exact S8 in any key or value, or the expected value was sourced from an inadmissible observed/producer/build/runtime surface | `N5`; later audit | a key/value widening or wrong expected-policy source is constructible | fail closed |
| `S8_NOT_RETAINED_EXACTLY` | the exact `S8` bytes are not retained in `S13`'s tree, or `parsed(S8)` differs from `parsed(EMBEDDED_ENTITLEMENT_PAYLOAD)` | `N7` | a lossy or parsed-only retention is constructible | fail closed |
| `POLICY_CLOSURE_RESULT_NOT_RECORDED` | `S11` records no application/result for `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` under the current successor authority | `N6a` | a result-recording omission is constructible | fail closed |
| `SEAL_PROJECTION_ELISION_INVALID` | a superblob member is neither retained nor elided-with-digest; or an elided member's digest does not equal its slot or derived binding; or, in the supported seal schema (`nSpecialSlots = 7`), an unbound special slot −4 or −6 is non-zero rather than the required all-zero entry | `N4b`, `N5` | a miscounted or mislabelled projection is constructible, and a non-zero unbound slot is constructible | fail closed |
| `SEAL_PROJECTION_PRIVACY_VIOLATION` | a retained projection member contains a forbidden personal-data field class | `N4b`, `N5` | a projection may include a personal value | fail closed |
| `RENDER_NOT_BYTE_REPRODUCIBLE` | a re-render from `S1` is not byte-identical to `S2` | `N6b` | a non-deterministic renderer is constructible | fail closed |
| `REPRODUCIBILITY_PROOF_VACUOUS` | an effective-field perturbation did not diverge, or a non-effective one did | `N6b` | a vacuous proof is constructible | fail closed |
| `RESULT_MANIFEST_NOT_FINAL` | `S10` was not created last among result artifacts, or includes itself or `S13`'s commit SHA | `N6c` | a misordered or malformed manifest is constructible | fail closed |
| `EVIDENCE_PACKAGE_NOT_ADDITIVE` | `S13` modifies, deletes, renames or type-changes a path of `S7` or `S9` | `N7` | a non-additive diff is constructible | fail closed |
| `EVIDENCE_NOT_RETAINED` | a value recorded in this generation's own artifacts is assigned to no retention mode of §9.5; or is assigned to `RETAINED_OBJECT` and resolves to no retained home under arm (a), (b), (c) or (d) of §9.4; or is claimed in `RETAINED_SEAL_TIME_MEASUREMENT_ONLY` outside the closed set `MEASUREMENT_ONLY_DIGEST_KEYS`, or without its `P12` elision binding, or while a retained pre-image exists | `N7` | a scratch-only home, a missing required digest, and a foreign or mislabelled digest are each constructible, and each satisfies neither mode | fail closed |
| `EVIDENCE_REFERENCE_UNRESOLVED` | a declared reference resolves to no arm of §9.4 | `N7` | a dangling reference is constructible | fail closed |
| `DEPENDENCY_INVENTORY_DERIVATION_INVALID` | the closed P25 contract fails: frozen A2R identity or M1R base/venv/keg/native-profile eligibility fails; the required owner-pinned native-closure baseline is absent or mismatched; S4 violates its exact active-state typed echo schema; a container/fat table/slice/subtype/load-command violates `MACHO_CONTAINER_SLICE_POLICY_V1`, `MACHO_LOAD_COMMAND_POLICY_V1` or `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`; context resolution is unresolved/ambiguous/divergent; identity/parse/materialization do not consume one immutable byte image; a non-system target lies outside exact M1R Domain-P membership/Domain H or is admitted by host enumeration; optional/family/order/materialization/population/privacy rules fail | `N1`–`N7` | a seed/root/profile/baseline/S4/container/slice/command/context/source-race/domain/optional/family/materialization/population/privacy attack can violate the closed verifier derivation | fail closed |
| `GENERATION_B_TIER1_GATE_UNMET` | a §14.2 prerequisite does not exist or does not verify | `N8` | the capabilities are absent at this base (`MEASURED`) | Generation B blocked |
| `GATE_COVERAGE_INCOMPLETE` | a `MACHINE_REQUIRES_TIER1` predicate of §5.2 is named by no §14.2 row | `N8` | a predicate may be added without a gate row | Generation B blocked |
| `ENVELOPE_REFERENCE_NOT_ACCEPTED` | `S3`'s `execution_mode` or `target_safety_validation_ref` is absent, or is rejected by the governing C² rev-6 / rev-9 envelope checks | `N2`, `N5` | a producer may write an envelope value the governing contract does not accept | fail closed |


**Historical code-vocabulary deltas are repository history, not current authority.** Revision 15 does not
restate the old add/remove arithmetic because the live authority is `TABLE-CODES` itself. The table has a
one-to-one relation with `TABLE-PREDICATES`, checked by V-7; V-11 re-counts it against §3.3. Historical
owner-ruling branch codes remain absent because Revision 15 contains no runtime branch machinery.
`TARGET_SAFETY_NOT_VALIDATED` remains absent for the previously recorded reachability reason in §14.4.

### 13.2 No false single-stage invariant

A code **may** be evaluated and re-asserted at multiple stages, and that is intentional: fail-closed
conditions on the authority binding are re-asserted after the anchor freeze so that a post-freeze
divergence cannot pass. This specification therefore does **not** claim "every failure code appears at
exactly one stage", and it makes no completeness claim by literal-identifier search.

---

## 14. Implementation boundary, the `N8` gate, and target safety

### 14.1 This specification authorizes nothing

It defines the target architecture and does not authorize the implementation phase of §14.2, a plan, a
generation execution, a live probe, a widening, a Gate promotion, or any runtime policy decision.

### 14.2 `N8` — required Tier-1 implementation phase

**`GENERATION B MUST NOT EXECUTE` until every row of `TABLE-TIER1-GATE` exists and verifies.** Each row is evaluated by a **named command with an expected result**; a producer-authored boolean, prose statement, or caller-supplied path
satisfies no row. The gate is evaluated **before entry** and re-asserted before `N7`. Its evaluator is the
**verifier role**, and its result is recorded as `tier1_gate_state` in `S11` and as the pre-entry record in
the tracked run ledger. Neither record carries a personal value. **This table is the authority for the
gate's row count**; §3.3's declared value is a derived echo, re-derived from this table by `V-14` and
deliberately not restated here. Every `MACHINE_REQUIRES_TIER1` predicate of `TABLE-PREDICATES` other than
`P23` is named by at least one row, and the check that no predicate is unguarded is `V-10`. This table has **four declared row kinds**, and every row belongs to exactly one of them: **capability**
rows (1–18), which each name at least one predicate id of `TABLE-PREDICATES` and together form the domain
of `P22`; **rows 2 and 4 are phase-aware within that same capability-row kind** — their pre-entry arms prove
enforcement capability only, while generation-specific re-assertion/later audit additionally requires the
retained N4a event evidence declared in those rows; row 5 additionally carries the named `N4A_TO_N4B_SAME_INVOCATION_CONTINUITY` capability obligation and its test-only non-content sentinel oracle, mechanically distinguishing direct measurement-operation-result flow from equal-value recomputation without adding a predicate, retained field or DAG node; the single **aggregate** row (row 19), which names `P22`; the single **closure** row (row 20),
which names `P23`; and the single **re-verification** row (row 21), whose requirement is `§8.7`/`I-9`
rather than a §5.2 predicate, so it names **no** predicate id and is deliberately outside `P22`'s
capability domain. `V-10` and `P23` measure predicate-to-row coverage, not row-to-predicate coverage, so
row 21's existence is a requirement of §8.7 and of this table rather than of any predicate. The
`Exists today` column is an **availability disclosure**, not a §5.1 class label: `NO` means the capability
does not exist at this base, and `PARTIAL` means some git mechanics exist but the named resolver or
generator does not. **A pre-entry capability PASS is never evidence that a future N4a event already
occurred.** Generation-specific retained-event checks are evaluated only when their `S9`/`S7` subject
exists; missing, malformed, mismatching or cross-generation evidence fails closed.

| # | Prerequisite | Machine check | Expected | Exists today |
|---|---|---|---|---|
| 1 | Verifier-derived authority binding and echo coherence (`P1`) | derive the §7.2 tuple from repository authority; then substitute each echoed value in `S3` with a divergent value | derivation succeeds; every substitution ⇒ `AUTHORITY_ECHO_MISMATCH` | NO (the tuple derivation does not exist) |
| 2 | Phase-aware frozen effective-input binding (`P3a`, `P3b`) | **PRE-ENTRY CAPABILITY:** prove a verifier-owned exact renderer-input handoff exists, with no producer/caller re-discovery channel and no mutable-path substitution channel; force a bypass/re-render attempt. **GENERATION / LATER REPOSITORY:** resolve governed `B`, read `S9.identity.json.n4a_boundary_primitive`, resolve parent `S7`, recompute SHA-256 + octet count over exact `S1`, then parse its effective write root and compare with `S3` from the same `S7` under the existing unique-resolution / declared-root / provenance-token law | pre-entry: governed handoff succeeds and forced bypass/re-render fails closed, without claiming an `N4a` event; generation/later: exact S1 commitment matches and `P3b` comparison passes, else `RENDER_INPUT_NOT_FROZEN` / `OUTPUT_ROOT_AMBIGUOUS`; missing, malformed, mismatching or cross-generation retained evidence fails closed | NO (`stage-b-build-app.sh:11` re-runs discovery inline) |
| 3 | Generation-identity derivation and separation (`P2`) | recompute the identity derivation; then reuse a committed identity | recomputation equals the `S3` echo; reuse ⇒ `GENERATION_IDENTITY_COLLISION` | NO (`GENERATION_IDENTITY_COLLISION` matches no implementation file) |
| 4 | Phase-aware sign-time byte binding (`P4`) | **PRE-ENTRY CAPABILITY:** prove the verifier controls the signer-input measurement boundary, measures the exact immutable object consumed by the signer, and rejects substitution. **GENERATION / LATER REPOSITORY:** resolve governed `B`, compare `signer_entitlements_sha256` + `signer_entitlements_octets` in the N4a primitive against exact `S2` in parent `S7`, and require the row-2 / `P3a` renderer-input binding | pre-entry: exact-object measurement capability succeeds and substitution fails closed, without claiming an `N4a` event; generation/later: signer commitment matches exact `S2` and required `P3a` binding passes, else `SIGNING_ENTITLEMENTS_NOT_FROZEN` / `RENDER_INPUT_NOT_FROZEN`; final signed output alone is insufficient | NO |
| 5 | Origin-sensitive N4a→N4b continuity plus build-output seal (`P5a`, `P5b`; `N4A_TO_N4B_SAME_INVOCATION_CONTINUITY`) | invoke exact production boundary/call site with the same immutable handoff object; substitute only the exact private leaf primitive in test process; prove same post-return code identity. Reject post-return discriminator and alternate scalar source. Mutate production/test split, recomputation and alternate helper. **Negative-scan A:** CLI/env/artifact-schema/runtime-policy/producer/build-adapter/feature-config. **Negative-scan B:** signatures/constructors/callable-DI/setters/mutators/factories/registries/plugin-provider maps/callbacks/hooks/strategies/public-internal measurer APIs/module-loader-import hooks/mutable measurer globals/generic callable config/dynamic dispatch/equivalents. **Negative-scan C:** production package/install roots, production dependency manifests/distributions, production source roots, ordinary production `sys.path`/module-search closure, ordinary import resolution and production re-export/alias graph. Require packaging exclusion, source-root exclusion, module-search non-resolution, ordinary import failure and no re-export. Preserve selector falsifiers `measurer=`, setter and registry. Reject replay/forged/duplicate/second/stale capability. Verify B projection/S10 | only exact production core with fixed private test-owned leaf oracle passes; every split/recompute/helper/selector/package/import/re-export/replay/copy/reuse attack fails before B; ordinary production import of oracle fails; no sentinel is retained/event evidence | NO |
| 6 | Verifier-owned N5 event-time subject, no caller/producer-selected subject (`P6`) | prove the operational `codesign` subject is the transient sealed signed application returned by this generation's N4a lifecycle; attempt a deliberately substituted/caller-selected bundle and require no CLI or producer field that can retarget the subject; separately verify B remains only the durable projection/identity anchor | substituted or retargeted event-time subject ⇒ `SIGNED_BYTES_NOT_VERIFIER_DERIVED`; no claim that `codesign` can run against B | NO |
| 7 | Exact S8 retention and verifier-derived entitlement-policy closure (`P7`, `P8`) | lawful verifier-produced S1/S8 fixture; independently derive expected policy. Falsify path/key widening plus **wrong types**: Boolean true→numeric 1, array→scalar, string→non-string, scalar/collection coercion, wrong array order. Require exact S8 and parsed S8==embedded payload | lawful fixture closes exact type-strict policy/P8; every path/key/type mutation ⇒ `ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE`; lossy S8 ⇒ `S8_NOT_RETAINED_EXACTLY` | NO |
| 8 | Policy-closure application/result record (`P9`) | inspect S11 after a lawful fixture and then omit the P7 application/result row | current `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` result present; omission ⇒ `POLICY_CLOSURE_RESULT_NOT_RECORDED`; S11 result is never accepted as expected-policy or primitive event evidence | NO |
| 9 | Entitlement key closure (`P10`) | fixtures with one permitted-set-violating key and each of the four prohibited network keys | `ENTITLEMENT_ALLOWLIST_VIOLATION` in every case | NO |
| 10 | Signing-identity derived-value check (`P11`) | fixture with a substituted pre-build declared value, and one with a post-build value wrongly placed in `S4` | `SIGNING_IDENTITY_DRIFT` | NO |
| 11 | Canonical projection, elision-digest computation and privacy scan (`P12`, `P13`) | reconstruct the projection manifest from the produced bundle; require the −2 slot and CMS digests to equal the declared elision digests; require the unbound special slots −4 and −6 to be all-zero; run the closed personal-value scan over declared and textual members | every superblob member accounted; digest equality, else `SEAL_PROJECTION_ELISION_INVALID`; zero forbidden classes, else `SEAL_PROJECTION_PRIVACY_VIOLATION` | NO |
| 12 | Reproducibility byte equality and non-vacuity (`P14`, `P15`) | re-render from `S1`; then perturb one effective and one non-effective field | byte-equality with `S2`, else `RENDER_NOT_BYTE_REPRODUCIBLE`; divergence pattern as specified, else `REPRODUCIBILITY_PROOF_VACUOUS` | NO |
| 13 | Result finalization order and manifest record (`P16`, `P17`) | create result artifacts out of order; omit the design-record consumption record | `RESULT_MANIFEST_NOT_FINAL`; `AUTHORITY_CONSUMPTION_NOT_RECORDED` | NO |
| 14 | Anchor byte equality, immutability and digest recording (`P18a`, `P18b`, `P18c`) | compare every anchored path against `git cat-file -p S7:<path>`; omit one digest from `S11` | agreement, else `FROZEN_EVIDENCE_MUTATED_BY_BUILD` / `PREBUILD_ANCHOR_NOT_FROZEN`; omission ⇒ `ANCHOR_DIGEST_NOT_RECORDED` | NO |
| 15 | Reference resolution including deterministic authority arm (d) (`P19`) | fixture package with all four classes; for arm (d) freeze the evaluation controller commit, derive `commit_id = base_controller_commit`, derive `blob_id` from `commit_id:repository_path`, require `strict_ancestry=true` under §7.2, parse exact `decision_record_id`, and compare P17 SHA-256 of those exact bytes; then substitute a reviewer/sibling/later ref and each tuple component | each class resolves exactly once; independent derivation yields the same arm-(d) tuple/bytes; substituted ref/tuple/digest or untagged/dangling reference ⇒ `EVIDENCE_REFERENCE_UNRESOLVED` | PARTIAL — git mechanics exist, arm-(d) resolver does not |
| 16 | Package retention and additivity (`P20`, `P21`) | per-hop diffs `S7`..`S9`, `S9`..`S13`, `S7`..`S13`; §9.5 mode assignment over the staged package: assign every value recorded in `S8`/`S9`/`S11`/`S12`/`S10`, resolve mode A under arm (a)/(b)/(c)/(d), otherwise verify mode B's three conditions (closed membership in `MEASUREMENT_ONLY_DIGEST_KEYS`, `P12` elision binding, proven-absent pre-image) | empty diffs, else `EVIDENCE_PACKAGE_NOT_ADDITIVE`; **every value outside `MEASUREMENT_ONLY_DIGEST_KEYS` resolves as a retained object** (retained-object resolution) and **exactly the two enumerated elided-member digests resolve as retained measurement records** (retained measurement-record resolution), the two resolution kinds reported separately, else `EVIDENCE_NOT_RETAINED` | PARTIAL — git mechanics exist, no generator |
| 17 | Envelope-reference acceptance (`P24`) | `S3`'s `execution_mode` and `target_safety_validation_ref` present and accepted by the governing envelope checks | acceptance, else `ENVELOPE_REFERENCE_NOT_ACCEPTED` | NO |
| 18 | Verifier-derived S1 A2R/M1R authorization + closed Mach-O/context/same-byte/domain closure (`P25`) | from synthetic fixtures enforce exact frozen Python/lock and FFmpeg/FFprobe constants; mechanically derive base and coherent keg roots; validate run-scoped venv binding; exercise total `PATH_CANONICALIZATION_V1` including the project-owned 32-hop ceiling and precedence; exercise project-writer quiescence and complete Census-A/Census-B equality/classification/digest rules of `PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1`; invoke exactly `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` for arbitrary bounded-root files and `MACHO_NATIVE_CONTAINER_PARSE_V1` only at the closed native-parser entry; construct deterministic synthetic `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` manifests from Census-A native immutable images without using the host; prove current real baseline state is `NOT_OBSERVED` and therefore pre-entry Generation B is blocked; validate every active-state field of `TABLE-S4-A2R-M1R-ECHO-SCHEMA`; exercise every row of `TABLE-MACHO-CONTAINER-SLICE-POLICY`, every row of `TABLE-MACHO-HEADER64-V1`, every numeric row of `TABLE-MACHO-LOAD-COMMAND-POLICY`, and every accepted row of `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`; require exact accepted-policy↔structure-row bijection; reject every unlisted command; preserve context fixed point, Census-A same-byte derivation, Domain P/H/system, empty optional registry, family/order/privacy; execute every falsifier in `TABLE-TIER1-ADVERSARIAL-MATRIX` | synthetic lawful capability fixtures behave exactly as declared; current pre-entry eligibility fails specifically on absent owner-pinned native-closure baseline rather than fabricating it; every root/canonicalization/quiescence/census/classifier/parser/profile/closure/S4/container/header/subtype/command/context/TOCTOU/domain/optional/inventory/privacy attack fails before tracked generation evidence with `DEPENDENCY_INVENTORY_DERIVATION_INVALID`; no synthetic census/profile becomes runtime authority | NO |
| 19 | Phase-aware Tier-1 gate conjunction over every prerequisite row above (`P22`) | **PRE-ENTRY:** evaluate the conjunction of rows 1–18 using the pre-entry capability arms of rows 2 and 4. **GENERATION RE-ASSERTION / LATER AUDIT:** evaluate the same row-1-through-row-18 conjunction, but rows 2 and 4 additionally require their retained-event-evidence arms from the generation's own `S9` + parent `S7`. Never combine a pre-entry capability result with generation-specific event evidence as though they were one observation | every prerequisite row applicable to the phase exists and verifies, else `GENERATION_B_TIER1_GATE_UNMET`; pre-entry success makes no claim that future N4a occurred, and a retained-generation audit cannot substitute capability-only evidence for rows 2/4 event binding | NO (the capabilities are absent at this base, `MEASURED`) |
| 20 | Gate-coverage closure (`P23`) | mechanically enumerate the `MACHINE_REQUIRES_TIER1` rows of `TABLE-PREDICATES` **other than `P23` itself**, and require each to be named by at least one other row of this table | zero unguarded predicates, else `GATE_COVERAGE_INCOMPLETE` | NO |
| 21 | Later retained-evidence re-measurement checks (§8.7) | from B remeasure retained subjects; from S13 read exact S8; from parent S7 read exact verifier-produced S1; reconstruct §10.3 expected policy and re-run type-strict P7/P8. Confirm event-time provenance result but **do not claim historical host dependency re-observation**; historical B1 metadata only; no `codesign` on B/N5 re-observation claim | retained checks match; zero host-reobservation, B1-as-gate or `codesign`-reexecution claims | NO |

### 14.2.1 Revision-18 Tier-1 adversarial matrix (`TABLE-TIER1-ADVERSARIAL-MATRIX`)

This matrix is the required deterministic falsifier surface for rows 5 and 18. It is synthetic
implementation-capability testing only. Synthetic roots, namespace censuses, manifests, baseline values and native bytes used
by these tests are fixtures only; they create no authoritative M1R profile, Generation-B/N4a/N5/S9 event
evidence, profile-freeze measurement, host observation or runtime authorization.

| Domain | Deterministic case | Required outcome |
|---|---|---|
| M1R roots / closure | exact frozen interpreter canonicalizes inside a valid `python@3.14/<versioned-keg>` root | derive `PYTHON_BASE_RUNTIME_ROOT_V1`; root check passes, but Generation-B eligibility still blocked while baseline is `NOT_OBSERVED` |
| M1R roots / closure | exact interpreter bytes copied outside `/opt/homebrew/Cellar/python@3.14/<versioned-keg>` | fail P25 |
| M1R roots / closure | candidate versioned keg contains a Python subject with wrong version/architecture/digest | fail P25 |
| M1R roots / closure | synthetic runtime located at exact `/private/tmp/vip-gate0/<generation_identity>/runtime/python-venv` under an exclusive verifier reservation; entrypoint resolves to frozen base, exact lock is bound, and synthetic owner-pinned fixture profile matches | capability fixture passes; fixture baseline is test-only and grants no runtime authority |
| M1R roots / closure | historical Stage-A venv absolute path presented as authority | fail P25 |
| M1R roots / closure | run-scoped venv Python entrypoint does not resolve to exact frozen base interpreter subject | fail P25 |
| M1R roots / closure | run-scoped venv bound to wrong lock digest | fail P25 |
| M1R roots / closure | any directory symlink occurs beneath either bounded scan root | do not traverse; fail P25 |
| M1R roots / closure | native Mach-O regular file with a nonstandard filename extension | included by byte/container recognition if otherwise supported |
| M1R roots / closure | file ending `.so` contains non-Mach-O bytes | not a native-closure member merely by suffix |
| M1R roots / closure | synthetic owner-pinned fixture plus injected native member | profile token/count/digest mismatch; fail P25 |
| M1R roots / closure | synthetic owner-pinned fixture plus removed native member | profile token/count/digest mismatch; fail P25 |
| M1R roots / closure | synthetic owner-pinned fixture plus byte-mutated native member | profile digest mismatch; fail P25 |
| M1R roots / closure | closure serializer receives duplicate canonical row | fail P25 |
| M1R roots / closure | same canonical rows enumerated in different traversal orders | identical sorted serialization and profile digest |
| M1R roots / closure | pure-Python/data/cache bytes mutate while native member set/bytes are unchanged | native-closure profile unchanged; no claim of full software-supply-chain integrity |
| M1R roots / closure | authoritative native-closure baseline unavailable | Generation B ineligible: `BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE` |
| FFmpeg coherent keg | frozen FFmpeg and FFprobe canonicalize to the same valid `/opt/homebrew/Cellar/ffmpeg/<keg-id>` and satisfy frozen identities | derive one `HOMEBREW_FFMPEG_KEG_ROOT_V1` subject |
| FFmpeg coherent keg | FFmpeg and FFprobe canonicalize to different keg roots | fail P25 |
| FFmpeg coherent keg | exact frozen binary bytes copied outside canonical `ffmpeg` Cellar formula domain | fail P25 |
| FFmpeg coherent keg | mutable `/opt/homebrew/opt/ffmpeg` locators both resolve to one lawful frozen keg | locator accepted only after canonical root + identity checks |
| FFmpeg coherent keg | mutable alias/relink drifts to another keg or binary | fail P25; authority does not update |
| FFmpeg coherent keg | correct canonical path shape but FFmpeg or FFprobe digest differs | fail P25 |
| S4 A2R/M1R echo | the exact active-state key set is present with exact types/values and no undeclared key | echo-coherence capability passes; echo grants no authority |
| S4 A2R/M1R echo | parameterized fixture omits each field required by the active state, one field per test case | every omission fails P25 |
| S4 A2R/M1R echo | any undeclared key is inserted into `S4.a2r_m1r_echo` | fail P25 |
| S4 A2R/M1R echo | parameterized fixture gives each schema field a wrong JSON type | every wrong type fails P25 |
| S4 A2R/M1R echo | echo is well-typed but conflicts with independently verifier-derived observation | fail P25 |
| S4 A2R/M1R echo | baseline state is `NOT_OBSERVED` and digest/count keys are absent | honest current-state representation; no placeholder digest/count |
| S4 A2R/M1R echo | baseline state is `NOT_OBSERVED` but digest/count key is `null`, empty, zero or synthetic | fail P25 |
| M1R wrapper | empty byte string | `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` returns exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | one arbitrary byte | return exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | three arbitrary bytes | return exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | ASCII prefix `from` / bytes `66 72 6f 6d` | return exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | JSON/data prefix such as bytes `7b 22 6b 22` (`{"k"`) | return exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | ZIP prefix `50 4b 03 04` | return exactly `NON_NATIVE`; native parser not invoked |
| M1R wrapper | listed rejected `MH_CIGAM_64` bytes `fe ed fa cf` | return exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25 |
| M1R wrapper | listed rejected 32-bit `MH_MAGIC` bytes `ce fa ed fe` | return exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25 |
| M1R wrapper | listed supported `MH_MAGIC_64` prefix with truncated Header64 | native parser is invoked; wrapper returns exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25; never `NON_NATIVE` |
| M1R wrapper | listed supported fully valid native object | native parser succeeds; wrapper returns exactly `NATIVE_MEMBER` |
| Native parser entry | unlisted magic is passed directly as an already-governed native subject | `MACHO_NATIVE_CONTAINER_PARSE_V1` fails exactly `REJECT_UNSUPPORTED` |
| Native parser entry | listed `REJECT_UNSUPPORTED` magic is passed as native | fail exactly `REJECT_UNSUPPORTED` |
| Native parser entry | listed `SUPPORTED` magic with complete valid project grammar | parse succeeds under the closed project grammar |
| Native parser entry | listed `SUPPORTED` magic with malformed supported grammar | fail closed; parser result cannot be downgraded to ordinary `NON_NATIVE` |
| Native parser entry | generic parser/library recognizes a future native magic absent from the project table | project result remains `REJECT_UNSUPPORTED`; external parser knowledge cannot widen authority |
| Native container / slice | supported thin `MH_MAGIC_64` little-endian arm64 ALL | PASS if all remaining structure/commands are valid |
| Native container / slice | supported fat32 big-endian containing exactly one valid arm64 ALL/V8 slice | inspect exactly that arm64 slice; PASS if graph valid |
| Native container / slice | supported fat64 big-endian containing exactly one valid arm64 ALL/V8 slice | inspect exactly that arm64 slice; PASS if graph valid |
| Native parser / container slice | at `MACHO_NATIVE_CONTAINER_PARSE_V1` entry, listed rejected or unlisted container magic/endianness | fail P25 / `REJECT_UNSUPPORTED` |
| Native container / slice | fat architecture table truncated | fail P25 |
| Native container / slice | very large `nfat_arch` makes mathematical `metadata_end` exceed immutable file length | fail P25 |
| Native container / slice | very large decoded offset/size has mathematical `offset + size > file_length`; host-width wraparound is attempted | fail P25 |
| Native container / slice | declared slice lies out of bounds | fail P25 |
| Native container / slice | two declared slice ranges overlap | fail P25 |
| Native container / slice | declared alignment is outside 0..63 or slice offset violates `2^align` | fail P25 |
| Native container / slice | exact `CPU_TYPE_ARM64` / raw subtype ALL = 0 | supported |
| Native container / slice | exact `CPU_TYPE_ARM64` / raw subtype V8 = 1 | supported |
| Native container / slice | raw subtype ARM64E = 2 | fail P25 |
| Native container / slice | raw ARM64 subtype carries any feature bit | fail P25 |
| Native container / slice | x86_64-only thin or fat input | fail P25 |
| Native container / slice | zero supported arm64 slices after full structural validation | fail P25 |
| Native container / slice | more than one supported arm64 slice (including ALL + V8) | fail P25; no preference selection |
| Native container / slice | fat entry CPU type/subtype disagrees with inner selected thin header | fail P25 |
| Native container / slice | load-command table/header is truncated, misaligned or does not consume exact `ncmds`/`sizeofcmds` | fail P25 |
| Load-command numeric policy | LC_SEGMENT exact value `0x00000001` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_SYMTAB exact value `0x00000002` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_SYMSEG exact value `0x00000003` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_THREAD exact value `0x00000004` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_UNIXTHREAD exact value `0x00000005` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LOADFVMLIB exact value `0x00000006` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_IDFVMLIB exact value `0x00000007` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_IDENT exact value `0x00000008` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_FVMFILE exact value `0x00000009` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_PREPAGE exact value `0x0000000a` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_DYSYMTAB exact value `0x0000000b` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LOAD_DYLIB exact value `0x0000000c` fixture | exactly one governed dependency edge with normal target-resolution law |
| Load-command numeric policy | LC_ID_DYLIB exact value `0x0000000d` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LOAD_DYLINKER exact value `0x0000000e` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_ID_DYLINKER exact value `0x0000000f` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_PREBOUND_DYLIB exact value `0x00000010` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_ROUTINES exact value `0x00000011` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_SUB_FRAMEWORK exact value `0x00000012` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_SUB_UMBRELLA exact value `0x00000013` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_SUB_CLIENT exact value `0x00000014` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_SUB_LIBRARY exact value `0x00000015` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_TWOLEVEL_HINTS exact value `0x00000016` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_PREBIND_CKSUM exact value `0x00000017` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LOAD_WEAK_DYLIB exact value `0x80000018` fixture | exactly one governed dependency edge with normal target-resolution law |
| Load-command numeric policy | LC_SEGMENT_64 exact value `0x00000019` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_ROUTINES_64 exact value `0x0000001a` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_UUID exact value `0x0000001b` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_RPATH exact value `0x8000001c` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_CODE_SIGNATURE exact value `0x0000001d` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_SEGMENT_SPLIT_INFO exact value `0x0000001e` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_REEXPORT_DYLIB exact value `0x8000001f` fixture | exactly one governed dependency edge with normal target-resolution law |
| Load-command numeric policy | LC_LAZY_LOAD_DYLIB exact value `0x00000020` fixture | exactly one governed dependency edge with normal target-resolution law |
| Load-command numeric policy | LC_ENCRYPTION_INFO exact value `0x00000021` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLD_INFO exact value `0x00000022` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLD_INFO_ONLY exact value `0x80000022` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LOAD_UPWARD_DYLIB exact value `0x80000023` fixture | exactly one governed dependency edge with normal target-resolution law |
| Load-command numeric policy | LC_VERSION_MIN_MACOSX exact value `0x00000024` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_VERSION_MIN_IPHONEOS exact value `0x00000025` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_FUNCTION_STARTS exact value `0x00000026` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLD_ENVIRONMENT exact value `0x00000027` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | LC_MAIN exact value `0x80000028` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DATA_IN_CODE exact value `0x00000029` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_SOURCE_VERSION exact value `0x0000002a` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLIB_CODE_SIGN_DRS exact value `0x0000002b` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_ENCRYPTION_INFO_64 exact value `0x0000002c` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LINKER_OPTION exact value `0x0000002d` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_LINKER_OPTIMIZATION_HINT exact value `0x0000002e` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_VERSION_MIN_TVOS exact value `0x0000002f` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_VERSION_MIN_WATCHOS exact value `0x00000030` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_NOTE exact value `0x00000031` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_BUILD_VERSION exact value `0x00000032` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLD_EXPORTS_TRIE exact value `0x80000033` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_DYLD_CHAINED_FIXUPS exact value `0x80000034` fixture | accepted with declared non-edge role and zero dependency edge |
| Load-command numeric policy | LC_FILESET_ENTRY exact value `0x80000035` fixture | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | unknown numeric command with `LC_REQ_DYLD` bit set | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | unknown numeric command without `LC_REQ_DYLD` bit | fail P25 / `REJECT_UNSUPPORTED` |
| Load-command numeric policy | parser/library exposes a symbolic name for a numeric value absent from project V1 table | fail P25 / `REJECT_UNSUPPORTED`; parser knowledge cannot widen policy |
| Mach-O graph | one direct lawful non-system dependency | included exactly once |
| Mach-O graph | lawful transitive non-system dependency | included by fixed-point closure |
| Mach-O graph | same canonical dependency reachable twice | one global identity only after context agreement |
| Mach-O graph | unresolved dependency edge | fail P25 |
| Mach-O graph | one edge resolves to multiple distinct canonical targets | fail P25 |
| Mach-O graph | unique `@loader_path` target | deterministic PASS |
| Mach-O graph | unique `@executable_path` target | deterministic PASS under carried originating context |
| Mach-O graph | unique `@rpath` target under governed ordered LC_RPATH set | deterministic PASS |
| Context closure | same dylib reached from two governed executable seeds | evaluate both state contexts |
| Context closure | same `@executable_path` edge resolves identically across contexts | one globally de-duplicated target |
| Context closure | same install name resolves differently across lawful contexts | fail P25 |
| Context closure | fully resolved cycle | fixed-point PASS; no duplicate |
| Context closure | ambiguous `@rpath` | fail P25 |
| Context closure | traversal-order permutations | byte-identical final inventory/order |
| TOCTOU | host source mutates after initial verifier read | hash/parse/materialized bytes remain the initial transient image |
| TOCTOU | SHA, container/slice parse, load commands and materialization inspect one source | all derive from exactly one transient byte image |
| TOCTOU | attempted second host read substitutes later content | fail P25 / substitution impossible under governed interface |
| Domain | exact member of synthetic owner-pinned M1R Python native profile | Domain P/Python-family admission in capability fixture |
| Domain | lexically under venv/base root but not present in verified M1R native profile | no Domain-P authority; fail unless separately lawful under Domain H/system |
| Domain | lawful Cellar dependency reached by deterministic graph | Domain H admission |
| Domain | arbitrary Cellar file not reached by graph | fail P25 |
| Domain | dependency outside verified M1R native membership/Domain H/system | fail P25 |
| Domain | attempted Cellar host scan/enumeration to grant permission | fail P25 |
| System | canonical target under `/usr/lib` or `/System/Library` | observed/classified system; no entitlement role |
| Optional seeds | production registry is exactly `[]` | PASS |
| Optional seeds | runtime/config attempts registry insertion | fail P25 |
| Optional seeds | historical `mpg123` or `zstd` name alone | no authority; registry remains empty |
| Optional seeds | test-only synthetic registry fixture has required semantic seed missing | resolver fails closed; fixture never becomes production authority |
| Optional seeds | test-only synthetic registry fixture resolves one semantic seed to multiple versioned candidates | resolver fails closed; fixture never becomes production authority |
| Optional seeds | future generation requires unmodelled optional/dlopen-only component | generation ineligible pending owner-approved design revision |
| Inventory | producer supplies one extra canonical index | fail P25 |
| Inventory | producer omits one derived index | fail P25 |
| Inventory | producer reorders derived identities | fail P25 |
| Inventory | producer duplicates a derived identity | fail P25 |
| Inventory | producer expands list to 1,000 entries | fail P25 |
| Inventory | same identity reachable from both families while an exact M1R Python native member | emitted once; Python family precedence |
| Inventory | producer proposes the same identity in both families | proposal grants no authority; verifier derives one family or fails P25 |
| Inventory | family cannot be determined under exact membership/reachability rules | fail P25 |
| Oracle isolation | callable `measurer` parameter added to production boundary | row 5 negative scan fails |
| Oracle isolation | production setter hook added | row 5 negative scan fails |
| Oracle isolation | production factory accepting measurer added | row 5 negative scan fails |
| Oracle isolation | production registry added | row 5 negative scan fails |
| Oracle isolation | callback/plugin map selects helper | row 5 negative scan fails |
| Oracle isolation | mutable production global holds selectable measurer | row 5 negative scan fails |
| Oracle isolation | production module-loader/import selector added | row 5 negative scan fails |
| Oracle isolation | test oracle physically placed under production package/source root | row 5 negative scan fails |
| Oracle isolation | test oracle resolvable through ordinary production `sys.path`/module search | row 5 negative scan fails |
| Oracle isolation | production dependency/install manifest includes test oracle | row 5 negative scan fails |
| Oracle isolation | production module re-exports/aliases test oracle | row 5 negative scan fails |
| Oracle isolation | ordinary production import resolves test oracle | row 5 negative scan fails |
| Oracle isolation | oracle exists only on test path and ordinary production import fails | valid test-only isolation |

| Generation-bound venv | exact verifier-derived `RUN_SCOPED_VENV_ROOT_V1` under a fresh exclusive reservation | locator/binding condition passes; remaining A2R/M1R checks still required |
| Generation-bound venv | producer/S3/S4/runtime policy nominates an alternate venv root | fail P25; nominated path is non-authoritative |
| Generation-bound venv | derived generation namespace already exists before reservation | fail P25 on collision; do not adopt it |
| Generation-bound venv | generation namespace or `runtime/python-venv` path component is a symlink/alias | fail P25 |
| Generation-bound venv | namespace from a prior or already-used generation is presented for reuse | fail P25 |
| Generation-bound venv | profile/lock-correct runtime is located under a different generation identity | fail P25 |
| Generation-bound venv | profile/lock-correct runtime is at a non-derived absolute root | fail P25 |
| Exhaustive enumeration | supported native Mach-O is placed in a deeply nested package subtree | it is enumerated and included |
| Exhaustive enumeration | supported native Mach-O is placed beneath a dot/hidden directory | it is enumerated and included |
| Exhaustive enumeration | supported native Mach-O is placed in an arbitrary non-`site-packages` subtree | it is enumerated and included |
| Exhaustive enumeration | supported native Mach-O has a nonstandard/native-unhinting filename | byte policy determines membership; it is included if supported |
| Exhaustive enumeration | implementation fixture scans only known runtime directories and omits an otherwise reachable subtree | capability fails P25; incomplete traversal is non-conforming |
| Exhaustive enumeration | FIFO/socket/device/other unsupported filesystem entry appears beneath a root | fail P25 |
| Symlink / scope | file symlink is dangling | fail P25 |
| Symlink / scope | file symlink resolves outside both Python roots | fail P25 |
| Symlink / scope | venv file symlink resolves to supported native file under base root, including `bin/python`→base interpreter | classify canonical target under `BASE_RUNTIME`; no venv alias row |
| Symlink / scope | repeated file-symlink aliases resolve to one canonical target | collapse before serialization to one target-owning row |
| Symlink / scope | canonical Python roots are equal, nested in either direction, or otherwise overlap ambiguously | fail P25 before traversal |
| Symlink / scope | two distinct canonical relative paths are Unicode-normalization lookalikes | preserve exact UTF-8 bytes as distinct pathname subjects; no normalization |
| Symlink / scope | two distinct canonical relative paths differ only by case on a filesystem that admits both | preserve as distinct pathname subjects; no case folding |
| S4 exact key set | `NOT_OBSERVED` object contains exactly `S4_NOT_OBSERVED_KEYS_V1` | schema coherence passes; digest/count absent |
| S4 exact key set | synthetic future `MEASURED_AND_OWNER_PINNED` object contains exactly `S4_MEASURED_AND_OWNER_PINNED_KEYS_V1` with fixture digest/count | schema capability passes only as synthetic fixture; no runtime authority |
| S4 exact key set | duplicate JSON/object member name | fail P25 before schema validation |
| S4 exact key set | alias/synonym is used instead of a defined key | fail P25 |
| S4 exact key set | one required key is missing | fail P25 |
| S4 exact key set | one key has wrong JSON type | fail P25 |
| S4 exact key set | well-typed echo conflicts with verifier-derived truth | fail P25 |
| S4 exact key set | `NOT_OBSERVED` contains either digest or count key | fail P25 |
| S4 exact key set | `MEASURED_AND_OWNER_PINNED` omits either digest or count key | fail P25 |
| FAT structural grammar | declared slice starts before `metadata_end` and overlaps FAT metadata | fail P25 |
| FAT structural grammar | declared slice has `size = 0` | fail P25 |
| FAT structural grammar | unrelated non-selected slice has opaque malformed non-Mach-O payload but valid outer FAT range/alignment | outer validation passes; payload is ignored and contributes no edge |
| FAT structural grammar | valid slice ranges contain one or more gaps | permitted; gaps ignored |
| FAT structural grammar | valid final slice is followed by trailing bytes | permitted; trailing bytes ignored |
| FAT structural grammar | huge decoded arithmetic values exceed host machine word but mathematical table/range inequalities are decidable | validity follows mathematical integers only; host-width behavior cannot change result |
| FAT structural grammar | full architecture table is truncated | fail P25 |
| FAT structural grammar | mathematical slice end exceeds immutable file length | fail P25 |
| FAT structural grammar | pairwise slice ranges overlap | fail P25 |
| FAT structural grammar | align > 63 or offset is not divisible by mathematical `2^align` | fail P25 |
| FAT structural grammar | FAT64 `reserved != 0` | fail P25 |
| FAT structural grammar | selected allowed-arm64 outer CPU type/subtype differs from inner thin header | fail P25 |
| Load-command structural grammar | `LC_SEGMENT` / `0x00000001`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_SYMTAB` / `0x00000002`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_SYMSEG` / `0x00000003`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_THREAD` / `0x00000004`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_UNIXTHREAD` / `0x00000005`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_IDENT` / `0x00000008`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYSYMTAB` / `0x0000000b`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LOAD_DYLIB` / `0x0000000c`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ID_DYLIB` / `0x0000000d`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LOAD_DYLINKER` / `0x0000000e`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ID_DYLINKER` / `0x0000000f`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ROUTINES` / `0x00000011`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_TWOLEVEL_HINTS` / `0x00000016`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_PREBIND_CKSUM` / `0x00000017`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LOAD_WEAK_DYLIB` / `0x80000018`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_SEGMENT_64` / `0x00000019`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ROUTINES_64` / `0x0000001a`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_UUID` / `0x0000001b`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_RPATH` / `0x8000001c`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_CODE_SIGNATURE` / `0x0000001d`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_SEGMENT_SPLIT_INFO` / `0x0000001e`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_REEXPORT_DYLIB` / `0x8000001f`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LAZY_LOAD_DYLIB` / `0x00000020`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ENCRYPTION_INFO` / `0x00000021`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYLD_INFO` / `0x00000022`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYLD_INFO_ONLY` / `0x80000022`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LOAD_UPWARD_DYLIB` / `0x80000023`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_VERSION_MIN_MACOSX` / `0x00000024`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_VERSION_MIN_IPHONEOS` / `0x00000025`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_FUNCTION_STARTS` / `0x00000026`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_MAIN` / `0x80000028`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DATA_IN_CODE` / `0x00000029`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_SOURCE_VERSION` / `0x0000002a`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYLIB_CODE_SIGN_DRS` / `0x0000002b`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_ENCRYPTION_INFO_64` / `0x0000002c`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LINKER_OPTION` / `0x0000002d`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails; one required pad/reserved zero byte changed nonzero fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LINKER_OPTIMIZATION_HINT` / `0x0000002e`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_VERSION_MIN_TVOS` / `0x0000002f`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_VERSION_MIN_WATCHOS` / `0x00000030`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_NOTE` / `0x00000031`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_BUILD_VERSION` / `0x00000032`: minimal valid row fixture; undersized fixed/formula fixture; malformed count/formula or unparsed trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYLD_EXPORTS_TRIE` / `0x80000033`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_DYLD_CHAINED_FIXUPS` / `0x80000034`: minimal valid row fixture; undersized fixed/formula fixture; oversized cmdsize/trailing byte fails | minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction |
| Load-command structural grammar | `LC_LOAD_DYLIB` has valid numeric value but fixed payload shorter than 24 bytes | fail P25; no edge is emitted |
| Load-command structural grammar | `LC_ID_DYLIB` has invalid string offset, missing NUL, or nonzero required terminal padding | fail P25 |
| Load-command structural grammar | `LC_SEGMENT_64` `cmdsize != 72 + nsects×80` | fail P25 |
| Load-command structural grammar | `LC_BUILD_VERSION` `cmdsize != 24 + ntools×8` | fail P25 |
| Load-command structural grammar | `LC_LOAD_DYLINKER`, `LC_ID_DYLINKER` or `LC_RPATH` violates exact offset/NUL/zero-padding law | fail P25 |
| Load-command structural grammar | two command intervals overlap or any interval leaves the declared command region | fail P25 |
| Load-command structural grammar | command walk consumes a count different from `ncmds` | fail P25 |
| Load-command structural grammar | command walk byte total differs from `sizeofcmds` | fail P25 |

| PATH_CANONICALIZATION_V1 | direct self-referential symlink under an authorized root | resolver result exactly `SYMLINK_CYCLE`; fail P25; terminate without traversal |
| PATH_CANONICALIZATION_V1 | two symlinks resolve to each other | resolver result exactly `SYMLINK_CYCLE`; fail P25; terminate without host retry/ELOOP semantics |
| PATH_CANONICALIZATION_V1 | longer symlink chain repeats an earlier symlink pathname identity | resolver result exactly `SYMLINK_CYCLE`; fail P25 |
| PATH_CANONICALIZATION_V1 | symlink target is missing | resolver result exactly `DANGLING`; fail P25 |
| PATH_CANONICALIZATION_V1 | an intermediate target component is missing | resolver result exactly `DANGLING`; fail P25 |
| PATH_CANONICALIZATION_V1 | injected permission/I/O/canonicalization failure prevents one canonical target | resolver result exactly `CANONICALIZATION_FAILURE`; fail P25 |
| PATH_CANONICALIZATION_V1 | symlink uniquely resolves to an unsupported filesystem object | resolver result exactly `RESOLVED_UNSUPPORTED_OBJECT`; fail P25 |
| PATH_CANONICALIZATION_V1 | symlink uniquely resolves to a regular file inside exactly one authorized root | resolver result exactly `RESOLVED_REGULAR_FILE`; continue only under existing target-owning file-symlink law |
| PATH_CANONICALIZATION_V1 | symlink uniquely resolves to a real directory | resolver result exactly `RESOLVED_DIRECTORY`; directory-symlink law fails P25 and never traverses it |
| Resolver hop bound | acyclic chain requires 31 symlink-target expansions and then reaches one regular file | may continue to ordinary final regular-file classification if all other rules pass; `symlink_hops = 31` |
| Resolver hop bound | acyclic chain requires exactly 32 symlink-target expansions and then reaches one regular file | may continue to ordinary final regular-file classification if all other rules pass; no 33rd expansion occurs |
| Resolver hop bound | current counter is 32 and resolving the next observed symlink would require expansion 33 | return exactly `CANONICALIZATION_FAILURE_HOP_LIMIT`; fail P25; do not expand target 33 |
| Resolver hop bound | external/root mutation continually produces fresh never-before-visited symlink pathname identities | terminate at the project-owned ceiling with `CANONICALIZATION_FAILURE_HOP_LIMIT`; no claim that external mutation was prevented |
| Resolver hop bound | repeated pathname is encountered at hop 5 | return exactly `SYMLINK_CYCLE`, not hop-limit failure |
| Resolver hop bound | host/library has an operational symlink limit lower than 32 | host limit is not project authority; an earlier host observation failure maps fail-closed through the existing canonicalization-failure family and does not redefine the project constant |
| Resolver hop bound | host/library would permit more than 32 symlink expansions | project ceiling controls; expansion 33 is forbidden and returns `CANONICALIZATION_FAILURE_HOP_LIMIT` |
| Stable census | insert a file into a directory already enumerated by Census A before Census B | Census A/B namespace sets differ; fail P25 |
| Stable census | remove an entry between Census A and Census B | Census A/B namespace sets differ; fail P25 |
| Stable census | rename an entry between Census A and Census B | Census A/B namespace sets differ; fail P25 |
| Stable census | replace a Census-A regular file pathname with a symlink before Census B | entry-kind/namespace row differs; fail P25 |
| Stable census | replace a Census-A symlink pathname with a regular file before Census B | entry-kind/namespace row differs; fail P25 |
| Stable census | retarget a symlink while preserving its pathname | raw target bytes and/or canonical target identity differs; fail P25 |
| Stable census | mutate bytes of a Census-A `NATIVE_MEMBER` while preserving namespace | Census-B native stability digest differs; fail P25 |
| Stable census | Census-A ordinary regular file `NON_NATIVE` becomes `NATIVE_MEMBER` before Census B | classification transition; fail P25 |
| Stable census | Census-A `NATIVE_MEMBER` becomes `NON_NATIVE` before Census B | classification transition; fail P25 |
| Stable census | relocate a native pathname between roots or pathnames | namespace/root-scope rows differ; fail P25 |
| Stable census | mutate pure-Python/data content while pathname/type remain unchanged and both censuses classify `NON_NATIVE` | allowed by M1R; namespace/classification stability passes; no full-content-integrity claim |
| Stable census | Census A and Census B are exactly identical and all native stability digests match | stable-census capability passes; fixture grants no runtime/profile authority |
| Stable census / classifier transition | one ordinary subject is `NON_NATIVE` in Census A and remains `NON_NATIVE` in Census B, while ordinary content changes | may pass if namespace/classification obligations otherwise hold; ordinary non-native byte equality is not required |
| Stable census / classifier transition | one subject is `NON_NATIVE` in Census A and `NATIVE_MEMBER` in Census B | fail P25 |
| Stable census / classifier transition | one subject is `NATIVE_MEMBER` in Census A and `NON_NATIVE` in Census B | fail P25 |
| Stable census / classifier transition | one subject is `NATIVE_MEMBER` in both censuses but native digest changes | fail P25 |
| Stable census / classifier transition | either Census A or Census B returns `UNSUPPORTED_MACHO_CANDIDATE` | fail P25 immediately |
| Stable census | producer, build adapter, or runtime/config surface retains project write capability to either root during capture | project-writer quiescence not established; fail P25 before successful capture |
| Stable census | verifier mutates either authorized root during capture | verifier-quiescence invariant violated; fail P25 |
| Mach-O header64 | exact 32-byte `MH_MAGIC_64` ARM64 header with subtype 0 and empty command region | `TABLE-MACHO-HEADER64-V1` accepts header; command region begins/ends at 32 |
| Mach-O header64 | supported `MH_MAGIC_64` prefix but selected slice has fewer than 32 bytes | invalid/truncated supported candidate; fail P25; never classify `NON_NATIVE` |
| Mach-O header64 | selected thin header magic is not `0xfeedfacf` | fail project header/container policy |
| Mach-O header64 | `cputype` is not raw `0x0100000c` | fail P25 |
| Mach-O header64 | raw `cpusubtype = 2` (ARM64E) | fail P25 |
| Mach-O header64 | raw `cpusubtype` is an unknown value other than 0 or 1 | fail P25 |
| Mach-O header64 | mathematical `32 + sizeofcmds` exceeds selected-slice length | fail P25 without host-integer overflow semantics |
| Mach-O header64 | `ncmds=0`, `sizeofcmds=0` with otherwise valid 32-byte header | accept empty command region; consumed command count and bytes are both exactly zero |
| Mach-O header64 | `ncmds>0`, `sizeofcmds=0` | exact command-count/byte-total law cannot both hold; fail P25 |
| Mach-O header64 | bytes shaped like a load command begin at selected-slice offset 31 | non-authoritative placement; walker still starts exactly at 32 and malformed project walk fails P25 |
| Mach-O header64 | bytes shaped like a load command begin at selected-slice offset 33 | non-authoritative placement; walker still starts exactly at 32 and malformed project walk fails P25 |
| Mach-O header64 | valid FAT container selects ARM64 slice at nonzero file offset with valid header at selected-slice-local byte 0 | header origin is selected-slice-local 0; command walker begins selected-slice-local 32 |
| Mach-O header64 | valid standalone thin input | file byte 0 is header origin; command walker begins file byte 32 |
| Mach-O header64 | arbitrary raw `filetype` with all project-required fields/commands valid | accepted as raw V1 metadata; no independent rejection |
| Mach-O header64 | arbitrary raw `flags` with all project-required fields/commands valid | accepted as raw V1 metadata; no independent rejection |
| Mach-O header64 | arbitrary raw `reserved` with all project-required fields/commands valid | accepted as raw V1 metadata; no independent rejection |
| Mach-O header64 | generic parser rejects an otherwise project-valid header solely because of stricter `filetype`/`flags`/`reserved` semantics | generic-parser result is non-normative; project result remains determined solely by V1 grammar |
Every numeric row of `TABLE-MACHO-LOAD-COMMAND-POLICY` has exactly one numeric-policy fixture row above, and the three unknown/parser-knowledge cases separately prove the default-reject law. Every accepted numeric value additionally has exactly one `Load-command structural grammar` fixture-family row generated from the one-to-one structure table; each family contains the required valid, undersized, formula/trailing and applicable padding/reserved falsifiers. S4 omission/type fixtures
iterate the active-state field set of `TABLE-S4-A2R-M1R-ECHO-SCHEMA`; they are not a single cherry-picked
field. Container fixtures cover every supported V1 encoding and explicit reject boundaries.

`P23`'s gate-coverage clause is what makes this table complete rather than illustrative: a predicate that
no row names is a capability with no gate, and the check fails closed. `P22` is the conjunction of rows
1–18 of `TABLE-TIER1-GATE` and is named by the aggregate row; `P23` is named by the closure row. No
predicate is ever its own gate. These are required future implementation tests, not tests executed by this
design-authoring turn.

### 14.3 Present-state honesty — runtime evidence and M1R baseline remain `NOT_OBSERVED`

Generation B has not run under this design. No N4a/N5/S9 event, live Stage-B result, provider/model event
or protected-media operation is claimed.

Separately and critically, no authoritative `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` profile-freeze
measurement exists in repository evidence. Therefore:

- `PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`;
- no baseline digest/member count is present or inferable;
- synthetic Tier-1 fixture profiles are capability-test data only;
- `GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`;
- future measurement requires separate owner authorization and later owner pinning before it can become
  seed-profile authority.

This design does not upgrade `NOT_OBSERVED` to an evidence class or runtime result.

### 14.4 Target safety — the orphan code removed and deferred

`TARGET_SAFETY_NOT_VALIDATED` is **removed**: the orphan code and its claim are deleted from this
specification, and target safety is deferred to the governing existing contract.

**Why the alternative is impossible, measured.** The alternative would have defined a predicate by which
the verifier derives `target_safety_state` from the referenced validation attempt **and** the seal-derived
signed entitlement inventory. Three measured facts close that path:

1. `derive_target_safety_state(*, artifact, receipt_intent_label, run_config_digest,
   receipt_schema_version, now)` takes **no inventory parameter** and never compares an inventory; it only
   requires that the artifact's `configuration_binding.entitlement_inventory_digest` **is a digest**.
2. The C07 entitlement-inventory check is consumed by the **offline producer**
   `scripts/target-safety-validate.py`, which runs **before** the generation; it defaults to `NOT_OBSERVED`
   / `SIGNED_BUNDLE_NOT_PRESENT` when no inventory is supplied.
3. The only verifier-derived signed inventory in A′ comes from seal `B` at `N4b`, i.e. **during** the
   generation.

The offline artifact therefore cannot bind a digest of an inventory that does not yet exist, and
`derive_target_safety_state` — which returns `VALIDATED` only when every required check is `PASS` — can
never return `VALIDATED` in A′. Installing a predicate on that basis would have installed a **false
prerequisite** that blocks Generation B forever while claiming to gate it.

**What replaces it.** Target safety remains governed by C² rev-6 §11.5 and `C15`
(blob `f0d070f6e34ca107c03c8cfd35b79b246110f4a0`), including the `target_safety_validation_ref` reference
carried in `S3` and the derived `VALIDATED` | `STALE` | `NOT_OBSERVED` vocabulary; this specification
asserts **no** target-safety result of its own and creates no predicate, node or failure code for it.

**Re-entry trigger.** If any future stage launches the application, this specification must be re-entered
with (i) a new predicate whose subject is the seal-derived inventory, (ii) a named failure code, and (iii)
an explicit statement of which artifact is the inventory's lawful home — because the temporal ordering
above must then be re-solved, not assumed. No orphan failure code remains in §13.1.

---

## 15. Verification strategy

`V-1`…`V-21`. Each check states its class, drawn **only** from the four §5.1 labels. `DOCUMENT_CHECK`
checks are executable against this document's text and the phase-correct candidate-lineage or separately pinned immutable repository objects declared by §7.1; `MACHINE_REQUIRES_TIER1` checks require the §14.2
capabilities and **were not executed in this turn**. There is no fifth label. **This table is the authority
for the check count**; §3.3's declared value is a derived echo checked by `V-13`.

| # | Check | Method | Expected | Class |
|---|---|---|---|---|
| V-1 | Node count self-consistency | mechanically count the `S`-rows of §3.1 and compare with §3.3's declared node echo | equal | `DOCUMENT_CHECK` |
| V-2 | Stage, sub-stage and conditional-node counts | count the `N`-rows of §4.1 and §4.2, and the conditional nodes declared in §3.2; compare each with §3.3 | all equal | `DOCUMENT_CHECK` |
| V-3 | Rank-group count | count distinct ranks in §4.3 and compare with §3.3; also require every rank value used in §4.4 to appear in §4.3 | equal; zero undeclared ranks | `DOCUMENT_CHECK` |
| V-4 | **Edge-table rank validation** | for every §4.4 row require `CONSUMER_RANK > CONSUMED_RANK`, `CONSUMER != CONSUMED`, no repeated ordered pair, and that both rank cells name members of the rank set of §4.3; require the row count to equal §3.3's declared edge echo | row count equal; zero violations | `DOCUMENT_CHECK` |
| V-5 | No self edge, no future edge, no duplicate ordered pair | scan §4.4 for `CONSUMER == CONSUMED`, `CONSUMER_RANK ≤ CONSUMED_RANK`, and repeated ordered pairs | zero | `DOCUMENT_CHECK` |
| V-6 | **Non-edge completeness and declaration** | enumerate every unordered pair sharing a rank in §4.3 and require it to appear exactly once in §4.5; require the §4.5 row count to equal §3.3's declared non-edge echo | set equality; count equal | `DOCUMENT_CHECK` |
| V-7 | **Predicate-to-code and code-to-predicate closure** | every §5.2 row names **exactly one** code defined in §13.1, and every §13.1 row is named by **exactly one** §5.2 predicate | zero gaps; zero orphans; no many-to-one mapping | `DOCUMENT_CHECK` |
| V-8 | Predicate count self-consistency | mechanically count the `P`-rows of §5.2 and compare with §3.3's declared predicate echo | equal | `DOCUMENT_CHECK` |
| V-9 | **Code vocabulary uniqueness** | one code row of `TABLE-CODES` = exactly one code token; no duplicate code token; each code row's `Evaluated at`, `Reachable because` and `Resulting branch` cells are non-empty. The instrument counts **rows and tokens**, and makes **no** claim about how many code names happen to contain a digit | zero duplicates; zero empty cells | `DOCUMENT_CHECK` |
| V-10 | **Tier-1 gate coverage, tier honesty and origin-sensitive continuity** | require coverage/closed labels; row 5 must bind exact production boundary/call-site/post-return code identity with leaf-only substitution, forbid post-return discriminators/alternate source, require split/recompute/helper mutations, enumerate configuration/data + programmatic selector + physical/logical package/import domains, and require every oracle isolation falsifier in `TABLE-TIER1-ADVERSARIAL-MATRIX`. Mechanically require production package/install/source-root exclusion, production `sys.path`/module-search non-resolution, ordinary production import failure and no re-export/alias. Test duplicate/current/second/stale capability cases; oracle remains test-only capability evidence | zero coverage/tier defects; same-production-core + fixed-private-leaf + complete production-unreachability explicit; every selector/package/import falsifier present; zero capability/event conflation | `DOCUMENT_CHECK` |
| V-11 | Failure-code count self-consistency | mechanically count the code-rows of §13.1 **by row, not by token shape**, and compare with §3.3's declared code echo | equal | `DOCUMENT_CHECK` |
| V-12 | **Reachability and consumer closure** | every §13.1 row has a non-empty `Reachable because` cell; every field declared in §7.2, §7.3, `TABLE-S4-A2R-M1R-ECHO-SCHEMA`, the closed §8.2 primitive schema, §9.7 and §12.4 names a predicate or stage obligation. Require the S4 echo schema to bind exclusively to P25; its conditional baseline fields obey active-state presence/absence. `S3.target_safety_validation_ref` resolves to P24; `S3.argv` to N2 plus P18a/P18b; all five N4a primitive fields bind to their named obligations/consumers; every §3.1 node names ≥1 consumer | zero empty/unbound fields; exact S4 conditional schema binding; all N4a primitive fields bound; zero nodes without consumer | `DOCUMENT_CHECK` |
| V-13 | Verification-check count self-consistency | mechanically count the `V`-rows of §15 and compare with §3.3's declared check echo | equal | `DOCUMENT_CHECK` |
| V-14 | Tier-1 gate and adversarial-row count self-consistency | mechanically count the data rows of `TABLE-TIER1-GATE` and `TABLE-TIER1-ADVERSARIAL-MATRIX`; compare both with §3.3 echoes; require every explicit Revision-18 resolver-hop, M1R-wrapper, native-parser-entry and Census-transition falsifier plus all preserved stable-census/Header64 falsifiers; count all eight rows of `TABLE-MACHO-HEADER64-V1`; additionally require exactly one numeric-policy adversarial fixture for every numeric policy row plus the three unknown/parser-knowledge cases; derive the accepted numeric set (`DEPENDENCY_EDGE` + `SUPPORTED_NONEDGE`) and require exact set equality with `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1`; require exactly one structural fixture-family row per accepted value | both declared counts equal; Header64 rows = 8; required RR17 closure falsifiers present; numeric-policy fixture equality; accepted-policy↔structure-row↔structural-fixture bijection | `DOCUMENT_CHECK` |
| V-15 | Table count self-consistency | mechanically count the load-bearing machine-readable tables named in §17, including `TABLE-TIER1-ADVERSARIAL-MATRIX` and `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1` | equal to §3.3's declared echo | `DOCUMENT_CHECK` |
| V-16 | **`S7`/`S9`/`S13` topology and self-identity** | `parent(S9) = S7`, `parent(S13) = S9`, the three `git diff --diff-filter=MDRT --name-only` ranges are empty, and **no path inside `B`'s tree carries `B`'s commit SHA or tree SHA**; those values appear only in `S10` | empty for all three ranges; zero self-reference in `B` | `MACHINE_REQUIRES_TIER1` |
| V-17 | **Reference-resolution model** | §9.4 declares exactly four reference classes/arms; arm (c) alone resolves commit/tree identities; arm (d) derives the six-element authority tuple under §7.2, with `commit_id=base_controller_commit`, deterministic `strict_ancestry`, exact `commit_id:repository_path` bytes/blob and P17 digest. No commit is resolved as a file and no fifth class exists | four classes; deterministic arm-(d) values; exact byte/digest binding; no fifth class | `DOCUMENT_CHECK` |
| V-18 | **Verifier-derived security truth is not producer-selectable** | inspect schemas/fields/graph/predicates for zero selectors over OD-1/B1/expected policy/canonical roles/seed membership/cardinality/family/order/optional registry/M1R baseline/parser policy/P20/oracle. Require exact A2R constants + M1R owner token; exact base/venv/keg-root rules; `PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`; `PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1=32` with exact cycle/hop-limit precedence; project-writer quiescence; exact two-census namespace/classification/native-digest stability; Census-A byte provenance; exact `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` ↔ `MACHO_NATIVE_CONTAINER_PARSE_V1` layering; lock-vs-closure semantic separation; closed exact-key S4 schema; exact container/subtype table; exact `TABLE-MACHO-HEADER64-V1` and offset-32 command anchor; exact numeric load-command table with default reject at parser entry; one-to-one accepted-command structural table; preserved context fixed point/domain/system/optional/de-dup/family/order/privacy. Require every §14.2.1 attack | zero producer/runtime security selectors; exact owner-approved constants; baseline not fabricated; canonicalization total by project bound; ordinary-file/native-parser classification single-valued; zero producer-authored population/oracle/profile; Census-A bytes remain governing after stability check | `DOCUMENT_CHECK` |
| V-19 | **Successor authority, owner-decision binding, Mode-A design-record binding and runtime-policy separation** | candidate-lineage: new Revision-18 ruling formal table and canonical JSON projection have exact typed equality and `supersedes` root. Separately pinned: resolve Option-A, A2R and M1R owner decisions plus RR17-1/RR17-2/RR17-3 and moderator at explicit immutable commit/path/blob tuples. Future: §7.2/P19(d) resolves only the integrated Revision-18 ruling from future controller evaluation. Profile-freeze authorization, owner pinning and runtime policy remain separate acts | formal/projection equality; all three owner tuples + RR17 tuples resolve; future-controller substitution prohibited; no profile-freeze/runtime-policy/baseline conflation | `DOCUMENT_CHECK` |
| V-20 | Placeholder scan | normative closed token set: `UNFILLED_WORK_MARKER_TOKENS = {TODO, TBD, FIXME, XXX}`. Run a deterministic literal-token scanner with each of those four tokens supplied as a separate pattern argument, plus the empty-heading test. The scan domain is this document's text **excluding the whole of this row's own cells**, because this row necessarily declares the tokens. A heading is empty only when followed by no paragraph before the next heading at the same or shallower level | zero occurrences of any member of `UNFILLED_WORK_MARKER_TOKENS` outside this row's own cells; zero empty headings | `DOCUMENT_CHECK` |
| V-21 | **Phase-correct authority immutability and frozen-plan preservation** | re-resolve candidate-lineage contracts/C²/frozen plan/historical design/root/B+D1/Rev8/Rev11/Rev12/Rev13/Rev14/Rev15/Rev16/Rev17/new Rev18 ruling from the candidate SHA; resolve Option-A/A2R/M1R owner decisions and RR17 reviewer/moderator evidence only at separately pinned immutable tuples; verify formal supersession/projection equality. Do not derive future `base_controller_commit` or require the current pre-integration controller to contain the new ruling | all candidate and pinned objects match correct domains; frozen plan remains `827ad4e19f56812562dc93376a36f33204800a8d`; no candidate/reviewer/moderator/owner-decision commit substitutes for future controller | `DOCUMENT_CHECK` |

**Honest limits.** The `DOCUMENT_CHECK` class verifies this specification's internal consistency; it is
not a runtime certification. `V-16` requires the §14.2 capabilities and was **not** executed. `V-20`
cannot be satisfied by the repository's implemented secret scan, which matches credential shapes only; the
personal-value class is a forward-compliance obligation whose historical occurrences are disclosed in
§12.6 rather than claimed clean. Because revision 1 shows that a count check can pass while the invariant
it names is falsified, `V-4` and `V-5` are bound to `TABLE-EDGES` — the sole graph of record — and not to
prose "consumed by" cells. Every row of `TABLE-VERIFICATION-CHECKS` whose subject is a table is bound to
**that table by identity**, and every count-bearing row (`V-1`, `V-2`, `V-3`, `V-4`, `V-6`, `V-8`,
`V-11`, `V-13`, `V-14`, `V-15`) **re-counts the table it names** and compares the result with §3.3's
echo. A row whose method cannot produce its expected result is not admissible; `V-9` carries no
token-shape literal, and `V-10`'s expected result is produced by the corrected `P22`/`P23` model, so no
row of this table makes a claim its own instrument cannot derive.

---

## 16. Historical finding coverage

The full 227-row matrix is **referenced, not copied**:
`docs/agent-runs/run-20260920-gate0-recovery-evidence-architecture-reset/lanes/LANE-F-findings-matrix.md`.
It is **referenced evidence only**, and it is **not** an input to any normative set-algebra instrument of
this specification.

| Class | Representative members | Structural rule in this revision |
|---|---|---|
| **RC-A** — unbounded artifact-graph coupling | `MC-1`; `MB-1`, `RD-7`, `E-33`; `CY-2`…`CY-6` | `I-1` (dependency rank discipline) realised by `TABLE-EDGES`, and `I-2` (same-rank independence) realised by `TABLE-NONEDGES`; the anchor set is a verifier constant (`I-3`); no separate anchor artifact (§3.2) |
| **RC-B** — mutation-after-freeze via hybrid artifacts | `MC-2`; `MB-4`, `RD-2` | `I-4`, `I-5`, `P18a`–`P18c`, `P21`; the additive chain `S7` ≺ `S9` ≺ `S13` (§9.6) |
| **RC-C** — producer election of a security branch | `MC-3`; `O-14`/`O-15` write-only fields | **Structurally eliminated**: OD-1(b) is fixed by current design authority and there is no runtime branch to elect. §2.3 excludes selector machinery, `I-6` states the property, and P1/P2 bind authority values while P7 derives policy truth independently |
| **RC-D** — a record asserts completeness it lacks | `MC-4`, `MC-5`; `MB-1`, `MB-2`, `R1-BLOCKER-1` | The two deterministic closure domains of §16.2 with a declared normalization key — the instrument is the **membership check over two finite literal sets run against this run's ledger**, as §16.2's own text states, and it is deliberately **not** a row of `TABLE-VERIFICATION-CHECKS`; §13.2 refuses the false single-stage invariant; §15 labels every check's class and refuses results it cannot produce |
| **RC-E** — descriptive-artifact creep | cumulative | §17 line and scope discipline; historical artifacts referenced rather than reproduced |

### 16.1 Explicit accounting for `MC-1`…`MC-5` and `N-12`

| Finding | Disposition in this revision |
|---|---|
| `MC-1` — the mutual digest cycle made the anchor uncreatable | **Structurally eliminated**: the separate anchor artifact is dropped, the anchor set is a verifier constant, and the edge table forbids the edge (§3.2, §4.4, §4.6) |
| `MC-2` — a frozen manifest re-verified after a hybrid artifact was rewritten | **Structurally eliminated**: no in-anchor manifest, no hybrid path, additive chain checked per hop (§3.2, §9.6, `I-4`, `I-5`, `P18a`–`P18c`, `P21`) |
| `MC-3` — the branch selector was producer-authored and bound by nothing | **Structurally eliminated in this revision**: the runtime selector, owner-ruling artifact, delta artifact and branch resolver do not exist. `OD_1_B_ONLY` is design-fixed, historical B1 is not a future predicate, and `VERIFIER_DERIVED_ENTITLEMENT_POLICY_CLOSURE_V1` is verifier-derived (`I-6`, `P7`, `P1`, `P2`) |
| `MC-4` — a reported finding had no disposition while two surfaces asserted completeness | **Handled by two explicitly enumerated closure domains** with a declared normalization key (§16.2), not by a literal-identifier grep and not by an unbounded historical union |
| `MC-5` — a false "exactly one canonical stage" assertion with a recorded `PASS` | **Not inherited and repaired**: many-to-many stage evaluation is declared intentional, `V-10` forbids describing a `MACHINE_REQUIRES_TIER1` predicate as enforced, every count-bearing check re-counts its own table, and `V-4`/`V-5` use the sole graph of record (§13.2, §15) |
| `N-12` — identity-code ambiguity | **Structurally resolved**: one identity concept, `GENERATION_IDENTITY_COLLISION`, defined in §13.1 and evaluated at `N2` by `P2`; generation-namespace reuse is now used only for the Revision-15 run-scoped-venv binding and fails under P25/P2 without creating a second identity concept or failure code |

### 16.2 Deterministic closure domains

This specification defines **exactly two** closure domains, both explicitly enumerated, with a declared
normalization key. **Neither is a union over historical review comments**, and the 227-row matrix is not
an input to either.

| Domain | Definition | Members | Normalization key | Disposition duty |
|---|---|---|---|---|
| **`PRIOR_MATERIAL_SET`** | exactly the `P-MB-1`…`P-MB-18` groups enumerated in the named final-review closeout `docs/audits/2026-09-20-gate0-recovery-evidence-dag-spec-final-review-closeout.md` | exactly **18** | the literal `P-MB-<n>` identifier of that closeout | the remediation run ledger disposes **every** member |
| **`CURRENT_REMEDIATION_SET`** | exactly the `MB-1`…`MB-13` material blockers enumerated in the named revision-2 closeout `docs/audits/2026-09-20-gate0-recovery-evidence-dag-spec-revision-closeout.md` | exactly **13** | the literal `MB-<n>` identifier of that closeout | the remediation run ledger disposes **every** member |

The closure requirement is: **every member of both domains carries exactly one disposition row** in the
remediation run ledger, and no disposition row names an identifier outside the two domains. The
instrument is a **membership check over two finite literal sets**, not a set difference over an unbounded
comment universe; it is therefore deterministically runnable by inspection of two named documents and one
ledger, and its normalization key is the identifier literal itself. Lane-local finding identifiers from
historical review memos are **not** normalized, **not** unioned, and **not** required to appear.

---

### 16.3 RR13 successor closure

| Finding | Status | Revision-14 author-side design disposition |
|---|---|---|
| `RR13-3-AD-01` | `CLOSED_IN_CANDIDATE` | M1R owner authority defines `PYTHON_BASE_RUNTIME_ROOT_V1`, eligible run-scoped venv conditions, bounded `PYTHON_NATIVE_RUNTIME_CLOSURE_V1` membership/serialization/profile identity, lock-vs-closure semantics and the future-baseline lifecycle; current baseline remains `NOT_OBSERVED` and Generation B blocked (§7.4, §12.2.1) |
| `RR13-3-AD-02` | `CLOSED_IN_CANDIDATE` | M1R defines `HOMEBREW_FFMPEG_KEG_ROOT_V1` as the canonical shared `/opt/homebrew/Cellar/ffmpeg/<keg-id>` containing exact frozen FFmpeg/FFprobe paths while retaining every A2R version/architecture/digest check (§12.2.1) |
| `RR13-3-F01` | `CLOSED_IN_CANDIDATE` | `TABLE-S4-A2R-M1R-ECHO-SCHEMA` is closed and typed; active-state required fields, conditional digest/count absence/presence, extra security fields, wrong type and conflicts fail P25; echoes remain non-authoritative (§7.4) |
| `RR13-4-F01` | `CLOSED_IN_CANDIDATE` | `TABLE-MACHO-CONTAINER-SLICE-POLICY` enumerates V1 magic/endianness, validates the complete fat table/ranges/overlap/alignment, accepts only raw ARM64 subtype 0 or 1 with no feature bits, requires exactly one supported arm64 slice and forbids parser preference (§12.2.2) |
| `RR13-4-F02` | `CLOSED_IN_CANDIDATE` | `TABLE-MACHO-LOAD-COMMAND-POLICY` owns exact uint32 dispositions; every absent numeric value is `REJECT_UNSUPPORTED` regardless of parser/header knowledge or `LC_REQ_DYLD`; every table row has a Tier-1 fixture (§12.2.2, §14.2.1) |
| `RR13-2-N01` | `CLOSED_IN_CANDIDATE` | historical Revision-13 author memo remains unchanged; Revision 14 carries a freshly derived adversarial-row echo bound to V-14 and does not inherit 73 (§3.3, §14.2.1, V-14) |

RR13-1 PASS and RR13-2 PASS are not reopened. RR13-4's independently closed context-sensitive
`@executable_path`, `@loader_path`, `@rpath`, fixed-point, one-image TOCTOU/materialization,
system-domain, empty optional registry, global de-dup/family/order and privacy/later-audit surfaces remain
normative. Those rows preserve the historical Revision-14 author-side dispositions. Independent RR14 review is now durable evidence; the six resulting blockers and their Revision-15 candidate closures are stated in §16.4. Revision 16 preserves those surfaces without certifying them.

### 16.4 RR14 independent-review closure

The six rows below are the complete Revision-15 remediation set adjudicated by the RR14 moderator. These
are author-side candidate dispositions, not independent certification.

| Finding | Status | Revision-15 candidate closure |
|---|---|---|
| `RR14-2-F01` | `CLOSED_IN_CANDIDATE` | exact P2-derived `GENERATION_NAMESPACE_V1` and `RUN_SCOPED_VENV_ROOT_V1`; exclusive verifier reservation; collision/reuse/symlink/wrong-root fail-closed law |
| `RR14-2-F02` | `CLOSED_IN_CANDIDATE` | exhaustive lstat-first recursive enumeration of every entry beneath both real roots; no suffix/package/known-directory/host-discovery shortcut |
| `RR14-2-F03` | `CLOSED_IN_CANDIDATE` | disjoint/non-nested canonical roots; directory-symlink failure; target-owning scope for file symlinks; alias collapse; exact UTF-8/no normalization/no case fold |
| `RR14-2-F04` | `CLOSED_IN_CANDIDATE` | exact two-state S4 key sets; every undeclared/duplicate/alias/missing/wrong-type/conflicting member fails; baseline digest/count exact conditional presence |
| `RR14-3-F01` | `CLOSED_IN_CANDIDATE` | complete FAT32/FAT64 outer grammar, mathematical-integer arithmetic, metadata disjointness, nonzero slices, opaque unrelated payloads, allowed gaps/trailing bytes, selected-arm64 inner/outer equality |
| `RR14-3-F02` | `CLOSED_IN_CANDIDATE` | project-owned one-to-one accepted-command structure table; exact command formulas/string/padding/global-region law; external-reference policy A stated per applicable row; parser defaults non-normative |

`NEEDS_NEW_OWNER_DECISION` rows: none. The moderator expressly classified all six as closure inside
existing authority.

### 16.5 Revision-15 pre-review mechanical correction

| Finding | Status | Revision-16 candidate disposition |
|---|---|---|
| `PR15-F01-ADVERSARIAL-ROW-COUNT-SELF-INCONSISTENCY` | `CLOSED_IN_CANDIDATE` | `V-14` re-counts the finished successor's complete adversarial table through its table boundary and compares that fresh result with §3.3; the stale Revision-15 echo is not inherited. The adversarial rows themselves are preserved. |

This is an author-side mechanical correction only. It is not independent certification of the Revision-15
substantive closure surfaces and creates no new architecture, implementation, runtime, profile-freeze or
execution authority.

### 16.6 RR16 independent-review remediation

RR16-1 independently passed the Revision-16 authority/C²/mechanical/evidence-lifecycle surfaces. RR16-2
and RR16-3 identified exactly the three moderator-accepted material specification-closure findings below.
These are author-side Revision-17 candidate dispositions, not independent certification.

| Finding | Status | Revision-17 candidate closure |
|---|---|---|
| `RR16-2-F01` | `CLOSED_IN_CANDIDATE` | `PATH_CANONICALIZATION_V1` defines a total finite result partition for every encountered symlink, explicit cycle detection by repeated symlink pathname identity, deterministic dangling/canonicalization-failure outcomes, and fail-closed unsupported/directory behavior before the existing regular-file cross-root law. |
| `RR16-2-F02` | `CLOSED_IN_CANDIDATE` | `PYTHON_NATIVE_CLOSURE_STABLE_CENSUS_V1` requires project-writer/verifier quiescence, two complete namespace censuses, exact namespace equality, native-classification/digest stability, and downstream reuse of Census-A immutable native bytes; transient census material is not retained and no atomic-snapshot/full-supply-chain claim is made. |
| `RR16-3-F01` | `CLOSED_IN_CANDIDATE` | `TABLE-MACHO-HEADER64-V1` owns all eight little-endian 32-byte header fields, exact raw-field behavior, mathematical `32 + sizeofcmds` bounds, standalone/FAT-local origins, and the exact offset-32 command walker used by M1R and dependency parsing. |

`NEEDS_NEW_OWNER_DECISION` rows: none. No row changes Option A, A2R, M1R or C².

### 16.7 RR17 independent-review convergence and Revision-18 closure

RR17-1 independently passed the Revision-17 formal-authority/C²/mechanical/evidence-lifecycle surfaces.
RR17-3 independently passed the complete Header64/native-parser structural surface. RR17-2 identified
exactly the two moderator-accepted material specification-closure findings below. These are author-side
Revision-18 candidate dispositions, not independent certification.

| Finding | Status | Revision-18 candidate closure |
|---|---|---|
| `RR17-2-F01` | `CLOSED_IN_CANDIDATE` | `PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1 = 32` is project-owned; every invocation starts at zero, checks the ceiling before target expansion, increments before repeated-pathname evaluation, returns `SYMLINK_CYCLE` for a repeat before the ceiling, and returns exact `CANONICALIZATION_FAILURE_HOP_LIMIT` instead of performing expansion 33. Host `MAXSYMLINKS`/realpath/ELOOP/library limits are non-authoritative. |
| `RR17-2-F02` | `CLOSED_IN_CANDIDATE` | `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1(bytes)` is the sole Census-A/B arbitrary-file classifier: <4 or unlisted first four bytes ⇒ `NON_NATIVE`; listed reject or malformed listed-supported candidate ⇒ `UNSUPPORTED_MACHO_CANDIDATE`; valid listed-supported candidate ⇒ `NATIVE_MEMBER`. `MACHO_NATIVE_CONTAINER_PARSE_V1(bytes)` remains the fail-closed native parser where unlisted/rejected encodings ⇒ `REJECT_UNSUPPORTED`. |

No row changes Option A, A2R, M1R or C². RR17-2's already-closed directory/file-symlink scope,
project-writer quiescence, namespace-row grammar, Census-A/B equality, native-byte stability, post-census
Census-A immutable-image binding, privacy/non-retention, producer non-selection and baseline honesty are
preserved. RR17-3's eight-row Header64 grammar, FAT grammar, numeric/structural command grammar and
same-byte semantics are unchanged.

### 16.8 Revision-18 author-side Six-Cycle final refinement

The checks below are author-side specification verification only. They do not certify implementation,
authorize runtime work, or substitute for fresh independent Revision-18 review.

**1. FACTUAL.** Re-resolve the exact Revision-17 subject/spec/ruling, all three RR17 reviewer tuples,
moderator convergence, Option-A/A2R/M1R owner tuples, C² blob and frozen implementation-plan blob. The
Revision-17 freeze record remains later metadata and is not candidate ancestry.

**2. CONSISTENCY.** Cross-check the 32-hop resolver contract, stable-census transition law, ordinary-file
wrapper/native-parser separation, Domain P, closed container/Header64/FAT/load-command grammar, Tier-1
matrix, P19/P20 and the Revision-18 ruling projection.

**3. CONTRACT.** Require zero new DAG nodes, retained census artifacts, P19 classes, P20 modes, predicates,
global failure-code families, runtime selectors or profile-freeze authority; preserve the narrow M1R
permission-shaping scope and the unchanged frozen implementation plan.

**4. EXPERIMENTAL VALIDITY.** Synthetic path/byte/census fixtures are future Tier-1 capability tests only.
They are not `MEASURED` profile-freeze evidence, a future owner-pinned baseline, a Generation-B event or
runtime authority.

**5. PROVENANCE / SAFETY.** Falsify endless fresh symlink observations, attempted expansion 33, a repeat
before the ceiling, host-limit substitution, ordinary Python/JSON/ZIP bytes, unknown/future native magic,
malformed supported magic, classifier/parser disagreement, Census classification/digest transitions and
baseline fabrication.

**6. HANDOFF / CONVERGENCE.** Exactly the two RR17 findings have one candidate disposition:

| Finding | Final author status |
|---|---|
| `RR17-2-F01` | `CLOSED_IN_CANDIDATE` |
| `RR17-2-F02` | `CLOSED_IN_CANDIDATE` |

**Fresh Revision-18 mechanical derivation.** These are derived echoes of the normative tables/sets, not
replacement authority:

| Quantity | Fresh derived value |
|---|---:|
| Nodes | **12** |
| Conditional nodes | **0** |
| Stages | **9** |
| Sub-stages | **5** |
| Rank groups | **10** |
| Dependency edges | **28** |
| Equal-rank non-edges | **3** |
| Predicates | **29** |
| Failure codes | **29** |
| Verification checks | **21** |
| Tier-1 gate rows | **21** |
| Tier-1 adversarial data rows | **316** |
| Load-bearing tables | **14** |
| P19 reference classes | **4** |
| P20 retention modes | **2** |
| Mode-B keys | **2** |
| Numeric load-command policy rows | **54** |
| Accepted load-command values | **43** |
| Load-command structure rows | **43** |
| Header64 rows | **8** |

Fresh set derivation gives
`accepted numeric set == structural-validator numeric set`, with zero duplicates and empty differences in
both directions. The Revision-18 additions therefore change only the legitimate adversarial-matrix row
echo (Revision 17 had 289); they do not change the 54/43/43 command closure or eight-row Header64 grammar.

`PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`.

`GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`.

`OPTIONAL_TOOL_SEED_REGISTRY_V1 = []`.

`C2_AMENDMENT_REQUIRED = NO`.

## 17. Scope, size discipline, and disposition

**Line budget, stated honestly.** The target for this revision is **600–900 lines**. This revision's frozen
artifact is **longer than that target**, and this section does not claim otherwise. The overage is
deliberate and is recorded as a justified exception in this run's ledger; the exact line count is a
**measurement of this revision's frozen artefact**, recorded there and in the turn's closeout, and is
deliberately **not** asserted here, because a later edit could falsify a literal. The reason for the
overage is structural rather than narrative: the load-bearing content is the set of machine-readable
tables enumerated in the directory below; that directory is the authority for the count, §3.3 echoes it and
`V-15` re-derives it from the directory itself, and the count is deliberately **not** restated here. Those
tables are precisely the closure surface that the `P-MB` and `MB` groups require.

**Table directory — the authority for §3.3's load-bearing-table echo.** Each row names one stable table
identity. `V-15` counts the rows of this directory and compares the result with §3.3's declared echo; the
row counts of the individual tables are **not** restated here. **Section numbers are navigational prose,
not authority.** The `Section (navigational)` column of this directory, and an inline section number
written beside a table identity elsewhere in this document, are navigational aids only: they are **not**
themselves authority, they may drift as the document is reorganised, and no closure duty attaches to them.

| Stable table id | Table | Section (navigational) |
|---|---|---|
| `TABLE-NODES` | artifact-model node table | §3.1 |
| `TABLE-STAGES` | the stage table and the sub-stage table | §4.1, §4.2 |
| `TABLE-EDGES` | dependency edge table — the sole graph of record; realises invariant `I-1` | §4.4 |
| `TABLE-NONEDGES` | declared non-edges at shared ranks; realises invariant `I-2` | §4.5 |
| `TABLE-PREDICATES` | predicate table | §5.2 |
| `TABLE-CODES` | failure vocabulary | §13.1 |
| `TABLE-TIER1-GATE` | the `N8` required Tier-1 implementation phase | §14.2 |
| `TABLE-S4-A2R-M1R-ECHO-SCHEMA` | exact typed non-authoritative S4 A2R/M1R echo schema | §7.4 |
| `TABLE-MACHO-CONTAINER-SLICE-POLICY` | closed Mach-O container encoding / ARM64 slice policy | §12.2.2 |
| `TABLE-MACHO-HEADER64-V1` | exact project-owned selected-thin 64-bit Mach header grammar and command-region anchor | §12.2.2 |
| `TABLE-MACHO-LOAD-COMMAND-POLICY` | closed project-owned numeric load-command dispositions | §12.2.2 |
| `TABLE-MACHO-LOAD-COMMAND-STRUCTURE-V1` | one-to-one structural validators for every accepted numeric command | §12.2.2 |
| `TABLE-TIER1-ADVERSARIAL-MATRIX` | deterministic M1R/parser/context/TOCTOU/domain/optional/inventory/oracle falsifiers preserved from Revision 15 | §14.2.1 |
| `TABLE-VERIFICATION-CHECKS` | verification checks | §15 |

Compressing the load-bearing tables into prose is the exact defect `P-MB-3` identified, where a
"consumed by" cell could not be resolved by the check that named it. Prose has been reduced to the
minimum that keeps each table interpretable; `RC-E` (descriptive-artifact creep) is addressed by **not**
embedding the 227-row finding matrix, the historical certification transcripts, the owner-decision texts,
or any repeated evidence narrative — all are referenced by path and blob. Historical runtime OD-1 branch machinery remains absent — the conditional S5/S6 ruling/delta nodes are not defined. Current `OD_1_B_ONLY` is fixed by design authority and needs no runtime selector. The design-authority, verifier-derivation, privacy-disclosure and closure-domain text remains present. The predicate and failure-code deltas are
**not** restated here: they are derived from `TABLE-PREDICATES` and `TABLE-CODES`, and the revision-2
comparison is recorded in §13.1 and in the run ledger. The net line delta against revision 2 is likewise
recorded in the run ledger, not asserted here. **Nothing in this paragraph is a changed-section list**; it
names no revision-7 edit, and §1.1's history policy governs.

A future revision **must not add a node, a stage, a rank, a predicate, a code, a check or a gate row
without naming what it replaces, or why the addition is necessary.**

The Revision-18 RR17 final specification-closure successor **author-side** terminal disposition is recorded outside this self-identifying artifact in this run's author-verification / candidate-freeze evidence. Its permitted author outcomes are `READY_FOR_INDEPENDENT_REV18_REVIEW`, `REV18_REMEDIATION_NOT_CLOSED`, or `NEEDS_NEW_OWNER_DECISION`. A frozen review candidate is still
**not independently certified**, does not become owner-approved for implementation by being frozen, and
does not authorize plan writing or runtime execution.

**This specification does not authorize implementation, does not invoke plan writing, and is not a
certification.**
