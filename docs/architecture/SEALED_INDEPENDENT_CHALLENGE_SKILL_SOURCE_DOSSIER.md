# Sealed Independent Challenge & Cross-Audit — Skill Source Dossier

**Status:** source dossier for future skill authoring — **NOT** a deployed skill, NOT a governing workflow, NOT implementation authorization  
**Repository role:** durable design/lessons input for future cross-project skill creation  
**Origin:** Video Intelligence Pipeline Gate-3 recovery experiment, September 2026  
**Intended portability:** this repository first, then other repositories/projects after skill validation  

---

## 0. Why this file exists

This document captures the reusable method learned from a high-risk engineering recovery experiment. Its purpose is **not** to preserve the detailed Gate-3 technical findings. Those already exist in their own audit and reconciliation artifacts. Its purpose is to preserve everything a future skill author needs in order to turn the successful method into a reusable, tested skill without accidentally reintroducing the parts that were slow, unsafe, redundant, or misleading.

The future skill should help an agent answer questions such as:

- When ordinary implementation/review has stalled, when should an independent challenge workflow be activated?
- When is a second full implementation useful, and when is a targeted challenger better?
- How should multiple reviewers be kept independent long enough to generate genuinely new evidence?
- How should staged unblinding work?
- How should disagreements be resolved without majority voting?
- How should the workflow avoid infinite reviewer loops?
- How should reasoning-heavy work and expensive runtime work be separated?
- How should Git or another durable evidence store be used so that every candidate and report is attributable to an immutable state?
- When should the process stop, escalate to an arbiter, defer to runtime evidence, or ask the owner for a decision?

This dossier intentionally contains positive lessons, negative lessons, anti-patterns, rationale, examples, and candidate future designs. A future `SKILL.md` should be much shorter and should distill only the behavior that survives RED–GREEN–REFACTOR testing.

---

# 1. Executive summary of the proven method

The experiment demonstrated that a useful high-risk review pattern is:

1. preserve the strongest existing implementation as a **primary candidate** rather than starting over;
2. create an **independent targeted challenger** focused on the highest-risk residuals rather than automatically duplicating the whole system;
3. freeze both candidates at exact immutable revisions;
4. run two independent auditors with different information histories:
   - one **context-rich auditor** that knows the project history;
   - one **cold auditor** that starts from current authority and code without inheriting prior conclusions;
5. keep the auditors sealed from each other's findings while each produces its own baseline triple:
   - Candidate A only;
   - Candidate B only;
   - A-vs-B comparison;
6. only after both baseline triples are frozen, perform **staged unblinding**;
7. allow exactly one reciprocal cross-review generation;
8. reconcile findings using authority and direct evidence, **not reviewer voting**;
9. produce a bounded repair/adoption packet and explicit owner checkpoint;
10. only after static repair, spend scarce runtime/API/local-machine budget on the minimum remaining evidence questions.

The strongest practical outcome was not “which agent won?” It was a **confidence map**:

- which substrate was worth keeping;
- which defects were real;
- which challenger contributions were safe to adopt;
- which challenger contributions were themselves unsafe;
- which tests were genuinely discriminating;
- which issues were statically resolvable;
- which issues truly required runtime evidence;
- what exact bounded repair package should be implemented next.

---

# 2. The original problem pattern

The method emerged because normal development had become stuck in a high-risk area.

The important problem symptoms were generic, not Gate-3-specific:

- substantial implementation work already existed;
- repeated review found problems but did not yield a trustworthy end state;
- test suites could be GREEN while the evidence chain still contained false-GREEN paths;
- restarting the entire subsystem would have thrown away useful work;
- simply asking another reviewer to “check it again” risked repeating the same assumptions;
- runtime validation was more scarce/costly than static reasoning;
- the owner wanted stronger assurance before allowing integration or expensive execution;
- repository state was complex enough that chat-only reasoning would not be durable evidence.

This is the target problem class for the future skill.

The future skill should **not** be triggered merely because a task is difficult. It should be triggered when the combination of **risk + uncertainty + sunk implementation value + repeated stall or false-GREEN concern** makes ordinary single-path review insufficient.

---

# 3. What happened in the proving experiment — abstracted chronology

The following chronology is included because a future skill author needs to understand why each protocol rule exists. It is intentionally abstracted away from most Gate-3 implementation details.

## 3.1 Existing coordinator/executor path had accumulated useful work but stalled

A pre-existing coordinator and executor path had already produced a large implementation plan, prototypes, synthetic evidence, and a substantial candidate. This was not worthless work. However, repeated review exposed defects and the process was no longer converging efficiently.

**Lesson:** when a project has a large body of reusable engineering, the default should not be “start over independently.” The workflow should preserve sunk value unless evidence shows the base is unsalvageable.

## 3.2 Candidate A was built as a reuse-first full-system substrate

A context-rich ChatGPT path reused prior work and materialized a broad Candidate A rather than restarting Gate 3 from first principles.

Candidate A later proved to be:

- substantial;
- structurally reusable;
- not safe to accept unchanged.

Its tests were broadly GREEN, yet independent audits still found load-bearing semantic, evidence-binding, schema, QC, and end-to-end gaps.

**Lesson:** high test counts do not substitute for adversarial authority review. “GREEN” is evidence about the tested behavior, not proof that the right behavior was tested.

## 3.3 Candidate B was created as a targeted challenger, not a second full implementation

A fresh session was assigned a narrow challenger role. It independently attacked the highest-risk residuals and implemented/tested alternative handling for those seams.

This asymmetric design was highly productive. Candidate B:

- found safer fail-closed behavior in some areas;
- contributed useful adversarial tests;
- contributed useful durability/binding ideas;
- did not need to recreate the whole subsystem;
- also contained defects of its own.

**Lesson:** a challenger should normally challenge assumptions and dangerous seams, not duplicate every file of the base candidate.

## 3.4 Both candidates were frozen before audit

Candidate implementations were pinned to exact implementation SHAs. Separate documentation-only freeze records captured provenance without changing implementation semantics.

**Lesson:** reviewers must audit immutable candidates. “Latest branch head” is not a stable experimental object.

## 3.5 Two independent auditors were used

The experiment deliberately combined two different reviewer profiles:

- **Context-rich Master Auditor:** knew the long project history and therefore had strong architectural context, but was potentially vulnerable to anchoring on previous project conclusions.
- **Cold Code Auditor:** approached the frozen candidates without prior Master findings, reducing anchoring but lacking some long-history context.

This combination produced real value. Each auditor found material issues the other had initially missed.

**Lesson:** independence is useful when the reviewers have meaningfully different information histories, not merely different names.

## 3.6 Auditors were sealed during baseline review

Each auditor independently completed:

1. A-only audit;
2. B-only audit;
3. A-vs-B comparison.

Neither was allowed to read the other auditor's reports until its own triple was frozen.

**Lesson:** early cross-reading destroys much of the value of a cold second opinion by creating anchoring and convergence pressure.

## 3.7 Controlled unblinding happened only after frozen baselines

After both triples were frozen, each auditor was allowed to read the other's three reports and write exactly one cross-review.

The cross-review did not edit historical reports. It created a new evidence layer.

**Lesson:** preserve baseline observations as historical evidence. Do not retroactively rewrite them after learning what the other reviewer found.

## 3.8 Cross-audit materially changed the conclusion details

The cross-audit did not overturn the broad direction, but it materially improved it.

Examples of value generated by the cross-audit:

- the cold auditor found source-authority, evidence-state, retry-identity, and resource-evidence defects the context-rich auditor had missed;
- the context-rich auditor found normative schema/QC/end-to-end omissions the cold auditor had underweighted or missed;
- the cold audit demonstrated that some challenger code initially considered reusable was itself unsafe;
- the context-rich auditor demonstrated that some issues classified as “runtime unresolved” were actually statically missing implementation and therefore should be repaired before spending runtime budget;
- the exact historical adversarial test was found to be stronger in the base candidate than in the challenger, despite the challenger having been created specifically to attack that seam.

**Lesson:** reciprocal review is not redundant when the baseline reviews are genuinely independent.

## 3.9 Final reconciliation produced composition, not a winner

The final disposition was a composition decision:

- retain the broad Candidate-A substrate;
- adopt/adapt selected Candidate-B contributions;
- reject unsafe Candidate-B contributions;
- add fresh repairs where neither candidate solved the problem;
- reduce the target-runtime matrix to a small finite set.

In the proving experiment, the final reconciliation normalized many overlapping audit findings into **15 canonical static repair items** and a compact set of runtime evidence groups.

The numeric details are not themselves generic protocol requirements. The generic lesson is that the workflow should produce a **bounded, deduplicated repair register**, not a pile of reviewer comments.

---

# 4. What worked especially well

## 4.1 Context-rich + cold review was complementary

The most important empirical success was that the cold reviewer found real problems the context-rich reviewer missed, while the context-rich reviewer found important integration/normative problems the cold reviewer missed.

This validates the use of two information-history profiles.

### Why it worked

The context-rich reviewer had advantages in:

- understanding historical architecture decisions;
- recognizing normative plan drift;
- seeing integration consequences across many components.

The cold reviewer had advantages in:

- not inheriting previous confidence;
- reading current code literally;
- questioning assumptions that had become “obvious” inside the long-running session.

A future skill should preserve this asymmetry where possible.

## 4.2 Exact immutable revisions made the experiment interpretable

Every important candidate/report was bound to an exact Git SHA. That prevented moving-target review.

Without this, statements such as “Auditor 1 found X but Auditor 2 did not” would be ambiguous because they might have reviewed different code.

A future skill should require exact immutable candidate identity. Git SHA is ideal in code repositories; another content-addressed or immutable artifact identity can substitute outside Git.

## 4.3 Durable artifacts were superior to chat-only handoffs

Audit reports were committed to the repository. Later reviewers could retrieve the exact report rather than relying on a conversational paraphrase.

This reduced:

- context loss;
- accidental summary distortion;
- dependence on the original agent remaining available;
- ambiguity about which revision of a finding was reviewed.

A future skill should prefer durable artifacts whenever the working environment supports them.

## 4.4 Targeted challenger was more efficient than duplicate implementation

Candidate B was not asked to rebuild the entire system. It focused on the most dangerous seams.

This reduced duplicated effort while still producing independent evidence.

Default future policy should therefore be:

> **Base + targeted challenger** unless there is a concrete reason that two genuinely competing full architectures need symmetric implementation.

## 4.5 Staged unblinding preserved independence without wasting reconciliation value

Permanent isolation would have left disagreements unresolved. Immediate cross-reading would have weakened independence.

Staged unblinding achieved both:

- independent discovery first;
- adversarial reconciliation second.

This is one of the most important reusable parts of the method.

## 4.6 One reciprocal generation prevented infinite review loops

The workflow allowed one Master→Cold review and one Cold→Master review, then stopped.

No review-of-review-of-review loop was allowed.

This bounded the convergence cost while still exposing disagreements.

A future skill should retain this default stop rule.

## 4.7 Evidence hierarchy prevented “two agents agree” from becoming authority

The workflow explicitly resolved disagreements using:

1. explicit owner authorization;
2. governing specifications/contracts;
3. direct exact-revision repository evidence;
4. attributable executed evidence;
5. inference.

Reviewer agreement was never treated as proof by itself.

This must be a foundational future-skill rule.

## 4.8 Static review reduced expensive runtime work

Some questions originally looked like runtime-validation questions. Cross-audit showed that the implementation was statically incomplete, so runtime testing would have been wasted until repair.

The final runtime package was therefore smaller and more targeted.

Generic lesson:

> Resolve everything that can be resolved statically before spending metered API, scarce hardware, protected-resource, or expensive local-runtime budget.

## 4.9 Composition was better than forced winner selection

The experiment did not force `A` or `B` to win globally.

It allowed results such as:

- keep A substrate;
- use B tests;
- adapt B concept;
- reject B implementation;
- fresh repair neither candidate solved;
- defer operational question to runtime.

This made the result much more useful than branch-level winner selection.

---

# 5. What was weak, costly, or risky

These are not reasons to discard the method. They are design inputs for the future skill.

## 5.1 Time cost was high

The dominant practical cost in the proving experiment was elapsed human/agent time.

There were multiple serial gates:

- candidate construction/freeze;
- A-only audit;
- B-only audit;
- A-vs-B comparison;
- reciprocal cross-review;
- final reconciliation.

In the actual environment, much of the reasoning work had low marginal monetary cost, making this trade-off attractive. That economic fact must **not** be hard-coded into the skill because product pricing, usage limits, and deployment surfaces change.

Generalizable rule:

> Route reasoning-heavy work to the lowest-marginal-cost sufficiently capable surface available; reserve metered or operationally scarce execution surfaces for questions that truly require them.

## 5.2 Manual orchestration was burdensome

The owner manually moved prompts/results between sessions and asked which stage came next.

This worked but is not ideal.

A future skill should reduce manual state tracking through a small durable workflow state such as:

- current phase;
- candidate SHAs;
- audit SHAs;
- allowed read set;
- prohibited read set;
- next legal transition;
- owner checkpoints.

Do not over-automate the owner decision points themselves.

## 5.3 Same-model correlation remains possible

Two “independent” sessions can still share:

- the same underlying model family;
- similar learned priors;
- the same authority documents;
- the same prompt framing.

Therefore independence is not equivalent to statistical independence.

The skill must never claim:

> “Two reviewers agree, therefore the answer is correct.”

It may claim only that independently isolated review paths converged on the available evidence.

## 5.4 A cold auditor can lose useful historical context

Cold review reduces anchoring but can miss why a constraint exists or underweight integration consequences.

This is why cold review should complement, not automatically replace, context-rich review.

## 5.5 A context-rich auditor can anchor on prior conclusions

Long-running coordinator sessions are useful but can inherit:

- sunk-cost attachment;
- familiarity bias;
- prior severity choices;
- assumptions that are no longer re-questioned.

A future skill should explicitly state this as the reason for a cold lane.

## 5.6 Final reconciler bias is possible

In the proving experiment, the context-rich Master Auditor performed final reconciliation. This was acceptable because the reciprocal cross-audit had already eliminated material static reviewer conflict.

This should **not** become an unconditional rule.

If material static conflict remains after reciprocal review, the future workflow should permit a **fresh arbiter** rather than automatically giving the Master reviewer the final word.

Suggested conditional:

- if reviewers converge or remaining issues are clearly runtime/owner-dependent → normal reconciler;
- if load-bearing static conflict remains → fresh arbiter from the same frozen evidence packet;
- no additional reciprocal reply loop.

## 5.7 The full protocol is overkill for small deterministic bugs

A syntax bug, isolated unit-test failure, obvious contract violation, or mechanically checkable defect should be solved by ordinary TDD/systematic debugging.

Applying the full sealed workflow to every bug would waste time and create documentation noise.

This is a major trigger-design requirement for the future skill.

## 5.8 Audit artifacts can become too verbose

Comprehensive reports are useful, but repeated restatement of the same authority or findings can consume context and reviewer attention.

Future skill should emphasize:

- frozen full reports as durable artifacts;
- compact chat handoffs;
- normalized final registers;
- no repeated narrative once an artifact is addressable by exact identity.

## 5.9 Independence can be accidentally broken

Common leakage routes include:

- letting Cold read Master report titles/counts before its own report freezes;
- including one auditor's conclusions in the other auditor's prompt;
- using shared mutable scratch documents;
- asking an agent to “continue from the other reviewer”; 
- letting a candidate self-report become audit evidence.

The future skill needs explicit sealing rules, not vague “be independent” language.

---

# 6. Terminology to use and avoid

## 6.1 Preferred term

**Sealed independent review with staged unblinding**

or, for a shorter workflow name:

**Sealed Independent Challenge & Cross-Audit**

## 6.2 Avoid calling it “double-blind” by default

The proving experiment was not a scientific double-blind trial:

- candidate identities were known;
- authority documents were shared;
- eventual unblinding was intentional;
- reviewers could often infer architectural context.

“Double-blind” may be used colloquially in explanation, but the formal skill should use the more accurate staged-unblinding terminology.

## 6.3 Candidate terminology

- **Primary candidate / Base candidate:** strongest existing implementation intended to preserve prior investment.
- **Targeted challenger:** independent alternative attack/repair implementation for selected high-risk seams.
- **Symmetric challenger:** full independent competing implementation, used only when architecture-level competition is genuinely justified.
- **Context-rich auditor:** reviewer with project-history context.
- **Cold auditor:** reviewer deliberately withheld from other review conclusions and unnecessary historical framing.
- **Reconciler:** combines frozen findings after cross-review.
- **Fresh arbiter:** optional independent adjudicator when material static conflict survives reciprocal cross-review.

---

# 7. Recommended risk-tiered operating modes

A major improvement over the proving experiment is to make the future skill risk-adaptive.

## 7.1 LIGHT mode

Use when:

- impact is moderate;
- there is one primary candidate;
- ordinary review is insufficient but there is no evidence of systemic false-GREEN behavior;
- time cost matters more than maximal independence.

Suggested shape:

1. freeze primary candidate;
2. one cold audit against authority;
3. reconcile findings;
4. repair or escalate.

No challenger and no reciprocal cross-audit by default.

## 7.2 STANDARD mode

Use when:

- risk is high;
- a reusable base exists;
- one or more dangerous seams are uncertain;
- an independent alternative implementation/test would add information.

Suggested shape:

1. freeze authority/base;
2. build targeted challenger;
3. freeze A/B;
4. context-rich audit + cold audit in parallel where possible;
5. compare A/B;
6. one reconciliation;
7. optional reciprocal review if findings materially diverge.

## 7.3 FULL SEALED mode

Use when:

- consequences of false acceptance are high;
- repeated stalls have occurred;
- tests may be false-GREEN;
- multiple evidence-authority layers interact;
- substantial sunk implementation makes restart expensive;
- runtime validation is scarce/costly;
- owner wants high assurance before integration.

Suggested shape — proven experiment:

1. freeze common authority;
2. freeze/build primary A;
3. independently build targeted or symmetric B;
4. freeze both;
5. Master A-only;
6. Cold A-only;
7. Master B-only;
8. Cold B-only;
9. Master A-vs-B;
10. Cold A-vs-B;
11. verify both sealed triples are complete;
12. staged unblinding;
13. one Master review of Cold triple;
14. one Cold review of Master triple;
15. no second reciprocal generation;
16. final evidence-based reconciliation;
17. owner checkpoint;
18. selected candidate repair/implementation;
19. selected candidate freeze;
20. minimal runtime certification.

The skill should choose the lightest mode that plausibly addresses the risk.

---

# 8. Trigger criteria for the future skill

The future skill should activate on symptoms, not project names.

Strong triggers include combinations of:

- high-impact subsystem or migration;
- repeated implementation/review stall;
- substantial existing implementation worth preserving;
- suspicion that GREEN tests do not test the actual authority requirement;
- multiple plausible implementations with unclear trade-offs;
- evidence/certification/security/safety semantics where false-GREEN is expensive;
- reviewers disagreeing about root cause or severity;
- expensive runtime validation that should be preceded by static reduction;
- integration across independently governed subsystems;
- owner explicitly requests independent/cold/cross-audit review;
- long context-rich session may be anchoring on its own previous assumptions.

Potential skill description language to test later:

> `Use when a high-risk implementation has stalled, may be false-GREEN, has competing repair paths, or needs independent evidence before integration or expensive runtime validation.`

This is a **candidate** description only. Per Superpowers skill-authoring guidance, the final description must be tested and should contain triggers only, not summarize the workflow.

---

# 9. When NOT to use the future skill

The skill should actively refuse escalation to Full Sealed when ordinary engineering is enough.

Do not use Full Sealed for:

- obvious syntax/type errors;
- a single deterministic failing test with a clear root cause;
- tiny isolated changes;
- mechanical schema/count/reference mismatches that static tooling can settle;
- tasks where no meaningful independent hypothesis exists;
- situations where the base is obviously disposable and a clean rewrite is cheaper;
- pure brainstorming before any candidate exists, unless the question itself is competing architecture validation;
- low-impact formatting/docs work;
- cases where independent reviewers would necessarily consume exactly the same conclusions and cannot be meaningfully sealed.

Default to existing workflows such as:

- brainstorming;
- systematic debugging;
- test-driven development;
- ordinary code review;
- verification-before-completion.

The future skill should **compose with** these skills, not replace them.

---

# 10. Role architecture

## 10.1 Owner

Responsibilities:

- defines authority/scope;
- approves experiment activation when required;
- approves any scope widening;
- receives final exact construction checkpoint;
- authorizes selected implementation/runtime execution.

The owner is not expected to manually adjudicate technical details unless evidence leaves a genuine owner-level choice.

## 10.2 Coordinator / experiment controller

Responsibilities:

- freezes common authority;
- assigns branches/roles;
- enforces read/write boundaries;
- verifies candidate/report SHAs;
- advances state only after durable evidence;
- does not manufacture extra work merely to fill agent capacity.

## 10.3 Primary candidate builder

Responsibilities:

- preserves/reuses strongest existing substrate;
- does not self-certify final acceptance;
- commits exact candidate implementation;
- produces a separate freeze record if needed.

## 10.4 Targeted challenger

Responsibilities:

- attacks named high-risk assumptions/seams;
- does not automatically recreate the whole project;
- produces independent code/tests/evidence where it adds information;
- explicitly distinguishes out-of-scope surfaces;
- may prove the base is stronger on some seams.

## 10.5 Context-rich auditor

Responsibilities:

- evaluates against authority, not builder claims;
- uses historical context where relevant;
- remains sealed from cold findings until its baseline freezes;
- records integration/normative issues that a narrow cold reading may miss.

## 10.6 Cold auditor

Responsibilities:

- starts from frozen authority and candidate state;
- does not read context-rich audit conclusions before its baseline freezes;
- independently tests assumptions;
- records `NOT_OBSERVED` rather than importing narrative claims.

## 10.7 Reconciler

Responsibilities:

- consumes frozen reports only after allowed unblinding;
- normalizes duplicate findings;
- resolves disagreements by authority/evidence;
- produces exact retain/adapt/test-only/reject/fresh-repair/runtime decisions;
- stops at owner checkpoint.

## 10.8 Fresh arbiter — optional

Trigger only if:

- material static conflict remains after one reciprocal cross-review generation;
- neither authority nor direct code evidence resolves it;
- the conflict is not genuinely runtime- or owner-dependent.

The arbiter gets the frozen evidence packet, not a conversational argument between auditors.

---

# 11. Independence and sealing contract

A future skill should treat independence as a concrete access-control problem.

## 11.1 Candidate freeze

Before audit:

- exact implementation revision recorded;
- freeze record, if any, must be distinguishable from implementation state;
- candidate branch must not move during sealed review;
- auditors should use exact revisions, not branch names alone.

## 11.2 Auditor sealing

Before its own baseline triple is frozen, an auditor must not consume:

- the other auditor's reports;
- the other auditor's verdict/counts;
- summaries of the other auditor's unique findings;
- prompts that leak those findings indirectly.

Shared allowed inputs:

- common authority;
- exact candidate code;
- historical evidence that predates both candidate audits;
- candidate role/scope records.

## 11.3 Staged unblinding

Unblinding is allowed only when:

- both required baseline sets are committed;
- exact report SHAs are verified;
- neither baseline is mutable.

Then reviewers may critique each other once.

## 11.4 No retroactive baseline editing

After unblinding:

- baseline reports remain immutable historical observations;
- corrections/reweighting go into cross-review or reconciliation artifacts;
- never silently rewrite history to make auditors appear consistent.

---

# 12. Evidence hierarchy and adjudication rules

The future skill should encode a hierarchy similar to:

1. explicit current owner authorization;
2. frozen governing contracts/specifications;
3. approved design/plan at the relevant authority layer;
4. direct exact-revision code/repository evidence;
5. attributable executed evidence;
6. reviewer inference.

Rules:

- reviewer confidence is never authority;
- reviewer count is never authority;
- test count is never authority;
- builder self-report is evidence only at the level actually attributable;
- a runtime claim cannot be upgraded from static inspection;
- lack of evidence must remain `NOT_OBSERVED` or equivalent project vocabulary;
- disagreement should be resolved by evidence, not majority vote;
- two differently worded findings with one root defect should be normalized into one final repair item.

---

# 13. Candidate comparison should be component-level, not winner-take-all

The future skill should encourage per-surface dispositions such as:

- `A_STRONGER`
- `B_STRONGER`
- `COMPLEMENTARY`
- `BOTH_DEFICIENT`
- `RUNTIME_UNRESOLVED`

And adoption choices such as:

- direct adoption;
- adapt before integration;
- tests only;
- design guidance only;
- reject;
- fresh implementation required;
- runtime decision required.

These labels are examples, not mandatory universal vocabulary.

The principle is mandatory:

> Compare capabilities and evidence surfaces, not branch prestige.

---

# 14. Git/durability contract

Git was a major enabler in the proving experiment because ChatGPT sessions could write and independently verify durable artifacts.

A future skill should prefer the following where available:

- exclusive writable branch per role;
- common exact authority base;
- exact immutable candidate SHAs;
- one dedicated commit per audit report;
- report read-back verification;
- compare parent→child to prove only authorized files changed;
- separate implementation SHA from documentation-only freeze SHA;
- final reconciliation records exact inputs;
- no direct canonical-main writes during experimentation unless explicitly authorized;
- selected/hybrid branch created only after owner checkpoint.

If Git is unavailable, substitute another immutable/content-addressed artifact system. The underlying requirement is **durable attributable state**, not Git branding.

---

# 15. Cost/time allocation policy

The proving experiment suggests a useful general optimization:

## 15.1 Separate reasoning cost from execution cost

Reasoning tasks:

- static audit;
- code reading;
- authority comparison;
- report reconciliation;
- test-design review;
- candidate composition.

Execution tasks:

- local machine runtime;
- expensive model/provider calls;
- large simulations;
- protected hardware/data;
- costly API validation.

Default policy:

> Spend cheap/reversible reasoning first to shrink the expensive execution frontier.

## 15.2 Product-neutral wording

Do **not** encode statements such as:

- “ChatGPT is free”;
- “Codex is expensive”;
- “DeepSeek always has more context”;
- fixed plan limits or pricing.

Those can become stale.

Instead the future skill should inspect the current environment and choose among available surfaces based on:

- marginal monetary cost;
- usage quota pressure;
- context capacity;
- repository/tool access;
- runtime access;
- required model capability;
- independence value.

## 15.3 Practical lesson from the proving experiment

In this experiment, chat-based reasoning was cheap enough that time became the primary cost, while local/runtime/API-style execution was treated as more scarce. This made a reasoning-heavy sealed audit attractive.

That is an example deployment policy, not a universal rule.

---

# 16. Why GitHub/tool access mattered

The experiment benefited from an agent surface that could:

- inspect exact repository revisions;
- create branch-scoped durable reports;
- verify commits/read-back;
- compare commits;
- keep chat summaries small.

A future skill should exploit such access when available.

Without durable repository access, the workflow can still operate, but should create equivalent immutable artifacts outside chat. A chat transcript alone is a weak long-term evidence store.

---

# 17. Anti-patterns the future skill must actively resist

## 17.1 Duplicate implementation just to create “independence”

**Bad:** rebuild the entire system with B even when A is mostly reusable.

**Why:** wastes time and makes reconciliation harder without necessarily increasing information.

**Preferred:** targeted challenger unless two genuinely competing architectures justify symmetric candidates.

## 17.2 Majority voting

**Bad:** two reviewers say X, one says Y, therefore X wins.

**Why:** correlated reviewers can share the same mistake.

**Preferred:** authority → exact evidence → execution → inference.

## 17.3 Early unblinding

**Bad:** show Cold the Master report “to save time.”

**Why:** destroys the main benefit of the cold lane.

## 17.4 Moving-target audit

**Bad:** audit “the latest branch.”

**Why:** different reviewers may inspect different code.

## 17.5 Treating builder self-report as verification

**Bad:** “Builder says 79/79 tests passed, so accept.”

**Why:** test scope may be wrong; execution may not match target environment; builder may have missed false-GREEN paths.

## 17.6 Repairing during baseline audit

**Bad:** auditor changes candidate code while discovering findings.

**Why:** destroys the frozen comparison object and contaminates later audit.

## 17.7 Infinite review recursion

**Bad:** reviewer A replies to B, B replies to A, A replies again indefinitely.

**Why:** time grows without necessarily generating new independent evidence.

**Preferred:** one reciprocal generation, then reconciliation or fresh arbiter.

## 17.8 Runtime before static closure

**Bad:** spend expensive runtime budget on code that is statically missing the required behavior.

**Why:** a green run cannot prove missing logic.

## 17.9 Treating the challenger as automatically superior

**Bad:** assume independent B must be safer because it was designed as a challenger.

**Why:** the proving experiment found important defects inside B itself.

## 17.10 Treating the base as automatically privileged

**Bad:** keep A because it is larger or has more sunk work.

**Why:** base status is not evidence. If A were unsalvageable, the workflow must be able to reject it.

## 17.11 Using Full Sealed for trivial work

**Bad:** activate five-session protocol for a deterministic one-line bug.

**Why:** ceremony becomes the dominant cost.

## 17.12 Conflating independence with different model branding

**Bad:** “different vendor/model = independent; same model = not independent.”

**Why:** independence also depends on context exposure, shared prompts, authority packet, and staged information access.

The skill should reason about **information-path independence**, not only model labels.

---

# 18. Bounded convergence rules

The future skill should be intentionally finite.

Recommended defaults:

- one candidate/challenger generation before sealed audit unless evidence requires otherwise;
- one baseline triple per auditor in Full Sealed mode;
- one reciprocal cross-review generation;
- zero iterative reply-to-reply cross-audit loops;
- one fresh arbiter only if material static conflict survives;
- one final reconciliation;
- bounded repair/certification generations, delegated to the project's governing engineering workflow.

Stop conditions should include:

### Converged with repairs

- no unresolved material static reviewer conflict;
- repair register normalized;
- runtime frontier finite;
- owner can approve one exact construction.

### Runtime resolution required

- remaining dispute cannot be settled from authority/static evidence;
- exact runtime experiment is specified.

### Owner decision required

- two authority-compatible alternatives remain and choice is policy/product preference.

### Static conflict remains

- use fresh arbiter or stop; do not fabricate certainty.

---

# 19. Six-Cycle Iterative Refinement integration

The future skill should be compatible with the project's Six-Cycle discipline but should not blindly add six verbose reports at every stage.

Use the six dimensions as a cumulative audit lens:

## Cycle 1 — Authority / traceability

Questions:

- Are all roles working from the same frozen authority?
- Are candidates/reports tied to exact immutable identities?
- Did any role exceed authorization?
- Is provenance durable?

## Cycle 2 — Implementation correctness

Questions:

- Does code implement the actual governing behavior?
- Are important semantics represented correctly?
- Are candidate comparisons fair to their authorized scopes?

## Cycle 3 — Verification / runtime / adversarial strength

Questions:

- Do tests attack the real historical failure?
- Can false-GREEN paths remain?
- Is executed evidence attributable?
- What remains `NOT_OBSERVED`?

## Cycle 4 — Architecture / integration

Questions:

- Can the contribution integrate without introducing a second authority channel?
- Are interfaces/record shapes compatible?
- Is the challenger solving the seam or merely creating a parallel subsystem?

## Cycle 5 — Repository / operational readiness

Questions:

- Are branches/commits/artifacts durable?
- Is retry/recovery behavior safe?
- Are run identities/resource claims/persistence trustworthy?
- Is manual orchestration creating avoidable error?

## Cycle 6 — Strategic refinement / next frontier

Questions:

- What should be retained, adapted, rejected, freshly repaired, or deferred to runtime?
- Is the protocol still worth its time cost?
- Can the expensive runtime matrix be reduced?
- What is the smallest next authorized step?

The final skill should use these dimensions where they add information, not as empty ceremonial headings.

---

# 20. Interaction with Superpowers methodology

This future skill should be trigger-based and compose with existing skills rather than replacing them.

Expected routing examples:

- new architecture for the candidate/challenge system → `brainstorming`;
- approved implementation design → `writing-plans`;
- isolated implementation branches/worktrees → `using-git-worktrees`;
- feature/repair implementation → `test-driven-development`;
- unexpected test/runtime failure → `systematic-debugging`;
- review feedback processing → `receiving-code-review`;
- completed work before integration → `requesting-code-review`;
- success/completion claims → `verification-before-completion`;
- creation/editing of this future skill → `writing-skills`.

The future skill should **not** require all Superpowers skills every time. It should call the relevant sub-skill when the workflow reaches that type of task.

---

# 21. Skill-authoring implications from Superpowers `writing-skills`

Superpowers treats skill creation as TDD for process documentation.

Therefore this dossier is **not sufficient by itself** to deploy a skill.

The future creation sequence should be:

## RED

1. define pressure scenarios;
2. run them **without** the skill;
3. observe actual failure modes/rationalizations;
4. save representative baseline outputs.

## GREEN

1. write the smallest `SKILL.md` that addresses the observed failures;
2. keep trigger description focused on when to use, not workflow summary;
3. run the same scenarios with the skill;
4. verify behavior changes.

## REFACTOR

1. search for new loopholes/rationalizations;
2. tighten wording;
3. retest;
4. keep the runtime skill concise; move heavy background out of the always-loaded path.

This source dossier is intentionally broad so the future author has enough material. The deployed skill should be much smaller.

---

# 22. Current external skill-format facts worth preserving

Current OpenAI skill guidance describes skills as reusable workflows centered on `SKILL.md`, optionally with supporting resources. Skills are intended to reduce repeated prompting and improve consistency across recurring multi-step work.

Current Agent Skills/Superpowers guidance also supports a portable Markdown-based skill bundle model.

Useful current references for the future author:

- OpenAI Academy — Using skills: `https://openai.com/academy/skills/`
- OpenAI Help — Skills in ChatGPT: `https://help.openai.com/en/articles/20001066`
- Agent Skills specification: `https://agentskills.io/specification`
- Superpowers `writing-skills` skill in the installed Superpowers plugin/repository.

These URLs are authoring references, not workflow authority. Re-check them when the skill is actually created because product surfaces and specifications can change.

---

# 23. Future skill type

The proposed skill is best understood as a hybrid of:

- **discipline-enforcing skill** — prevents early unblinding, majority voting, moving-target audits, infinite review loops, and premature runtime spend;
- **technique skill** — teaches how to structure A/B challenge, sealed review, cross-audit, and reconciliation;
- **pattern skill** — teaches the mental model “independent evidence paths before convergence.”

Because discipline failures are central, pressure testing is mandatory.

---

# 24. Candidate future skill names

Names should remain provisional until RED testing shows how agents search for the problem.

Candidates:

- `running-sealed-cross-audits`
- `using-independent-challenge-review`
- `reconciling-competing-candidates`
- `running-independent-challenge-audits`
- `breaking-false-green-convergence`

Current preference for clarity:

**`running-sealed-cross-audits`**

Alternative if broader than audit:

**`using-independent-challenge-review`**

Do not finalize the name before discovery/trigger tests.

---

# 25. Proposed runtime skill structure

A future concise `SKILL.md` might contain:

1. YAML frontmatter — trigger-only description;
2. Core principle;
3. When to use / when not to use;
4. mode selection: Light / Standard / Full Sealed;
5. authority freeze requirements;
6. role/access matrix;
7. staged workflow;
8. adjudication hierarchy;
9. stop conditions / arbiter rule;
10. quick reference table;
11. common mistakes / rationalization table;
12. one compact worked example;
13. required sub-skill references;
14. verification checklist.

The Gate-3 story should **not** be copied wholesale into `SKILL.md`. At most, one compact abstract example should demonstrate why staged independent review matters.

---

# 26. RED-phase pressure scenarios for future skill testing

The following scenarios are hypotheses for baseline testing. They should be run **without** the new skill first.

## Scenario R1 — deadline pressure causes early unblinding

Prompt pressure:

- two auditors exist;
- Master has already found blockers;
- Cold is still working;
- user asks to “save time” by sending Master findings to Cold.

Expected unskilled failure:

- agent leaks findings to Cold;
- independence is destroyed.

Desired skilled behavior:

- keep Cold sealed;
- let Cold finish its baseline;
- unblind only after freeze.

## Scenario R2 — sunk-cost pressure causes automatic acceptance of base

Prompt pressure:

- Candidate A is very large;
- dozens of tests pass;
- replacing it would be expensive.

Expected unskilled failure:

- reviewer minimizes structural blockers because “most of it works.”

Desired skilled behavior:

- preserve reusable substrate but still classify load-bearing defects honestly.

## Scenario R3 — challenger prestige causes automatic preference for B

Prompt pressure:

- B was created explicitly as an independent adversary;
- B has elegant fail-closed tests.

Expected unskilled failure:

- assume B is safer everywhere.

Desired skilled behavior:

- audit B independently and permit A to be stronger on some surfaces.

## Scenario R4 — duplicated full implementation wastes effort

Prompt pressure:

- A is 80% reusable;
- user requests “an independent version.”

Expected unskilled failure:

- rebuild everything as B.

Desired skilled behavior:

- propose targeted challenger unless full architectural competition is justified.

## Scenario R5 — majority vote substitutes for evidence

Prompt pressure:

- two reviewers say PASS;
- one reviewer identifies a precise authority violation.

Expected unskilled failure:

- accept majority PASS.

Desired skilled behavior:

- adjudicate the exact violation against authority/code.

## Scenario R6 — infinite review loop

Prompt pressure:

- after reciprocal cross-review, reviewer A wants to respond again to B.

Expected unskilled failure:

- allow another round.

Desired skilled behavior:

- stop; reconcile or use fresh arbiter if material static conflict remains.

## Scenario R7 — expensive runtime used before static repair

Prompt pressure:

- Mac/FFmpeg/API validation is available but costly;
- code statically lacks the required feature.

Expected unskilled failure:

- run expensive validation anyway.

Desired skilled behavior:

- repair static omission first; reserve runtime for behavior that exists.

## Scenario R8 — moving target

Prompt pressure:

- builders continue committing while auditors review branch names.

Expected unskilled failure:

- continue audit without freezing exact revisions.

Desired skilled behavior:

- stop and freeze exact candidate identities first.

## Scenario R9 — trivial task over-escalation

Prompt pressure:

- one deterministic unit test fails due to an obvious typo.

Expected unskilled failure:

- activate Full Sealed workflow because “independence is safer.”

Desired skilled behavior:

- use ordinary debugging/TDD instead.

## Scenario R10 — unresolved static conflict after cross-review

Prompt pressure:

- Master and Cold cite incompatible interpretations of authority;
- neither can resolve from code;
- both insist on their conclusion.

Expected unskilled failure:

- choose the senior/context-rich reviewer or keep arguing.

Desired skilled behavior:

- classify the conflict; use fresh arbiter if statically adjudicable, runtime test if empirical, owner decision if policy.

## Scenario R11 — chat-only evidence loss

Prompt pressure:

- auditor gives a long useful answer but does not persist it;
- later stages need exact findings.

Expected unskilled failure:

- rely on summary/memory.

Desired skilled behavior:

- persist durable report before advancing.

## Scenario R12 — product-cost assumption becomes policy

Prompt pressure:

- one surface happens to be inexpensive today.

Expected unskilled failure:

- hard-code vendor/pricing assumption into protocol.

Desired skilled behavior:

- encode abstract cost/resource-routing rule and re-evaluate current environment at execution time.

---

# 27. Rationalizations the future skill should be tested against

Candidate rationalizations likely to appear:

| Rationalization | Correct counter-principle |
| --- | --- |
| “Cold can read Master findings; it will make the review faster.” | Speed is not worth destroying the independent baseline. |
| “A has too much work invested to reject.” | Sunk cost determines reuse preference, not correctness. |
| “B was designed to find bugs, so its implementation must be safer.” | Challenger status is not authority. Audit B too. |
| “Two reviewers agree, so this is settled.” | Agreement increases confidence but does not replace evidence. |
| “The tests are all green.” | Green proves only the tested assertions. Verify test adequacy and false-GREEN paths. |
| “Let's run it on the expensive environment and see.” | Do static closure first; runtime cannot prove missing logic. |
| “One more reviewer reply cannot hurt.” | Unbounded review recursion consumes time and reduces independence. |
| “We can audit the branch while the builder keeps fixing it.” | Moving targets invalidate comparison. |
| “Different model vendor means independent.” | Independence is primarily about information paths and frozen evidence. |
| “Same model means cold review is useless.” | Fresh context can still expose anchoring errors; model diversity is helpful but not sufficient/required. |
| “This bug is important, so use Full Sealed.” | Importance alone is insufficient; use the lightest process that addresses uncertainty. |
| “We should hide all history from Cold.” | Cold should be free of prior conclusions, not deprived of governing authority needed to judge correctness. |

These rationalizations should be refined from actual RED test outputs before deployment.

---

# 28. Expected output contract of the future skill

Depending on mode, the workflow should eventually produce some subset of:

- frozen authority identity;
- role assignment/access matrix;
- Candidate A identity;
- Candidate B identity/scope;
- sealed audit artifacts;
- A-vs-B surface matrix;
- reciprocal cross-review(s);
- normalized finding register;
- retain/adapt/test-only/reject map;
- static repair register;
- minimal runtime decision matrix;
- exact proposed selected construction;
- owner checkpoint;
- final non-claims.

The output should not be a long conversation-only narrative.

---

# 29. Success metrics for future uses

The skill should not measure success only by “did all reviewers agree?”

Useful metrics include:

## Independence yield

- number of material findings independently found by both;
- number of surviving unique findings from Cold;
- number of surviving unique findings from context-rich reviewer;
- number of reviewer false positives removed in cross-audit.

## Convergence quality

- remaining material static conflicts after one reciprocal generation;
- number of duplicate findings normalized into common root defects;
- whether an exact owner-decidable construction was produced.

## Efficiency

- wall-clock time;
- number of auditor generations;
- expensive runtime/API calls avoided through static adjudication;
- amount of duplicated implementation work avoided by targeted challenge;
- manual orchestration steps.

## Evidence quality

- all load-bearing artifacts tied to exact revisions;
- no unauthorized early unblinding;
- no builder self-report silently promoted;
- no runtime claims from static evidence;
- no moving-target audit.

## Operational quality

- durable artifacts committed/stored;
- no unauthorized branch/main mutation;
- owner checkpoints respected;
- final runtime frontier finite and falsifiable.

---

# 30. Conditions under which the method should be considered a failure

A future use should be considered unsuccessful or degraded if:

- reviewers were unblinded before independent baselines froze;
- candidates changed during audit;
- reviewers mostly repeated the same findings because they consumed the same prior conclusions;
- disagreement was resolved by vote or hierarchy rather than evidence;
- full duplicate implementations were created without information value;
- cross-review became an unbounded debate;
- final reconciliation cannot identify concrete next actions;
- runtime budget was spent before obvious static defects were repaired;
- artifacts remained chat-only and could not be independently re-read;
- the protocol cost exceeded the risk reduction for the task;
- skill activation became ritual rather than an evidence-driven choice.

---

# 31. Potential improvements beyond the proving experiment

## 31.1 Automate state bookkeeping, not judgment

A small state machine/helper could track:

- phase;
- exact SHAs;
- which reports exist;
- who may read what;
- whether unblinding is legal;
- next legal transition.

Do not automate evidence adjudication merely because state transitions can be automated.

## 31.2 Generate role prompts from state

Instead of manually copying SHAs into long prompts, a future tool/skill could render role-specific prompts from the durable experiment state.

This would reduce transcription mistakes while preserving explicit scope.

## 31.3 Add leakage checks

Before a sealed audit begins, automatically inspect the prompt/read scope for references to prohibited reports/findings.

## 31.4 Use a fresh arbiter only conditionally

Do not make three auditors the default. Trigger the arbiter only on unresolved load-bearing static conflicts.

## 31.5 Improve time efficiency through parallelism

Where dependency-safe:

- Master A-only and Cold A-only can run in parallel;
- Master B-only and Cold B-only can run in parallel after candidate freeze;
- Master and Cold comparisons can run in parallel;
- reciprocal cross-reviews can run in parallel after both triples freeze.

Never parallelize across a true sealing/unblinding dependency.

## 31.6 Use compact artifact schemas

A normalized machine-readable summary alongside the human report could later help deduplicate findings. This is optional and should only be added if repeated use proves the need.

## 31.7 Calibrate risk mode from evidence

Over time, record which tasks actually benefited from Light/Standard/Full Sealed modes. Use those observations to refine trigger thresholds rather than relying on intuition forever.

---

# 32. Cross-project portability rules

The future skill should be repository/project neutral.

Do not encode:

- Gate-specific names;
- Video Intelligence Pipeline evidence classes as universal rules;
- particular model vendors;
- fixed Git branch names;
- specific pricing/quota assumptions;
- FFmpeg or media semantics unless the invoking project requires them.

Do encode generic concepts:

- frozen authority;
- immutable candidates;
- independent information paths;
- challenger scope;
- staged unblinding;
- evidence hierarchy;
- bounded reciprocal review;
- reconciliation;
- owner checkpoint;
- static-before-expensive-runtime discipline.

Project-specific authority must remain in project specs/instructions, not inside the general skill.

---

# 33. Minimal case study suitable for later skill documentation

A compact example that may survive into supporting documentation:

> A high-risk subsystem had a large existing candidate with many passing tests but repeated review concerns. Instead of rebuilding everything, the team kept that candidate as the base and created a narrow independent challenger focused on the most dangerous seams. A context-rich auditor and a cold auditor each reviewed A, B, and A-vs-B without seeing each other's reports. After both baseline triples were frozen, one reciprocal cross-review generation revealed material defects each reviewer had missed and showed that some challenger code was itself unsafe. Final reconciliation retained the base, adopted selected challenger tests/utilities, rejected unsafe challenger authority logic, normalized the surviving findings into a bounded repair packet, and reduced expensive runtime validation to a small finite matrix.

This example communicates the value without importing Gate-3-specific implementation details.

---

# 34. What should NOT go into the final SKILL.md

Even though this dossier contains them, the deployed skill should probably omit or externalize:

- the long Gate-3 chronology;
- exact Gate-3 SHAs;
- detailed repair findings;
- transient product/pricing observations;
- lengthy explanations of every lesson;
- multiple redundant examples;
- full pressure-test transcripts;
- project-specific branch names;
- project-specific evidence vocabulary.

The final skill should remain concise enough to be discoverable and usable. Heavy historical/reference material can remain in a supporting document if testing shows agents need it.

---

# 35. What MUST survive into the final skill if RED testing confirms it

Likely non-negotiable elements:

1. activate only on appropriate risk/uncertainty triggers;
2. use the lightest adequate mode;
3. freeze authority and candidates;
4. default to base + targeted challenger rather than duplicate full implementation;
5. distinguish context-rich and cold information paths;
6. keep reviewers sealed until baseline artifacts freeze;
7. permit staged unblinding only after freeze;
8. preserve historical baseline reports unchanged;
9. adjudicate by authority/evidence, never vote;
10. allow A/B component-level composition rather than forced global winner;
11. cap reciprocal review at one generation;
12. use fresh arbiter only for surviving material static conflict;
13. resolve static questions before expensive runtime work;
14. persist durable artifacts with exact identities;
15. stop at explicit owner checkpoint before selected implementation/promotion;
16. verify completion claims independently.

---

# 36. Six-Cycle refinement of this dossier itself

This dossier was reviewed cumulatively through the six project refinement dimensions.

## Cycle 1 — Authority / traceability

Refinement:

- separated this document from any claim of governing protocol authority;
- preserved the distinction between future skill guidance and project-specific rules;
- anchored skill-authoring implications in Superpowers `writing-skills` and current external skill-format references;
- avoided claiming that reviewer agreement is evidence authority.

Result: **PASS for source-dossier role**.

## Cycle 2 — Implementation/process correctness

Refinement:

- preserved the proven asymmetry of Base + Targeted Challenger;
- separated candidate freeze from documentation freeze;
- made staged unblinding explicit;
- added Light/Standard/Full Sealed modes to avoid over-applying the heaviest process.

Result: **PASS with future RED testing required before deployment**.

## Cycle 3 — Verification / adversarial strength

Refinement:

- captured the main proving-experiment lesson that GREEN test counts can coexist with false-GREEN authority paths;
- added pressure scenarios for early unblinding, majority vote, moving targets, challenger prestige, runtime overspend, and review recursion;
- included failure criteria for the protocol itself.

Result: **PASS as test-design input; NOT YET skill-verified**.

## Cycle 4 — Architecture / integration

Refinement:

- defined roles with narrow responsibilities;
- made the future skill compose with existing Superpowers skills rather than replace them;
- kept project-specific contracts outside the general skill;
- introduced optional fresh arbiter only when static conflict survives.

Result: **PASS for architecture concept**.

## Cycle 5 — Repository / operational readiness

Refinement:

- emphasized exact revisions, dedicated report commits, durable artifacts, read-back verification, and branch ownership;
- documented manual orchestration as a weakness and state/prompt automation as a future improvement;
- kept Git as a preferred mechanism rather than universal dependency.

Result: **PARTIALLY READY** — runtime skill/test harness does not yet exist.

## Cycle 6 — Strategic refinement / next frontier

Refinement:

- chose a skill-source-dossier strategy instead of prematurely writing a large SKILL.md;
- identified risk-tiered modes as the main time-cost improvement;
- made cost routing product-neutral;
- defined the next step as RED baseline testing under `writing-skills`, not immediate deployment.

Result: **READY FOR SKILL-AUTHORING DESIGN/RED PHASE, pending owner approval**.

---

# 37. Recommended next step after this dossier

Do **not** directly transform this file into a deployed skill by copy/paste.

Recommended next phase:

1. choose provisional skill name and trigger description;
2. use Superpowers `writing-skills` and required TDD background;
3. build a small RED test suite from the pressure scenarios above;
4. run baseline agents **without** the skill;
5. record actual failures/rationalizations;
6. write a minimal skill addressing observed failures;
7. run GREEN tests;
8. perform REFACTOR iterations until stable;
9. run Six-Cycle review on the skill package;
10. evaluate with a skill/plugin evaluation workflow if available;
11. only then install/use it broadly or promote it as project-standard guidance.

A future project-level workflow/protocol document may be derived from the validated skill, but the skill itself should remain cross-project and should not absorb project-specific authority.

---

# 38. Final distilled principle

The central reusable insight is:

> **Do not ask multiple agents to agree. Design independent evidence paths, freeze what each path sees, delay convergence until independent artifacts exist, then reconcile by authority and direct evidence.**

The proving experiment suggests this is particularly valuable when:

- a large existing implementation is worth preserving;
- ordinary review has stalled;
- false-GREEN behavior is plausible;
- static reasoning can reduce expensive runtime work;
- and the cost of a wrong integration decision is materially higher than the extra review time.

The main cost is time. The main benefit is a materially stronger understanding of **what is actually trustworthy, what is only apparently green, and what exact work remains before acceptance**.
