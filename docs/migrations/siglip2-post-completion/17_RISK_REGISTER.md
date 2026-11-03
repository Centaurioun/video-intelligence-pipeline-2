# SigLIP2 Migration and Benchmark Risk Register

**Information state:** `INFERRED_DESIGN` + `SNAPSHOT` + `REVERIFY_AT_V1_COMPLETION` + `NOT_AUTHORIZED_FOR_EXECUTION`

## Scale

Impact:

- **Critical** — can invalidate provenance, compare incompatible candidates, or corrupt temporal/editorial authority.
- **High** — can block migration/benchmark or produce materially misleading evidence.
- **Medium** — can increase cost, complexity, or stale-work risk.
- **Low** — bounded operational inconvenience.

Likelihood is qualitative and must be refreshed after V1 completion.

## Register

| ID | Risk | Impact | Current likelihood | Trigger / evidence | Mitigation |
|---|---|---|---|---|---|
| R001 | V1/V2 768-D vectors mistakenly treated as compatible | Critical | Medium | equal dimensions encourage false equivalence | semantic-space identity + separate roots + rejection tests |
| R002 | So400m 1152-D meets hidden `768 * 4` assumptions | High | High before refactor | current write/test constants | profile-derived dimension/row width + synthetic 1152 tests |
| R003 | V1 text preprocessing carried into SigLIP2 incompletely | High | High if copied | V1 contract only records `padding=max_length`; SigLIP2 adds lowercase/max_length/truncation defaults | freeze full SigLIP2 contract and bind to semantic identity |
| R004 | Processor digest omits SigLIP2 tokenizer assets | High | High if V1 list reused | V1 list contains `spiece.model`; SigLIP2 repositories expose `tokenizer.model` | inventory frozen bundle before defining digest set |
| R005 | Future dependency/API drift breaks loader | High | Medium | no complete semantic-runtime lock in repo today | migration-day exact runtime freeze + bounded compatibility probe |
| R006 | MPS silently falls back or behaves differently | High | Low/Medium | device/runtime variance | explicit device checks, no silent fallback, record environment |
| R007 | So400m exceeds practical memory/batch envelope | High | Medium | larger model, 384 input, 1152 width | bounded smoke, batch-size measurement, no archive extrapolation |
| R008 | Preparation docs become stale while V1 evolves | High | High | V1 still active | staleness labels + mandatory post-completion refresh protocol |
| R009 | Future agent treats preparation as execution authority | Critical | Medium | runbooks/launch packets exist before activation | explicit `NOT_AUTHORIZED_FOR_EXECUTION`, activation checklist |
| R010 | Public benchmarks substitute for project evidence | High | Medium | SigLIP2 paper reports gains | mandatory frozen local three-way benchmark |
| R011 | Corpus selection favors one representation | High | Medium | unbalanced 10–20 video sample | corpus rubric + freeze manifest + bias audit |
| R012 | Query set is changed after outputs are inspected | Critical | Medium | human optimization/cherry-picking | freeze query set/digest before comparative interpretation |
| R013 | Relevance judgments drift after model identity is known | Critical | Medium | reviewer bias | predeclared rubric, blinded review where practical, immutable judgments |
| R014 | Winner rules are changed after results | Critical | Medium | post-hoc thresholding | freeze winner rules before final comparison |
| R015 | Raw cosine values compared across spaces | High | Medium | convenient but invalid comparison | rank/relevance metrics only across candidates |
| R016 | Model migration widens into unrelated temporal/edit/QC rewrite | High | Medium | “while we are here” refactor pressure | preserve-boundaries document + review gate |
| R017 | Historical Gate-0 adapter edited destructively | Medium/High | Medium | easiest loader path appears to be in historical adapter | evaluate successor adapter first; preserve V1 reproducibility |
| R018 | V1 candidate becomes unreproducible after migration | Critical | Medium | missing tag/runtime/model receipt | freeze V1 milestone before V2 work |
| R019 | Full archive is indexed before winner decision | High | Medium | desire to “just run it” | ADR-0002 activation and authorization gates |
| R020 | Small smoke timing is extrapolated as measured 400h timing | High | Medium | planning pressure | mark extrapolations as inference; full scale remains `NOT_OBSERVED` |
| R021 | Benchmark uses different sample PTS per model | Critical | Low/Medium | separate decode/sampling paths drift | freeze identical source-native sample positions |
| R022 | Model acquisition uses mutable upstream branch rather than revision | High | Medium | default HF `main` convenience | freeze immutable revision + local hashes |
| R023 | Runtime comparison uses different hardware/runtime identity without disclosure | High | Medium | migration spans time | benchmark run manifest pins code/model/runtime/hardware |
| R024 | Automatic cleanup removes candidate evidence before benchmark | High | Low/Medium | storage pressure | explicit retention/preservation until decision |
| R025 | Better retrieval is mistaken for exact temporal evidence | Critical | Low if invariants held | stronger model confidence | preserve source-native refinement/evidence classes |

## Highest-Priority Controls

The following controls prevent multiple risks at once:

1. immutable candidate identity;
2. separate semantic spaces/index roots;
3. complete preprocessing provenance;
4. mandatory post-completion refresh;
5. TDD for model/profile/dimension changes;
6. frozen corpus/query/relevance/metrics/winner rules;
7. explicit execution authorization;
8. benchmark run manifests with hardware/runtime identity.

## Escalation Conditions

Stop and redesign rather than patch locally if:

- V2 Base requires broad unrelated changes outside the representation boundary;
- supporting 1152-D requires duplicated storage/search implementations;
- exact processor identity cannot be made deterministic;
- the acquired checkpoint cannot be loaded offline under the approved trust boundary;
- benchmark arms cannot use comparable source/sample inputs;
- the V1 baseline cannot be reproduced.

## Ownership

This register is preparatory.

At V1 completion, every risk must be reclassified as:

- still open;
- mitigated by final V1;
- obsolete;
- newly discovered;
- blocked pending evidence.
