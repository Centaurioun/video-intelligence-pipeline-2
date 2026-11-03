# Gate-0 Revision-18 Evidence-DAG Implementation Plan v7 — V6 Review Remediation Successor

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:subagent-driven-development or superpowers:executing-plans only after a later explicit implementation authorization. This document is a plan, not execution authority. Steps use checkbox syntax when executed later.

**Goal:** implement the final owner-approved Gate-0 Revision-18 Recovery Evidence-DAG and Tier-1 synthetic enforcement surface without widening Revision 18, while closing exactly the three accepted V6-review blockers V7-01, V7-02 and V7-03 and preserving all independently accepted V6 closures.

**Architecture:** frozen. Option-A + A2R + M1R remain final; C² is unchanged and `C2_AMENDMENT_REQUIRED=NO`. V7 changes only implementation-plan mechanical contracts for controlled verifier inputs, Path namespace default-deny, and independent scanner-policy conformance. Revision-18 architecture is unchanged.

**Tech Stack:** CPython standard library; existing Gate-0 helpers; pytest 8.3.3; bounded Git CLI object plumbing; existing Stage-B shell build boundary. No new dependency.

**Spec:** `docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md` blob `21e651503bff6dc2b369ad45923d16a3af8adf1c`.

## Global Constraints

- no implementation is authorized by this plan;
- no profile-freeze measurement, venv provisioning, host scan, otool/file/Homebrew/pip, dependency install/download, build/sign, Generation B, live Stage B, provider/model activity, protected media, runtime-policy approval or Gate promotion;
- `PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`;
- `GENERATION_B_ELIGIBILITY=BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`;
- exact five-field N4a retained primitive; no new retained field/node/evidence class;
- `tests/gate0/conftest.py` remains byte-unchanged.

## Review Focus

1. controlled verifier identity: every command-consumed base/plan/phase input must be machine-bound, START/END-equal and independently checked against later explicit authorization;
2. Path namespace default deny: only explicitly policy-carried harmless Path calls may be safe; every other normalized Path callable is EFFECT_UNKNOWN unless already classified as traversal;
3. scanner-policy conformance: the production scanner source region is plan-owned exact bytes and independently checked by the controlled verifier before FV3;
4. exact-instance provenance and retained V6 authority/expectation separation must not regress;
5. row160/source-form, pytest-recorder, exact-stdin and historical-equivalence closures must remain compatible except where V7 directly changes a controlled verifier body.

---

## 1. Frozen authority, v7 successor identity and non-regression line

### 1.1 Plan lineage

- failed v1 plan blob: `18ba38319aa67ed0995cb2cc3f8d04937f188dcc`
- failed v2 plan blob: `e0eae8ea0a34a5f06c6d0d4e9ea11e62dc4ab1f2`
- failed v3 plan blob: `aa63f52007d1e3d8b80e4c03dc1bdd5cb14468e6`
- failed v4 plan blob: `fc5599caeaabe32878e1b56de75207265bad3b59`
- failed v5 plan blob: `7df69992b520def485eb4a1cda6b7f0fe8982fdd`
- failed v6 review subject / exact v7 base: `290f09b6363d963ce5b2b8cb699100f3a1ad78ba`
- failed v6 plan blob: `8f324fe3951b307b4f634346cff37552d2ef38d8`
- v7 branch: `planning/gate0-rev18-implementation-plan-v7`
- v7 path: `docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md`

V1 through V6 remain immutable historical review evidence. V7 is a new successor and does not edit any prior plan.

### 1.2 Final approved Revision-18 authority

- design subject: `b4619eb4a9ea37d63ed3f1e459a690648a4c52cb`
- spec blob: `21e651503bff6dc2b369ad45923d16a3af8adf1c`
- ruling blob: `97c8c7e0ebddad715bf1002a44d71720965735d9`
- final owner approval commit: `51c18a8f96f54b670ef6c7d8b9c2700828a0c3c1`
- final owner approval blob: `3f6230e8663e4267eddf7cada1608ea5396708b2`

Preserved owner-level design tokens:

- `G0-DEPENDENCY-CLOSURE-A-VERIFIER-SEED-MACHO-V1`
- `G0-SEED-AUTHORITY-A2R-FROZEN-NATIVE-RUNTIME-PROFILE-V1`
- `G0-A2R-M1R-PERMISSION-NATIVE-CLOSURE-KEG-ROOT-V1`

`C2_AMENDMENT_REQUIRED=NO`.

### 1.3 Binding V6-review convergence

- moderator convergence: `f7fb6ecc60ea0b135f7bde87c301f2f47309060f` / blob `b49b59c505382a27eaadb4918d96fe49c72166a1`;
- moderator intake: `3b7fc3157419e3c34d69c8b6553c842b594c9b39` / blob `e9819950d80532641617083ae729956295539280`;
- V6R-1: `3fc599180c10ca1edc3227cb3365fa3e0d92d20b` / blob `67155dd74664d4fbc6233a4e0c978b09a242e815` / accepted `V6R1-F01`;
- V6R-2: `1e3f1cc9fc39d3ed131b090c57e81550104f2a3d` / blob `151d433117ae6e6ee4ed05f0e6b35840e575cd8c` / accepted `V6R2-F01,V6R2-F02`;
- V6R-3: `9d1bf908f55931d0fc1d5a6c1e9e68b804af86d9` / blob `6c8b3562e3589eb97fe4d91c3509ddc994a7b9f8` / PASS.

The moderator accepted exactly three unique material plan blockers and `ARCHITECTURE_DECISION_REQUIRED=NO`.

### 1.4 Preserved V6 closures

V7 preserves without redesign:

- exact pytest 8.3.3 recorder semantics, strict/non-strict XPASS distinction, XFAIL/FAILED/ERROR/SKIPPED and duplicate-terminal rejection;
- V5-06 hook-order-independent historical baseline and one recorder shared by baseline/FV1/FV2;
- V6-03 `NONE | EXACT_BYTES`, capture-before-execution, same captured bytes to child, START/END stdin equality, exact argv/cwd/sequencing/manifest uniqueness and altered-stdin rejection;
- one machine `EffectPolicy`, empty os/asyncio harmless allowlists, multiprocessing fail-closed, empty network allowlist, exact three process leaves, shell-true fail-closed, unknown-external/unresolved-dynamic fail-closed and local-wrapper propagation;
- V6R-3 exact 13-entry source-form registry, used-id equality, `CALLABLE_MEASURER_PARAMETER`, row160 normative hash `6b5133644514246d1d83ec6a1fd8edf88e0c5c2a354a93b24fb2e35afc1a688d`, STATIC_REJECT / `row 5 negative scan fails`, expectation separation and anti-echo;
- VerifiedRepositoryContext, AnchoredS1, exact-instance handles, deterministic empty-origin environment, M1R one-argument classifier, RR18-2-N01 0/1/2/3, exact native serialization, 32-hop precedence, Mach-O 8/54/43, five-field N4a, P20 closed set, row21 retained-only/no-reobservation, capability/event honesty;
- source-form architecture and all 316 construction/expectation records unchanged.

## 2. Current evidence and authorization state

`PYTHON_NATIVE_CLOSURE_BASELINE = NOT_OBSERVED`

`GENERATION_B_ELIGIBILITY = BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`

`IMPLEMENTATION_AUTHORIZED = NO`

`PROFILE_FREEZE_MEASUREMENT_AUTHORIZED = NO`

`BUILD_SIGN_AUTHORIZED = NO`

`GENERATION_B_AUTHORIZED = NO`

`LIVE_STAGE_B_AUTHORIZED = NO`

`PROVIDER_MODEL_ACTIVITY_AUTHORIZED = NO`

`PROTECTED_MEDIA_AUTHORIZED = NO`

No activity prohibited by the owner prompt is authorized by this plan.

## 3. V7 remediation closure map

| Accepted finding | Binding V7 closure |
|---|---|
| V7-01 / V6R1-F01 | §§4.2/4.2.1/7/10.1/10.4/10.6.1 + Task 1 bind exact command-consumed control inputs in `CommandLedgerEvent.control_inputs`; externally authorized implementation-base SHA and approved V7 plan Git-blob identity are values, canonical V7 plan path is exact, phase is closed PRE/POST; START/END and FV4 require exact equality; FV1/shared driver independently verify canonical path + approved V7 blob before reading plan truth |
| V7-02 / V6R2-F01 | §§5.2/7/10.3 + Task 1 add machine-carried `path_harmless_call_allowlist`, exact Path binding normalization and `path_unlisted_callable_policy=EFFECT_UNKNOWN_FAIL_CLOSED`; the sole traversal leaf remains exact CensusFS `list_entries -> os.scandir` |
| V7-03 / V6R2-F02 | §§7/10.3.1/10.6.1 + Task 1 freeze exact plan-owned `scan_production_effects` source bytes; the controlled FV driver independently compares implementation source bytes/digest and rejects scanner-only widening even when the widened symbol is absent from production roots |

No closure changes Revision-18 architecture or runtime authority.

## 4. Future implementation-run preconditions, exact pytest recorder and controlled-run ledger

A later explicit implementation authorization must identify `G0_REV18_IMPLEMENTATION_BASE`, the exact approved v5 plan blob and an already-present `GATE0_PY`. No provisioning is implied. `"$GATE0_PY" -m pytest --version` must report exactly pytest 8.3.3 or stop at `GATE0_REV18_IMPLEMENTATION_BLOCKED_LOCAL_TEST_ENV`.

### 4.1 Exact recorder

The future implementation environment is pinned to `pytest == 8.3.3`. The following recorder semantics are specific to that version. In pytest 8.3.3 a strict xfail that unexpectedly passes produces a **failed call report**, has a string `longrepr` beginning exactly `[XPASS(strict)]`, and does **not** carry `wasxfail`. V6 never infers strict XPASS from arbitrary failure text: all four predicates in the strict branch are mandatory.

The plan-owned recorder implementation is exactly:

~~~python
class ExactOutcomeRecorder:
    def __init__(self):
        self.pre = []
        self.deselected = set()
        self.executed = set()
        self.phases = {}
        self.collection_errors = []
        self.outcomes = {}

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items):
        ids = [item.nodeid for item in items]
        if self.pre or len(ids) != len(set(ids)):
            raise RuntimeError("invalid collection snapshot")
        self.pre = ids

    def pytest_deselected(self, items):
        for item in items:
            self.deselected.add(item.nodeid)
            self._terminal(item.nodeid, "DESELECTED")

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append((report.nodeid, str(report.longrepr), "ERROR"))

    def pytest_runtest_logreport(self, report):
        self.executed.add(report.nodeid)
        self.phases.setdefault(report.nodeid, {})[report.when] = report

    def pytest_runtest_logfinish(self, nodeid, location):
        p = self.phases.get(nodeid, {})
        setup, call, teardown = p.get("setup"), p.get("call"), p.get("teardown")
        reports = [r for r in (setup, call, teardown) if r is not None]
        if (setup and setup.failed) or (teardown and teardown.failed):
            outcome = "ERROR"
        elif call and getattr(call, "wasxfail", None) and call.passed:
            outcome = "XPASSED"
        elif (
            call
            and call.failed
            and not getattr(call, "wasxfail", None)
            and isinstance(call.longrepr, str)
            and call.longrepr.startswith("[XPASS(strict)]")
        ):
            outcome = "XPASSED"
        elif any(r.skipped and getattr(r, "wasxfail", None) for r in reports):
            outcome = "XFAILED"
        elif call and call.failed:
            outcome = "FAILED"
        elif any(r.skipped for r in reports):
            outcome = "SKIPPED"
        elif call and call.passed:
            outcome = "PASSED"
        else:
            outcome = "ERROR"
        self._terminal(nodeid, outcome)

    def _terminal(self, nodeid, outcome):
        if nodeid in self.outcomes:
            raise RuntimeError(f"second terminal outcome:{nodeid}")
        self.outcomes[nodeid] = outcome

    def snapshot(self):
        pre = tuple(sorted(self.pre))
        deselected = tuple(sorted(self.deselected))
        executed = tuple(sorted(self.executed))
        missing = set(pre) - set(deselected) - set(executed)
        if missing:
            raise RuntimeError(f"collected without terminal path:{sorted(missing)}")
        return {
            "schema": "gate0-rev18-pytest-recorder.v4",
            "pre_deselection_node_ids": list(pre),
            "deselected_node_ids": list(deselected),
            "executed_node_ids": list(executed),
            "collection_errors": [list(x) for x in sorted(self.collection_errors)],
            "outcomes": dict(sorted(self.outcomes.items())),
        }
~~~

Terminal classification precedence is exact:

1. setup/teardown failure -> ERROR;
2. call report has `wasxfail` and call is passed -> XPASSED (non-strict XPASS);
3. call phase is failed, has no `wasxfail`, `longrepr` is `str`, and it starts exactly `[XPASS(strict)]` -> XPASSED;
4. any skipped report carrying `wasxfail` -> XFAILED;
5. ordinary call failure -> FAILED;
6. ordinary skip -> SKIPPED;
7. ordinary successful call -> PASSED;
8. otherwise -> ERROR.

Collection failure remains a collection error with ERROR semantics. Deselection remains DESELECTED. A node may receive only one terminal outcome.

The collection hook remains `@pytest.hookimpl(tryfirst=True)`, so the historical pre-deselection snapshot remains hook-order independent.

Exact pre-Task-1 baseline command:

~~~bash
PYTHONPATH=src "$GATE0_PY" - <<'PY'
import json, os
from pathlib import Path
import pytest

class ExactOutcomeRecorder:
    def __init__(self):
        self.pre = []
        self.deselected = set()
        self.executed = set()
        self.phases = {}
        self.collection_errors = []
        self.outcomes = {}

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items):
        ids = [item.nodeid for item in items]
        if self.pre or len(ids) != len(set(ids)):
            raise RuntimeError("invalid collection snapshot")
        self.pre = ids

    def pytest_deselected(self, items):
        for item in items:
            self.deselected.add(item.nodeid)
            self._terminal(item.nodeid, "DESELECTED")

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append((report.nodeid, str(report.longrepr), "ERROR"))

    def pytest_runtest_logreport(self, report):
        self.executed.add(report.nodeid)
        self.phases.setdefault(report.nodeid, {})[report.when] = report

    def pytest_runtest_logfinish(self, nodeid, location):
        p = self.phases.get(nodeid, {})
        setup, call, teardown = p.get("setup"), p.get("call"), p.get("teardown")
        reports = [r for r in (setup, call, teardown) if r is not None]
        if (setup and setup.failed) or (teardown and teardown.failed):
            outcome = "ERROR"
        elif call and getattr(call, "wasxfail", None) and call.passed:
            outcome = "XPASSED"
        elif (
            call
            and call.failed
            and not getattr(call, "wasxfail", None)
            and isinstance(call.longrepr, str)
            and call.longrepr.startswith("[XPASS(strict)]")
        ):
            outcome = "XPASSED"
        elif any(r.skipped and getattr(r, "wasxfail", None) for r in reports):
            outcome = "XFAILED"
        elif call and call.failed:
            outcome = "FAILED"
        elif any(r.skipped for r in reports):
            outcome = "SKIPPED"
        elif call and call.passed:
            outcome = "PASSED"
        else:
            outcome = "ERROR"
        self._terminal(nodeid, outcome)

    def _terminal(self, nodeid, outcome):
        if nodeid in self.outcomes:
            raise RuntimeError(f"second terminal outcome:{nodeid}")
        self.outcomes[nodeid] = outcome

    def snapshot(self):
        pre = tuple(sorted(self.pre))
        deselected = tuple(sorted(self.deselected))
        executed = tuple(sorted(self.executed))
        missing = set(pre) - set(deselected) - set(executed)
        if missing:
            raise RuntimeError(f"collected without terminal path:{sorted(missing)}")
        return {
            "schema": "gate0-rev18-pytest-recorder.v4",
            "pre_deselection_node_ids": list(pre),
            "deselected_node_ids": list(deselected),
            "executed_node_ids": list(executed),
            "collection_errors": [list(x) for x in sorted(self.collection_errors)],
            "outcomes": dict(sorted(self.outcomes.items())),
        }

if pytest.__version__ != "8.3.3":
    raise SystemExit("pinned pytest 8.3.3 required")
recorder = ExactOutcomeRecorder()
code = pytest.main(["tests/gate0", "-q", "-ra"], plugins=[recorder])
snap = recorder.snapshot()
snap["schema"] = "gate0-rev18-prechange-baseline.v4"
snap["base_sha"] = os.environ["G0_REV18_IMPLEMENTATION_BASE"]
if snap["collection_errors"] or any(v in {"FAILED", "ERROR"} for v in snap["outcomes"].values()):
    raise SystemExit("historical baseline not clean")
Path(".git/gate0-rev18-prechange-baseline-v4.json").write_text(
    json.dumps(snap, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
raise SystemExit(code)
PY
~~~

The exact stdin bytes for this command are the bytes of `import json, os
from pathlib import Path
import pytest

class ExactOutcomeRecorder:
    def __init__(self):
        self.pre = []
        self.deselected = set()
        self.executed = set()
        self.phases = {}
        self.collection_errors = []
        self.outcomes = {}

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items):
        ids = [item.nodeid for item in items]
        if self.pre or len(ids) != len(set(ids)):
            raise RuntimeError("invalid collection snapshot")
        self.pre = ids

    def pytest_deselected(self, items):
        for item in items:
            self.deselected.add(item.nodeid)
            self._terminal(item.nodeid, "DESELECTED")

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors.append((report.nodeid, str(report.longrepr), "ERROR"))

    def pytest_runtest_logreport(self, report):
        self.executed.add(report.nodeid)
        self.phases.setdefault(report.nodeid, {})[report.when] = report

    def pytest_runtest_logfinish(self, nodeid, location):
        p = self.phases.get(nodeid, {})
        setup, call, teardown = p.get("setup"), p.get("call"), p.get("teardown")
        reports = [r for r in (setup, call, teardown) if r is not None]
        if (setup and setup.failed) or (teardown and teardown.failed):
            outcome = "ERROR"
        elif call and getattr(call, "wasxfail", None) and call.passed:
            outcome = "XPASSED"
        elif (
            call
            and call.failed
            and not getattr(call, "wasxfail", None)
            and isinstance(call.longrepr, str)
            and call.longrepr.startswith("[XPASS(strict)]")
        ):
            outcome = "XPASSED"
        elif any(r.skipped and getattr(r, "wasxfail", None) for r in reports):
            outcome = "XFAILED"
        elif call and call.failed:
            outcome = "FAILED"
        elif any(r.skipped for r in reports):
            outcome = "SKIPPED"
        elif call and call.passed:
            outcome = "PASSED"
        else:
            outcome = "ERROR"
        self._terminal(nodeid, outcome)

    def _terminal(self, nodeid, outcome):
        if nodeid in self.outcomes:
            raise RuntimeError(f"second terminal outcome:{nodeid}")
        self.outcomes[nodeid] = outcome

    def snapshot(self):
        pre = tuple(sorted(self.pre))
        deselected = tuple(sorted(self.deselected))
        executed = tuple(sorted(self.executed))
        missing = set(pre) - set(deselected) - set(executed)
        if missing:
            raise RuntimeError(f"collected without terminal path:{sorted(missing)}")
        return {
            "schema": "gate0-rev18-pytest-recorder.v4",
            "pre_deselection_node_ids": list(pre),
            "deselected_node_ids": list(deselected),
            "executed_node_ids": list(executed),
            "collection_errors": [list(x) for x in sorted(self.collection_errors)],
            "outcomes": dict(sorted(self.outcomes.items())),
        }

if pytest.__version__ != "8.3.3":
    raise SystemExit("pinned pytest 8.3.3 required")
recorder = ExactOutcomeRecorder()
code = pytest.main(["tests/gate0", "-q", "-ra"], plugins=[recorder])
snap = recorder.snapshot()
snap["schema"] = "gate0-rev18-prechange-baseline.v4"
snap["base_sha"] = os.environ["G0_REV18_IMPLEMENTATION_BASE"]
if snap["collection_errors"] or any(v in {"FAILED", "ERROR"} for v in snap["outcomes"].values()):
    raise SystemExit("historical baseline not clean")
Path(".git/gate0-rev18-prechange-baseline-v4.json").write_text(
    json.dumps(snap, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
raise SystemExit(code)
` as represented between the here-doc delimiter line and terminating `PY`, including the final LF and excluding both delimiter lines. The block id is `PRETASK_BASELINE_PY`.

Baseline fields remain exactly: `schema`, `base_sha`, `pre_deselection_node_ids`, `deselected_node_ids`, `executed_node_ids`, `collection_errors`, `outcomes`.

### 4.2 Controller-owned command ledger

Before Task 1, the implementation controller initializes untracked `.git/gate0-rev18-controlled-run-ledger-v3.jsonl`. This verification metadata is not Gate evidence and creates no evidence class.

Every direct controller-spawned plan command emits START then END. V7 retains exact argv/cwd/selected-environment/stdin binding and adds one separate exact machine field: `control_inputs`.

- START/END agree byte-for-byte on argv, cwd, environment, control_inputs, task_step_id, stdin_mode, stdin_octets and stdin_sha256.
- NONE remains exactly 0/null. EXACT_BYTES remains capture-before-execution, identical child bytes, identical START/END metadata.
- `control_inputs` is an ordered tuple of exact `(key,value)` pairs. Its key sequence must equal `AllowedControlledCommand.required_control_keys` exactly. Missing, extra or reordered keys fail.
- `G0_REV18_IMPLEMENTATION_BASE` must equal the exact later authorization-provided lowercase 40-hex implementation-base SHA.
- `G0_REV18_V7_PLAN_PATH` must equal exactly `docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md`.
- `G0_REV18_APPROVED_PLAN_BLOB` must equal the exact later authorization-provided lowercase 40-hex Git blob of the approved V7 plan; path text without matching bytes is insufficient.
- `G0_REV18_VERIFY_PHASE` is exactly `PRE_RECEIPT | POST_RECEIPT` and must equal FV4's requested phase.
- all commands not listed with required control keys must carry an empty control_inputs tuple; extra authority-like environment or control fields do not widen identity.

The ordinary selected environment remains exactly:

~~~json
{
  "schema": "G0_REV18_V7_SELECTED_ENV_POLICY_V1",
  "selected_keys": [
    "GATE0_PY",
    "PYTHONPATH",
    "PATH",
    "LC_ALL",
    "LANG",
    "TZ",
    "PYTHONHASHSEED"
  ],
  "policies": {
    "CONTROLLER_SELECTED_ENV_EXACT": "Record exactly the seven selected keys after controller resolution; START and END values must match byte-for-byte.",
    "PYTHONPATH_SRC_EXACT": "Same seven-key rule, additionally PYTHONPATH must equal exactly src and argv[0] ${GATE0_PY} resolves to the exact recorded GATE0_PY value."
  }
}
~~~

Behavior-defining verifier authority is separately machine-carried:

~~~json
{
  "schema": "G0_REV18_V7_CONTROL_INPUT_POLICY_V1",
  "canonical_v7_plan_path": "docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md",
  "fields": [
    {"name": "G0_REV18_IMPLEMENTATION_BASE", "value_rule": "EXACT_LATER_AUTHORIZATION_LOWER_HEX_40"},
    {"name": "G0_REV18_V7_PLAN_PATH", "value_rule": "EXACT_CANONICAL_V7_REPOSITORY_RELATIVE_PATH"},
    {"name": "G0_REV18_APPROVED_PLAN_BLOB", "value_rule": "EXACT_LATER_AUTHORIZATION_V7_GIT_BLOB_LOWER_HEX_40"},
    {"name": "G0_REV18_VERIFY_PHASE", "value_rule": "EXACT_ONE_OF_PRE_RECEIPT_POST_RECEIPT"}
  ],
  "task_step_required_keys": {
    "PRETASK_BASELINE_CAPTURE": ["G0_REV18_IMPLEMENTATION_BASE"],
    "FV1_EXACT_TEST_SET": ["G0_REV18_V7_PLAN_PATH", "G0_REV18_APPROVED_PLAN_BLOB"],
    "FV2_FV3_FV4_FV5_FV6_FV8_DRIVER": ["G0_REV18_V7_PLAN_PATH", "G0_REV18_APPROVED_PLAN_BLOB", "G0_REV18_IMPLEMENTATION_BASE", "G0_REV18_VERIFY_PHASE"]
  },
  "all_other_task_steps_required_keys": []
}
~~~

A later explicit implementation authorization is incomplete and MUST stop before Task 1 unless it supplies both `AUTHORIZED_IMPLEMENTATION_BASE_SHA` and `AUTHORIZED_V7_PLAN_BLOB`. No implementation helper may invent/discover them.

FV4 recomputes each EXACT_BYTES body from the approved V7 plan. PRETASK_BASELINE_PY is unchanged from V6. FV1_PY and FV_DRIVER_PY change only for V7-01/V7-03 and receive freshly recomputed exact octet/digest values.

The pre-Task-1 snapshot and prohibited-generated-path rules, direct-command scope, exact command/event sequencing and bounded no-host-history claim remain V6-exact.

### 4.2.1 Exact allowed controlled-command manifest### 4.2.1 Exact allowed controlled-command manifest

The following manifest is the sole direct-controller command allowlist. A ledger event pair not matching exactly one record fails FV4. A manifest record may be used more than once only when the plan explicitly repeats that verification step after review remediation; each occurrence still receives a new `command_sequence`.

~~~json
{
  "schema": "G0_REV18_V7_ALLOWED_CONTROLLED_COMMANDS_V1",
  "records": [
    {
      "task_step_id": "ENV_PYTEST_VERSION_CHECK",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "--version"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "PRETASK_WORKTREE_SNAPSHOT",
      "argv": [
        "git",
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "PRETASK_BASELINE_CAPTURE",
      "argv": [
        "${GATE0_PY}",
        "-"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [
        "G0_REV18_IMPLEMENTATION_BASE"
      ],
      "stdin_mode": "EXACT_BYTES",
      "stdin_block_id": "PRETASK_BASELINE_PY",
      "expected_stdin_octets": 3741,
      "expected_stdin_sha256": "988f93f310ff698872539012a0f60cc2516a4dc82a380fda425832170ef9d9b5"
    },
    {
      "task_step_id": "T01_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_constants.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T01_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_constants.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T01_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
        "tests/gate0/unit/test_evidence_constants.py",
        "tests/gate0/unit/evidence_dag_fixtures.py",
        "tests/gate0/unit/evidence_dag_interface_manifest.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T01_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add Revision-18 evidence contracts"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T02_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_macho.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T02_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_macho.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T02_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
        "tests/gate0/unit/test_evidence_macho.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T02_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add closed Mach-O parser"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T03_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_runtime.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T03_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_runtime.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T03_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
        "tests/gate0/unit/test_evidence_runtime.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T03_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add stable native census"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T04_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_git.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T04_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_git.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T04_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_git.py",
        "tests/gate0/unit/test_evidence_git.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T04_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add evidence Git plumbing"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T05_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_authority.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T05_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_authority.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T05_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
        "tests/gate0/unit/test_evidence_authority.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T05_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add verifier authority and P2 identity"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T06_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_snapshot.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T06_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_snapshot.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T06_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
        "tests/gate0/unit/test_evidence_snapshot.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T06_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add verifier frozen snapshots"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T07_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_anchor.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T07_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_anchor.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T07_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
        "tests/gate0/unit/test_evidence_anchor.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T07_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add exact S7 anchor"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T08_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_boundary.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T08_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_boundary.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T08_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
        "tests/gate0/unit/test_evidence_boundary.py",
        "tests/gate0/unit/evidence_dag_oracle_manifest.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T08_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add N4a verifier boundary"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T09_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_projection.py",
        "tests/gate0/unit/test_evidence_seal.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T09_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_projection.py",
        "tests/gate0/unit/test_evidence_seal.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T09_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
        "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
        "tests/gate0/unit/test_evidence_projection.py",
        "tests/gate0/unit/test_evidence_seal.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T09_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add privacy-reduced S9 seal"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T10_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_s8.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T10_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_s8.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T10_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
        "tests/gate0/unit/test_evidence_s8.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T10_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add verifier-owned N5 S8 extraction"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T11_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_references.py",
        "tests/gate0/unit/test_evidence_retention.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T11_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_references.py",
        "tests/gate0/unit/test_evidence_retention.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T11_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_references.py",
        "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
        "tests/gate0/unit/test_evidence_references.py",
        "tests/gate0/unit/test_evidence_retention.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T11_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add P19 P20 closure"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T12_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_results.py",
        "tests/gate0/unit/test_evidence_package.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T12_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_results.py",
        "tests/gate0/unit/test_evidence_package.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T12_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_results.py",
        "src/gate0/feasibility/macos_stage_b_evidence_package.py",
        "tests/gate0/unit/test_evidence_results.py",
        "tests/gate0/unit/test_evidence_package.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T12_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add result and package artifacts"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T13_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_gate.py",
        "tests/gate0/unit/test_evidence_adversarial.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T13_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_gate.py",
        "tests/gate0/unit/test_evidence_adversarial.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T13_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
        "tests/gate0/unit/test_evidence_gate.py",
        "tests/gate0/unit/test_evidence_adversarial.py",
        "tests/gate0/unit/evidence_dag_adversarial_cases.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T13_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add complete Tier-1 gate"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T14_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_orchestrator.py",
        "tests/gate0/unit/test_stage_b_evidence_dag_cli.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T14_GREEN",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_evidence_orchestrator.py",
        "tests/gate0/unit/test_stage_b_evidence_dag_cli.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T14_GIT_ADD",
      "argv": [
        "git",
        "add",
        "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
        "scripts/stage-b-evidence-dag.py",
        "tests/gate0/unit/test_evidence_orchestrator.py",
        "tests/gate0/unit/test_stage_b_evidence_dag_cli.py"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T14_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "feat(gate0): add evidence DAG orchestration"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T15_RED",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T15_GREEN_PYTEST",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T15_GREEN_BASH_N",
      "argv": [
        "bash",
        "-n",
        "scripts/stage-b-build-app.sh"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T15_GIT_ADD",
      "argv": [
        "git",
        "add",
        "scripts/stage-b-build-app.sh",
        "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
        ".gitignore"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T15_GIT_COMMIT",
      "argv": [
        "git",
        "commit",
        "-m",
        "refactor(gate0): bind static Stage-B build boundary"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "FV1_EXACT_TEST_SET",
      "argv": [
        "${GATE0_PY}",
        "-"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [
        "G0_REV18_V7_PLAN_PATH",
        "G0_REV18_APPROVED_PLAN_BLOB"
      ],
      "stdin_mode": "EXACT_BYTES",
      "stdin_block_id": "FV1_PY",
      "expected_stdin_octets": 1847,
      "expected_stdin_sha256": "c2d804325b95e79abbcba08a2523888e6822125ca69e41aacbeb6cb64e3e217a"
    },
    {
      "task_step_id": "FV2_FV3_FV4_FV5_FV6_FV8_DRIVER",
      "argv": [
        "${GATE0_PY}",
        "-"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [
        "G0_REV18_V7_PLAN_PATH",
        "G0_REV18_APPROVED_PLAN_BLOB",
        "G0_REV18_IMPLEMENTATION_BASE",
        "G0_REV18_VERIFY_PHASE"
      ],
      "stdin_mode": "EXACT_BYTES",
      "stdin_block_id": "FV_DRIVER_PY",
      "expected_stdin_octets": 7608,
      "expected_stdin_sha256": "f7672c1b3f01c99a80bd67929ce7c22b43e6c5e194b5cf6f36a4d2fb6eb8b8e5"
    },
    {
      "task_step_id": "FV7_STATIC_PYTEST",
      "argv": [
        "${GATE0_PY}",
        "-m",
        "pytest",
        "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
        "-q"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "PYTHONPATH_SRC_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "FV7_BASH_N",
      "argv": [
        "bash",
        "-n",
        "scripts/stage-b-build-app.sh"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T16_GIT_ADD_RECEIPT",
      "argv": [
        "git",
        "add",
        "docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    },
    {
      "task_step_id": "T16_GIT_COMMIT_RECEIPT",
      "argv": [
        "git",
        "commit",
        "-m",
        "docs(gate0): record Revision-18 implementation verification"
      ],
      "cwd_policy": "EXACT_REPOSITORY_ROOT",
      "selected_environment_policy": "CONTROLLER_SELECTED_ENV_EXACT",
      "required_control_keys": [],
      "stdin_mode": "NONE",
      "stdin_block_id": null,
      "expected_stdin_octets": 0,
      "expected_stdin_sha256": null
    }
  ]
}
~~~

For EXACT_BYTES records, `expected_stdin_octets` and `expected_stdin_sha256` above are computed from the exact frozen V7 code-block body referenced by `stdin_block_id`. FV4 recomputes them from the externally blob-approved V7 plan bytes; implementation code never authors these values.

## 5. Complete plan-owned enum / dataclass / callable / protocol contract

This section is normative. No implementation file may redefine expected truth.

### 5.1 Enum manifest

~~~json[
  {
    "name": "EvidenceFailureCode",
    "values": [
      "AUTHORITY_ECHO_MISMATCH",
      "AUTHORITY_CONSUMPTION_NOT_RECORDED",
      "GENERATION_IDENTITY_COLLISION",
      "RENDER_INPUT_NOT_FROZEN",
      "OUTPUT_ROOT_AMBIGUOUS",
      "PREBUILD_ANCHOR_NOT_FROZEN",
      "FROZEN_EVIDENCE_MUTATED_BY_BUILD",
      "ANCHOR_DIGEST_NOT_RECORDED",
      "BUILD_OUTPUT_SEAL_NOT_FROZEN",
      "SEAL_IDENTITY_HOME_INCOMPLETE",
      "SIGNING_ENTITLEMENTS_NOT_FROZEN",
      "SIGNING_IDENTITY_DRIFT",
      "SIGNED_BYTES_NOT_VERIFIER_DERIVED",
      "ENTITLEMENT_ALLOWLIST_VIOLATION",
      "ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE",
      "S8_NOT_RETAINED_EXACTLY",
      "POLICY_CLOSURE_RESULT_NOT_RECORDED",
      "SEAL_PROJECTION_ELISION_INVALID",
      "SEAL_PROJECTION_PRIVACY_VIOLATION",
      "RENDER_NOT_BYTE_REPRODUCIBLE",
      "REPRODUCIBILITY_PROOF_VACUOUS",
      "RESULT_MANIFEST_NOT_FINAL",
      "EVIDENCE_PACKAGE_NOT_ADDITIVE",
      "EVIDENCE_NOT_RETAINED",
      "EVIDENCE_REFERENCE_UNRESOLVED",
      "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
      "GENERATION_B_TIER1_GATE_UNMET",
      "GATE_COVERAGE_INCOMPLETE",
      "ENVELOPE_REFERENCE_NOT_ACCEPTED"
    ]
  },
  {
    "name": "NativeCandidateClassification",
    "values": [
      "NON_NATIVE",
      "UNSUPPORTED_MACHO_CANDIDATE",
      "NATIVE_MEMBER"
    ]
  },
  {
    "name": "CanonicalizationTerminalFamily",
    "values": [
      "SYMLINK_CYCLE",
      "DANGLING",
      "CANONICALIZATION_FAILURE",
      "RESOLVED_REGULAR_FILE",
      "RESOLVED_DIRECTORY",
      "RESOLVED_UNSUPPORTED_OBJECT"
    ]
  },
  {
    "name": "CanonicalizationFailureReason",
    "values": [
      "CANONICALIZATION_FAILURE_HOP_LIMIT"
    ]
  },
  {
    "name": "EntryKind",
    "values": [
      "DIRECTORY",
      "REGULAR_FILE",
      "SYMLINK"
    ]
  },
  {
    "name": "CensusScopeTag",
    "values": [
      "BASE_RUNTIME",
      "RUN_SCOPED_VENV"
    ]
  },
  {
    "name": "LoadCommandDisposition",
    "values": [
      "DEPENDENCY_EDGE",
      "SUPPORTED_NONEDGE",
      "REJECT_UNSUPPORTED"
    ]
  },
  {
    "name": "ReferenceClass",
    "values": [
      "PATH_REFERENCE",
      "FILE_BLOB_REFERENCE",
      "COMMIT_OBJECT_REFERENCE",
      "AUTHORITY_DESIGN_RECORD_REFERENCE"
    ]
  },
  {
    "name": "ReferenceValueKind",
    "values": [
      "DIGEST",
      "COMMIT_ID",
      "TREE_ID",
      "BLOB_ID"
    ]
  },
  {
    "name": "RetentionMode",
    "values": [
      "RETAINED_OBJECT",
      "RETAINED_SEAL_TIME_MEASUREMENT_ONLY"
    ]
  },
  {
    "name": "Tier1Phase",
    "values": [
      "PRE_ENTRY",
      "GENERATION_REASSERTION",
      "LATER_AUDIT"
    ]
  },
  {
    "name": "Tier1RowKind",
    "values": [
      "CAPABILITY",
      "AGGREGATE",
      "CLOSURE",
      "REVERIFICATION"
    ]
  },
  {
    "name": "HistoricalOutcome",
    "values": [
      "PASSED",
      "FAILED",
      "ERROR",
      "SKIPPED",
      "XFAILED",
      "XPASSED",
      "DESELECTED"
    ]
  },
  {
    "name": "OracleInspectionDomain",
    "values": [
      "A",
      "B",
      "C"
    ]
  },
  {
    "name": "OracleInspectionMechanism",
    "values": [
      "AST_SIGNATURE",
      "AST_CONSTRUCTOR",
      "AST_ASSIGNMENT",
      "AST_CALL",
      "AST_IMPORT",
      "TEXT_SCHEMA",
      "IMPORT_GRAPH",
      "PACKAGE_MANIFEST",
      "DEPENDENCY_MANIFEST",
      "IMPORT_RESOLUTION",
      "REEXPORT_GRAPH",
      "PATH_ABSENCE",
      "CALL_REACHABILITY_GRAPH"
    ]
  },
  {
    "name": "OracleExpectedResult",
    "values": [
      "ABSENT",
      "IMPORT_FAILS"
    ]
  },
  {
    "name": "AdversarialObservedKind",
    "values": [
      "PASS",
      "EVIDENCE_FAILURE",
      "STATIC_REJECT"
    ]
  },
  {
    "name": "ShellSinkKind",
    "values": [
      "BUILD_DESTINATION",
      "COPY_DESTINATION",
      "CODESIGN_ENTITLEMENTS",
      "CODESIGN_IDENTITY",
      "CODESIGN_SUBJECT",
      "DIRECTORY_DESTINATION",
      "STDOUT_REPORTED_PATH"
    ]
  },
  {
    "name": "ProbeEventKind",
    "values": [
      "ENUMERATE",
      "LSTAT",
      "READLINK",
      "READ_BYTES",
      "CLASSIFY",
      "CANONICALIZE",
      "PRODUCTION_CALL",
      "PROCESS_LEAF",
      "STATIC_REJECT"
    ]
  },
  {
    "name": "AdversarialActionKind",
    "values": [
      "M1R_CONFIGURE_ROOT_CLOSURE",
      "FFMPEG_CONFIGURE_KEG",
      "S4_CONFIGURE_ECHO",
      "CLASSIFIER_CONFIGURE_BYTES",
      "MACHO_CONFIGURE_CONTAINER",
      "LOAD_COMMAND_CONFIGURE_NUMERIC",
      "GRAPH_CONFIGURE_DEPENDENCY",
      "GRAPH_CONFIGURE_CONTEXT",
      "TOCTOU_CONFIGURE_SOURCE",
      "DOMAIN_CONFIGURE_MEMBERSHIP",
      "OPTIONAL_SEEDS_CONFIGURE",
      "INVENTORY_CONFIGURE",
      "ORACLE_CONFIGURE_SOURCE",
      "VENV_CONFIGURE_NAMESPACE",
      "CENSUS_CONFIGURE_ENUMERATION",
      "CENSUS_CONFIGURE_SYMLINK",
      "FAT_CONFIGURE_STRUCTURE",
      "LOAD_COMMAND_CONFIGURE_STRUCTURE",
      "PATH_CONFIGURE_CANONICALIZATION",
      "PATH_CONFIGURE_HOP_BOUND",
      "CENSUS_CONFIGURE_STABLE",
      "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
      "MACHO_CONFIGURE_HEADER64"
    ]
  },
  {
    "name": "ActionArgType",
    "values": [
      "STRING",
      "INTEGER",
      "HEX",
      "PATH",
      "BOOLEAN",
      "ENUM",
      "STRING_TUPLE",
      "JSON"
    ]
  },
  {
    "name": "EffectKind",
    "values": [
      "PROCESS",
      "NETWORK",
      "TRAVERSAL",
      "EFFECT_UNKNOWN"
    ]
  },
  {
    "name": "ShellCommandFamily",
    "values": [
      "SWIFT_BUILD",
      "MKDIR",
      "CP_INFO",
      "CP_PRODUCT",
      "CODESIGN_SIGN",
      "CODESIGN_VERIFY",
      "ECHO"
    ]
  },
  {
    "name": "LedgerEventMarker",
    "values": [
      "START",
      "END"
    ]
  },
  {
    "name": "FixtureMutationOpcode",
    "values": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ]
  },
  {
    "name": "StdinMode",
    "values": [
      "NONE",
      "EXACT_BYTES"
    ]
  },
  {
    "name": "SyntheticSourceArtifactKind",
    "values": [
      "PYTHON_SOURCE",
      "DEPENDENCY_MANIFEST",
      "IMPORT_RESOLUTION_FIXTURE"
    ]
  }
]
~~~

### 5.2 Dataclass/type manifest

~~~json
[
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "EvidenceDagError",
    "fields": [
      {
        "name": "code",
        "type": "EvidenceFailureCode"
      },
      {
        "name": "reason",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "CanonicalizationResult",
    "fields": [
      {
        "name": "family",
        "type": "CanonicalizationTerminalFamily"
      },
      {
        "name": "reason",
        "type": "CanonicalizationFailureReason | None"
      },
      {
        "name": "canonical_target",
        "type": "PurePath | None"
      },
      {
        "name": "symlink_hops",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "CensusNamespaceRow",
    "fields": [
      {
        "name": "scope_tag",
        "type": "CensusScopeTag"
      },
      {
        "name": "relative_path_utf8",
        "type": "bytes"
      },
      {
        "name": "entry_kind",
        "type": "EntryKind"
      },
      {
        "name": "raw_link_target",
        "type": "bytes | None"
      },
      {
        "name": "canonicalization_result",
        "type": "CanonicalizationResult | None"
      },
      {
        "name": "canonical_target",
        "type": "PurePath | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "NativeManifestRow",
    "fields": [
      {
        "name": "scope_tag",
        "type": "CensusScopeTag"
      },
      {
        "name": "relative_path_utf8",
        "type": "bytes"
      },
      {
        "name": "sha256_hex",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "FSEntryObservation",
    "fields": [
      {
        "name": "path",
        "type": "PurePath"
      },
      {
        "name": "kind",
        "type": "EntryKind"
      },
      {
        "name": "raw_link_target",
        "type": "bytes | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "StableCensusResult",
    "fields": [
      {
        "name": "namespace_a",
        "type": "tuple[CensusNamespaceRow, ...]"
      },
      {
        "name": "namespace_b",
        "type": "tuple[CensusNamespaceRow, ...]"
      },
      {
        "name": "census_a_native_images",
        "type": "tuple[tuple[PurePath, bytes], ...]"
      },
      {
        "name": "native_manifest_rows",
        "type": "tuple[NativeManifestRow, ...]"
      },
      {
        "name": "native_manifest_bytes",
        "type": "bytes"
      },
      {
        "name": "native_manifest_sha256",
        "type": "str"
      },
      {
        "name": "native_member_count",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "MachOHeader64",
    "fields": [
      {
        "name": "magic",
        "type": "int"
      },
      {
        "name": "cputype",
        "type": "int"
      },
      {
        "name": "cpusubtype",
        "type": "int"
      },
      {
        "name": "filetype",
        "type": "int"
      },
      {
        "name": "ncmds",
        "type": "int"
      },
      {
        "name": "sizeofcmds",
        "type": "int"
      },
      {
        "name": "flags",
        "type": "int"
      },
      {
        "name": "reserved",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ParsedLoadCommand",
    "fields": [
      {
        "name": "command_value",
        "type": "int"
      },
      {
        "name": "command_size",
        "type": "int"
      },
      {
        "name": "disposition",
        "type": "LoadCommandDisposition"
      },
      {
        "name": "dependency_install_name",
        "type": "bytes | None"
      },
      {
        "name": "rpath_value",
        "type": "bytes | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ParsedMachO",
    "fields": [
      {
        "name": "selected_slice_offset",
        "type": "int"
      },
      {
        "name": "selected_slice_length",
        "type": "int"
      },
      {
        "name": "header",
        "type": "MachOHeader64"
      },
      {
        "name": "load_commands",
        "type": "tuple[ParsedLoadCommand, ...]"
      },
      {
        "name": "dependency_edges",
        "type": "tuple[bytes, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "FrozenArtifact",
    "fields": [
      {
        "name": "role",
        "type": "Literal['S1','S2','S3','S4']"
      },
      {
        "name": "repository_path",
        "type": "str"
      },
      {
        "name": "data",
        "type": "bytes"
      },
      {
        "name": "sha256",
        "type": "str"
      },
      {
        "name": "octets",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "AuthorityTuple",
    "fields": [
      {
        "name": "base_controller_commit",
        "type": "str"
      },
      {
        "name": "applicable_spec_blob",
        "type": "str"
      },
      {
        "name": "applicable_plan_blob",
        "type": "str"
      },
      {
        "name": "design_record_blob",
        "type": "str"
      },
      {
        "name": "generation_ordinal",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ProducerSnapshotInputs",
    "fields": [
      {
        "name": "argv",
        "type": "tuple[str, ...]"
      },
      {
        "name": "declared_output_root",
        "type": "str"
      },
      {
        "name": "output_root_provenance_token",
        "type": "str"
      },
      {
        "name": "execution_mode",
        "type": "str"
      },
      {
        "name": "target_safety_validation_ref",
        "type": "str"
      },
      {
        "name": "s4_bytes",
        "type": "bytes"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "DependencyInventoryEntry",
    "fields": [
      {
        "name": "family",
        "type": "Literal['PYTHON','TOOL']"
      },
      {
        "name": "canonical_source_identity",
        "type": "str"
      },
      {
        "name": "materialized_role",
        "type": "str"
      },
      {
        "name": "immutable_bytes",
        "type": "bytes"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "VerifierSnapshotInputs",
    "fields": [
      {
        "name": "authority",
        "type": "AuthorityTuple"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "canonical_roles",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "stable_census",
        "type": "StableCensusResult"
      },
      {
        "name": "verified_ffmpeg_bytes",
        "type": "bytes"
      },
      {
        "name": "verified_ffprobe_bytes",
        "type": "bytes"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "FrozenSnapshotSet",
    "fields": [
      {
        "name": "s1",
        "type": "FrozenArtifact"
      },
      {
        "name": "s2",
        "type": "FrozenArtifact"
      },
      {
        "name": "s3",
        "type": "FrozenArtifact"
      },
      {
        "name": "s4",
        "type": "FrozenArtifact"
      },
      {
        "name": "dependency_inventory",
        "type": "tuple[DependencyInventoryEntry, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "AnchoredBlob",
    "fields": [
      {
        "name": "repository_path",
        "type": "str"
      },
      {
        "name": "blob_id",
        "type": "str"
      },
      {
        "name": "sha256",
        "type": "str"
      },
      {
        "name": "octets",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "S7AnchorCreateResult",
    "fields": [
      {
        "name": "commit_sha",
        "type": "str"
      },
      {
        "name": "tree_sha",
        "type": "str"
      },
      {
        "name": "parent_commit_sha",
        "type": "str"
      },
      {
        "name": "anchored",
        "type": "tuple[AnchoredBlob, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "S7VerificationResult",
    "fields": [
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      },
      {
        "name": "anchored_digests",
        "type": "tuple[tuple[str, str], ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "VerifiedRepositoryContext",
    "fields": [
      {
        "name": "canonical_root",
        "type": "Path"
      },
      {
        "name": "git_dir",
        "type": "Path"
      },
      {
        "name": "evaluation_commit",
        "type": "str"
      },
      {
        "name": "base_controller_commit",
        "type": "str"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "root_device",
        "type": "int"
      },
      {
        "name": "root_inode",
        "type": "int"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "AnchoredS1Handle",
    "fields": [
      {
        "name": "s7_commit_sha",
        "type": "str"
      },
      {
        "name": "s1_repository_path",
        "type": "str"
      },
      {
        "name": "s1_blob_id",
        "type": "str"
      },
      {
        "name": "frozen_s1",
        "type": "FrozenArtifact"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "repository_context_token",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "N4ABoundaryPrimitive",
    "fields": [
      {
        "name": "format",
        "type": "Literal['N4A_BOUNDARY_PRIMITIVE_V1']"
      },
      {
        "name": "renderer_input_sha256",
        "type": "str"
      },
      {
        "name": "renderer_input_octets",
        "type": "int"
      },
      {
        "name": "signer_entitlements_sha256",
        "type": "str"
      },
      {
        "name": "signer_entitlements_octets",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "VerifierOwnedSealedDestination",
    "fields": [
      {
        "name": "scratch_root",
        "type": "Path"
      },
      {
        "name": "application_path",
        "type": "Path"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "repository_context_token",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "VerifierOwnedSigningIdentity",
    "fields": [
      {
        "name": "value",
        "type": "str"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "repository_context_token",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "N4ASealCapability",
    "fields": [
      {
        "name": "_generation_identity",
        "type": "str"
      },
      {
        "name": "_repository_context_token",
        "type": "str"
      },
      {
        "name": "_lifecycle_token",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "N4ATransientApplication",
    "fields": [
      {
        "name": "_generation_identity",
        "type": "str"
      },
      {
        "name": "_subject_path",
        "type": "Path"
      },
      {
        "name": "_repository_context_token",
        "type": "str"
      },
      {
        "name": "_lifecycle_token",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "VerifierOwnedBuildContext",
    "fields": [
      {
        "name": "repository_context",
        "type": "VerifiedRepositoryContext"
      },
      {
        "name": "sealed_destination",
        "type": "VerifierOwnedSealedDestination"
      },
      {
        "name": "signing_identity",
        "type": "VerifierOwnedSigningIdentity"
      },
      {
        "name": "generation_identity",
        "type": "str"
      },
      {
        "name": "_registration_token",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "N4AProductionResult",
    "fields": [
      {
        "name": "primitive",
        "type": "N4ABoundaryPrimitive"
      },
      {
        "name": "seal_capability",
        "type": "N4ASealCapability"
      },
      {
        "name": "transient_application",
        "type": "N4ATransientApplication"
      },
      {
        "name": "renderer_output_s2",
        "type": "FrozenArtifact"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "SignedImageProjection",
    "fields": [
      {
        "name": "info_plist_bytes",
        "type": "bytes"
      },
      {
        "name": "code_resources_bytes",
        "type": "bytes"
      },
      {
        "name": "codedirectory_bytes",
        "type": "bytes"
      },
      {
        "name": "entitlements_blob",
        "type": "bytes"
      },
      {
        "name": "der_entitlements_blob",
        "type": "bytes"
      },
      {
        "name": "requirements_bytes",
        "type": "bytes | None"
      },
      {
        "name": "cms_bytes",
        "type": "bytes | None"
      },
      {
        "name": "measurement_digests",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "special_slot_state",
        "type": "tuple[tuple[int, bytes], ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "SealResult",
    "fields": [
      {
        "name": "commit_sha",
        "type": "str"
      },
      {
        "name": "tree_sha",
        "type": "str"
      },
      {
        "name": "parent_s7_commit_sha",
        "type": "str"
      },
      {
        "name": "projection_members",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "identity_json_sha256",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ParsedEntitlementPolicy",
    "fields": [
      {
        "name": "app_sandbox",
        "type": "bool"
      },
      {
        "name": "read_only_paths",
        "type": "tuple[str, ...]"
      },
      {
        "name": "read_write_paths",
        "type": "tuple[str, ...]"
      },
      {
        "name": "keys",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "S8Capture",
    "fields": [
      {
        "name": "exact_bytes",
        "type": "bytes"
      },
      {
        "name": "sha256",
        "type": "str"
      },
      {
        "name": "parsed_policy",
        "type": "ParsedEntitlementPolicy"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "DomainEvaluation",
    "fields": [
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "Tier1RowDefinition",
    "fields": [
      {
        "name": "row_id",
        "type": "int"
      },
      {
        "name": "kind",
        "type": "Tier1RowKind"
      },
      {
        "name": "predicate_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "evaluator_id",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "Tier1RowResult",
    "fields": [
      {
        "name": "row_id",
        "type": "int"
      },
      {
        "name": "kind",
        "type": "Tier1RowKind"
      },
      {
        "name": "predicate_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "Tier1GateResult",
    "fields": [
      {
        "name": "phase",
        "type": "Tier1Phase"
      },
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "rows",
        "type": "tuple[Tier1RowResult, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "Tier1EvaluationInputs",
    "fields": [
      {
        "name": "authority",
        "type": "DomainEvaluation"
      },
      {
        "name": "snapshots",
        "type": "DomainEvaluation"
      },
      {
        "name": "anchor",
        "type": "DomainEvaluation"
      },
      {
        "name": "boundary",
        "type": "DomainEvaluation"
      },
      {
        "name": "seal",
        "type": "DomainEvaluation"
      },
      {
        "name": "s8_policy",
        "type": "DomainEvaluation"
      },
      {
        "name": "references",
        "type": "tuple[ReferenceResolution, ...]"
      },
      {
        "name": "retention",
        "type": "tuple[RetentionEvaluation, ...]"
      },
      {
        "name": "reproducibility",
        "type": "DomainEvaluation"
      },
      {
        "name": "envelope",
        "type": "DomainEvaluation"
      },
      {
        "name": "dependency_provenance",
        "type": "DomainEvaluation"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RetainedEventEvidence",
    "fields": [
      {
        "name": "s9_commit_sha",
        "type": "str"
      },
      {
        "name": "parent_s7_commit_sha",
        "type": "str"
      },
      {
        "name": "s13_commit_sha",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RetainedRow21Inputs",
    "fields": [
      {
        "name": "b_commit_sha",
        "type": "str"
      },
      {
        "name": "s13_commit_sha",
        "type": "str"
      },
      {
        "name": "parent_s7_commit_sha",
        "type": "str"
      },
      {
        "name": "s8_path",
        "type": "str"
      },
      {
        "name": "s11_result_path",
        "type": "str"
      },
      {
        "name": "s1_path",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "S11Inputs",
    "fields": [
      {
        "name": "predicate_results",
        "type": "tuple[tuple[str, bool], ...]"
      },
      {
        "name": "anchored_digests",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "policy_closure_result",
        "type": "bool"
      },
      {
        "name": "decision_record_id",
        "type": "str"
      },
      {
        "name": "authority_record_sha256",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ReproducibilityInputs",
    "fields": [
      {
        "name": "exact_s1",
        "type": "FrozenArtifact"
      },
      {
        "name": "exact_s2",
        "type": "FrozenArtifact"
      },
      {
        "name": "effective_field_mutation",
        "type": "tuple[str, str]"
      },
      {
        "name": "noneffective_field_mutation",
        "type": "tuple[str, str]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ResultArtifacts",
    "fields": [
      {
        "name": "s11_bytes",
        "type": "bytes"
      },
      {
        "name": "s12_bytes",
        "type": "bytes"
      },
      {
        "name": "s10_bytes",
        "type": "bytes"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "PackageResult",
    "fields": [
      {
        "name": "s13_commit_sha",
        "type": "str"
      },
      {
        "name": "parent_s9_commit_sha",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_orchestrator",
    "name": "EvidenceDagOrchestrator",
    "fields": [
      {
        "name": "repository_context",
        "type": "VerifiedRepositoryContext"
      },
      {
        "name": "anchor",
        "type": "S7AnchorCreateResult"
      },
      {
        "name": "anchored_s1",
        "type": "AnchoredS1Handle"
      },
      {
        "name": "snapshots",
        "type": "FrozenSnapshotSet"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "P2InvalidCase",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "authority",
        "type": "AuthorityTuple"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "StableCensusObservation",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "subaction_id",
        "type": "str"
      },
      {
        "name": "trace",
        "type": "tuple[str, ...]"
      },
      {
        "name": "success",
        "type": "bool"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      },
      {
        "name": "governing_call_count",
        "type": "int"
      },
      {
        "name": "mutation_observed",
        "type": "bool"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "NormativeAdversarialRow",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "domain",
        "type": "str"
      },
      {
        "name": "case_text",
        "type": "str"
      },
      {
        "name": "required_outcome",
        "type": "str"
      },
      {
        "name": "domain_sha256",
        "type": "str"
      },
      {
        "name": "case_sha256",
        "type": "str"
      },
      {
        "name": "outcome_sha256",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "AdversarialExecutionRequest",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "action_kind",
        "type": "AdversarialActionKind"
      },
      {
        "name": "action_args",
        "type": "tuple[FixtureMutationOp, ...]"
      },
      {
        "name": "governing_callable_id",
        "type": "str"
      },
      {
        "name": "probe_id",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "AdversarialExecutionObservation",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "governing_callable_id",
        "type": "str"
      },
      {
        "name": "probe_id",
        "type": "str"
      },
      {
        "name": "production_call_count",
        "type": "int"
      },
      {
        "name": "process_leaf_count",
        "type": "int"
      },
      {
        "name": "mutation_observed",
        "type": "bool"
      },
      {
        "name": "post_mutation_invariant_passed",
        "type": "bool"
      },
      {
        "name": "observed_kind",
        "type": "AdversarialObservedKind"
      },
      {
        "name": "observed_failure_code",
        "type": "EvidenceFailureCode | None"
      },
      {
        "name": "observed_detail",
        "type": "str | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedParameter",
    "fields": [
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "annotation",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedInterface",
    "fields": [
      {
        "name": "module",
        "type": "str"
      },
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "parameters",
        "type": "tuple[ExpectedParameter, ...]"
      },
      {
        "name": "return_annotation",
        "type": "str"
      },
      {
        "name": "governed_error_type",
        "type": "str"
      },
      {
        "name": "visibility",
        "type": "Literal['PUBLIC','PRIVATE_SECURITY','TEST_SUPPORT']"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedEnum",
    "fields": [
      {
        "name": "module",
        "type": "str"
      },
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "values",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedDataclass",
    "fields": [
      {
        "name": "module",
        "type": "str"
      },
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "fields",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "frozen",
        "type": "bool"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellAssignment",
    "fields": [
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "raw_value",
        "type": "str"
      },
      {
        "name": "source_variables",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellArgvToken",
    "fields": [
      {
        "name": "raw",
        "type": "str"
      },
      {
        "name": "normalized",
        "type": "str"
      },
      {
        "name": "source_variables",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellCommand",
    "fields": [
      {
        "name": "line_no",
        "type": "int"
      },
      {
        "name": "argv_tokens",
        "type": "tuple[ShellArgvToken, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellSink",
    "fields": [
      {
        "name": "kind",
        "type": "ShellSinkKind"
      },
      {
        "name": "command_index",
        "type": "int"
      },
      {
        "name": "argv_index",
        "type": "int"
      },
      {
        "name": "source_variables",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellContract",
    "fields": [
      {
        "name": "required_nonempty_variables",
        "type": "tuple[str, ...]"
      },
      {
        "name": "assignments",
        "type": "tuple[ShellAssignment, ...]"
      },
      {
        "name": "assignment_edges",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "commands",
        "type": "tuple[ShellCommand, ...]"
      },
      {
        "name": "sinks",
        "type": "tuple[ShellSink, ...]"
      },
      {
        "name": "referenced_variables",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "EvidenceReference",
    "fields": [
      {
        "name": "reference_class",
        "type": "ReferenceClass"
      },
      {
        "name": "repository_path",
        "type": "str | None"
      },
      {
        "name": "object_id",
        "type": "str | None"
      },
      {
        "name": "expected_sha256",
        "type": "str | None"
      },
      {
        "name": "authority_ref",
        "type": "str | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ReferenceResolutionContext",
    "fields": [
      {
        "name": "s7_commit_sha",
        "type": "str"
      },
      {
        "name": "s13_commit_sha",
        "type": "str"
      },
      {
        "name": "base_controller_commit",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "ReferenceResolution",
    "fields": [
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "resolved_arm",
        "type": "Literal['a','b','c','d'] | None"
      },
      {
        "name": "resolved_object_id",
        "type": "str | None"
      },
      {
        "name": "resolved_sha256",
        "type": "str | None"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RecordedEvidenceValue",
    "fields": [
      {
        "name": "artifact_role",
        "type": "Literal['S8','S9','S11','S12','S10']"
      },
      {
        "name": "key",
        "type": "str"
      },
      {
        "name": "value_kind",
        "type": "ReferenceValueKind"
      },
      {
        "name": "value",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RetentionContext",
    "fields": [
      {
        "name": "s7_commit_sha",
        "type": "str"
      },
      {
        "name": "s9_commit_sha",
        "type": "str"
      },
      {
        "name": "s13_commit_sha",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RetentionAssignment",
    "fields": [
      {
        "name": "value",
        "type": "RecordedEvidenceValue"
      },
      {
        "name": "mode",
        "type": "RetentionMode"
      }
    ],
    "frozen": true
  },
  {
    "module": "macos_stage_b_evidence_constants",
    "name": "RetentionEvaluation",
    "fields": [
      {
        "name": "passed",
        "type": "bool"
      },
      {
        "name": "mode",
        "type": "RetentionMode | None"
      },
      {
        "name": "resolution_kind",
        "type": "Literal['RETAINED_OBJECT','RETAINED_MEASUREMENT_RECORD'] | None"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "SyntheticSignedImage",
    "fields": [
      {
        "name": "executable_region",
        "type": "bytes"
      },
      {
        "name": "info_plist",
        "type": "bytes"
      },
      {
        "name": "code_resources",
        "type": "bytes"
      },
      {
        "name": "codedirectory",
        "type": "bytes"
      },
      {
        "name": "entitlements_blob",
        "type": "bytes"
      },
      {
        "name": "der_entitlements_blob",
        "type": "bytes"
      },
      {
        "name": "requirements_blob",
        "type": "bytes"
      },
      {
        "name": "cms_blob",
        "type": "bytes"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "CommandExerciseResult",
    "fields": [
      {
        "name": "accepted",
        "type": "bool"
      },
      {
        "name": "dependency_edges",
        "type": "tuple[bytes, ...]"
      },
      {
        "name": "failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "SyntheticEntry",
    "fields": [
      {
        "name": "kind",
        "type": "EntryKind"
      },
      {
        "name": "data",
        "type": "bytes | None"
      },
      {
        "name": "raw_link_target",
        "type": "bytes | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "SyntheticCensusFS",
    "fields": [
      {
        "name": "start",
        "type": "PurePath"
      },
      {
        "name": "entries",
        "type": "dict[PurePath, SyntheticEntry]"
      },
      {
        "name": "expansion_count",
        "type": "int"
      },
      {
        "name": "read_counts",
        "type": "dict[PurePath, int]"
      },
      {
        "name": "host_limit",
        "type": "int | None"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ProbeEvent",
    "fields": [
      {
        "name": "kind",
        "type": "ProbeEventKind"
      },
      {
        "name": "subject",
        "type": "str"
      },
      {
        "name": "ordinal",
        "type": "int"
      },
      {
        "name": "detail",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "CensusCaseFixture",
    "fields": [
      {
        "name": "base_root",
        "type": "PurePath"
      },
      {
        "name": "venv_root",
        "type": "PurePath"
      },
      {
        "name": "fs",
        "type": "SyntheticCensusFS"
      },
      {
        "name": "trace",
        "type": "list[ProbeEvent]"
      },
      {
        "name": "mutation_state",
        "type": "tuple[tuple[str, str], ...]"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "TmpGitRepo",
    "fields": [
      {
        "name": "root",
        "type": "Path"
      },
      {
        "name": "env",
        "type": "dict[str, str]"
      },
      {
        "name": "head_commit",
        "type": "str"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "MutableNativeSource",
    "fields": [
      {
        "name": "reads",
        "type": "tuple[bytes, ...]"
      },
      {
        "name": "read_count",
        "type": "int"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "SnapshotFixture",
    "fields": [
      {
        "name": "verifier_inputs",
        "type": "VerifierSnapshotInputs"
      },
      {
        "name": "producer_inputs",
        "type": "ProducerSnapshotInputs"
      },
      {
        "name": "mutable_native_source",
        "type": "MutableNativeSource"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "RetentionFixture",
    "fields": [
      {
        "name": "context",
        "type": "RetentionContext"
      },
      {
        "name": "mode_a_value",
        "type": "RecordedEvidenceValue"
      },
      {
        "name": "requirements_mode_b_value",
        "type": "RecordedEvidenceValue"
      },
      {
        "name": "cms_mode_b_value",
        "type": "RecordedEvidenceValue"
      },
      {
        "name": "foreign_digest_value",
        "type": "RecordedEvidenceValue"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ResultBuilder",
    "fields": [
      {
        "name": "s11_inputs",
        "type": "S11Inputs"
      },
      {
        "name": "reproducibility_inputs",
        "type": "ReproducibilityInputs"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "RetainedRow21Fixture",
    "fields": [
      {
        "name": "inputs",
        "type": "RetainedRow21Inputs"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "HelperContract",
    "fields": [
      {
        "name": "owner",
        "type": "str"
      },
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "signature",
        "type": "str"
      },
      {
        "name": "semantics",
        "type": "str"
      },
      {
        "name": "governed_error_type",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture",
    "fields": [
      {
        "name": "enums",
        "type": "tuple[ExpectedEnum, ...]"
      },
      {
        "name": "dataclasses",
        "type": "tuple[ExpectedDataclass, ...]"
      },
      {
        "name": "interfaces",
        "type": "tuple[ExpectedInterface, ...]"
      },
      {
        "name": "helpers",
        "type": "tuple[HelperContract, ...]"
      },
      {
        "name": "expected_node_ids",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "OpaqueHandleForgeryCase",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "handle_kind",
        "type": "str"
      },
      {
        "name": "mutation_kind",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "StructuralCommandCase",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "command_value",
        "type": "int"
      },
      {
        "name": "variant",
        "type": "Literal['VALID','UNDERSIZED','FORMULA_OR_TRAILING','NONZERO_RESERVED_OR_PADDING']"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "Header64Case",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "fixture_id",
        "type": "str"
      },
      {
        "name": "expected_success",
        "type": "bool"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "FatStructureCase",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "fixture_id",
        "type": "str"
      },
      {
        "name": "expected_success",
        "type": "bool"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "AdversarialFixture",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "fixture_builder_id",
        "type": "str"
      },
      {
        "name": "fixture_state",
        "type": "bytes"
      },
      {
        "name": "resource_tokens",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "ObservationProbeHandle",
    "fields": [
      {
        "name": "probe_id",
        "type": "str"
      },
      {
        "name": "events",
        "type": "list[ProbeEvent]"
      }
    ],
    "frozen": false
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "StableCensusConstructionSpec",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "fixture_builder_id",
        "type": "str"
      },
      {
        "name": "subaction_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "governing_callable_id",
        "type": "str"
      },
      {
        "name": "probe_observer_id",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "StableCensusSubcaseExpectation",
    "fields": [
      {
        "name": "subaction_id",
        "type": "str"
      },
      {
        "name": "expected_trace",
        "type": "tuple[str, ...]"
      },
      {
        "name": "expected_success",
        "type": "bool"
      },
      {
        "name": "expected_failure_code",
        "type": "EvidenceFailureCode | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "StableCensusExpectation",
    "fields": [
      {
        "name": "case_id",
        "type": "str"
      },
      {
        "name": "subcases",
        "type": "tuple[StableCensusSubcaseExpectation, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "OracleInspectionRequest",
    "fields": [
      {
        "name": "domain",
        "type": "OracleInspectionDomain"
      },
      {
        "name": "surface_id",
        "type": "str"
      },
      {
        "name": "production_paths",
        "type": "tuple[str, ...]"
      },
      {
        "name": "mechanism",
        "type": "OracleInspectionMechanism"
      },
      {
        "name": "forbidden_form",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "OracleInspectionExpectation",
    "fields": [
      {
        "name": "surface_id",
        "type": "str"
      },
      {
        "name": "expected",
        "type": "OracleExpectedResult"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "OracleInspectionObservation",
    "fields": [
      {
        "name": "surface_id",
        "type": "str"
      },
      {
        "name": "mechanism",
        "type": "OracleInspectionMechanism"
      },
      {
        "name": "matches",
        "type": "tuple[str, ...]"
      },
      {
        "name": "reachable_symbols",
        "type": "tuple[str, ...]"
      },
      {
        "name": "import_resolution",
        "type": "tuple[str, ...]"
      },
      {
        "name": "import_succeeded",
        "type": "bool | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "PostMutationInvariant",
    "fields": [
      {
        "name": "observer_id",
        "type": "str"
      },
      {
        "name": "expected_state_sha256",
        "type": "str"
      },
      {
        "name": "required_targets",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "AdversarialConstructionSpec",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "normative_row_sha256",
        "type": "str"
      },
      {
        "name": "domain",
        "type": "str"
      },
      {
        "name": "builder_id",
        "type": "str"
      },
      {
        "name": "action_kind",
        "type": "AdversarialActionKind"
      },
      {
        "name": "action_args",
        "type": "tuple[FixtureMutationOp, ...]"
      },
      {
        "name": "governing_callable_id",
        "type": "str"
      },
      {
        "name": "probe_id",
        "type": "str"
      },
      {
        "name": "post_mutation_invariant",
        "type": "PostMutationInvariant"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "AdversarialExpectation",
    "fields": [
      {
        "name": "row_id",
        "type": "str"
      },
      {
        "name": "expected_kind",
        "type": "AdversarialObservedKind"
      },
      {
        "name": "expected_failure_code",
        "type": "EvidenceFailureCode | None"
      },
      {
        "name": "expected_detail",
        "type": "str | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedProtocolMethod",
    "fields": [
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "parameters",
        "type": "tuple[ExpectedParameter, ...]"
      },
      {
        "name": "return_annotation",
        "type": "str"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "ExpectedProtocol",
    "fields": [
      {
        "name": "module",
        "type": "str"
      },
      {
        "name": "name",
        "type": "str"
      },
      {
        "name": "classification",
        "type": "Literal['PROTOCOL']"
      },
      {
        "name": "methods",
        "type": "tuple[ExpectedProtocolMethod, ...]"
      },
      {
        "name": "visibility",
        "type": "Literal['PUBLIC','PRIVATE_SECURITY','TEST_SUPPORT']"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ShellCommandFamilyRule",
    "fields": [
      {
        "name": "family",
        "type": "ShellCommandFamily"
      },
      {
        "name": "executables",
        "type": "tuple[str, ...]"
      },
      {
        "name": "context",
        "type": "str"
      },
      {
        "name": "argv_shape",
        "type": "tuple[str, ...]"
      },
      {
        "name": "allowed_options",
        "type": "tuple[str, ...]"
      },
      {
        "name": "source_positions",
        "type": "tuple[tuple[int, str], ...]"
      },
      {
        "name": "sink_positions",
        "type": "tuple[tuple[int, ShellSinkKind], ...]"
      },
      {
        "name": "aliases_may_feed_sinks",
        "type": "bool"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "EffectPolicy",
    "fields": [
      {
        "name": "schema",
        "type": "Literal['G0_REV18_V7_EFFECT_POLICY_V1']"
      },
      {
        "name": "production_roots",
        "type": "tuple[str, ...]"
      },
      {
        "name": "safe_import_prefixes",
        "type": "tuple[str, ...]"
      },
      {
        "name": "forbidden_network_prefixes",
        "type": "tuple[str, ...]"
      },
      {
        "name": "process_effect_rules",
        "type": "tuple[str, ...]"
      },
      {
        "name": "traversal_effect_rules",
        "type": "tuple[str, ...]"
      },
      {
        "name": "os_harmless_call_allowlist",
        "type": "tuple[str, ...]"
      },
      {
        "name": "asyncio_harmless_call_allowlist",
        "type": "tuple[str, ...]"
      },
      {
        "name": "path_harmless_call_allowlist",
        "type": "tuple[str, ...]"
      },
      {
        "name": "path_constructor_policy",
        "type": "Literal['CONSTRUCTION_ONLY_NO_EFFECT']"
      },
      {
        "name": "path_binding_resolution_policy",
        "type": "str"
      },
      {
        "name": "path_unlisted_callable_policy",
        "type": "Literal['EFFECT_UNKNOWN_FAIL_CLOSED']"
      },
      {
        "name": "multiprocessing_policy",
        "type": "Literal['FAIL_CLOSED_IMPORT_OR_CALL']"
      },
      {
        "name": "allowed_process_leaves",
        "type": "tuple[str, ...]"
      },
      {
        "name": "allowed_traversal_leaf",
        "type": "str"
      },
      {
        "name": "local_module_call_resolution_policy",
        "type": "str"
      },
      {
        "name": "unresolved_dynamic_local_edge_policy",
        "type": "Literal['FAIL_CLOSED']"
      },
      {
        "name": "unknown_external_import_policy",
        "type": "Literal['FAIL_CLOSED']"
      },
      {
        "name": "security_relevant_unlisted_call_policy",
        "type": "Literal['EFFECT_UNKNOWN_FAIL_CLOSED']"
      },
      {
        "name": "shell_true_policy",
        "type": "Literal['FAIL_CLOSED']"
      },
      {
        "name": "network_allowlist",
        "type": "tuple[str, ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "EffectScanFinding",
    "fields": [
      {
        "name": "kind",
        "type": "EffectKind"
      },
      {
        "name": "module",
        "type": "str"
      },
      {
        "name": "function",
        "type": "str"
      },
      {
        "name": "symbol",
        "type": "str"
      },
      {
        "name": "line",
        "type": "int"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "EffectScanResult",
    "fields": [
      {
        "name": "findings",
        "type": "tuple[EffectScanFinding, ...]"
      },
      {
        "name": "resolved_local_edges",
        "type": "tuple[tuple[str, str], ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "CommandLedgerEvent",
    "fields": [
      {
        "name": "schema",
        "type": "Literal['gate0-rev18-controlled-run-ledger.v3']"
      },
      {
        "name": "event_sequence",
        "type": "int"
      },
      {
        "name": "command_sequence",
        "type": "int"
      },
      {
        "name": "marker",
        "type": "LedgerEventMarker"
      },
      {
        "name": "argv",
        "type": "tuple[str, ...]"
      },
      {
        "name": "cwd",
        "type": "str"
      },
      {
        "name": "environment",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "control_inputs",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "task_step_id",
        "type": "str"
      },
      {
        "name": "stdin_mode",
        "type": "StdinMode"
      },
      {
        "name": "stdin_octets",
        "type": "int"
      },
      {
        "name": "stdin_sha256",
        "type": "str | None"
      },
      {
        "name": "exit_status",
        "type": "int | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "PytestRecorderSnapshot",
    "fields": [
      {
        "name": "schema",
        "type": "Literal['gate0-rev18-pytest-recorder.v4']"
      },
      {
        "name": "pre_deselection_node_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "deselected_node_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "executed_node_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "collection_errors",
        "type": "tuple[tuple[str, str, str], ...]"
      },
      {
        "name": "outcomes",
        "type": "tuple[tuple[str, HistoricalOutcome], ...]"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "FixtureMutationOp",
    "fields": [
      {
        "name": "opcode",
        "type": "FixtureMutationOpcode"
      },
      {
        "name": "target",
        "type": "str"
      },
      {
        "name": "value",
        "type": "str"
      },
      {
        "name": "aux",
        "type": "str | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "AllowedControlledCommand",
    "fields": [
      {
        "name": "task_step_id",
        "type": "str"
      },
      {
        "name": "argv",
        "type": "tuple[str, ...]"
      },
      {
        "name": "cwd_policy",
        "type": "Literal['EXACT_REPOSITORY_ROOT']"
      },
      {
        "name": "selected_environment_policy",
        "type": "str"
      },
      {
        "name": "required_control_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "stdin_mode",
        "type": "StdinMode"
      },
      {
        "name": "stdin_block_id",
        "type": "str | None"
      },
      {
        "name": "expected_stdin_octets",
        "type": "int"
      },
      {
        "name": "expected_stdin_sha256",
        "type": "str | None"
      }
    ],
    "frozen": true
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "SyntheticForbiddenSourceForm",
    "fields": [
      {
        "name": "source_form_id",
        "type": "str"
      },
      {
        "name": "artifact_kind",
        "type": "SyntheticSourceArtifactKind"
      },
      {
        "name": "target_path_or_module",
        "type": "str"
      },
      {
        "name": "utf8_text",
        "type": "str"
      },
      {
        "name": "template_parameters",
        "type": "tuple[tuple[str, str], ...]"
      },
      {
        "name": "required_property",
        "type": "str"
      },
      {
        "name": "observer_id",
        "type": "str"
      },
      {
        "name": "canonical_observation",
        "type": "str"
      }
    ],
    "frozen": true
  }
]
~~~

### 5.3 Callable manifest

~~~json
[
  {
    "module": "macos_stage_b_evidence_runtime",
    "name": "canonicalize_path_v1",
    "parameters": [
      {
        "name": "path",
        "annotation": "PurePath"
      },
      {
        "name": "fs",
        "annotation": "CensusFS"
      }
    ],
    "return_annotation": "CanonicalizationResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_runtime",
    "name": "capture_stable_census",
    "parameters": [
      {
        "name": "base_root",
        "annotation": "PurePath"
      },
      {
        "name": "venv_root",
        "annotation": "PurePath"
      },
      {
        "name": "fs",
        "annotation": "CensusFS"
      }
    ],
    "return_annotation": "StableCensusResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_runtime",
    "name": "serialize_native_manifest",
    "parameters": [
      {
        "name": "result",
        "annotation": "StableCensusResult"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_runtime",
    "name": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "parameters": [
      {
        "name": "data",
        "annotation": "bytes"
      }
    ],
    "return_annotation": "NativeCandidateClassification",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_macho",
    "name": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "parameters": [
      {
        "name": "data",
        "annotation": "bytes"
      }
    ],
    "return_annotation": "ParsedMachO",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "read_blob_at",
    "parameters": [
      {
        "name": "commit_sha",
        "annotation": "str"
      },
      {
        "name": "repository_path",
        "annotation": "str"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "blob_id_at",
    "parameters": [
      {
        "name": "commit_sha",
        "annotation": "str"
      },
      {
        "name": "repository_path",
        "annotation": "str"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "object_type",
    "parameters": [
      {
        "name": "object_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "Literal['commit','tree','blob']",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "commit_parent",
    "parameters": [
      {
        "name": "commit_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "commit_tree",
    "parameters": [
      {
        "name": "commit_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "strict_ancestor",
    "parameters": [
      {
        "name": "ancestor_commit",
        "annotation": "str"
      },
      {
        "name": "descendant_commit",
        "annotation": "str"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "reachable_committed_generation_identities",
    "parameters": [
      {
        "name": "evaluation_commit",
        "annotation": "str"
      }
    ],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "additive_mdrt_paths",
    "parameters": [
      {
        "name": "base_commit",
        "annotation": "str"
      },
      {
        "name": "head_commit",
        "annotation": "str"
      }
    ],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "verify_repository_context",
    "parameters": [
      {
        "name": "authority",
        "annotation": "AuthorityTuple"
      },
      {
        "name": "evaluation_commit",
        "annotation": "str"
      }
    ],
    "return_annotation": "VerifiedRepositoryContext",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "_validate_verified_repository_context",
    "parameters": [
      {
        "name": "context",
        "annotation": "VerifiedRepositoryContext"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "_run_git",
    "parameters": [
      {
        "name": "argv",
        "annotation": "tuple[str, ...]"
      },
      {
        "name": "cwd",
        "annotation": "Path"
      }
    ],
    "return_annotation": "subprocess.CompletedProcess[bytes]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_authority",
    "name": "derive_generation_identity",
    "parameters": [
      {
        "name": "authority",
        "annotation": "AuthorityTuple"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_authority",
    "name": "validate_s4_a2r_m1r_echo",
    "parameters": [
      {
        "name": "s4_bytes",
        "annotation": "bytes"
      },
      {
        "name": "authority",
        "annotation": "AuthorityTuple"
      }
    ],
    "return_annotation": "DomainEvaluation",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_snapshot",
    "name": "derive_frozen_snapshots",
    "parameters": [
      {
        "name": "verifier_inputs",
        "annotation": "VerifierSnapshotInputs"
      },
      {
        "name": "producer_inputs",
        "annotation": "ProducerSnapshotInputs"
      }
    ],
    "return_annotation": "FrozenSnapshotSet",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_snapshot",
    "name": "render_s2_from_s1",
    "parameters": [
      {
        "name": "s1",
        "annotation": "FrozenArtifact"
      }
    ],
    "return_annotation": "FrozenArtifact",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_snapshot",
    "name": "_derive_dependency_inventory_from_host",
    "parameters": [
      {
        "name": "verifier_inputs",
        "annotation": "VerifierSnapshotInputs"
      }
    ],
    "return_annotation": "tuple[DependencyInventoryEntry, ...]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_snapshot",
    "name": "_read_host_native_image",
    "parameters": [
      {
        "name": "path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_anchor",
    "name": "create_s7_anchor",
    "parameters": [
      {
        "name": "parent_commit_sha",
        "annotation": "str"
      },
      {
        "name": "artifacts",
        "annotation": "tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]"
      }
    ],
    "return_annotation": "S7AnchorCreateResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_anchor",
    "name": "verify_s7_anchor",
    "parameters": [
      {
        "name": "anchor",
        "annotation": "S7AnchorCreateResult"
      },
      {
        "name": "artifacts",
        "annotation": "tuple[FrozenArtifact, FrozenArtifact, FrozenArtifact, FrozenArtifact]"
      }
    ],
    "return_annotation": "S7VerificationResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_anchor",
    "name": "resolve_anchored_s1",
    "parameters": [
      {
        "name": "repository_context",
        "annotation": "VerifiedRepositoryContext"
      },
      {
        "name": "anchor",
        "annotation": "S7AnchorCreateResult"
      }
    ],
    "return_annotation": "AnchoredS1Handle",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_anchor",
    "name": "_extract_registered_anchored_s1",
    "parameters": [
      {
        "name": "handle",
        "annotation": "AnchoredS1Handle"
      },
      {
        "name": "repository_context",
        "annotation": "VerifiedRepositoryContext"
      }
    ],
    "return_annotation": "FrozenArtifact",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_boundary",
    "name": "_create_verifier_owned_build_context",
    "parameters": [
      {
        "name": "repository_context",
        "annotation": "VerifiedRepositoryContext"
      },
      {
        "name": "anchor",
        "annotation": "S7AnchorCreateResult"
      }
    ],
    "return_annotation": "VerifierOwnedBuildContext",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_boundary",
    "name": "invoke_stage_b_build_app",
    "parameters": [
      {
        "name": "s2",
        "annotation": "FrozenArtifact"
      },
      {
        "name": "build_context",
        "annotation": "VerifierOwnedBuildContext"
      }
    ],
    "return_annotation": "N4ATransientApplication",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_boundary",
    "name": "measure_and_handoff_n4a",
    "parameters": [
      {
        "name": "anchored_s1",
        "annotation": "AnchoredS1Handle"
      },
      {
        "name": "anchored_s2",
        "annotation": "FrozenArtifact"
      },
      {
        "name": "build_context",
        "annotation": "VerifierOwnedBuildContext"
      }
    ],
    "return_annotation": "N4AProductionResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_boundary",
    "name": "_run_stage_b_build_process",
    "parameters": [
      {
        "name": "s2",
        "annotation": "FrozenArtifact"
      },
      {
        "name": "build_context",
        "annotation": "VerifierOwnedBuildContext"
      },
      {
        "name": "private_s2_file",
        "annotation": "Path"
      },
      {
        "name": "env",
        "annotation": "dict[str, str]"
      }
    ],
    "return_annotation": "subprocess.CompletedProcess[bytes]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_boundary",
    "name": "_validate_registered_handle",
    "parameters": [
      {
        "name": "handle",
        "annotation": "VerifierOwnedSealedDestination | VerifierOwnedSigningIdentity | VerifierOwnedBuildContext | N4ASealCapability | N4ATransientApplication"
      },
      {
        "name": "repository_context",
        "annotation": "VerifiedRepositoryContext"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_projection",
    "name": "project_signed_image",
    "parameters": [
      {
        "name": "image",
        "annotation": "SyntheticSignedImage"
      }
    ],
    "return_annotation": "SignedImageProjection",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_seal",
    "name": "seal_n4b",
    "parameters": [
      {
        "name": "s7",
        "annotation": "S7AnchorCreateResult"
      },
      {
        "name": "capability",
        "annotation": "N4ASealCapability"
      }
    ],
    "return_annotation": "SealResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_s8",
    "name": "extract_s8_from_n4a_application",
    "parameters": [
      {
        "name": "application",
        "annotation": "N4ATransientApplication"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_s8",
    "name": "capture_and_evaluate_s8",
    "parameters": [
      {
        "name": "application",
        "annotation": "N4ATransientApplication"
      },
      {
        "name": "exact_s1",
        "annotation": "FrozenArtifact"
      },
      {
        "name": "seal",
        "annotation": "SealResult"
      }
    ],
    "return_annotation": "S8Capture",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_s8",
    "name": "_run_codesign_entitlements",
    "parameters": [
      {
        "name": "application",
        "annotation": "N4ATransientApplication"
      }
    ],
    "return_annotation": "subprocess.CompletedProcess[bytes]",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "macos_stage_b_evidence_references",
    "name": "resolve_p19_reference",
    "parameters": [
      {
        "name": "reference",
        "annotation": "EvidenceReference"
      },
      {
        "name": "context",
        "annotation": "ReferenceResolutionContext"
      }
    ],
    "return_annotation": "ReferenceResolution",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_retention",
    "name": "assign_p20_retention",
    "parameters": [
      {
        "name": "value",
        "annotation": "RecordedEvidenceValue"
      },
      {
        "name": "context",
        "annotation": "RetentionContext"
      }
    ],
    "return_annotation": "RetentionAssignment",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_retention",
    "name": "evaluate_p20_retention",
    "parameters": [
      {
        "name": "assignment",
        "annotation": "RetentionAssignment"
      },
      {
        "name": "context",
        "annotation": "RetentionContext"
      }
    ],
    "return_annotation": "RetentionEvaluation",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_results",
    "name": "serialize_s11",
    "parameters": [
      {
        "name": "inputs",
        "annotation": "S11Inputs"
      },
      {
        "name": "tier1_result",
        "annotation": "Tier1GateResult"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_results",
    "name": "build_result_artifacts",
    "parameters": [
      {
        "name": "inputs",
        "annotation": "S11Inputs"
      },
      {
        "name": "tier1_result",
        "annotation": "Tier1GateResult"
      },
      {
        "name": "reproducibility_inputs",
        "annotation": "ReproducibilityInputs"
      },
      {
        "name": "seal",
        "annotation": "SealResult"
      },
      {
        "name": "s8",
        "annotation": "S8Capture"
      }
    ],
    "return_annotation": "ResultArtifacts",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_package",
    "name": "create_s13_package",
    "parameters": [
      {
        "name": "s9_commit_sha",
        "annotation": "str"
      },
      {
        "name": "result_artifacts",
        "annotation": "ResultArtifacts"
      },
      {
        "name": "s8",
        "annotation": "S8Capture"
      }
    ],
    "return_annotation": "PackageResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_gate",
    "name": "evaluate_tier1_preentry",
    "parameters": [
      {
        "name": "inputs",
        "annotation": "Tier1EvaluationInputs"
      }
    ],
    "return_annotation": "Tier1GateResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_gate",
    "name": "evaluate_tier1_generation",
    "parameters": [
      {
        "name": "inputs",
        "annotation": "Tier1EvaluationInputs"
      },
      {
        "name": "retained",
        "annotation": "RetainedEventEvidence"
      }
    ],
    "return_annotation": "Tier1GateResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_gate",
    "name": "evaluate_tier1_later_audit",
    "parameters": [
      {
        "name": "inputs",
        "annotation": "Tier1EvaluationInputs"
      },
      {
        "name": "retained",
        "annotation": "RetainedEventEvidence"
      }
    ],
    "return_annotation": "Tier1GateResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_gate",
    "name": "evaluate_row21_retained_reverification",
    "parameters": [
      {
        "name": "retained",
        "annotation": "RetainedRow21Inputs"
      }
    ],
    "return_annotation": "Tier1RowResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_orchestrator",
    "name": "EvidenceDagOrchestrator.evaluate_generation_gate",
    "parameters": [],
    "return_annotation": "Tier1GateResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_orchestrator",
    "name": "EvidenceDagOrchestrator.serialize_s11_with",
    "parameters": [
      {
        "name": "gate",
        "annotation": "Tier1GateResult"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "macos_stage_b_evidence_orchestrator",
    "name": "EvidenceDagOrchestrator.verify_retained_package",
    "parameters": [
      {
        "name": "retained",
        "annotation": "RetainedRow21Inputs"
      }
    ],
    "return_annotation": "Tier1RowResult",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PUBLIC"
  },
  {
    "module": "scripts.stage-b-evidence-dag",
    "name": "build_parser",
    "parameters": [],
    "return_annotation": "argparse.ArgumentParser",
    "governed_error_type": "ValueError",
    "visibility": "PUBLIC"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "parse_stage_b_shell_contract",
    "parameters": [
      {
        "name": "text",
        "annotation": "str"
      }
    ],
    "return_annotation": "ShellContract",
    "governed_error_type": "ShellContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "contract_source_reaches_sink",
    "parameters": [
      {
        "name": "contract",
        "annotation": "ShellContract"
      },
      {
        "name": "source_variable",
        "annotation": "str"
      },
      {
        "name": "sink_kind",
        "annotation": "ShellSinkKind"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "load_plan_contract",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "PlanContractFixture",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture.expand_expected_new_test_node_ids",
    "parameters": [],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture.enum_values",
    "parameters": [
      {
        "name": "name",
        "annotation": "str"
      }
    ],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture.effect_scanner_source_contract_bytes",
    "parameters": [],
    "return_annotation": "bytes",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "TmpGitRepo.commit_file",
    "parameters": [
      {
        "name": "path",
        "annotation": "str"
      },
      {
        "name": "data",
        "annotation": "bytes"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "TmpGitRepo.write_worktree",
    "parameters": [
      {
        "name": "path",
        "annotation": "str"
      },
      {
        "name": "data",
        "annotation": "bytes"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "TmpGitRepo.commit_s10_generation_ids",
    "parameters": [
      {
        "name": "generation_ids",
        "annotation": "tuple[str, ...]"
      }
    ],
    "return_annotation": "str",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "TmpGitRepo.commit_required_authority_paths",
    "parameters": [],
    "return_annotation": "str",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ResultBuilder.create_s10_before_s12",
    "parameters": [],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "execute_handle_forgery_case",
    "parameters": [
      {
        "name": "case",
        "annotation": "OpaqueHandleForgeryCase"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "build_structural_case_bytes",
    "parameters": [
      {
        "name": "case",
        "annotation": "StructuralCommandCase"
      }
    ],
    "return_annotation": "bytes",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "execute_header64_case",
    "parameters": [
      {
        "name": "case",
        "annotation": "Header64Case"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "execute_fat_structure_case",
    "parameters": [
      {
        "name": "case",
        "annotation": "FatStructureCase"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "macos_stage_b_evidence_git",
    "name": "_discover_repository_root_from_module_location",
    "parameters": [],
    "return_annotation": "Path",
    "governed_error_type": "EvidenceDagError",
    "visibility": "PRIVATE_SECURITY"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "execute_stable_census_construction",
    "parameters": [
      {
        "name": "spec",
        "annotation": "StableCensusConstructionSpec"
      }
    ],
    "return_annotation": "tuple[StableCensusObservation, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "compare_stable_census",
    "parameters": [
      {
        "name": "observations",
        "annotation": "tuple[StableCensusObservation, ...]"
      },
      {
        "name": "expectation",
        "annotation": "StableCensusExpectation"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "inspect_oracle_request",
    "parameters": [
      {
        "name": "request",
        "annotation": "OracleInspectionRequest"
      }
    ],
    "return_annotation": "OracleInspectionObservation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "compare_oracle_observation",
    "parameters": [
      {
        "name": "observation",
        "annotation": "OracleInspectionObservation"
      },
      {
        "name": "expectation",
        "annotation": "OracleInspectionExpectation"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "construction_for",
    "parameters": [
      {
        "name": "normative_row",
        "annotation": "NormativeAdversarialRow"
      }
    ],
    "return_annotation": "AdversarialConstructionSpec",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "expectation_for",
    "parameters": [
      {
        "name": "row_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "AdversarialExpectation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "build_adversarial_fixture",
    "parameters": [
      {
        "name": "builder_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "AdversarialFixture",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "apply_adversarial_action",
    "parameters": [
      {
        "name": "action_kind",
        "annotation": "AdversarialActionKind"
      },
      {
        "name": "action_args",
        "annotation": "tuple[FixtureMutationOp, ...]"
      },
      {
        "name": "fixture",
        "annotation": "AdversarialFixture"
      }
    ],
    "return_annotation": "AdversarialFixture",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "observe_post_mutation",
    "parameters": [
      {
        "name": "fixture",
        "annotation": "AdversarialFixture"
      },
      {
        "name": "invariant",
        "annotation": "PostMutationInvariant"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "install_observation_probe",
    "parameters": [
      {
        "name": "probe_id",
        "annotation": "str"
      },
      {
        "name": "governing_callable_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "ObservationProbeHandle",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "invoke_governing_adversarial_callable",
    "parameters": [
      {
        "name": "request",
        "annotation": "AdversarialExecutionRequest"
      },
      {
        "name": "fixture",
        "annotation": "AdversarialFixture"
      },
      {
        "name": "probe",
        "annotation": "ObservationProbeHandle"
      }
    ],
    "return_annotation": "AdversarialExecutionObservation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "compare_adversarial_observation",
    "parameters": [
      {
        "name": "observation",
        "annotation": "AdversarialExecutionObservation"
      },
      {
        "name": "expectation",
        "annotation": "AdversarialExpectation"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "scan_production_effects",
    "parameters": [
      {
        "name": "policy",
        "annotation": "EffectPolicy"
      }
    ],
    "return_annotation": "EffectScanResult",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "census_construction",
    "parameters": [
      {
        "name": "case_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "StableCensusConstructionSpec",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "census_expectation",
    "parameters": [
      {
        "name": "case_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "StableCensusExpectation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "expectation_for_subaction",
    "parameters": [
      {
        "name": "expectation",
        "annotation": "StableCensusExpectation"
      },
      {
        "name": "subaction_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "StableCensusExpectation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "run_census_cheat_falsifier",
    "parameters": [
      {
        "name": "cheat",
        "annotation": "str"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "oracle_expectation_for",
    "parameters": [
      {
        "name": "surface_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "OracleInspectionExpectation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "positive_falsifier_for",
    "parameters": [
      {
        "name": "mechanism",
        "annotation": "OracleInspectionMechanism"
      }
    ],
    "return_annotation": "tuple[OracleInspectionRequest, SyntheticSourceTree]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "inspect_oracle_request_against_tree",
    "parameters": [
      {
        "name": "request",
        "annotation": "OracleInspectionRequest"
      },
      {
        "name": "tree",
        "annotation": "SyntheticSourceTree"
      }
    ],
    "return_annotation": "OracleInspectionObservation",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "observation_has_forbidden_match",
    "parameters": [
      {
        "name": "observation",
        "annotation": "OracleInspectionObservation"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_oracle_manifest",
    "name": "oracle_echo_inspector_falsifier",
    "parameters": [],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "run_stage_replacement_falsifier",
    "parameters": [
      {
        "name": "stage",
        "annotation": "str"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "plan_family_rule",
    "parameters": [
      {
        "name": "family",
        "annotation": "ShellCommandFamily"
      }
    ],
    "return_annotation": "ShellCommandFamilyRule",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "derived_family_sinks",
    "parameters": [
      {
        "name": "contract",
        "annotation": "ShellContract"
      },
      {
        "name": "family",
        "annotation": "ShellCommandFamily"
      }
    ],
    "return_annotation": "tuple[tuple[int, ShellSinkKind], ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture.protocol",
    "parameters": [
      {
        "name": "name",
        "annotation": "str"
      }
    ],
    "return_annotation": "ExpectedProtocol",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "ExactOutcomeRecorder.snapshot",
    "parameters": [],
    "return_annotation": "dict[str, object]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "PlanContractFixture.unbound_fixture_references",
    "parameters": [],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "exact_protocol_shape",
    "parameters": [
      {
        "name": "protocol_type",
        "annotation": "type"
      }
    ],
    "return_annotation": "ExpectedProtocol",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "exercise_recorder_case",
    "parameters": [
      {
        "name": "case_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "HistoricalOutcome",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "scan_synthetic_effect_source",
    "parameters": [
      {
        "name": "source",
        "annotation": "str"
      }
    ],
    "return_annotation": "EffectScanResult",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "validate_controlled_run_ledger",
    "parameters": [
      {
        "name": "events",
        "annotation": "tuple[CommandLedgerEvent, ...]"
      },
      {
        "name": "phase",
        "annotation": "str"
      },
      {
        "name": "implementation_base_sha",
        "annotation": "str"
      },
      {
        "name": "approved_plan_blob_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "validate_changed_path_set",
    "parameters": [
      {
        "name": "changed_paths",
        "annotation": "tuple[str, ...]"
      },
      {
        "name": "phase",
        "annotation": "str"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "prohibited_generated_artifact_present",
    "parameters": [
      {
        "name": "before",
        "annotation": "tuple[str, ...]"
      },
      {
        "name": "after",
        "annotation": "tuple[str, ...]"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv2",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      },
      {
        "name": "baseline_path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv3",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv4",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      },
      {
        "name": "ledger_path",
        "annotation": "Path"
      },
      {
        "name": "before_snapshot_path",
        "annotation": "Path"
      },
      {
        "name": "phase",
        "annotation": "str"
      },
      {
        "name": "receipt_path",
        "annotation": "Path | None"
      },
      {
        "name": "implementation_base_sha",
        "annotation": "str"
      },
      {
        "name": "approved_plan_blob_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv5",
    "parameters": [
      {
        "name": "base_sha",
        "annotation": "str"
      },
      {
        "name": "phase",
        "annotation": "str"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv6",
    "parameters": [
      {
        "name": "repository_root",
        "annotation": "Path"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_fv8",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "effect_policy_from_mapping",
    "parameters": [
      {
        "name": "mapping",
        "annotation": "Mapping[str, object]"
      }
    ],
    "return_annotation": "EffectPolicy",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "validate_command_event_pair",
    "parameters": [
      {
        "name": "start",
        "annotation": "CommandLedgerEvent"
      },
      {
        "name": "end",
        "annotation": "CommandLedgerEvent"
      },
      {
        "name": "allowed",
        "annotation": "AllowedControlledCommand"
      },
      {
        "name": "expected_control_inputs",
        "annotation": "tuple[tuple[str, str], ...]"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "validate_source_form_registry",
    "parameters": [
      {
        "name": "registry",
        "annotation": "tuple[SyntheticForbiddenSourceForm, ...]"
      },
      {
        "name": "used_ids",
        "annotation": "tuple[str, ...]"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "source_form_for",
    "parameters": [
      {
        "name": "source_form_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "SyntheticForbiddenSourceForm",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "used_insert_source_form_ids",
    "parameters": [
      {
        "name": "constructions",
        "annotation": "tuple[AdversarialConstructionSpec, ...]"
      }
    ],
    "return_annotation": "tuple[str, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "observe_source_form_property",
    "parameters": [
      {
        "name": "fixture",
        "annotation": "AdversarialFixture"
      },
      {
        "name": "source_form",
        "annotation": "SyntheticForbiddenSourceForm"
      }
    ],
    "return_annotation": "bool",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "construction_for_id",
    "parameters": [
      {
        "name": "row_id",
        "annotation": "str"
      }
    ],
    "return_annotation": "AdversarialConstructionSpec",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_adversarial_cases",
    "name": "insert_source_form_into_neutral_fixture",
    "parameters": [
      {
        "name": "source_form",
        "annotation": "SyntheticForbiddenSourceForm"
      }
    ],
    "return_annotation": "AdversarialFixture",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "exact_ledger_pair_for",
    "parameters": [
      {
        "name": "allowed",
        "annotation": "AllowedControlledCommand"
      },
      {
        "name": "control_inputs",
        "annotation": "tuple[tuple[str, str], ...] | None"
      }
    ],
    "return_annotation": "tuple[CommandLedgerEvent, CommandLedgerEvent]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "write_effect_policy_variant",
    "parameters": [
      {
        "name": "tmp_path",
        "annotation": "Path"
      },
      {
        "name": "contract",
        "annotation": "PlanContractFixture"
      },
      {
        "name": "mode",
        "annotation": "str"
      },
      {
        "name": "field",
        "annotation": "str"
      }
    ],
    "return_annotation": "Path",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_approved_plan_identity",
    "parameters": [
      {
        "name": "repository_root",
        "annotation": "Path"
      },
      {
        "name": "plan_path",
        "annotation": "Path"
      },
      {
        "name": "approved_plan_blob_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_interface_manifest",
    "name": "verify_effect_scanner_source_contract",
    "parameters": [
      {
        "name": "plan_path",
        "annotation": "Path"
      },
      {
        "name": "scanner_path",
        "annotation": "Path"
      }
    ],
    "return_annotation": "None",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "exact_controlled_run_ledger_for",
    "parameters": [
      {
        "name": "contract",
        "annotation": "PlanContractFixture"
      },
      {
        "name": "phase",
        "annotation": "str"
      },
      {
        "name": "implementation_base_sha",
        "annotation": "str"
      },
      {
        "name": "approved_plan_blob_sha",
        "annotation": "str"
      }
    ],
    "return_annotation": "tuple[CommandLedgerEvent, ...]",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  },
  {
    "module": "tests.gate0.unit.evidence_dag_fixtures",
    "name": "write_scanner_contract_fixture",
    "parameters": [
      {
        "name": "tmp_path",
        "annotation": "Path"
      },
      {
        "name": "source",
        "annotation": "bytes"
      }
    ],
    "return_annotation": "Path",
    "governed_error_type": "TestContractError",
    "visibility": "TEST_SUPPORT"
  }
]
~~~

### 5.4 Protocol manifest

~~~json[
  {
    "module": "macos_stage_b_evidence_runtime",
    "name": "CensusFS",
    "visibility": "PUBLIC",
    "methods": [
      {
        "name": "list_entries",
        "parameters": [
          {
            "name": "directory",
            "annotation": "PurePath"
          }
        ],
        "return_annotation": "tuple[FSEntryObservation, ...]"
      },
      {
        "name": "lstat_kind",
        "parameters": [
          {
            "name": "path",
            "annotation": "PurePath"
          }
        ],
        "return_annotation": "EntryKind"
      },
      {
        "name": "readlink_bytes",
        "parameters": [
          {
            "name": "path",
            "annotation": "PurePath"
          }
        ],
        "return_annotation": "bytes"
      },
      {
        "name": "read_file_bytes",
        "parameters": [
          {
            "name": "path",
            "annotation": "PurePath"
          }
        ],
        "return_annotation": "bytes"
      },
      {
        "name": "path_exists",
        "parameters": [
          {
            "name": "path",
            "annotation": "PurePath"
          }
        ],
        "return_annotation": "bool"
      }
    ],
    "classification": "PROTOCOL"
  }
]
~~~

### 5.5 Exact production constants and closed sets

- `MEASUREMENT_ONLY_DIGEST_KEYS=frozenset({"requirements_blob_sha256","cms_signature_blob_sha256"})`.
- Header64 table row count = 8; numeric load-command rows = 54; accepted structural rows = 43.
- `ACCEPTED_COMMAND_VALUES` is the exact 43-value accepted numeric set from Rev18; `REJECTED_COMMAND_VALUES` is the exact 11-value rejected set; their union is the exact 54-row table.
- `PATH_CANONICALIZATION_MAX_SYMLINK_HOPS_V1=32`.
- N4a retained primitive field order is exactly `format, renderer_input_sha256, renderer_input_octets, signer_entitlements_sha256, signer_entitlements_octets`.
- `OPTIONAL_TOOL_SEED_REGISTRY_V1=()`.
- `M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` has exactly one parameter `data: bytes`.

### 5.6 Authority / generation identity

`derive_generation_identity(authority: AuthorityTuple) -> str` preserves the v3-approved four semantic H inputs only: base controller commit, applicable spec blob, applicable plan blob, generation ordinal. `design_record_blob` remains authority/P17 material but is not added to H. All malformed identities/ordinals fail `GENERATION_IDENTITY_COLLISION` before the hash leaf.

### 5.7 Verified repository context

Production retains one fixed private zero-argument repository-root discovery leaf:

`_discover_repository_root_from_module_location() -> Path`

`verify_repository_context(authority, evaluation_commit)` always calls that leaf. It exposes no raw-root parameter, config selector, environment selector or dependency-injection hook. It then performs the already-frozen bounded Git checks, normalized module-derived root == Git top-level check, symlink rejection, device/inode binding, evaluation/base-controller commit binding, generation binding and exact-instance registration.

Synthetic tests may monkeypatch only that exact private call site inside the test process to return `TmpGitRepo.root`; the fixture then calls the real production `verify_repository_context`. The monkeypatch is never retained and is not Gate evidence.

### 5.8 Anchored S1 and exact-instance opaque handles

`resolve_anchored_s1(repository_context, anchor)` verifies the registered repository context, verifies S7, reads exact `S1.json` and its blob id from S7, constructs the immutable S1 internally, and registers exactly that `AnchoredS1Handle` instance. N4a accepts the handle, not a raw S1.

The boundary extracts S1 only through `_extract_registered_anchored_s1(handle, repository_context)`. Equality of fields/bytes/digest is insufficient; exact registered instance identity and parent context identity are mandatory.

The same instance-registration rule applies to `VerifiedRepositoryContext`, `AnchoredS1Handle`, `VerifierOwnedSealedDestination`, `VerifierOwnedSigningIdentity`, `VerifierOwnedBuildContext`, `N4ASealCapability`, and `N4ATransientApplication`. Factory tokens/guards are defense-in-depth and are never sufficient authority by themselves. Validation requires exact type, exact registered instance, current generation, valid lifecycle, parent context identity, and unused state where applicable.

`_create_verifier_owned_build_context(repository_context, anchor)` derives:
- signing identity only by reading the exact anchored S4 under S7;
- scratch root only as `repository_context.canonical_root/.stage-b-build/<generation_identity>`;
- private S2 only below that scratch root;
- sealed destination only as `<scratch>/StageBSandboxRunner.app`.
It accepts no raw root, destination, application path, signing string, factory seed, or guard.

### 5.9 Signed-image projection and row-21 production input

`project_signed_image(image: SyntheticSignedImage) -> SignedImageProjection` is exact. Requirements and CMS preimages are absent from the returned projection, their only lawful Mode-B digests are in `measurement_digests`, and special slots -4/-6 remain structural all-zero state outside P20.

Production row-21 takes `RetainedRow21Inputs`. Pytest owns a separate `RetainedRow21Fixture` wrapper whose `.inputs` field is that production type; production never imports the fixture type.

### 5.10 Orchestrator

`EvidenceDagOrchestrator` is a concrete production class with the exact fields/methods in the manifest. It stores typed outputs only, cannot retarget N5, cannot expose build/sign/live commands through the CLI, and cannot enter Generation B while the baseline is `NOT_OBSERVED`.

### 5.11 FV8 source of truth

The four machine blocks in §§5.1–5.4 are the complete plan-owned FV8 source of truth: enums, dataclasses/types, callables/interfaces, and protocols. Implementation mirrors are never the oracle. FV8 compares exact enum order; dataclass fields/order/types/frozen state; callable parameter names/order/annotations/returns/error/visibility; and protocol module/name/classification/method order/parameter names/order/annotations/returns. Missing, extra or mismatched protocol method fails.

## 6. Complete one-owner test helper / fixture manifest

`tests/gate0/conftest.py` remains byte-unchanged. Every new pytest fixture starts `evidence_dag_`. Every helper has exactly one owner.

~~~json
[
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_authority",
    "signature": "evidence_dag_authority() -> AuthorityTuple",
    "semantics": "four exact lower-hex repository identities plus lawful ordinal 1; no raw authority fixture name",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "mutate_lower_hex",
    "signature": "mutate_lower_hex(value: str) -> str",
    "semantics": "change exactly one lowercase hex nibble, preserve length",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "P2_INVALID_CASES",
    "signature": "P2_INVALID_CASES: tuple[P2InvalidCase, ...]",
    "semantics": "exact ten §8.1 malformed/overflow cases",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "make_thin_arm64",
    "signature": "make_thin_arm64(*, ncmds: int, commands: bytes, filetype: int = 2, flags: int = 0, reserved: int = 0, cpusubtype: int = 0) -> bytes",
    "semantics": "exact 32-byte Header64 followed by commands",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_minimal_command_fixture",
    "signature": "build_minimal_command_fixture(command_value: int) -> bytes",
    "semantics": "minimal valid accepted structural command; rejected value raises ValueError",
    "governed_error_type": "ValueError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "exercise_command_fixture",
    "signature": "exercise_command_fixture(command_bytes: bytes) -> CommandExerciseResult",
    "semantics": "wrap one command in one minimal thin arm64 image and invoke production parser",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "chain_fs",
    "signature": "chain_fs(n: int, *, host_limit: int | None = None) -> SyntheticCensusFS",
    "semantics": "exactly n symlink expansions before one regular file",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "cycle_fs",
    "signature": "cycle_fs(repeat_at_hop: int = 2) -> SyntheticCensusFS",
    "semantics": "repeat exact pathname at requested hop",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "competing_hop_cycle_fs",
    "signature": "competing_hop_cycle_fs() -> SyntheticCensusFS",
    "semantics": "32 successful expansions then already-seen symlink pathname",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_two_root_fixture",
    "signature": "build_census_two_root_fixture() -> CensusCaseFixture",
    "semantics": "base+venv roots, nested real dirs, regular files and stable native/non-native members",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_directory_symlink_fixture",
    "signature": "build_census_directory_symlink_fixture() -> CensusCaseFixture",
    "semantics": "directory symlink with traversal sentinel",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_file_symlink_fixture",
    "signature": "build_census_file_symlink_fixture() -> CensusCaseFixture",
    "semantics": "file symlink with exact raw target bytes and canonical target",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_ab_mutation_fixture",
    "signature": "build_census_ab_mutation_fixture() -> CensusCaseFixture",
    "semantics": "independent A/B views with mutation hook",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_native_mutation_fixture",
    "signature": "build_census_native_mutation_fixture() -> CensusCaseFixture",
    "semantics": "Census-A native bytes plus independent Census-B mutation",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_transition_fixture",
    "signature": "build_census_transition_fixture() -> CensusCaseFixture",
    "semantics": "controlled NON_NATIVE/NATIVE_MEMBER transitions",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_census_transient_state_fixture",
    "signature": "build_census_transient_state_fixture() -> CensusCaseFixture",
    "semantics": "traceable transient namespace/raw-link state with durable serialization sentinel",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "execute_stable_census_construction",
    "signature": "execute_stable_census_construction(spec: StableCensusConstructionSpec) -> tuple[StableCensusObservation, ...]",
    "semantics": "fresh fixture per subaction -> action -> real production census -> independent observation; no expectation access",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "compare_stable_census",
    "signature": "compare_stable_census(observations: tuple[StableCensusObservation, ...], expectation: StableCensusExpectation) -> bool",
    "semantics": "external comparator only",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "expectation_for_subaction",
    "signature": "expectation_for_subaction(expectation: StableCensusExpectation, subaction_id: str) -> StableCensusExpectation",
    "semantics": "return one-subcase comparison truth; never passed to execution",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "run_census_cheat_falsifier",
    "signature": "run_census_cheat_falsifier(cheat: str) -> bool",
    "semantics": "replace one execution stage with named cheat and return comparator result; every defined cheat must be False",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_tmp_git_repo",
    "signature": "evidence_dag_tmp_git_repo(tmp_path: Path) -> TmpGitRepo",
    "semantics": "isolated no-remote repository with deterministic author metadata",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_frozen_s1",
    "signature": "evidence_dag_frozen_s1() -> FrozenArtifact",
    "semantics": "minimal canonical S1 value used only before verifier anchoring",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_frozen_s2",
    "signature": "evidence_dag_frozen_s2(evidence_dag_frozen_s1: FrozenArtifact) -> FrozenArtifact",
    "semantics": "renderer-produced S2 from exact fixture S1",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_snapshot",
    "signature": "evidence_dag_snapshot() -> SnapshotFixture",
    "semantics": "verifier/producer inputs plus one-read mutable native source",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_s7_anchor",
    "signature": "evidence_dag_s7_anchor(evidence_dag_tmp_git_repo: TmpGitRepo, evidence_dag_frozen_s1: FrozenArtifact, evidence_dag_frozen_s2: FrozenArtifact) -> S7AnchorCreateResult",
    "semantics": "test-support-only exact S1/S2/S3/S4 commit created directly inside evidence_dag_tmp_git_repo; it does not call or require the production Task-7 anchor module",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "anchor_mutation_fixture",
    "signature": "anchor_mutation_fixture(mutation: Literal['missing','extra','changed','wrong_parent']) -> S7VerificationResult",
    "semantics": "one exact S7 falsifier",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_verified_repository_context",
    "signature": "evidence_dag_verified_repository_context(evidence_dag_tmp_git_repo: TmpGitRepo, evidence_dag_s7_anchor: S7AnchorCreateResult, evidence_dag_authority: AuthorityTuple, monkeypatch: pytest.MonkeyPatch) -> VerifiedRepositoryContext",
    "semantics": "patch only macos_stage_b_evidence_git._discover_repository_root_from_module_location to TmpGitRepo.root, then invoke real verify_repository_context at evidence_dag_s7_anchor.commit_sha; evaluation commit therefore equals exact S7 commit",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_anchored_s1",
    "signature": "evidence_dag_anchored_s1(evidence_dag_verified_repository_context: VerifiedRepositoryContext, evidence_dag_s7_anchor: S7AnchorCreateResult) -> AnchoredS1Handle",
    "semantics": "registered exact S1 handle resolved from S7/Git",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_build_context",
    "signature": "evidence_dag_build_context(evidence_dag_verified_repository_context: VerifiedRepositoryContext, evidence_dag_s7_anchor: S7AnchorCreateResult) -> VerifierOwnedBuildContext",
    "semantics": "registered destination and signing identity derived only from verified context/S7",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_n4a_result",
    "signature": "evidence_dag_n4a_result() -> N4AProductionResult",
    "semantics": "lawful registered N4a handles with private process leaf substituted",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_synthetic_n4a_result",
    "signature": "evidence_dag_synthetic_n4a_result() -> N4AProductionResult",
    "semantics": "pure synthetic boundary result; no build/sign process",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_signed_image",
    "signature": "evidence_dag_signed_image() -> SyntheticSignedImage",
    "semantics": "complete synthetic code-signature image with requirements/CMS and slots -4/-6",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_retention",
    "signature": "evidence_dag_retention() -> RetentionFixture",
    "semantics": "Mode-A, exact two Mode-B candidates and foreign digest",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_reference_case",
    "signature": "build_reference_case(reference_class: ReferenceClass) -> tuple[EvidenceReference, ReferenceResolutionContext, Literal['a','b','c','d']]",
    "semantics": "one lawful concrete P19 case per class",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_result_builder",
    "signature": "evidence_dag_result_builder() -> ResultBuilder",
    "semantics": "typed S11/reproducibility inputs with out-of-order refusal hook",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_retained_row21",
    "signature": "evidence_dag_retained_row21() -> RetainedRow21Fixture",
    "semantics": "pytest wrapper whose .inputs is production RetainedRow21Inputs; no host/app path",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_orchestrator",
    "signature": "evidence_dag_orchestrator() -> EvidenceDagOrchestrator",
    "semantics": "non-live orchestrator with typed synthetic inputs",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_cli_parser",
    "signature": "evidence_dag_cli_parser() -> argparse.ArgumentParser",
    "semantics": "parser from scripts/stage-b-evidence-dag.py without command execution",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "parse_stage_b_shell_contract",
    "signature": "parse_stage_b_shell_contract(text: str) -> ShellContract",
    "semantics": "bounded fail-closed shell grammar and data-flow IR",
    "governed_error_type": "ShellContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_script_text",
    "signature": "evidence_dag_script_text() -> str",
    "semantics": "UTF-8 text of scripts/stage-b-build-app.sh",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_repo_root",
    "signature": "evidence_dag_repo_root() -> Path",
    "semantics": "test discovery root only; never passed as production repository authority",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "NORMATIVE_ADVERSARIAL_ROWS",
    "signature": "NORMATIVE_ADVERSARIAL_ROWS: tuple[NormativeAdversarialRow, ...]",
    "semantics": "exact 316 rows parsed from pinned spec blob in table order",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "construction_for",
    "signature": "construction_for(normative_row: NormativeAdversarialRow) -> AdversarialConstructionSpec",
    "semantics": "exact lookup in plan-owned 316 construction records; no expected fields",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "expectation_for",
    "signature": "expectation_for(row_id: str) -> AdversarialExpectation",
    "semantics": "exact separate expectation lookup",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "execute_adversarial_construction",
    "signature": "execute_adversarial_construction(spec: AdversarialConstructionSpec) -> AdversarialExecutionObservation",
    "semantics": "builder/action/mutation observer/probe/governing call receive construction only",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "contract_source_reaches_sink",
    "signature": "contract_source_reaches_sink(contract: ShellContract, source_variable: str, sink_kind: ShellSinkKind) -> bool",
    "semantics": "transitive assignment graph reachability from exact source variable to exact sink kind",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "evidence_dag_plan_contract",
    "signature": "evidence_dag_plan_contract() -> PlanContractFixture",
    "semantics": "load exact externally blob-approved frozen V7 plan and expose machine manifests",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "load_plan_contract",
    "signature": "load_plan_contract(plan_path: Path) -> PlanContractFixture",
    "semantics": "extract exact V7 machine blocks and source contracts; no implementation fallback",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "census_construction",
    "signature": "census_construction(case_id: str) -> StableCensusConstructionSpec",
    "semantics": "exact construction lookup for CENSUS-01..21",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "census_expectation",
    "signature": "census_expectation(case_id: str) -> StableCensusExpectation",
    "semantics": "separate expectation lookup",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "STRUCTURAL_COMMAND_CASES",
    "signature": "STRUCTURAL_COMMAND_CASES: tuple[StructuralCommandCase, ...]",
    "semantics": "exact 43×3 plus exact 15 fourth zero-padding/reserved falsifiers",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "HEADER64_CASES",
    "signature": "HEADER64_CASES: tuple[Header64Case, ...]",
    "semantics": "exact eight Header64 policy cases",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "FAT_STRUCTURE_CASES",
    "signature": "FAT_STRUCTURE_CASES: tuple[FatStructureCase, ...]",
    "semantics": "exact twelve FAT structural cases",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "HANDLE_FORGERY_CASES",
    "signature": "HANDLE_FORGERY_CASES: tuple[OpaqueHandleForgeryCase, ...]",
    "semantics": "exact seven handle kinds × eight mutation kinds from §7",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "execute_handle_forgery_case",
    "signature": "execute_handle_forgery_case(case: OpaqueHandleForgeryCase) -> None",
    "semantics": "construct lawful handle, apply one mutation, require rejection before governed leaf",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "ORACLE_INSPECTION_REQUESTS",
    "signature": "ORACLE_INSPECTION_REQUESTS: tuple[OracleInspectionRequest, ...]",
    "semantics": "exact A01–A07/B01–B16/C01–C07 expectation-free requests",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "ORACLE_INSPECTION_EXPECTATIONS",
    "signature": "ORACLE_INSPECTION_EXPECTATIONS: tuple[OracleInspectionExpectation, ...]",
    "semantics": "exact separate 30-result comparison truth",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "inspect_oracle_request",
    "signature": "inspect_oracle_request(request: OracleInspectionRequest) -> OracleInspectionObservation",
    "semantics": "execute exact mechanism without expectation access",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "oracle_expectation_for",
    "signature": "oracle_expectation_for(surface_id: str) -> OracleInspectionExpectation",
    "semantics": "exact separate expectation lookup",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "compare_oracle_observation",
    "signature": "compare_oracle_observation(observation: OracleInspectionObservation, expectation: OracleInspectionExpectation) -> bool",
    "semantics": "external comparator only",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "positive_falsifier_for",
    "signature": "positive_falsifier_for(mechanism: OracleInspectionMechanism) -> tuple[OracleInspectionRequest, SyntheticSourceTree]",
    "semantics": "one synthetic positive forbidden condition for each mechanism family",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "inspect_oracle_request_against_tree",
    "signature": "inspect_oracle_request_against_tree(request: OracleInspectionRequest, tree: SyntheticSourceTree) -> OracleInspectionObservation",
    "semantics": "same inspector against synthetic source tree; no expectation",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "observation_has_forbidden_match",
    "signature": "observation_has_forbidden_match(observation: OracleInspectionObservation) -> bool",
    "semantics": "true only on concrete observed forbidden match/reachability",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_oracle_manifest.py",
    "name": "oracle_echo_inspector_falsifier",
    "signature": "oracle_echo_inspector_falsifier() -> bool",
    "semantics": "replace inspector with constant-ABSENT observation; comparator must return False",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "build_structural_case_bytes",
    "signature": "build_structural_case_bytes(case: StructuralCommandCase) -> bytes",
    "semantics": "materialize exact structural variant from plan-owned case",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "execute_header64_case",
    "signature": "execute_header64_case(case: Header64Case) -> bool",
    "semantics": "invoke production parser on exact Header64 case; return observed acceptance",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "execute_fat_structure_case",
    "signature": "execute_fat_structure_case(case: FatStructureCase) -> bool",
    "semantics": "invoke production parser on exact FAT case; return observed acceptance",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "build_adversarial_fixture",
    "signature": "build_adversarial_fixture(builder_id: str) -> AdversarialFixture",
    "semantics": "neutral domain fixture with mutation_epoch 0; no expectation/action access",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "apply_adversarial_action",
    "signature": "apply_adversarial_action(action_kind: AdversarialActionKind, action_args: tuple[FixtureMutationOp, ...], fixture: AdversarialFixture) -> AdversarialFixture",
    "semantics": "closed typed action only; no expectation access",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "install_observation_probe",
    "signature": "install_observation_probe(probe_id: str, governing_callable_id: str) -> ObservationProbeHandle",
    "semantics": "probe configuration only; no expected fields",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "invoke_governing_adversarial_callable",
    "signature": "invoke_governing_adversarial_callable(request: AdversarialExecutionRequest, fixture: AdversarialFixture, probe: ObservationProbeHandle) -> AdversarialExecutionObservation",
    "semantics": "execute real governing callable/static inspection; request expectation-free",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "observe_post_mutation",
    "signature": "observe_post_mutation(fixture: AdversarialFixture, invariant: PostMutationInvariant) -> bool",
    "semantics": "read fixture state directly before governing call; do not trust action receipt",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "compare_adversarial_observation",
    "signature": "compare_adversarial_observation(observation: AdversarialExecutionObservation, expectation: AdversarialExpectation) -> bool",
    "semantics": "external comparator only",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "run_stage_replacement_falsifier",
    "signature": "run_stage_replacement_falsifier(stage: str) -> bool",
    "semantics": "replace exact named pipeline stage by no-op/echo/wrong behavior; full comparator must return False",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "scan_production_effects",
    "signature": "scan_production_effects(policy: EffectPolicy) -> EffectScanResult",
    "semantics": "exact §10.3.1 plan-owned source region; all effect decisions read only EffectPolicy fields; no implementation-only safe rule",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "SHELL_COMMAND_FAMILY_RULES",
    "signature": "SHELL_COMMAND_FAMILY_RULES: tuple[ShellCommandFamilyRule, ...]",
    "semantics": "exact §8.10 command-to-sink rules",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "plan_family_rule",
    "signature": "plan_family_rule(family: ShellCommandFamily) -> ShellCommandFamilyRule",
    "semantics": "exact rule lookup",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "derived_family_sinks",
    "signature": "derived_family_sinks(contract: ShellContract, family: ShellCommandFamily) -> tuple[tuple[int, ShellSinkKind], ...]",
    "semantics": "return sinks mechanically derived by parser for exact family",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "ExactOutcomeRecorder",
    "signature": "ExactOutcomeRecorder()",
    "semantics": "exact §4.1 pytest plugin; tryfirst collection snapshot; single terminal outcome; ERROR distinct from FAILED",
    "governed_error_type": "RuntimeError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "exact_protocol_shape",
    "signature": "exact_protocol_shape(protocol_type: type) -> ExpectedProtocol",
    "semantics": "strip self/cls, normalize annotations and method order exactly for FV8",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "exercise_recorder_case",
    "signature": "exercise_recorder_case(case_id: str) -> HistoricalOutcome",
    "semantics": "drive ExactOutcomeRecorder with exact synthetic pytest report sequence for the named terminal case",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "scan_synthetic_effect_source",
    "signature": "scan_synthetic_effect_source(source: str) -> EffectScanResult",
    "semantics": "run the same closed effect scanner over one synthetic module",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "validate_controlled_run_ledger",
    "signature": "validate_controlled_run_ledger(events: tuple[CommandLedgerEvent, ...], phase: str, implementation_base_sha: str, approved_plan_blob_sha: str) -> bool",
    "semantics": "validate exact schema/order/pairs/allowed-command set plus authorized base/blob, canonical V7 plan path and exact PRE/POST phase",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "validate_changed_path_set",
    "signature": "validate_changed_path_set(changed_paths: tuple[str, ...], phase: str) -> bool",
    "semantics": "exact equality with PRE or POST plan-owned path tuple",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "prohibited_generated_artifact_present",
    "signature": "prohibited_generated_artifact_present(before: tuple[str, ...], after: tuple[str, ...]) -> bool",
    "semantics": "compare snapshots against exact §4 prohibited generated-path patterns",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv2",
    "signature": "verify_fv2(plan_path: Path, baseline_path: Path) -> None",
    "semantics": "run full historical suite with ExactOutcomeRecorder and enforce exact §10.2 baseline/additive-set law",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv3",
    "signature": "verify_fv3(plan_path: Path) -> None",
    "semantics": "load exact plan-owned effect policy, scan exact production roots, fail on any unauthorized/unresolved/unknown effect",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv4",
    "signature": "verify_fv4(plan_path: Path, ledger_path: Path, before_snapshot_path: Path, phase: str, receipt_path: Path | None) -> None",
    "semantics": "validate ledger plus FV3/FV7/VCS/artifact corroboration; PRE forbids receipt dependency, POST requires receipt agreement",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv5",
    "signature": "verify_fv5(base_sha: str, phase: str) -> None",
    "semantics": "obtain tracked git diff path set from base..HEAD and require exact PRE or POST equality",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv6",
    "signature": "verify_fv6(repository_root: Path) -> None",
    "semantics": "verify exact protected blobs and zero protected-path diff",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_fv8",
    "signature": "verify_fv8(plan_path: Path) -> None",
    "semantics": "extract §§5.1–5.4 and compare exact implemented enum/dataclass/protocol/callable shapes",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "effect_policy_from_mapping",
    "signature": "effect_policy_from_mapping(mapping: Mapping[str, object]) -> EffectPolicy",
    "semantics": "require exact field names/order and exact plan-owned values before constructing EffectPolicy",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "validate_command_event_pair",
    "signature": "validate_command_event_pair(start: CommandLedgerEvent, end: CommandLedgerEvent, allowed: AllowedControlledCommand, expected_control_inputs: tuple[tuple[str, str], ...]) -> bool",
    "semantics": "bind exact argv/cwd/env/control-input/stdin metadata; required control keys and externally expected values are exact",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "SYNTHETIC_FORBIDDEN_SOURCE_FORMS",
    "signature": "SYNTHETIC_FORBIDDEN_SOURCE_FORMS: tuple[SyntheticForbiddenSourceForm, ...]",
    "semantics": "exact §8.9 closed 13-record registry",
    "governed_error_type": "N/A"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "validate_source_form_registry",
    "signature": "validate_source_form_registry(registry: tuple[SyntheticForbiddenSourceForm, ...], used_ids: tuple[str, ...]) -> None",
    "semantics": "require used id set == registry id set, exactly one record per id, no unknown id",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "source_form_for",
    "signature": "source_form_for(source_form_id: str) -> SyntheticForbiddenSourceForm",
    "semantics": "exact unique registry lookup; unknown or duplicate id fails",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "used_insert_source_form_ids",
    "signature": "used_insert_source_form_ids(constructions: tuple[AdversarialConstructionSpec, ...]) -> tuple[str, ...]",
    "semantics": "derive exact INSERT_SOURCE_FORM value ids from all 316 construction programs",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "observe_source_form_property",
    "signature": "observe_source_form_property(fixture: AdversarialFixture, source_form: SyntheticForbiddenSourceForm) -> bool",
    "semantics": "inspect exact inserted bytes/path/import fixture and prove the registry required_property/canonical_observation before governing call",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "construction_for_id",
    "signature": "construction_for_id(row_id: str) -> AdversarialConstructionSpec",
    "semantics": "exact unique 316-construction lookup",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_adversarial_cases.py",
    "name": "insert_source_form_into_neutral_fixture",
    "signature": "insert_source_form_into_neutral_fixture(source_form: SyntheticForbiddenSourceForm) -> AdversarialFixture",
    "semantics": "materialize exact registry bytes into a neutral synthetic fixture for property falsifier only",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "exact_ledger_pair_for",
    "signature": "exact_ledger_pair_for(allowed: AllowedControlledCommand, control_inputs: tuple[tuple[str, str], ...] | None = None) -> tuple[CommandLedgerEvent, CommandLedgerEvent]",
    "semantics": "construct exact START/END pair with identical control inputs; default values are deterministic test-only values for required keys",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "write_effect_policy_variant",
    "signature": "write_effect_policy_variant(tmp_path: Path, contract: PlanContractFixture, mode: str, field: str) -> Path",
    "semantics": "write a temporary plan clone whose sole mutation is DELETE of the named effect-policy key or RENAME of that key to field+'_RENAMED'; no production/repository file is written",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_approved_plan_identity",
    "signature": "verify_approved_plan_identity(repository_root: Path, plan_path: Path, approved_plan_blob_sha: str) -> None",
    "semantics": "require canonical V7 repository-relative path and actual Git blob identity of its bytes equal external approved-plan blob",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_interface_manifest.py",
    "name": "verify_effect_scanner_source_contract",
    "signature": "verify_effect_scanner_source_contract(plan_path: Path, scanner_path: Path) -> None",
    "semantics": "extract §10.3.1 source bytes/digest from approved plan and require exact implementation marker region, one scan_production_effects definition and no rebind",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "exact_controlled_run_ledger_for",
    "signature": "exact_controlled_run_ledger_for(contract: PlanContractFixture, phase: str, implementation_base_sha: str, approved_plan_blob_sha: str) -> tuple[CommandLedgerEvent, ...]",
    "semantics": "construct all 70 exact ordered START/END pairs with exact per-record control-input key sets and values",
    "governed_error_type": "TestContractError"
  },
  {
    "owner": "tests/gate0/unit/evidence_dag_fixtures.py",
    "name": "write_scanner_contract_fixture",
    "signature": "write_scanner_contract_fixture(tmp_path: Path, source: bytes) -> Path",
    "semantics": "write a temporary module wrapping supplied source bytes in exact V7 scanner markers; no repository/production mutation",
    "governed_error_type": "TestContractError"
  }
]
~~~

Fixture lineage is exact:

`evidence_dag_tmp_git_repo` → `evidence_dag_s7_anchor` → `evidence_dag_verified_repository_context` → `evidence_dag_anchored_s1` / `evidence_dag_build_context`.

The verified-context fixture monkeypatches only `macos_stage_b_evidence_git._discover_repository_root_from_module_location` to return that same `TmpGitRepo.root`, then calls the real production `verify_repository_context` at the exact `evidence_dag_s7_anchor.commit_sha`. No cwd mutation, hidden global repository root, production DI/config/root selector or retained monkeypatch exists.

## 7. Plan-owned exact new-test inventory

FV1 does not import an implementation-authored expected set. The exact plan-owned expansion grammar is:

~~~json
{
  "schema": "G0_REV18_V7_EXPECTED_NEW_TEST_NODE_IDS_V1",
  "singletons": [
    "tests/gate0/unit/test_evidence_constants.py::test_rev18_closed_enum_and_failure_sets",
    "tests/gate0/unit/test_evidence_constants.py::test_fixture_prefix_and_historical_name_are_disjoint",
    "tests/gate0/unit/test_evidence_constants.py::test_plan_owned_interface_manifest_is_unique_and_complete",
    "tests/gate0/unit/test_evidence_constants.py::test_helper_owner_manifest_has_one_owner_per_name",
    "tests/gate0/unit/test_evidence_constants.py::test_plan_owned_test_inventory_expands_without_duplicates",
    "tests/gate0/unit/test_evidence_macho.py::test_header64_exact_layout",
    "tests/gate0/unit/test_evidence_macho.py::test_numeric_policy_count_54_and_structure_count_43",
    "tests/gate0/unit/test_evidence_macho.py::test_unknown_command_default_reject",
    "tests/gate0/unit/test_evidence_macho.py::test_external_parser_knowledge_cannot_widen",
    "tests/gate0/unit/test_evidence_runtime.py::test_chain_31_succeeds",
    "tests/gate0/unit/test_evidence_runtime.py::test_chain_32_succeeds",
    "tests/gate0/unit/test_evidence_runtime.py::test_chain_33_stops_before_expansion_33",
    "tests/gate0/unit/test_evidence_runtime.py::test_competing_hop_limit_precedes_repeat",
    "tests/gate0/unit/test_evidence_runtime.py::test_repeat_at_hop_5_is_cycle",
    "tests/gate0/unit/test_evidence_runtime.py::test_host_limit_cannot_redefine_project_limit",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_exact_serialization",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_has_no_terminal_separator",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_duplicate_row_rejected",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_traversal_order_invariant",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_member_count_overflow_rejected",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_scope_length_overflow_rejected",
    "tests/gate0/unit/test_evidence_runtime.py::test_native_manifest_path_length_overflow_rejected",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_both_roots_fully_enumerated",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_lstat_classifies_before_link_follow",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_recurses_only_real_directories",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_directory_symlink_fails_without_traversal",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_file_symlink_retains_exact_raw_target_bytes",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_file_symlink_records_exact_canonical_target",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_resolved_target_owns_scope",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_namespace_row_grammar_exact",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_b_independently_reenumerates",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_a_b_namespace_sets_must_match_exactly",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_a_b_use_same_classifier",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_native_digest_stability_required",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_a_bytes_drive_parse_digest_and_materialization",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_non_native_content_only_mutation_may_pass",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_non_native_to_native_transition_fails",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_native_to_non_native_transition_fails",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_native_byte_mutation_fails",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_symlink_retarget_fails",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_insert_remove_rename_kind_mutations_fail",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_transient_state_is_not_serialized",
    "tests/gate0/unit/test_evidence_runtime.py::test_census_success_does_not_claim_atomic_historical_snapshot",
    "tests/gate0/unit/test_evidence_git.py::test_blob_read_uses_committed_object_not_worktree",
    "tests/gate0/unit/test_evidence_git.py::test_generation_identity_enumeration_is_distinct",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_has_no_raw_root_selector",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_copy_is_rejected",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_manual_reconstruction_rejected",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_alternate_clean_root_rejected",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_symlinked_root_rejected",
    "tests/gate0/unit/test_evidence_git.py::test_verified_repository_context_path_replacement_rejected_before_git_leaf",
    "tests/gate0/unit/test_evidence_authority.py::test_applicable_plan_blob_comes_from_fixed_controller_path",
    "tests/gate0/unit/test_evidence_authority.py::test_generation_ordinal_is_distinct_committed_count_plus_one",
    "tests/gate0/unit/test_evidence_authority.py::test_committed_generation_identity_reuse_rejected",
    "tests/gate0/unit/test_evidence_authority.py::test_s3_authority_echo_is_non_authoritative",
    "tests/gate0/unit/test_evidence_authority.py::test_s4_not_observed_exact_key_set",
    "tests/gate0/unit/test_evidence_authority.py::test_s4_measured_owner_pinned_exact_key_set",
    "tests/gate0/unit/test_evidence_snapshot.py::test_producer_dependency_lists_do_not_define_s1",
    "tests/gate0/unit/test_evidence_snapshot.py::test_census_a_first_bytes_drive_parse_digest_materialization",
    "tests/gate0/unit/test_evidence_snapshot.py::test_context_sensitive_fixed_point_keeps_originating_context",
    "tests/gate0/unit/test_evidence_snapshot.py::test_optional_seed_registry_is_empty",
    "tests/gate0/unit/test_evidence_snapshot.py::test_p24_envelope_reference_acceptance",
    "tests/gate0/unit/test_evidence_snapshot.py::test_target_safety_predicate_is_not_resurrected",
    "tests/gate0/unit/test_evidence_anchor.py::test_s7_exact_set_parent_and_reread",
    "tests/gate0/unit/test_evidence_anchor.py::test_anchored_s1_is_constructed_from_exact_s7_blob",
    "tests/gate0/unit/test_evidence_anchor.py::test_equal_value_caller_s1_cannot_substitute_for_registered_anchor",
    "tests/gate0/unit/test_evidence_boundary.py::test_n4a_retained_primitive_exactly_five_fields",
    "tests/gate0/unit/test_evidence_boundary.py::test_same_s1_renderer_s2_signer_object_chain",
    "tests/gate0/unit/test_evidence_boundary.py::test_build_environment_starts_empty_and_has_exact_seven_values",
    "tests/gate0/unit/test_evidence_boundary.py::test_build_context_uses_verified_repository_context_only",
    "tests/gate0/unit/test_evidence_boundary.py::test_private_s2_is_exclusive_nofollow_and_reread_exact",
    "tests/gate0/unit/test_evidence_boundary.py::test_destination_absent_before_build_and_same_after_checkpoint",
    "tests/gate0/unit/test_evidence_projection.py::test_project_signed_image_returns_typed_projection",
    "tests/gate0/unit/test_evidence_projection.py::test_requirements_and_cms_are_elided_with_only_lawful_digests",
    "tests/gate0/unit/test_evidence_projection.py::test_unbound_slots_minus4_minus6_are_zero_and_outside_p20",
    "tests/gate0/unit/test_evidence_projection.py::test_privacy_scan_rejects_declared_personal_fields",
    "tests/gate0/unit/test_evidence_seal.py::test_n4b_parent_and_additive_projection",
    "tests/gate0/unit/test_evidence_seal.py::test_seal_capability_is_single_use",
    "tests/gate0/unit/test_evidence_seal.py::test_b_tree_never_contains_own_commit_or_tree_sha",
    "tests/gate0/unit/test_evidence_s8.py::test_n5_positive_exact_bytes",
    "tests/gate0/unit/test_evidence_s8.py::test_n5_extractor_signature_is_exactly_one_application",
    "tests/gate0/unit/test_evidence_s8.py::test_n5_stdout_is_retained_without_decode_trim_or_reserialize",
    "tests/gate0/unit/test_evidence_s8.py::test_type_strict_boolean_true_is_not_integer_one",
    "tests/gate0/unit/test_evidence_s8.py::test_type_strict_arrays_are_not_scalars",
    "tests/gate0/unit/test_evidence_s8.py::test_exact_renderer_array_order_is_required",
    "tests/gate0/unit/test_evidence_references.py::test_arm_d_reviewer_sibling_later_substitution_fails",
    "tests/gate0/unit/test_evidence_references.py::test_arm_d_tuple_components_are_independently_bound",
    "tests/gate0/unit/test_evidence_retention.py::test_p20_closed_constant_exact_members",
    "tests/gate0/unit/test_evidence_retention.py::test_foreign_digest_cannot_be_mode_b",
    "tests/gate0/unit/test_evidence_retention.py::test_retained_preimage_forces_mode_a",
    "tests/gate0/unit/test_evidence_retention.py::test_minus4_minus6_structural_state_never_enters_recorded_value",
    "tests/gate0/unit/test_evidence_results.py::test_s11_serializes_supplied_gate_result_without_evaluating",
    "tests/gate0/unit/test_evidence_results.py::test_s10_before_s12_is_refused",
    "tests/gate0/unit/test_evidence_results.py::test_p17_records_exact_decision_id_and_authority_digest",
    "tests/gate0/unit/test_evidence_package.py::test_s13_parent_and_additivity",
    "tests/gate0/unit/test_evidence_package.py::test_all_preexisting_s7_s9_paths_are_byte_identical",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row01_authority_echo_coherence",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row02_phase_aware_s1_binding",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row03_generation_identity_tuple_and_reuse",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row04_phase_aware_s2_signer_binding",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row05_n4a_n4b_continuity_and_oracle_isolation",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row06_n5_subject_is_exact_n4a_transient_application",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row07_exact_s8_and_type_strict_policy",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row08_s11_policy_result_record",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row09_entitlement_key_closure",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row10_signing_identity_drift",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row11_projection_elision_and_privacy",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row12_reproducibility_and_nonvacuity",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row13_result_order_and_design_record",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row14_anchor_bytes_immutability_digests",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row15_p19_four_reference_arms",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row16_p20_p21_retention_and_additivity",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row17_c2_envelope_acceptance",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row18_p25_and_all_316_adversarial_rows",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row19_phase_aware_p22_conjunction",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row20_p23_self_excluding_coverage",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_row21_retained_evidence_reverification_only",
    "tests/gate0/unit/test_evidence_gate.py::test_tier1_shape_is_exact",
    "tests/gate0/unit/test_evidence_gate.py::test_row21_forbidden_production_call_sites_have_zero_calls",
    "tests/gate0/unit/test_evidence_adversarial.py::test_adversarial_mapping_count_ids_and_hashes_exact",
    "tests/gate0/unit/test_evidence_adversarial.py::test_executor_request_contains_no_expected_fields",
    "tests/gate0/unit/test_evidence_orchestrator.py::test_orchestrator_records_exact_actual_gate_result",
    "tests/gate0/unit/test_evidence_orchestrator.py::test_orchestrator_blocks_n4b_before_n4a",
    "tests/gate0/unit/test_evidence_orchestrator.py::test_orchestrator_blocks_n6_before_n5",
    "tests/gate0/unit/test_evidence_orchestrator.py::test_orchestrator_blocks_n7_before_s10",
    "tests/gate0/unit/test_evidence_orchestrator.py::test_orchestrator_blocks_generation_b_while_baseline_not_observed",
    "tests/gate0/unit/test_stage_b_evidence_dag_cli.py::test_cli_has_no_n5_subject_retargeting_argument",
    "tests/gate0/unit/test_stage_b_evidence_dag_cli.py::test_cli_has_no_build_sign_live_or_generation_b_command",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_contract_exact",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_required_variables_use_colon_question_guards",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_alias_graph_binds_s2_to_codesign_entitlements",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_alias_graph_binds_identity_to_codesign_sign",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_alias_graph_binds_sealed_destination_to_binary_and_final_app",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_has_zero_copy_sink_or_each_copy_sink_derives_from_sealed_destination",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_forbidden_fallbacks_absent",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_unsupported_syntax_fails_closed",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_has_no_discovery_renderer_or_n5_extraction",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_gitignore_contains_stage_b_build_exactly_once",
    "tests/gate0/unit/test_evidence_adversarial.py::test_normal_return_with_wrong_observed_detail_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_all_concrete_plan_snippets_bind_fixture_names",
    "tests/gate0/unit/test_evidence_anchor.py::test_verified_context_and_s7_share_exact_tmp_repo_lineage",
    "tests/gate0/unit/test_evidence_git.py::test_repository_root_discovery_leaf_is_private_zero_argument",
    "tests/gate0/unit/test_evidence_anchor.py::test_tmp_repo_monkeypatch_is_test_only_nonretained",
    "tests/gate0/unit/test_evidence_constants.py::test_censusfs_expected_protocol_record_is_exact",
    "tests/gate0/unit/test_evidence_constants.py::test_protocol_missing_extra_or_mismatch_fails_fv8",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_unknown_simple_command_rejected",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_unknown_path_option_rejected",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_unsupported_redirection_rejected",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_unclassified_path_bearing_argv_rejected",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_alternate_output_command_rejected",
    "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_extra_destination_argv_rejected",
    "tests/gate0/unit/test_evidence_constants.py::test_recorder_rejects_two_terminal_outcomes",
    "tests/gate0/unit/test_evidence_constants.py::test_fv1_requires_every_expected_node_passed",
    "tests/gate0/unit/test_evidence_constants.py::test_failed_collection_is_error_semantics",
    "tests/gate0/unit/test_evidence_constants.py::test_recorder_tryfirst_snapshot_is_registration_order_independent",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_policy_production_roots_are_exact",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_propagates_local_wrapper_effects",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_unresolved_dynamic_local_edge_fails_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_unknown_external_import_fails_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_only_exact_process_leaves_allowed",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_only_bounded_census_traversal_leaf_allowed",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_schema_is_exact",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_requires_every_authorized_command",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_rejects_prohibited_command_effect",
    "tests/gate0/unit/test_evidence_constants.py::test_fv4_artifact_scan_rejects_prohibited_generated_surfaces",
    "tests/gate0/unit/test_evidence_constants.py::test_fv4_pre_receipt_does_not_require_receipt",
    "tests/gate0/unit/test_evidence_constants.py::test_fv4_post_receipt_requires_exact_activity_agreement",
    "tests/gate0/unit/test_evidence_constants.py::test_fv4_receipt_no_cannot_override_contradiction",
    "tests/gate0/unit/test_evidence_constants.py::test_fv5_pre_receipt_exact_changed_path_set",
    "tests/gate0/unit/test_evidence_constants.py::test_fv5_post_receipt_exact_changed_path_set",
    "tests/gate0/unit/test_evidence_constants.py::test_fv5_missing_required_writer_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_fv5_extra_changed_path_fails",
    "tests/gate0/unit/test_evidence_runtime.py::test_census19_combined_or_synthesized_mutation_cannot_satisfy_row",
    "tests/gate0/unit/test_evidence_boundary.py::test_oracle_inspector_cannot_echo_expectation",
    "tests/gate0/unit/test_evidence_adversarial.py::test_all_316_construction_specs_have_concrete_action_semantics",
    "tests/gate0/unit/test_evidence_adversarial.py::test_construction_pipeline_has_no_expectation_access",
    "tests/gate0/unit/test_evidence_runtime.py::test_censusfs_protocol_is_fv8_machine_truth",
    "tests/gate0/unit/test_evidence_git.py::test_verified_context_uses_real_verifier_at_exact_s7_commit",
    "tests/gate0/unit/test_evidence_constants.py::test_recorder_strict_xpass_pytest_8_3_3_actual_case",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_policy_serialized_fields_equal_effectpolicy_dataclass_fields",
    "tests/gate0/unit/test_evidence_constants.py::test_fv3_refuses_missing_or_renamed_effect_policy_field",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_subprocess_alias_is_process",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_shell_true_fails_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_unlisted_os_callable_fails_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_allowed_command_manifest_is_exact_and_unique",
    "tests/gate0/unit/test_evidence_constants.py::test_command_manifest_stdin_digests_recompute_from_plan_blocks",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_same_argv_exact_stdin_passes",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_one_byte_changed_stdin_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_same_argv_different_python_program_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_exact_stdin_mismatched_octet_count_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_start_end_stdin_mismatch_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_none_with_nonzero_stdin_fails",
    "tests/gate0/unit/test_evidence_adversarial.py::test_source_form_registry_missing_used_form_fails",
    "tests/gate0/unit/test_evidence_adversarial.py::test_source_form_registry_duplicate_id_fails",
    "tests/gate0/unit/test_evidence_adversarial.py::test_insert_source_form_unknown_id_fails",
    "tests/gate0/unit/test_evidence_adversarial.py::test_row160_wrong_source_form_fails_property_observer",
    "tests/gate0/unit/test_evidence_adversarial.py::test_row160_source_without_callable_measurer_parameter_fails",
    "tests/gate0/unit/test_evidence_adversarial.py::test_row160_callable_measurer_parameter_is_mechanically_observed",
    "tests/gate0/unit/test_evidence_adversarial.py::test_all_13_used_source_form_ids_resolve_exactly_once",
    "tests/gate0/unit/test_evidence_adversarial.py::test_no_unknown_source_form_id_remains",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_same_argv_stdin_different_implementation_base_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_same_argv_stdin_different_plan_path_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_approved_plan_identity_wrong_bytes_at_canonical_path_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_pre_post_phase_mutation_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_start_end_control_input_mismatch_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_missing_required_control_input_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_command_ledger_extra_control_input_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_path_walk_is_fail_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_path_unlisted_callable_is_fail_closed",
    "tests/gate0/unit/test_evidence_constants.py::test_path_harmless_callable_requires_exact_allowlist_membership",
    "tests/gate0/unit/test_evidence_constants.py::test_path_listed_traversal_outside_census_leaf_fails",
    "tests/gate0/unit/test_evidence_constants.py::test_path_traversal_propagates_through_local_wrapper",
    "tests/gate0/unit/test_evidence_constants.py::test_path_alias_import_has_same_classification",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_source_contract_exact_region_is_required",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_source_contract_rejects_extra_safe_symbol",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_source_contract_rejects_renamed_or_extra_safe_list",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_source_contract_rejects_hidden_special_case_branch",
    "tests/gate0/unit/test_evidence_constants.py::test_effect_scanner_source_contract_rejects_widening_when_symbol_absent_from_roots"
  ],
  "param_families": [
    {
      "prefix": "tests/gate0/unit/test_evidence_macho.py::test_every_accepted_command_has_executable_minimal_fixture",
      "ids": [
        "0x00000001",
        "0x00000002",
        "0x00000003",
        "0x00000004",
        "0x00000005",
        "0x00000008",
        "0x0000000b",
        "0x0000000c",
        "0x0000000d",
        "0x0000000e",
        "0x0000000f",
        "0x00000011",
        "0x00000016",
        "0x00000017",
        "0x80000018",
        "0x00000019",
        "0x0000001a",
        "0x0000001b",
        "0x8000001c",
        "0x0000001d",
        "0x0000001e",
        "0x8000001f",
        "0x00000020",
        "0x00000021",
        "0x00000022",
        "0x80000022",
        "0x80000023",
        "0x00000024",
        "0x00000025",
        "0x00000026",
        "0x80000028",
        "0x00000029",
        "0x0000002a",
        "0x0000002b",
        "0x0000002c",
        "0x0000002d",
        "0x0000002e",
        "0x0000002f",
        "0x00000030",
        "0x00000031",
        "0x00000032",
        "0x80000033",
        "0x80000034"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_macho.py::test_every_rejected_numeric_policy_row_fails",
      "ids": [
        "0x00000006",
        "0x00000007",
        "0x00000009",
        "0x0000000a",
        "0x00000010",
        "0x00000012",
        "0x00000013",
        "0x00000014",
        "0x00000015",
        "0x00000027",
        "0x80000035"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_macho.py::test_load_command_structure",
      "ids": [
        "0x00000001-VALID",
        "0x00000001-UNDERSIZED",
        "0x00000001-FORMULA_OR_TRAILING",
        "0x00000002-VALID",
        "0x00000002-UNDERSIZED",
        "0x00000002-FORMULA_OR_TRAILING",
        "0x00000003-VALID",
        "0x00000003-UNDERSIZED",
        "0x00000003-FORMULA_OR_TRAILING",
        "0x00000004-VALID",
        "0x00000004-UNDERSIZED",
        "0x00000004-FORMULA_OR_TRAILING",
        "0x00000005-VALID",
        "0x00000005-UNDERSIZED",
        "0x00000005-FORMULA_OR_TRAILING",
        "0x00000008-VALID",
        "0x00000008-UNDERSIZED",
        "0x00000008-FORMULA_OR_TRAILING",
        "0x0000000b-VALID",
        "0x0000000b-UNDERSIZED",
        "0x0000000b-FORMULA_OR_TRAILING",
        "0x0000000c-VALID",
        "0x0000000c-UNDERSIZED",
        "0x0000000c-FORMULA_OR_TRAILING",
        "0x0000000c-NONZERO_RESERVED_OR_PADDING",
        "0x0000000d-VALID",
        "0x0000000d-UNDERSIZED",
        "0x0000000d-FORMULA_OR_TRAILING",
        "0x0000000d-NONZERO_RESERVED_OR_PADDING",
        "0x0000000e-VALID",
        "0x0000000e-UNDERSIZED",
        "0x0000000e-FORMULA_OR_TRAILING",
        "0x0000000e-NONZERO_RESERVED_OR_PADDING",
        "0x0000000f-VALID",
        "0x0000000f-UNDERSIZED",
        "0x0000000f-FORMULA_OR_TRAILING",
        "0x0000000f-NONZERO_RESERVED_OR_PADDING",
        "0x00000011-VALID",
        "0x00000011-UNDERSIZED",
        "0x00000011-FORMULA_OR_TRAILING",
        "0x00000011-NONZERO_RESERVED_OR_PADDING",
        "0x00000016-VALID",
        "0x00000016-UNDERSIZED",
        "0x00000016-FORMULA_OR_TRAILING",
        "0x00000017-VALID",
        "0x00000017-UNDERSIZED",
        "0x00000017-FORMULA_OR_TRAILING",
        "0x00000017-NONZERO_RESERVED_OR_PADDING",
        "0x80000018-VALID",
        "0x80000018-UNDERSIZED",
        "0x80000018-FORMULA_OR_TRAILING",
        "0x80000018-NONZERO_RESERVED_OR_PADDING",
        "0x00000019-VALID",
        "0x00000019-UNDERSIZED",
        "0x00000019-FORMULA_OR_TRAILING",
        "0x0000001a-VALID",
        "0x0000001a-UNDERSIZED",
        "0x0000001a-FORMULA_OR_TRAILING",
        "0x0000001a-NONZERO_RESERVED_OR_PADDING",
        "0x0000001b-VALID",
        "0x0000001b-UNDERSIZED",
        "0x0000001b-FORMULA_OR_TRAILING",
        "0x8000001c-VALID",
        "0x8000001c-UNDERSIZED",
        "0x8000001c-FORMULA_OR_TRAILING",
        "0x8000001c-NONZERO_RESERVED_OR_PADDING",
        "0x0000001d-VALID",
        "0x0000001d-UNDERSIZED",
        "0x0000001d-FORMULA_OR_TRAILING",
        "0x0000001e-VALID",
        "0x0000001e-UNDERSIZED",
        "0x0000001e-FORMULA_OR_TRAILING",
        "0x8000001f-VALID",
        "0x8000001f-UNDERSIZED",
        "0x8000001f-FORMULA_OR_TRAILING",
        "0x8000001f-NONZERO_RESERVED_OR_PADDING",
        "0x00000020-VALID",
        "0x00000020-UNDERSIZED",
        "0x00000020-FORMULA_OR_TRAILING",
        "0x00000020-NONZERO_RESERVED_OR_PADDING",
        "0x00000021-VALID",
        "0x00000021-UNDERSIZED",
        "0x00000021-FORMULA_OR_TRAILING",
        "0x00000021-NONZERO_RESERVED_OR_PADDING",
        "0x00000022-VALID",
        "0x00000022-UNDERSIZED",
        "0x00000022-FORMULA_OR_TRAILING",
        "0x80000022-VALID",
        "0x80000022-UNDERSIZED",
        "0x80000022-FORMULA_OR_TRAILING",
        "0x80000023-VALID",
        "0x80000023-UNDERSIZED",
        "0x80000023-FORMULA_OR_TRAILING",
        "0x80000023-NONZERO_RESERVED_OR_PADDING",
        "0x00000024-VALID",
        "0x00000024-UNDERSIZED",
        "0x00000024-FORMULA_OR_TRAILING",
        "0x00000025-VALID",
        "0x00000025-UNDERSIZED",
        "0x00000025-FORMULA_OR_TRAILING",
        "0x00000026-VALID",
        "0x00000026-UNDERSIZED",
        "0x00000026-FORMULA_OR_TRAILING",
        "0x80000028-VALID",
        "0x80000028-UNDERSIZED",
        "0x80000028-FORMULA_OR_TRAILING",
        "0x00000029-VALID",
        "0x00000029-UNDERSIZED",
        "0x00000029-FORMULA_OR_TRAILING",
        "0x0000002a-VALID",
        "0x0000002a-UNDERSIZED",
        "0x0000002a-FORMULA_OR_TRAILING",
        "0x0000002b-VALID",
        "0x0000002b-UNDERSIZED",
        "0x0000002b-FORMULA_OR_TRAILING",
        "0x0000002c-VALID",
        "0x0000002c-UNDERSIZED",
        "0x0000002c-FORMULA_OR_TRAILING",
        "0x0000002c-NONZERO_RESERVED_OR_PADDING",
        "0x0000002d-VALID",
        "0x0000002d-UNDERSIZED",
        "0x0000002d-FORMULA_OR_TRAILING",
        "0x0000002d-NONZERO_RESERVED_OR_PADDING",
        "0x0000002e-VALID",
        "0x0000002e-UNDERSIZED",
        "0x0000002e-FORMULA_OR_TRAILING",
        "0x0000002f-VALID",
        "0x0000002f-UNDERSIZED",
        "0x0000002f-FORMULA_OR_TRAILING",
        "0x00000030-VALID",
        "0x00000030-UNDERSIZED",
        "0x00000030-FORMULA_OR_TRAILING",
        "0x00000031-VALID",
        "0x00000031-UNDERSIZED",
        "0x00000031-FORMULA_OR_TRAILING",
        "0x00000032-VALID",
        "0x00000032-UNDERSIZED",
        "0x00000032-FORMULA_OR_TRAILING",
        "0x80000033-VALID",
        "0x80000033-UNDERSIZED",
        "0x80000033-FORMULA_OR_TRAILING",
        "0x80000034-VALID",
        "0x80000034-UNDERSIZED",
        "0x80000034-FORMULA_OR_TRAILING"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_macho.py::test_header64_policy_row",
      "ids": [
        "ROW01",
        "ROW02",
        "ROW03",
        "ROW04",
        "ROW05",
        "ROW06",
        "ROW07",
        "ROW08"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_macho.py::test_fat_structure_case",
      "ids": [
        "TRUNCATED_METADATA",
        "ZERO_SIZE",
        "MATH_BOUNDS",
        "OVERLAP",
        "ALIGN_RANGE",
        "ALIGN_OFFSET",
        "FAT64_RESERVED",
        "INNER_OUTER_MISMATCH",
        "OPAQUE_NONSELECTED",
        "GAPS",
        "TRAILING_BYTES",
        "SUPPORTED_SINGLE_ARM64"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_runtime.py::test_rr18_2_n01_short_bytes_never_enter_parser",
      "ids": [
        "0",
        "1",
        "2",
        "3"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_authority.py::test_generation_identity_mutates_with_each_normative_input",
      "ids": [
        "base_controller_commit",
        "applicable_spec_blob",
        "applicable_plan_blob",
        "generation_ordinal"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_authority.py::test_p2_invalid_preconditions_fail_before_hash",
      "ids": [
        "empty_identity",
        "uppercase_identity",
        "nonhex_identity",
        "wrong_width_identity",
        "u16_overflow_identity",
        "ordinal_zero",
        "ordinal_negative",
        "ordinal_string",
        "ordinal_2pow64",
        "ordinal_over_u64"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_anchor.py::test_anchor_mutations_fail",
      "ids": [
        "missing",
        "extra",
        "changed",
        "wrong_parent"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_boundary.py::test_registered_handle_forgery_fails_before_leaf",
      "ids": [
        "repository_context-shallow_copy",
        "repository_context-deep_copy",
        "repository_context-manual_reconstruction",
        "repository_context-copied_guard",
        "repository_context-changed_path",
        "repository_context-changed_generation",
        "repository_context-stale_lifecycle",
        "repository_context-replay_after_consumption",
        "anchored_s1-shallow_copy",
        "anchored_s1-deep_copy",
        "anchored_s1-manual_reconstruction",
        "anchored_s1-copied_guard",
        "anchored_s1-changed_path",
        "anchored_s1-changed_generation",
        "anchored_s1-stale_lifecycle",
        "anchored_s1-replay_after_consumption",
        "sealed_destination-shallow_copy",
        "sealed_destination-deep_copy",
        "sealed_destination-manual_reconstruction",
        "sealed_destination-copied_guard",
        "sealed_destination-changed_path",
        "sealed_destination-changed_generation",
        "sealed_destination-stale_lifecycle",
        "sealed_destination-replay_after_consumption",
        "signing_identity-shallow_copy",
        "signing_identity-deep_copy",
        "signing_identity-manual_reconstruction",
        "signing_identity-copied_guard",
        "signing_identity-changed_path",
        "signing_identity-changed_generation",
        "signing_identity-stale_lifecycle",
        "signing_identity-replay_after_consumption",
        "build_context-shallow_copy",
        "build_context-deep_copy",
        "build_context-manual_reconstruction",
        "build_context-copied_guard",
        "build_context-changed_path",
        "build_context-changed_generation",
        "build_context-stale_lifecycle",
        "build_context-replay_after_consumption",
        "seal_capability-shallow_copy",
        "seal_capability-deep_copy",
        "seal_capability-manual_reconstruction",
        "seal_capability-copied_guard",
        "seal_capability-changed_path",
        "seal_capability-changed_generation",
        "seal_capability-stale_lifecycle",
        "seal_capability-replay_after_consumption",
        "transient_application-shallow_copy",
        "transient_application-deep_copy",
        "transient_application-manual_reconstruction",
        "transient_application-copied_guard",
        "transient_application-changed_path",
        "transient_application-changed_generation",
        "transient_application-stale_lifecycle",
        "transient_application-replay_after_consumption"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_boundary.py::test_oracle_request_is_observed_then_compared",
      "ids": [
        "A01",
        "A02",
        "A03",
        "A04",
        "A05",
        "A06",
        "A07",
        "B01",
        "B02",
        "B03",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B09",
        "B10",
        "B11",
        "B12",
        "B13",
        "B14",
        "B15",
        "B16",
        "C01",
        "C02",
        "C03",
        "C04",
        "C05",
        "C06",
        "C07"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_s8.py::test_each_prohibited_network_entitlement_fails",
      "ids": [
        "com.apple.security.network.client",
        "com.apple.security.network.server",
        "com.apple.security.networking.networkextension",
        "com.apple.developer.networking.networkextension"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_references.py::test_each_p19_class_resolves_exactly_one_arm",
      "ids": [
        "PATH_REFERENCE",
        "FILE_BLOB_REFERENCE",
        "COMMIT_OBJECT_REFERENCE",
        "AUTHORITY_DESIGN_RECORD_REFERENCE"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_adversarial.py::test_every_rev18_adversarial_row_executes_governing_behavior",
      "ids": [
        "REV18-ADV-001",
        "REV18-ADV-002",
        "REV18-ADV-003",
        "REV18-ADV-004",
        "REV18-ADV-005",
        "REV18-ADV-006",
        "REV18-ADV-007",
        "REV18-ADV-008",
        "REV18-ADV-009",
        "REV18-ADV-010",
        "REV18-ADV-011",
        "REV18-ADV-012",
        "REV18-ADV-013",
        "REV18-ADV-014",
        "REV18-ADV-015",
        "REV18-ADV-016",
        "REV18-ADV-017",
        "REV18-ADV-018",
        "REV18-ADV-019",
        "REV18-ADV-020",
        "REV18-ADV-021",
        "REV18-ADV-022",
        "REV18-ADV-023",
        "REV18-ADV-024",
        "REV18-ADV-025",
        "REV18-ADV-026",
        "REV18-ADV-027",
        "REV18-ADV-028",
        "REV18-ADV-029",
        "REV18-ADV-030",
        "REV18-ADV-031",
        "REV18-ADV-032",
        "REV18-ADV-033",
        "REV18-ADV-034",
        "REV18-ADV-035",
        "REV18-ADV-036",
        "REV18-ADV-037",
        "REV18-ADV-038",
        "REV18-ADV-039",
        "REV18-ADV-040",
        "REV18-ADV-041",
        "REV18-ADV-042",
        "REV18-ADV-043",
        "REV18-ADV-044",
        "REV18-ADV-045",
        "REV18-ADV-046",
        "REV18-ADV-047",
        "REV18-ADV-048",
        "REV18-ADV-049",
        "REV18-ADV-050",
        "REV18-ADV-051",
        "REV18-ADV-052",
        "REV18-ADV-053",
        "REV18-ADV-054",
        "REV18-ADV-055",
        "REV18-ADV-056",
        "REV18-ADV-057",
        "REV18-ADV-058",
        "REV18-ADV-059",
        "REV18-ADV-060",
        "REV18-ADV-061",
        "REV18-ADV-062",
        "REV18-ADV-063",
        "REV18-ADV-064",
        "REV18-ADV-065",
        "REV18-ADV-066",
        "REV18-ADV-067",
        "REV18-ADV-068",
        "REV18-ADV-069",
        "REV18-ADV-070",
        "REV18-ADV-071",
        "REV18-ADV-072",
        "REV18-ADV-073",
        "REV18-ADV-074",
        "REV18-ADV-075",
        "REV18-ADV-076",
        "REV18-ADV-077",
        "REV18-ADV-078",
        "REV18-ADV-079",
        "REV18-ADV-080",
        "REV18-ADV-081",
        "REV18-ADV-082",
        "REV18-ADV-083",
        "REV18-ADV-084",
        "REV18-ADV-085",
        "REV18-ADV-086",
        "REV18-ADV-087",
        "REV18-ADV-088",
        "REV18-ADV-089",
        "REV18-ADV-090",
        "REV18-ADV-091",
        "REV18-ADV-092",
        "REV18-ADV-093",
        "REV18-ADV-094",
        "REV18-ADV-095",
        "REV18-ADV-096",
        "REV18-ADV-097",
        "REV18-ADV-098",
        "REV18-ADV-099",
        "REV18-ADV-100",
        "REV18-ADV-101",
        "REV18-ADV-102",
        "REV18-ADV-103",
        "REV18-ADV-104",
        "REV18-ADV-105",
        "REV18-ADV-106",
        "REV18-ADV-107",
        "REV18-ADV-108",
        "REV18-ADV-109",
        "REV18-ADV-110",
        "REV18-ADV-111",
        "REV18-ADV-112",
        "REV18-ADV-113",
        "REV18-ADV-114",
        "REV18-ADV-115",
        "REV18-ADV-116",
        "REV18-ADV-117",
        "REV18-ADV-118",
        "REV18-ADV-119",
        "REV18-ADV-120",
        "REV18-ADV-121",
        "REV18-ADV-122",
        "REV18-ADV-123",
        "REV18-ADV-124",
        "REV18-ADV-125",
        "REV18-ADV-126",
        "REV18-ADV-127",
        "REV18-ADV-128",
        "REV18-ADV-129",
        "REV18-ADV-130",
        "REV18-ADV-131",
        "REV18-ADV-132",
        "REV18-ADV-133",
        "REV18-ADV-134",
        "REV18-ADV-135",
        "REV18-ADV-136",
        "REV18-ADV-137",
        "REV18-ADV-138",
        "REV18-ADV-139",
        "REV18-ADV-140",
        "REV18-ADV-141",
        "REV18-ADV-142",
        "REV18-ADV-143",
        "REV18-ADV-144",
        "REV18-ADV-145",
        "REV18-ADV-146",
        "REV18-ADV-147",
        "REV18-ADV-148",
        "REV18-ADV-149",
        "REV18-ADV-150",
        "REV18-ADV-151",
        "REV18-ADV-152",
        "REV18-ADV-153",
        "REV18-ADV-154",
        "REV18-ADV-155",
        "REV18-ADV-156",
        "REV18-ADV-157",
        "REV18-ADV-158",
        "REV18-ADV-159",
        "REV18-ADV-160",
        "REV18-ADV-161",
        "REV18-ADV-162",
        "REV18-ADV-163",
        "REV18-ADV-164",
        "REV18-ADV-165",
        "REV18-ADV-166",
        "REV18-ADV-167",
        "REV18-ADV-168",
        "REV18-ADV-169",
        "REV18-ADV-170",
        "REV18-ADV-171",
        "REV18-ADV-172",
        "REV18-ADV-173",
        "REV18-ADV-174",
        "REV18-ADV-175",
        "REV18-ADV-176",
        "REV18-ADV-177",
        "REV18-ADV-178",
        "REV18-ADV-179",
        "REV18-ADV-180",
        "REV18-ADV-181",
        "REV18-ADV-182",
        "REV18-ADV-183",
        "REV18-ADV-184",
        "REV18-ADV-185",
        "REV18-ADV-186",
        "REV18-ADV-187",
        "REV18-ADV-188",
        "REV18-ADV-189",
        "REV18-ADV-190",
        "REV18-ADV-191",
        "REV18-ADV-192",
        "REV18-ADV-193",
        "REV18-ADV-194",
        "REV18-ADV-195",
        "REV18-ADV-196",
        "REV18-ADV-197",
        "REV18-ADV-198",
        "REV18-ADV-199",
        "REV18-ADV-200",
        "REV18-ADV-201",
        "REV18-ADV-202",
        "REV18-ADV-203",
        "REV18-ADV-204",
        "REV18-ADV-205",
        "REV18-ADV-206",
        "REV18-ADV-207",
        "REV18-ADV-208",
        "REV18-ADV-209",
        "REV18-ADV-210",
        "REV18-ADV-211",
        "REV18-ADV-212",
        "REV18-ADV-213",
        "REV18-ADV-214",
        "REV18-ADV-215",
        "REV18-ADV-216",
        "REV18-ADV-217",
        "REV18-ADV-218",
        "REV18-ADV-219",
        "REV18-ADV-220",
        "REV18-ADV-221",
        "REV18-ADV-222",
        "REV18-ADV-223",
        "REV18-ADV-224",
        "REV18-ADV-225",
        "REV18-ADV-226",
        "REV18-ADV-227",
        "REV18-ADV-228",
        "REV18-ADV-229",
        "REV18-ADV-230",
        "REV18-ADV-231",
        "REV18-ADV-232",
        "REV18-ADV-233",
        "REV18-ADV-234",
        "REV18-ADV-235",
        "REV18-ADV-236",
        "REV18-ADV-237",
        "REV18-ADV-238",
        "REV18-ADV-239",
        "REV18-ADV-240",
        "REV18-ADV-241",
        "REV18-ADV-242",
        "REV18-ADV-243",
        "REV18-ADV-244",
        "REV18-ADV-245",
        "REV18-ADV-246",
        "REV18-ADV-247",
        "REV18-ADV-248",
        "REV18-ADV-249",
        "REV18-ADV-250",
        "REV18-ADV-251",
        "REV18-ADV-252",
        "REV18-ADV-253",
        "REV18-ADV-254",
        "REV18-ADV-255",
        "REV18-ADV-256",
        "REV18-ADV-257",
        "REV18-ADV-258",
        "REV18-ADV-259",
        "REV18-ADV-260",
        "REV18-ADV-261",
        "REV18-ADV-262",
        "REV18-ADV-263",
        "REV18-ADV-264",
        "REV18-ADV-265",
        "REV18-ADV-266",
        "REV18-ADV-267",
        "REV18-ADV-268",
        "REV18-ADV-269",
        "REV18-ADV-270",
        "REV18-ADV-271",
        "REV18-ADV-272",
        "REV18-ADV-273",
        "REV18-ADV-274",
        "REV18-ADV-275",
        "REV18-ADV-276",
        "REV18-ADV-277",
        "REV18-ADV-278",
        "REV18-ADV-279",
        "REV18-ADV-280",
        "REV18-ADV-281",
        "REV18-ADV-282",
        "REV18-ADV-283",
        "REV18-ADV-284",
        "REV18-ADV-285",
        "REV18-ADV-286",
        "REV18-ADV-287",
        "REV18-ADV-288",
        "REV18-ADV-289",
        "REV18-ADV-290",
        "REV18-ADV-291",
        "REV18-ADV-292",
        "REV18-ADV-293",
        "REV18-ADV-294",
        "REV18-ADV-295",
        "REV18-ADV-296",
        "REV18-ADV-297",
        "REV18-ADV-298",
        "REV18-ADV-299",
        "REV18-ADV-300",
        "REV18-ADV-301",
        "REV18-ADV-302",
        "REV18-ADV-303",
        "REV18-ADV-304",
        "REV18-ADV-305",
        "REV18-ADV-306",
        "REV18-ADV-307",
        "REV18-ADV-308",
        "REV18-ADV-309",
        "REV18-ADV-310",
        "REV18-ADV-311",
        "REV18-ADV-312",
        "REV18-ADV-313",
        "REV18-ADV-314",
        "REV18-ADV-315",
        "REV18-ADV-316"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_stage_b_evidence_build_boundary.py::test_shell_family_derives_complete_sinks",
      "ids": [
        "SWIFT_BUILD",
        "MKDIR",
        "CP_INFO",
        "CP_PRODUCT",
        "CODESIGN_SIGN",
        "CODESIGN_VERIFY",
        "ECHO"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_constants.py::test_recorder_terminal_outcome_model",
      "ids": [
        "ORDINARY_PASS",
        "ORDINARY_ASSERTION_FAILURE",
        "SETUP_ERROR",
        "TEARDOWN_ERROR",
        "COLLECTION_ERROR",
        "ORDINARY_SKIP",
        "EXPECTED_XFAIL",
        "NONSTRICT_XPASS",
        "DESELECTED"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_constants.py::test_effect_process_surface_classification",
      "ids": [
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.getoutput",
        "subprocess.getstatusoutput",
        "os.system",
        "os.popen",
        "os.spawnv",
        "os.execv",
        "asyncio.create_subprocess_exec",
        "asyncio.create_subprocess_shell",
        "multiprocessing.Process",
        "os.posix_spawn",
        "os.posix_spawnp",
        "os.fork",
        "os.forkpty"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_constants.py::test_effect_network_prefix_rejected",
      "ids": [
        "socket",
        "ssl",
        "urllib.request",
        "http.client",
        "requests",
        "aiohttp",
        "httpx",
        "ftplib",
        "smtplib",
        "imaplib",
        "poplib",
        "telnetlib",
        "xmlrpc.client",
        "websockets",
        "paramiko",
        "grpc",
        "boto3"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_constants.py::test_effect_traversal_surface_classification",
      "ids": [
        "os.walk",
        "os.fwalk",
        "os.scandir",
        "os.listdir",
        "glob.glob",
        "glob.iglob",
        "Path.glob",
        "Path.rglob",
        "Path.iterdir"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_runtime.py::test_census19_each_mutation_independently_fails",
      "ids": [
        "INSERT",
        "REMOVE",
        "RENAME",
        "KIND_CHANGE"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_runtime.py::test_census_executor_cheat_is_detected",
      "ids": [
        "NO_OP_EXECUTOR",
        "SYNTHESIZED_TRACE",
        "NO_GOVERNING_CALL",
        "NO_MUTATION"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_boundary.py::test_oracle_mechanism_positive_falsifier",
      "ids": [
        "AST_SIGNATURE",
        "AST_CALL",
        "TEXT_SCHEMA",
        "AST_ASSIGNMENT",
        "AST_CONSTRUCTOR",
        "AST_IMPORT",
        "PATH_ABSENCE",
        "PACKAGE_MANIFEST",
        "DEPENDENCY_MANIFEST",
        "IMPORT_RESOLUTION",
        "REEXPORT_GRAPH",
        "CALL_REACHABILITY_GRAPH"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_adversarial.py::test_pipeline_stage_replacement_is_detected",
      "ids": [
        "BUILDER",
        "ACTION",
        "MUTATION_OBSERVER",
        "GOVERNING_CALL_EXECUTOR",
        "RESULT_PROBE"
      ]
    },
    {
      "prefix": "tests/gate0/unit/test_evidence_adversarial.py::test_construction_or_expectation_field_mutation_fails",
      "ids": [
        "builder_id",
        "action_kind",
        "action_args",
        "callable_id",
        "probe_id",
        "post_mutation_invariant",
        "expected_result"
      ]
    }
  ]
}
~~~

Expansion law: start with every singleton literal; for each parameter family append `[` + each listed id + `]` to the exact prefix; sort the resulting list; require pre-deduplication cardinality == set cardinality.

The V7 grammar expands mechanically to exactly **960** node IDs: 218 singleton nodes plus 24 parameter families expanding to 742 parameterized nodes. Unique node IDs = 960; duplicate node IDs = 0. Implementation may not add, remove or rename an Evidence-DAG test node without a later approved plan successor.

## 8. Load-bearing algorithm/test closure

### 8.1 P2 generation identity — exact H and complete negative closure

Preserve the v2 H byte encoding exactly:

~~~text
ASCII G0_GENERATION_IDENTITY_V1
one NUL octet
u16be(len(base_controller_commit ASCII bytes))
base_controller_commit lowercase ASCII bytes
u16be(len(applicable_spec_blob ASCII bytes))
applicable_spec_blob lowercase ASCII bytes
u16be(len(applicable_plan_blob ASCII bytes))
applicable_plan_blob lowercase ASCII bytes
u64be(generation_ordinal)
~~~

Generation identity is the lowercase 64-character SHA-256 hex digest of those exact bytes.

Every repository identity is verifier-derived and must be non-empty, lowercase, ASCII hexadecimal and exact Git object-id width used by this repository: 40 hex characters for commit ids and blob ids. The encoded length must fit u16.

generation_ordinal must be int but not bool and satisfy 1 <= generation_ordinal <= 2**64 - 1.

Every malformed precondition fails before the hash primitive is reached with EvidenceDagError(code=GENERATION_IDENTITY_COLLISION, ...). No generation identity is returned.

Exact negative family:

- repository identity empty;
- repository identity uppercase;
- repository identity non-hex;
- repository identity wrong length;
- synthetic repository identity whose encoded length exceeds u16;
- ordinal 0;
- ordinal -1;
- ordinal non-integer string "1";
- ordinal 2**64;
- ordinal 2**64 + 1.

Tests monkeypatch the module-private _sha256_generation_identity_payload(payload:bytes)->str to a forbidden callable and require call count zero for every invalid case.

Independent four-input mutation tests remain mandatory for base_controller_commit, applicable_spec_blob, applicable_plan_blob and generation_ordinal.

Committed identity reuse remains independently rejected by comparing the candidate against distinct generation identities read from reachable committed S10 manifests.



### 8.2 Exact hop-limit / cycle precedence

Each PATH_CANONICALIZATION_V1 invocation begins with:

symlink_hops = 0

visited_symlink_pathnames = empty set

Immediately before expansion of an observed symlink:

1. if symlink_hops == 32, return family CANONICALIZATION_FAILURE with reason CANONICALIZATION_FAILURE_HOP_LIMIT and do not expand;
2. otherwise increment symlink_hops exactly once;
3. then evaluate repeated pathname;
4. if pathname was already visited, return SYMLINK_CYCLE;
5. otherwise record pathname and continue.

Required executable cases:

- chain_fs(31) succeeds with expansion_count 31;
- chain_fs(32) succeeds with expansion_count 32;
- chain_fs(33) stops before expansion 33, reason hop-limit, expansion_count 32;
- competing_hop_cycle_fs has symlink_hops already 32 and the next observed pathname is also already visited and is a symlink; expected hop-limit, not cycle, expansion_count remains 32;
- repeated pathname at hop 5 returns SYMLINK_CYCLE;
- stricter synthetic host primitive limit maps fail-closed without redefining project constant 32;
- looser host primitive never permits expansion 33.



### 8.3 Stable-census construction/expectation split

The exact construction records contain no expected result, expected failure or expected trace:

~~~json
[
  {
    "case_id": "CENSUS-01",
    "fixture_builder_id": "build_census_two_root_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-02",
    "fixture_builder_id": "build_census_file_symlink_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-03",
    "fixture_builder_id": "build_census_two_root_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-04",
    "fixture_builder_id": "build_census_directory_symlink_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-05",
    "fixture_builder_id": "build_census_file_symlink_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-06",
    "fixture_builder_id": "build_census_file_symlink_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-07",
    "fixture_builder_id": "build_census_file_symlink_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-08",
    "fixture_builder_id": "build_census_two_root_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-09",
    "fixture_builder_id": "build_census_ab_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-10",
    "fixture_builder_id": "build_census_ab_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-11",
    "fixture_builder_id": "build_census_two_root_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-12",
    "fixture_builder_id": "build_census_native_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-13",
    "fixture_builder_id": "build_census_native_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-14",
    "fixture_builder_id": "build_census_transition_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-15",
    "fixture_builder_id": "build_census_transition_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-16",
    "fixture_builder_id": "build_census_transition_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-17",
    "fixture_builder_id": "build_census_native_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-18",
    "fixture_builder_id": "build_census_ab_mutation_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-19",
    "fixture_builder_id": "build_census_ab_mutation_fixture",
    "subaction_ids": [
      "INSERT",
      "REMOVE",
      "RENAME",
      "KIND_CHANGE"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-20",
    "fixture_builder_id": "build_census_transient_state_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "serialize_native_manifest",
    "probe_observer_id": "observe_census_trace"
  },
  {
    "case_id": "CENSUS-21",
    "fixture_builder_id": "build_census_transient_state_fixture",
    "subaction_ids": [
      "PRIMARY"
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_observer_id": "observe_census_trace"
  }
]
~~~

Comparison truth is separately frozen:

~~~json
[
  {
    "case_id": "CENSUS-01",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "ENUMERATE:BASE_RUNTIME>=1",
          "ENUMERATE:RUN_SCOPED_VENV>=1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-02",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "LSTAT_BEFORE_READLINK:ALL_SYMLINKS"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-03",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "DIRECTORY_RECURSE:REAL_ONLY"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-04",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "DIRECTORY_SYMLINK_TRAVERSAL_COUNT=0"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-05",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "RAW_LINK_TARGET_BYTES_EXACT=1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-06",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CANONICAL_TARGET_RECORDED=1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-07",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "RESOLVED_TARGET_SCOPE_OWNS_ROW=1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-08",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "NAMESPACE_ROW_FIELDS_EXACT=1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-09",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CENSUS_A_ENUMERATION_ID!=CENSUS_B_ENUMERATION_ID"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-10",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "BOTH_ROOTS_ENUMERATED_A_B=1"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-11",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CLASSIFIER_CALLABLE_ID_A=M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
          "CLASSIFIER_CALLABLE_ID_B=M1R_NATIVE_CANDIDATE_CLASSIFIER_V1"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-12",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "NATIVE_DIGEST_A!=NATIVE_DIGEST_B"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-13",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CENSUS_A_READ_COUNT_PER_NATIVE=1",
          "PARSE_DIGEST_MATERIALIZE_SOURCE=CENSUS_A_BYTES"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-14",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CLASS_A=NON_NATIVE",
          "CLASS_B=NON_NATIVE"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-15",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CLASS_A=NON_NATIVE",
          "CLASS_B=NATIVE_MEMBER"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-16",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CLASS_A=NATIVE_MEMBER",
          "CLASS_B=NON_NATIVE"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-17",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "CLASS_A=NATIVE_MEMBER",
          "CLASS_B=NATIVE_MEMBER",
          "NATIVE_DIGEST_A!=NATIVE_DIGEST_B"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-18",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "RAW_OR_CANONICAL_TARGET_A!=B"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-19",
    "subcases": [
      {
        "subaction_id": "INSERT",
        "expected_trace": [
          "FRESH_FIXTURE=1",
          "ACTION:INSERT",
          "GOVERNING_CALL:capture_stable_census",
          "MUTATION_OBSERVED=1",
          "RESULT:DEPENDENCY_INVENTORY_DERIVATION_INVALID"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      },
      {
        "subaction_id": "REMOVE",
        "expected_trace": [
          "FRESH_FIXTURE=1",
          "ACTION:REMOVE",
          "GOVERNING_CALL:capture_stable_census",
          "MUTATION_OBSERVED=1",
          "RESULT:DEPENDENCY_INVENTORY_DERIVATION_INVALID"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      },
      {
        "subaction_id": "RENAME",
        "expected_trace": [
          "FRESH_FIXTURE=1",
          "ACTION:RENAME",
          "GOVERNING_CALL:capture_stable_census",
          "MUTATION_OBSERVED=1",
          "RESULT:DEPENDENCY_INVENTORY_DERIVATION_INVALID"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      },
      {
        "subaction_id": "KIND_CHANGE",
        "expected_trace": [
          "FRESH_FIXTURE=1",
          "ACTION:KIND_CHANGE",
          "GOVERNING_CALL:capture_stable_census",
          "MUTATION_OBSERVED=1",
          "RESULT:DEPENDENCY_INVENTORY_DERIVATION_INVALID"
        ],
        "expected_success": false,
        "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID"
      }
    ]
  },
  {
    "case_id": "CENSUS-20",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "TRANSIENT_NAMESPACE_RAWLINK_PATH_STATE_IN_SERIALIZED_BYTES=0"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  },
  {
    "case_id": "CENSUS-21",
    "subcases": [
      {
        "subaction_id": "PRIMARY",
        "expected_trace": [
          "ATOMIC_HISTORICAL_SNAPSHOT_CLAIM_COUNT=0"
        ],
        "expected_success": true,
        "expected_failure_code": null
      }
    ]
  }
]
~~~

Execution is fixed: construction lookup -> fresh builder invocation for each subaction -> subaction mutation -> independent observer installation -> real `capture_stable_census` exactly once -> observation capture -> external expectation lookup/comparison. Builder, mutation, governing call and observer never receive `StableCensusExpectation`.

CENSUS-19 is four independent fresh-fixture subcases: INSERT, REMOVE, RENAME, KIND_CHANGE. Each independently invokes real production stable census and independently yields `DEPENDENCY_INVENTORY_DERIVATION_INVALID`. A combined mutation, reused fixture, synthesized trace, no-op executor, executor that omits the governing call, or action that performs no mutation cannot satisfy the row.

### 8.4 Native-manifest serialization

Preserve exact canonical serialization:

1. UTF-8 bytes of PYTHON_NATIVE_RUNTIME_CLOSURE_V1;
2. one NUL octet;
3. unsigned 64-bit big-endian member count;
4. for each sorted row: unsigned 16-bit big-endian scope-tag byte length; scope bytes; unsigned 32-bit big-endian path byte length; path bytes; 32 raw SHA-256 digest bytes.

Sort by scope-tag UTF-8 bytes, exact canonical relative-path UTF-8 bytes, then lowercase digest ASCII bytes.

Duplicate canonical row after target de-duplication fails.

No separator or newline follows the final 32 raw digest bytes.

Tests cover member-count overflow, scope-length overflow, path-length overflow, duplicate rows and traversal-order invariance.



### 8.5 Verifier-owned S1/context/handle provenance and deterministic build boundary

N4a signature is exactly:
`measure_and_handoff_n4a(anchored_s1: AnchoredS1Handle, anchored_s2: FrozenArtifact, build_context: VerifierOwnedBuildContext) -> N4AProductionResult`.

Before any renderer/process leaf:
1. validate the exact registered `VerifiedRepositoryContext` embedded in build_context;
2. validate exact registered build-context/destination/signing instances and parent context identity;
3. validate exact registered `AnchoredS1Handle` and extract its exact internally constructed immutable S1;
4. measure that exact S1 object and hand the same object identity to `render_s2_from_s1`;
5. require produced S2 bytes equal anchored S2, measure that produced object, then hand that same produced object to `invoke_stage_b_build_app`;
6. create only the existing five-field primitive.

Every handle type in §5.7 has parameterized negatives for shallow copy before consumption, deep copy before consumption, manual reconstruction, copied guard/token, changed path/private subject, changed generation, stale lifecycle, and replay after consumption. Failure occurs before renderer/filesystem/process leaf. A guard/token copied from a lawful handle never substitutes for exact instance registration.

Build environment still starts from exactly `env: dict[str,str] = {}` and adds only the seven v3-approved values: frozen S2, sealed destination, signing identity, HOME, TMPDIR, XDG_CACHE_HOME and fixed PATH. Host inherited variables do not survive.

Path checks are relative only to the registered verified repository context. Generation root is exclusive; .stage-b-build/generation/private-S2/destination components are non-symlink; private S2 is O_EXCL/no-follow and reread exact; destination is absent pre-build and revalidated by root device/inode/path identity post-build. Checkpoint honesty remains explicit; no OS-wide race-freedom claim is made.

### 8.6 N5 exact-instance provenance

`extract_s8_from_n4a_application(application: N4ATransientApplication) -> bytes` keeps one selector-free argument. Before `_run_codesign_entitlements`, validation requires the exact currently registered transient-application instance, exact parent repository-context token, current generation/lifecycle, unconsumed N5 state and exact private subject path. Wrong type, copied/reconstructed exact type, copied token, changed path/generation, stale lifecycle, prior consumption or commit-B subject all fail `SIGNED_BYTES_NOT_VERIFIER_DERIVED` with private leaf count zero. Positive stdout remains byte-exact.

### 8.7 Exact 30-record oracle request/expectation split

The request manifest remains exactly A01–A07, B01–B16, C01–C07 and contains no expectation:

~~~json
[
  {
    "domain": "A",
    "surface_id": "A01",
    "production_paths": [
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_SIGNATURE",
    "forbidden_form": "CLI option or argparse destination matching measurer|oracle|measurement_helper|measurement_strategy|measurement_callback"
  },
  {
    "domain": "A",
    "surface_id": "A02",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py"
    ],
    "mechanism": "AST_CALL",
    "forbidden_form": "os.environ/getenv access whose key can select measurer/oracle/helper/strategy"
  },
  {
    "domain": "A",
    "surface_id": "A03",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py"
    ],
    "mechanism": "TEXT_SCHEMA",
    "forbidden_form": "schema/dataclass field named measurer|oracle|measurement_helper|measurement_strategy|callback_selector"
  },
  {
    "domain": "A",
    "surface_id": "A04",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py"
    ],
    "mechanism": "TEXT_SCHEMA",
    "forbidden_form": "runtime-policy field/value selecting N4a measurer/oracle/helper"
  },
  {
    "domain": "A",
    "surface_id": "A05",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py"
    ],
    "mechanism": "TEXT_SCHEMA",
    "forbidden_form": "ProducerSnapshotInputs or producer-authored field selecting measurer/oracle/helper"
  },
  {
    "domain": "A",
    "surface_id": "A06",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "scripts/stage-b-build-app.sh"
    ],
    "mechanism": "TEXT_SCHEMA",
    "forbidden_form": "build/runtime-adapter config key selecting measurer/oracle/helper"
  },
  {
    "domain": "A",
    "surface_id": "A07",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_ASSIGNMENT",
    "forbidden_form": "feature/config switch whose branch target is a measurement/oracle/helper callable"
  },
  {
    "domain": "B",
    "surface_id": "B01",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py"
    ],
    "mechanism": "AST_SIGNATURE",
    "forbidden_form": "measure_and_handoff_n4a/invoke_stage_b_build_app parameter named or annotated as measurer|oracle|Callable helper"
  },
  {
    "domain": "B",
    "surface_id": "B02",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py"
    ],
    "mechanism": "AST_CONSTRUCTOR",
    "forbidden_form": "constructor field/argument carrying callable measurer/oracle/helper"
  },
  {
    "domain": "B",
    "surface_id": "B03",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "CALL_REACHABILITY_GRAPH",
    "forbidden_form": "production Callable/dependency-injection parameter capable of selecting N4a measurement behavior"
  },
  {
    "domain": "B",
    "surface_id": "B04",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_CALL",
    "forbidden_form": "setter API set_*measurer|set_*oracle|set_*measurement_helper"
  },
  {
    "domain": "B",
    "surface_id": "B05",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_CALL",
    "forbidden_form": "mutator API mutating measurement/oracle/helper selection"
  },
  {
    "domain": "B",
    "surface_id": "B06",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py"
    ],
    "mechanism": "AST_SIGNATURE",
    "forbidden_form": "factory parameter accepting measurer/oracle/callback/strategy"
  },
  {
    "domain": "B",
    "surface_id": "B07",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_ASSIGNMENT",
    "forbidden_form": "registry mapping key/value selecting measurer/oracle/helper"
  },
  {
    "domain": "B",
    "surface_id": "B08",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_ASSIGNMENT",
    "forbidden_form": "plugin/provider map selecting measurement helper"
  },
  {
    "domain": "B",
    "surface_id": "B09",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "CALL_REACHABILITY_GRAPH",
    "forbidden_form": "callback/hook parameter that can intercept N4a measurement"
  },
  {
    "domain": "B",
    "surface_id": "B10",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "CALL_REACHABILITY_GRAPH",
    "forbidden_form": "strategy parameter/object selecting measurement implementation"
  },
  {
    "domain": "B",
    "surface_id": "B11",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py"
    ],
    "mechanism": "CALL_REACHABILITY_GRAPH",
    "forbidden_form": "second production-reachable measurer/helper API besides the fixed private leaf"
  },
  {
    "domain": "B",
    "surface_id": "B12",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_IMPORT",
    "forbidden_form": "importlib/__import__/loader hook selecting measurement/oracle module"
  },
  {
    "domain": "B",
    "surface_id": "B13",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_ASSIGNMENT",
    "forbidden_form": "mutable module global storing selectable measurer/oracle/helper callable"
  },
  {
    "domain": "B",
    "surface_id": "B14",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py"
    ],
    "mechanism": "TEXT_SCHEMA",
    "forbidden_form": "generic configuration dataclass/dict field typed Callable or helper selector"
  },
  {
    "domain": "B",
    "surface_id": "B15",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_CALL",
    "forbidden_form": "getattr/globals/locals/eval/exec dynamic dispatch selecting measurement/oracle/helper"
  },
  {
    "domain": "B",
    "surface_id": "B16",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_ASSIGNMENT",
    "forbidden_form": "conditional/dict alias dispatch equivalent to a selector-bearing measurement call"
  },
  {
    "domain": "C",
    "surface_id": "C01",
    "production_paths": [
      "src/gate0/feasibility",
      "scripts"
    ],
    "mechanism": "PATH_ABSENCE",
    "forbidden_form": "evidence_dag_oracle_manifest.py or test oracle module beneath ordinary production source root"
  },
  {
    "domain": "C",
    "surface_id": "C02",
    "production_paths": [
      "pyproject.toml",
      "setup.py",
      "setup.cfg",
      "MANIFEST.in"
    ],
    "mechanism": "PACKAGE_MANIFEST",
    "forbidden_form": "tests.gate0.unit.evidence_dag_oracle_manifest or evidence_dag_oracle_manifest"
  },
  {
    "domain": "C",
    "surface_id": "C03",
    "production_paths": [
      "requirements/gate0-macos-stage-a.lock"
    ],
    "mechanism": "DEPENDENCY_MANIFEST",
    "forbidden_form": "test oracle/helper package or editable test path"
  },
  {
    "domain": "C",
    "surface_id": "C04",
    "production_paths": [
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "AST_CALL",
    "forbidden_form": "sys.path mutation adding repository tests/gate0/unit or repository root solely to expose test oracle"
  },
  {
    "domain": "C",
    "surface_id": "C05",
    "production_paths": [
      "src/gate0/feasibility",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "IMPORT_RESOLUTION",
    "forbidden_form": "ordinary production module-search resolution of tests.gate0.unit.evidence_dag_oracle_manifest"
  },
  {
    "domain": "C",
    "surface_id": "C06",
    "production_paths": [
      "src/gate0/feasibility",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "IMPORT_RESOLUTION",
    "forbidden_form": "ordinary production import tests.gate0.unit.evidence_dag_oracle_manifest"
  },
  {
    "domain": "C",
    "surface_id": "C07",
    "production_paths": [
      "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
      "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
      "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
      "src/gate0/feasibility/macos_stage_b_evidence_git.py",
      "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
      "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
      "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
      "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
      "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
      "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
      "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
      "src/gate0/feasibility/macos_stage_b_evidence_references.py",
      "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
      "src/gate0/feasibility/macos_stage_b_evidence_results.py",
      "src/gate0/feasibility/macos_stage_b_evidence_package.py",
      "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
      "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
      "scripts/stage-b-evidence-dag.py"
    ],
    "mechanism": "REEXPORT_GRAPH",
    "forbidden_form": "import/re-export/alias edge to tests.gate0.unit.evidence_dag_oracle_manifest or oracle helper"
  }
]
~~~

Separate comparison truth:

~~~json
[
  {
    "surface_id": "A01",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A02",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A03",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A04",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A05",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A06",
    "expected": "ABSENT"
  },
  {
    "surface_id": "A07",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B01",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B02",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B03",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B04",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B05",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B06",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B07",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B08",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B09",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B10",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B11",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B12",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B13",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B14",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B15",
    "expected": "ABSENT"
  },
  {
    "surface_id": "B16",
    "expected": "ABSENT"
  },
  {
    "surface_id": "C01",
    "expected": "ABSENT"
  },
  {
    "surface_id": "C02",
    "expected": "ABSENT"
  },
  {
    "surface_id": "C03",
    "expected": "ABSENT"
  },
  {
    "surface_id": "C04",
    "expected": "ABSENT"
  },
  {
    "surface_id": "C05",
    "expected": "IMPORT_FAILS"
  },
  {
    "surface_id": "C06",
    "expected": "IMPORT_FAILS"
  },
  {
    "surface_id": "C07",
    "expected": "ABSENT"
  }
]
~~~

Mechanism semantics are plan-owned:

~~~json
{
  "AST_SIGNATURE": "Parse exact function/class signatures and report concrete matching parameter/annotation/default spans.",
  "AST_CALL": "Parse AST Call nodes; resolve direct/local imported aliases to exact called symbols.",
  "TEXT_SCHEMA": "Parse exact schema/config structure and keys; token structure, not substring coincidence, controls matches.",
  "AST_ASSIGNMENT": "Parse Assign, AnnAssign and NamedExpr targets and normalized values.",
  "AST_CONSTRUCTOR": "Parse class constructors plus constructor call sites and resolve local class identities.",
  "AST_IMPORT": "Parse Import/ImportFrom and normalize relative imports to repository module identities.",
  "PATH_ABSENCE": "Inspect only request production_paths and report each path that exists.",
  "PACKAGE_MANIFEST": "Parse exact package manifest dependency/export fields from listed files.",
  "DEPENDENCY_MANIFEST": "Parse exact dependency/lock records and report matched client/provider capabilities.",
  "IMPORT_RESOLUTION": "Resolve using only synthetic import-test search paths and record candidate resolution order without importing production code.",
  "REEXPORT_GRAPH": "Build import/re-export edges and propagate exported symbol reachability to fixed point.",
  "CALL_REACHABILITY_GRAPH": "Build import, definition and call edges from production entrypoints through local modules; a selector/helper matches only when it can reach, select, replace or intercept N4a behavior."
}
~~~

B03, B09, B10 and B11 use `CALL_REACHABILITY_GRAPH`; local signature spelling alone cannot discharge a reachability claim. For each mechanism family, a positive synthetic falsifier injects the forbidden property and the inspector must return a concrete match/reachability observation. An anti-echo test replaces the inspector with one that always reports absence; external comparison must fail. The inspector never receives `OracleInspectionExpectation`.

### 8.8 Tier-1 row 21 retained-only re-verification

Production signature is `evaluate_row21_retained_reverification(retained: RetainedRow21Inputs) -> Tier1RowResult`, never a pytest fixture type. The dedicated test passes `evidence_dag_retained_row21.inputs` and patches these exact call sites to forbidden counters:
- `macos_stage_b_evidence_snapshot._derive_dependency_inventory_from_host`;
- `macos_stage_b_evidence_runtime.capture_stable_census`;
- `macos_stage_b_evidence_snapshot._read_host_native_image`;
- `macos_stage_b_evidence_boundary.invoke_stage_b_build_app`;
- `macos_stage_b_evidence_s8._run_codesign_entitlements`.

Count must remain zero while exact retained B/S8/S1/S11 are loaded, expected policy is reconstructed from retained S1/frozen semantics, P7/P8 rerun, S11 is treated as RESULT provenance only, B1 remains metadata-only and B is never a codesign subject.

### 8.9 Exact 316-row concrete mutation manifest

Normative rows come only from spec blob `21e651503bff6dc2b369ad45923d16a3af8adf1c`, exact table order. Row hash input is UTF-8 `trimmed_domain + NUL + trimmed_case_cell + NUL + trimmed_required_outcome_cell`, preserving inline Markdown in each trimmed cell. `post_mutation_invariant.expected_state_sha256` is SHA-256 of UTF-8 canonical JSON of the exact `action_args` array, where arrays preserve order, object keys are lexicographically sorted, strings use JSON escaping, and separators are exactly `,` and `:` with no insignificant whitespace; Python reference form is `json.dumps(action_args, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.

`FixtureMutationOp` opcode semantics are exact:

~~~json
{
  "SET_SCALAR": "Set the exact named synthetic-fixture scalar field to value.",
  "SET_BYTES_HEX": "Decode even-length hexadecimal value to bytes and replace the exact named byte field.",
  "SET_PATH": "Set the exact named PurePath field to the literal value; angle-bracket tokens are fixture-owned literal symbols, never host discovery.",
  "SET_SEQUENCE": "Split value on | and replace the exact named ordered sequence.",
  "ADD_ENTRY": "Add exactly one named entry to the exact fixture collection; duplicate add fails test construction.",
  "REMOVE_ENTRY": "Remove exactly one named entry from the exact fixture collection; absent remove fails test construction.",
  "RENAME_ENTRY": "Value is OLD->NEW; rename exactly that fixture entry.",
  "SET_ENTRY_KIND": "Replace exact entry kind enum at target.",
  "SET_SYMLINK_TARGET": "Replace exact synthetic symlink raw/canonical target at target.",
  "ADD_GRAPH_EDGE": "Value is FROM->TO; add exactly one directed edge.",
  "SET_GRAPH_RESOLUTION": "Set exact graph-edge resolution state.",
  "SET_READ_BEHAVIOR": "Set deterministic synthetic source read schedule.",
  "SET_FLAG": "Set exact boolean field; value must be true or false.",
  "SET_COUNT": "Set exact nonnegative integer field.",
  "SET_RANGE": "Set exact range-mode enum at target.",
  "INSERT_SOURCE_FORM": "Insert the exact synthetic AST/import/package forbidden-form fixture named by value."
}
~~~

After the closed opcode table, `INSERT_SOURCE_FORM` is further closed by the following **single machine-readable registry**. Exact artifact bytes are `utf8_text.encode("utf-8")` with no newline conversion; all `template_parameters` are empty, so there is no executor-authored templating. `INSERT_SOURCE_FORM` accepts only a `source_form_id` present exactly once below. Applying it materializes the exact artifact into the neutral synthetic fixture and runs the named observer before any governing call. The observer must obtain the exact `canonical_observation`; a symbolic receipt is insufficient.

~~~json
{
  "schema": "G0_REV18_V6_SYNTHETIC_FORBIDDEN_SOURCE_FORMS_V1",
  "records": [
    {
      "source_form_id": "CALLABLE_MEASURER_PARAMETER",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "from collections.abc import Callable\\n\\ndef production_boundary(payload: bytes, measurer: Callable[[bytes], object]) -> object:\\n    return measurer(payload)\\n",
      "template_parameters": [],
      "required_property": "AST FunctionDef production_boundary has positional parameter measurer annotated with root Callable and its body calls Name(measurer)",
      "observer_id": "observe_callable_measurer_parameter",
      "canonical_observation": "FUNCTION=production_boundary;PARAM=measurer;ANNOTATION_ROOT=Callable;CALLED=1"
    },
    {
      "source_form_id": "SETTER_HOOK",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "_measurer = None\\n\\ndef set_measurer(measurer):\\n    global _measurer\\n    _measurer = measurer\\n",
      "template_parameters": [],
      "required_property": "AST defines set_measurer(measurer) and assigns parameter measurer into mutable module global _measurer",
      "observer_id": "observe_setter_hook",
      "canonical_observation": "FUNCTION=set_measurer;PARAM=measurer;GLOBAL_ASSIGN=_measurer"
    },
    {
      "source_form_id": "FACTORY",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "def make_boundary(measurer):\\n    return lambda payload: measurer(payload)\\n",
      "template_parameters": [],
      "required_property": "AST defines factory make_boundary(measurer) whose returned callable invokes measurer",
      "observer_id": "observe_factory_measurer",
      "canonical_observation": "FUNCTION=make_boundary;PARAM=measurer;RETURNED_CALLABLE_CALLS=measurer"
    },
    {
      "source_form_id": "REGISTRY",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "MEASURER_REGISTRY = {}\\n",
      "template_parameters": [],
      "required_property": "AST module contains mutable assignment MEASURER_REGISTRY to Dict",
      "observer_id": "observe_registry",
      "canonical_observation": "ASSIGN=MEASURER_REGISTRY;VALUE=DICT"
    },
    {
      "source_form_id": "CALLBACK_PLUGIN_MAP",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "CALLBACK_PLUGINS = {\\\"measurer\\\": \\\"tests.gate0.unit.synthetic_oracle:measure\\\"}\\n",
      "template_parameters": [],
      "required_property": "AST module contains callback/plugin map key measurer selecting synthetic oracle symbol",
      "observer_id": "observe_callback_plugin_map",
      "canonical_observation": "ASSIGN=CALLBACK_PLUGINS;KEY=measurer;SELECTS=tests.gate0.unit.synthetic_oracle:measure"
    },
    {
      "source_form_id": "MUTABLE_GLOBAL",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "measurer = None\\n",
      "template_parameters": [],
      "required_property": "AST module contains mutable module-global assignment named measurer",
      "observer_id": "observe_mutable_global",
      "canonical_observation": "GLOBAL=measurer;VALUE=None"
    },
    {
      "source_form_id": "MODULE_LOADER",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "import importlib\\n\\ndef load_measurer(module_name):\\n    return importlib.import_module(module_name).measure\\n",
      "template_parameters": [],
      "required_property": "AST defines runtime module selector load_measurer using importlib.import_module on parameter module_name",
      "observer_id": "observe_module_loader",
      "canonical_observation": "FUNCTION=load_measurer;DYNAMIC_IMPORT=importlib.import_module;SELECTS=measure"
    },
    {
      "source_form_id": "PRODUCTION_SOURCE_PATH",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/test_oracle.py",
      "utf8_text": "def measure(payload):\\n    return payload\\n",
      "template_parameters": [],
      "required_property": "synthetic test oracle module exists physically beneath exact synthetic production source root",
      "observer_id": "observe_production_source_path",
      "canonical_observation": "PATH=synthetic_prod/test_oracle.py;UNDER_PRODUCTION_ROOT=1"
    },
    {
      "source_form_id": "ORDINARY_SYS_PATH",
      "artifact_kind": "IMPORT_RESOLUTION_FIXTURE",
      "target_path_or_module": "import_resolution/ordinary_sys_path.json",
      "utf8_text": "{\\\"module\\\":\\\"test_oracle\\\",\\\"ordinary_sys_path_resolves\\\":true,\\\"resolved_path\\\":\\\"synthetic_test_oracle/test_oracle.py\\\"}\\n",
      "template_parameters": [],
      "required_property": "ordinary production sys.path resolution fixture resolves module test_oracle",
      "observer_id": "observe_ordinary_sys_path_resolution",
      "canonical_observation": "MODULE=test_oracle;ORDINARY_SYS_PATH_RESOLVES=1"
    },
    {
      "source_form_id": "DEPENDENCY_MANIFEST",
      "artifact_kind": "DEPENDENCY_MANIFEST",
      "target_path_or_module": "synthetic_prod/requirements.txt",
      "utf8_text": "test-oracle @ file:///synthetic/test-oracle\\n",
      "template_parameters": [],
      "required_property": "exact dependency manifest contains test-oracle direct reference",
      "observer_id": "observe_dependency_manifest",
      "canonical_observation": "DEPENDENCY=test-oracle @ file:///synthetic/test-oracle"
    },
    {
      "source_form_id": "REEXPORT",
      "artifact_kind": "PYTHON_SOURCE",
      "target_path_or_module": "synthetic_prod/gate0_boundary.py",
      "utf8_text": "from test_oracle import measure as measure\\n",
      "template_parameters": [],
      "required_property": "AST production module imports and re-exports test_oracle.measure as measure",
      "observer_id": "observe_reexport",
      "canonical_observation": "FROM=test_oracle;IMPORT=measure;REEXPORT=measure"
    },
    {
      "source_form_id": "IMPORT_RESOLVES",
      "artifact_kind": "IMPORT_RESOLUTION_FIXTURE",
      "target_path_or_module": "import_resolution/production_import.json",
      "utf8_text": "{\\\"module\\\":\\\"test_oracle\\\",\\\"production_import_resolves\\\":true,\\\"resolved_path\\\":\\\"synthetic_test_oracle/test_oracle.py\\\"}\\n",
      "template_parameters": [],
      "required_property": "ordinary production import of test_oracle resolves",
      "observer_id": "observe_import_resolution",
      "canonical_observation": "MODULE=test_oracle;PRODUCTION_IMPORT_RESOLVES=1"
    },
    {
      "source_form_id": "TEST_PATH_ONLY_IMPORT_FAILS",
      "artifact_kind": "IMPORT_RESOLUTION_FIXTURE",
      "target_path_or_module": "import_resolution/test_path_only.json",
      "utf8_text": "{\\\"module\\\":\\\"test_oracle\\\",\\\"production_import_resolves\\\":false,\\\"test_path_only\\\":true}\\n",
      "template_parameters": [],
      "required_property": "test_oracle exists only on test path and ordinary production import fails",
      "observer_id": "observe_test_path_only_import_failure",
      "canonical_observation": "MODULE=test_oracle;PRODUCTION_IMPORT_RESOLVES=0;TEST_PATH_ONLY=1"
    }
  ]
}
~~~

The set of all `INSERT_SOURCE_FORM.value` ids used by the 316 construction records must equal the registry id set exactly. Missing, duplicate, unknown and unused registry ids fail construction validation.

For `CALLABLE_MEASURER_PARAMETER`, `observe_callable_measurer_parameter` parses the exact inserted Python bytes with `ast.parse` and requires: one `FunctionDef` named `production_boundary`; a positional parameter named `measurer`; annotation root exactly `Callable`; and a `Call` whose function is `Name(id="measurer")`. Merely storing the source-form id, merely hashing action arguments, or inserting another source form cannot satisfy this observer.



Every action kind uses this closed interpreter contract:

~~~json
{
  "M1R_CONFIGURE_ROOT_CLOSURE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "FFMPEG_CONFIGURE_KEG": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "S4_CONFIGURE_ECHO": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "CLASSIFIER_CONFIGURE_BYTES": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "MACHO_CONFIGURE_CONTAINER": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "LOAD_COMMAND_CONFIGURE_NUMERIC": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "GRAPH_CONFIGURE_DEPENDENCY": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "GRAPH_CONFIGURE_CONTEXT": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "TOCTOU_CONFIGURE_SOURCE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "DOMAIN_CONFIGURE_MEMBERSHIP": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "OPTIONAL_SEEDS_CONFIGURE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "INVENTORY_CONFIGURE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "ORACLE_CONFIGURE_SOURCE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "VENV_CONFIGURE_NAMESPACE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "CENSUS_CONFIGURE_ENUMERATION": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "CENSUS_CONFIGURE_SYMLINK": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "FAT_CONFIGURE_STRUCTURE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "LOAD_COMMAND_CONFIGURE_STRUCTURE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "PATH_CONFIGURE_CANONICALIZATION": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "PATH_CONFIGURE_HOP_BOUND": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "CENSUS_CONFIGURE_STABLE": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  },
  "MACHO_CONFIGURE_HEADER64": {
    "interpreter": "apply FixtureMutationOp records in listed order to the neutral builder fixture; no branch may inspect row outcome or expectation",
    "permitted_opcodes": [
      "SET_SCALAR",
      "SET_BYTES_HEX",
      "SET_PATH",
      "SET_SEQUENCE",
      "ADD_ENTRY",
      "REMOVE_ENTRY",
      "RENAME_ENTRY",
      "SET_ENTRY_KIND",
      "SET_SYMLINK_TARGET",
      "ADD_GRAPH_EDGE",
      "SET_GRAPH_RESOLUTION",
      "SET_READ_BEHAVIOR",
      "SET_FLAG",
      "SET_COUNT",
      "SET_RANGE",
      "INSERT_SOURCE_FORM"
    ],
    "postcondition": "direct read-back of every touched target must canonical-serialize to the action_args SHA-256 frozen in post_mutation_invariant"
  }
}
~~~

The expectation-free construction manifest is:

~~~json[
  {
    "row_id": "REV18-ADV-001",
    "normative_row_sha256": "9a7db1bcf193c16a8f565e06d49863c61c6866069c4744e47bf8ee8de92af842",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "m1r.interpreter.path",
        "value": "/opt/homebrew/Cellar/python@3.14/<versioned-keg>/bin/python3.14",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f368bf34f3e492291964bef460d1d04c0f5ec32cf7e13080a85dc5207e1ada72",
      "required_targets": [
        "fixture.baseline",
        "m1r.interpreter.path"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-002",
    "normative_row_sha256": "08e8ad3da74f9c414ee8f78e8627cb48e0de57662723a6450bef79d43f5a8c34",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "m1r.interpreter.path",
        "value": "/private/tmp/copied-python",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3f0fb798638173c234a41ab366da82aebeee9466a454ac20bb4f6887e47c494a",
      "required_targets": [
        "fixture.baseline",
        "m1r.interpreter.path"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-003",
    "normative_row_sha256": "8b80008e166ff88b333d7c86fb7db111143a1c23fe6a57bc5875e62491cea0bb",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "m1r.interpreter.identity_mutations",
        "value": "WRONG_VERSION|WRONG_ARCH|WRONG_DIGEST",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "85915f7176e603cfb213f05fe1a0b1bad7fc3ffdb4340f07da08c3bb1dc42509",
      "required_targets": [
        "fixture.baseline",
        "m1r.interpreter.identity_mutations"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-004",
    "normative_row_sha256": "3717d700f914553acca1c6faafcf5a50f583867176245a710eea64df251e42eb",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "m1r.venv.root",
        "value": "/private/tmp/vip-gate0/<generation_identity>/runtime/python-venv",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "m1r.reservation.exclusive",
        "value": "true",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.entrypoint.target",
        "value": "FROZEN_BASE",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.lock.binding",
        "value": "EXACT",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.profile.binding",
        "value": "OWNER_PINNED_MATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b5a17596f32a9b5ee9986d90a8f00a454dfa9c26e61eb92e666499a9cbb941b5",
      "required_targets": [
        "fixture.baseline",
        "m1r.entrypoint.target",
        "m1r.lock.binding",
        "m1r.profile.binding",
        "m1r.reservation.exclusive",
        "m1r.venv.root"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-005",
    "normative_row_sha256": "3d7e0035226d8e0a625f13fe5c52f7aa31a3dfe318a5d2357aa2949c6afa8de2",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "m1r.venv.root",
        "value": "HISTORICAL_STAGE_A_ABSOLUTE_PATH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ee2da4a883c89ddac4d51ce848cc12797af6f9b9fdb7f6539db2dce840999ac6",
      "required_targets": [
        "fixture.baseline",
        "m1r.venv.root"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-006",
    "normative_row_sha256": "8e30ced810c6666bc5242deff1ebcafbfcc8467f1fb5d0da3d357708802308f0",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.entrypoint.target",
        "value": "NOT_FROZEN_BASE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "44ff73f03dad5b115e425b1f1898422c07cbb8eab4c4992a17ac2bef0cd00f74",
      "required_targets": [
        "fixture.baseline",
        "m1r.entrypoint.target"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-007",
    "normative_row_sha256": "549a1f34c69c28fb4c1ea7e52748de67332c4380443f20e16a3e5769f1ef1d8c",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.lock.binding",
        "value": "WRONG_DIGEST",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "bfbb0569f26be8a3bb6ca79f02f0f1c47083e572d5467d95cbd702a0a2c80378",
      "required_targets": [
        "fixture.baseline",
        "m1r.lock.binding"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-008",
    "normative_row_sha256": "cdefd0dee0dacce34fba75e954ca264196b697220550ae639b2d09a458786ae4",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "m1r.scan_root.descendant",
        "value": "DIRECTORY_SYMLINK",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1aa3a841a06ae12d5d77db72bd579a1802777eb1e6a9e5f249d252d0cd74b542",
      "required_targets": [
        "fixture.baseline",
        "m1r.scan_root.descendant"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-009",
    "normative_row_sha256": "5e7fb31e412473f70e6b6b8c1343d8eac6aa1abcf8c68941b4acb31d43dea520",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.native.filename",
        "value": "native.weirdext",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e5b76cd1c01c31ed675257d325441f8c8d1e95683df82e87a1fe4065437d8a57",
      "required_targets": [
        "fixture.baseline",
        "m1r.native.filename"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-010",
    "normative_row_sha256": "d396f8159d234cc0ca8164b083d00106f840e7e1cb512f885708fe3ba44cff61",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.candidate.filename",
        "value": "fake.so",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.candidate.bytes",
        "value": "00010203",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b5c68eb432165564d5b6884465aa46494792bbd8ddd918c98d94fa2f65420649",
      "required_targets": [
        "fixture.baseline",
        "m1r.candidate.bytes",
        "m1r.candidate.filename"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-011",
    "normative_row_sha256": "d234e12ca6c02e2deb96c274019ec94ac76dc59ade38c32608085a264fbf9979",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "m1r.native_members",
        "value": "INJECTED_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "03c50723f210e14a31fc82a9574373f72ff0f707f7a5403b7d452ca1b3f2f49b",
      "required_targets": [
        "fixture.baseline",
        "m1r.native_members"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-012",
    "normative_row_sha256": "fcc4a5b02dda2ccffd8480ad3a5b3e125923ebdc0721a8f60a3676c1eeb4c6b9",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "REMOVE_ENTRY",
        "target": "m1r.native_members",
        "value": "BASELINE_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5b6c58f5f98dbbd076d119f4178f9b7f617dbaaf6f287500f4e0673db7835c81",
      "required_targets": [
        "fixture.baseline",
        "m1r.native_members"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-013",
    "normative_row_sha256": "0b9e9983a3e0e88ed0eac2df327f446307bd37b09c3cd5c2d56124696233d432",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.native_members.BASELINE_NATIVE",
        "value": "FEEDFACE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a68e6d13fc3cd16299fe1b5fe0847e3fd4113a355618e0f7a23a1a87102e970a",
      "required_targets": [
        "fixture.baseline",
        "m1r.native_members.BASELINE_NATIVE"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-014",
    "normative_row_sha256": "8e49fda23c399d46ed8490b0a8e9e727440ae100e32e23f2fd74236042260dbf",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "m1r.serializer.duplicate_row",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f3a3772dd014e5431d87b735a5d9c59db262b8ef8b1c4dab1d2dc3d3f0f8ec0f",
      "required_targets": [
        "fixture.baseline",
        "m1r.serializer.duplicate_row"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-015",
    "normative_row_sha256": "37479f0ecdf38c99a5b5da231e13c8291974018bb4aa4080899b5914285d6a90",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "m1r.enumeration.order",
        "value": "REVERSE_BASELINE_ORDER",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "176d22bd57c1250f1a946ca56d75456979f3fcb1b01bde79af327f6dd9d68c4e",
      "required_targets": [
        "fixture.baseline",
        "m1r.enumeration.order"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-016",
    "normative_row_sha256": "e8f7116fdf33d58097c47107421d6844130cfea68750f3b8338e6e2a5bb4ac98",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "m1r.non_native_bytes_mutated",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1e59cfcd537377461d12a6af82fe73b4d8db920f64fab878290141286befbeb2",
      "required_targets": [
        "fixture.baseline",
        "m1r.non_native_bytes_mutated"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-017",
    "normative_row_sha256": "a1cc7bcb1179af8674742dd21028b0b002cc658ef65ad5db99b03c632c14995d",
    "domain": "M1R roots / closure",
    "builder_id": "adv_build_m1r_roots",
    "action_kind": "M1R_CONFIGURE_ROOT_CLOSURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.baseline.state",
        "value": "NOT_OBSERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5ccb185acc7abb49c45225405c04d2004bc3e448355997f38ea0ddca8fb35b1f",
      "required_targets": [
        "fixture.baseline",
        "m1r.baseline.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-018",
    "normative_row_sha256": "41be9a59122f02d75385e76641fcaad45dda23412fbb7c94a537b92cd785823e",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "702109d1c04a8abbb72f712c8e810edeeaa868c9034a0570172354ec51c7cdb2",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-019",
    "normative_row_sha256": "751610cce38c29e0bc090ec4c6a66f17093b543ff947fcaf7763ebd7f60b3d42",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<other-keg>/bin/ffprobe",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "06ac820ffc6540211031b2c69ccb3269b5b101bddc5c185c5f57a61ddb9e9c83",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-020",
    "normative_row_sha256": "e60dc540f69db8bfa830f4fc7cd584b245fa087ad8d4bdbfd6b7ecfdb2f329c5",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/private/tmp/ffmpeg-copy",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "324fadef8e8249c561ce0e41113d42cdaa3bf0f75474bfd15a0a83f594b471cd",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-021",
    "normative_row_sha256": "b14617993cb86bdc69cf84106f34de3706f8d3c1a8e584dca6f2ce6d86ec3cc5",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "ffmpeg.mutable_alias.targets",
        "value": "KEG_A|KEG_A",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d16842f2c4f99e534746aaf984a74e86377439433cf95acc3e62f5b1bb4d4c18",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "ffmpeg.mutable_alias.targets",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-022",
    "normative_row_sha256": "d12d8c8cdf7dd36858f07a41795f8614114945d295261aac5c9046b140f32015",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "702109d1c04a8abbb72f712c8e810edeeaa868c9034a0570172354ec51c7cdb2",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-023",
    "normative_row_sha256": "fc8961dfa18ce5f1b82baa0908364d06865f2d09eecaf4085c00a4599b5847cf",
    "domain": "FFmpeg coherent keg",
    "builder_id": "adv_build_ffmpeg_keg",
    "action_kind": "FFMPEG_CONFIGURE_KEG",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffmpeg.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffmpeg",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "ffmpeg.ffprobe.path",
        "value": "/opt/homebrew/Cellar/ffmpeg/<keg-id>/bin/ffprobe",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "ffmpeg.identity.digest",
        "value": "WRONG",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "45c312f79200b800073e4ef1f79c33796040e2978dac4a8903ff02ef2bd5b1e6",
      "required_targets": [
        "ffmpeg.ffmpeg.path",
        "ffmpeg.ffprobe.path",
        "ffmpeg.identity.digest",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-024",
    "normative_row_sha256": "0582a080e888f49b3a393cb7a036b4d1fbebff9f99317269810c4ec2d8bc494a",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.keyset.mode",
        "value": "ACTIVE_EXACT",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "s4.keys",
        "value": "UNDECLARED_KEY",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e211c4fe58c1e170a26ff42aa60f1a309f06c46235c1cd328934737fda789e23",
      "required_targets": [
        "fixture.baseline",
        "s4.keys",
        "s4.keyset.mode"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-025",
    "normative_row_sha256": "b29af4fb58c06e6b35ec31f12eb569b27c04505822512e6ff89f593f517fbae7",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "s4.mutation.family",
        "value": "OMIT_EACH_REQUIRED_FIELD",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b62496e84acbe62e21e803c63bccafdd847c71a8be8be9c3f0355933f2540063",
      "required_targets": [
        "fixture.baseline",
        "s4.mutation.family"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-026",
    "normative_row_sha256": "4d34c3d6b660c34b7a583a401d5cb4d25790a99cf21ce07e0aa4118eb99a8a33",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "s4.keys",
        "value": "UNDECLARED_KEY",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9f6ef0b5584577a671184adb7e35ad96750d3b4006bd93f5242faa65ad827525",
      "required_targets": [
        "fixture.baseline",
        "s4.keys"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-027",
    "normative_row_sha256": "81de0b88e5b1d497ec2264cc08827e18464d90d977d8a65e6a2b93f182d7b800",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "s4.mutation.family",
        "value": "WRONG_TYPE_EACH_FIELD",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "22be58b9554e3c4abeb9ba3956ad8bdf0d2762741a157548d811716680ae8bac",
      "required_targets": [
        "fixture.baseline",
        "s4.mutation.family"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-028",
    "normative_row_sha256": "e46a8a1235254297bdabbb7a8482c408c148486f42a1812655d4d97c4ca2a9ee",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.echo.truth_binding",
        "value": "CONFLICT",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6a58bcc5f7812dc91536f66178c528e2dc4fb6df9000a67ea638454d08c9587b",
      "required_targets": [
        "fixture.baseline",
        "s4.echo.truth_binding"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-029",
    "normative_row_sha256": "2ce78be7d62e6408a58205aefe9fda1573e7318bfc0c684dbd803dcc260495a9",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.state",
        "value": "NOT_OBSERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "67aa28f4674adc4c00d87552e61b3506e2b1927e9cb12cd83e82396acfe071cc",
      "required_targets": [
        "fixture.baseline",
        "s4.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-030",
    "normative_row_sha256": "33770f726ffdb0960f879eaa86802cb2fbd9d5b77922e682d00857014a0f9007",
    "domain": "S4 A2R/M1R echo",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.state",
        "value": "NOT_OBSERVED",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "s4.digest_count.invalid_values",
        "value": "NULL|EMPTY|ZERO|SYNTHETIC",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "01b1d30a81aa2c6792a35fd5f8a24ce56b7dad3607170a4f5872bc5a1c118da4",
      "required_targets": [
        "fixture.baseline",
        "s4.digest_count.invalid_values",
        "s4.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-031",
    "normative_row_sha256": "0a56414ecf97bddbfad63862c7bafcba56652156752b4ae258c3fef0b785463a",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "13db7d8e2ef858756e682f48060b3772cc6e8b6ee35cd1edb5ab4491fb937502",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-032",
    "normative_row_sha256": "99196bd2aed9b4220ed9da2e50bcbf95f4f6bbd030e748c52279dbce3b06eaa2",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "00",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "10bf0294ee80d268189c2ec85911c99bdc04dec83938e8f147c498aca418e803",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-033",
    "normative_row_sha256": "d7309e3a4b19b07841a0d95747f4e084975f11ef48c9598fb61e98529035d699",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "000102",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2b36da84d971484503a70e2acec74cf020704c753a09c001712f150c7eea7f27",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-034",
    "normative_row_sha256": "a64d71619d19a4de584cfa37dea247ae21b4a0ae9a5ffe2041bea9e401a929cf",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "66726f6d",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "33245987d364de136206a90a6240891305091687a795aa1baf24e1ac3ce5edbe",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-035",
    "normative_row_sha256": "27aa128a56e75f7ab1768bc32a646b7cc65859409849ee02202a7e3466105ba0",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "7b226b22",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8758b52638f9623284b05397708a60c8fa5dd34d1875fd8baa19a5bcee9ee1f0",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-036",
    "normative_row_sha256": "9dec7f4031c7e92552b925aad3f5b12eaea409e2f2fef190d9d320fb4abaa0b7",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "504b0304",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d346b29c5500e684a18da3b31addd507c43c39f58cfa7ffac3525b33f5aae46b",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-037",
    "normative_row_sha256": "e9f9ecb75eafd795f1874a463845180a841bef996bb104a00444b6c2df598f7f",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "feedfacf",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "cf3bb0cda15796536a260fab95f242d516e7ef31876509238e62d15b8759bc54",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-038",
    "normative_row_sha256": "4befa10005677d6d500c53e480a4a32c94c8cbc7616f222abcc0505d2f11a76a",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "cefaedfe",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2e0bbf0692aca18f7bd10701cb217d354426dd163922f417fe989f503d927e7b",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-039",
    "normative_row_sha256": "a8a3c1a12c910fd161a118f10ab752369a127cc04451fb70c943ad2d4cbcef6b",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "cffaedfe0c000001",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c11a0a2848089251f9f475027b32cc8b2dddf2d7287f1a78fc0930f2e00b8a0e",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-040",
    "normative_row_sha256": "60440388820ce88ab14ad413eb79232fdd58d70579864965ada54efbd1c7088d",
    "domain": "M1R wrapper",
    "builder_id": "adv_build_classifier_bytes",
    "action_kind": "CLASSIFIER_CONFIGURE_BYTES",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "m1r.wrapper.fixture",
        "value": "FULL_VALID_NATIVE",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "m1r.wrapper.input",
        "value": "",
        "aux": null
      }
    ],
    "governing_callable_id": "M1R_NATIVE_CANDIDATE_CLASSIFIER_V1",
    "probe_id": "probe_classifier",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a94092f3611f9f74ed98c87f396e3cbb8a0fc0ab8e7fe0c474cf06e62c69bd6c",
      "required_targets": [
        "fixture.baseline",
        "m1r.wrapper.fixture",
        "m1r.wrapper.input"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-041",
    "normative_row_sha256": "005810e714e01a5614eb2ef88774c2ed08678142fae214581a621e9702bbe28f",
    "domain": "Native parser entry",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.magic",
        "value": "UNLISTED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c8d614e05f00d97dd87b6a459f810bd22dc7526a12054a30320b0f52e6ddfe0e",
      "required_targets": [
        "fixture.baseline",
        "macho.container.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-042",
    "normative_row_sha256": "16aae8c03aa2ea5fadaf0eb94f830a8c2835e27b9ff903ccf44cf2eba91c0452",
    "domain": "Native parser entry",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.magic",
        "value": "REJECT_UNSUPPORTED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "488e86b73e66bbcd135699bcfcb7e595cb9fa000d63e4e112f0ffcc2423a64a6",
      "required_targets": [
        "fixture.baseline",
        "macho.container.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-043",
    "normative_row_sha256": "435afd9b99c68a4378bc08f1a80db1592eac01bfc01c62f3633f1b2070e19333",
    "domain": "Native parser entry",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.grammar",
        "value": "VALID_SUPPORTED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dd03a09103c802d283f3063fb90b7716cd947ea7e13062730f6c259c34a6e326",
      "required_targets": [
        "fixture.baseline",
        "macho.container.grammar"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-044",
    "normative_row_sha256": "848ccf4ae8e61e8788cfc15527818237bae7fbb8b0bad0fa6c28b4d591f26587",
    "domain": "Native parser entry",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.grammar",
        "value": "MALFORMED_SUPPORTED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0732f6ab7822fba6a4e218aba31c36888d987ac8ed89db332df64bd8454146e1",
      "required_targets": [
        "fixture.baseline",
        "macho.container.grammar"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-045",
    "normative_row_sha256": "9a32c01f99edd8851ff2d938dde8d0b358b1d2104437611b0df3b82b4f9ef3a8",
    "domain": "Native parser entry",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.magic",
        "value": "EXTERNAL_PARSER_ONLY",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "33136316f0d60530e25491cf47ea62d3304d921b489d9a0eb815d2f158711125",
      "required_targets": [
        "fixture.baseline",
        "macho.container.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-046",
    "normative_row_sha256": "aadd8734eb0b7cef0ed58266e4e15b10c350b148648c7b8c4d5f341463c9ef3a",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "THIN64",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "74f88ef566d9628c3d1386b8b99bb90a18f52249cda0a93f6dc1e57dfe6e151a",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-047",
    "normative_row_sha256": "4daa60b9a2ee4f84763343f998af1c1bb26ce03a4f6c6b29aa803cc086452575",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "FAT32_BE",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8468d86fe163acc2e41e143232468789fb55330821a4975757e5296ffcbf1410",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-048",
    "normative_row_sha256": "a3c060baa72e9475db72fadac5e68bedf7089bfd3b3f2b4607d99bc6df683d38",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "FAT64_BE",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dc9a50a12d873673e2f74eb8285c73cf3885dc7eb2b38d4c670c2663dd536b15",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-049",
    "normative_row_sha256": "b820b4c3ba1bf0a79e07c53b320e136fa307ba2edf51592f76518c1410992482",
    "domain": "Native parser / container slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.magic",
        "value": "REJECTED_OR_UNLISTED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9878ac8c2e47b34303b03f05d9e2d5866ad3cf123405db1eb2591742e93deebe",
      "required_targets": [
        "fixture.baseline",
        "macho.container.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-050",
    "normative_row_sha256": "025764eeea6bf03fc9dba9e2ecef1e174bf96cdfb9c7a0d8468707aa669d86fb",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.fat.table_truncated",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b057718d2d2e3c1d8557041d077db3113bb09b48b06743e460912a677b816df",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.table_truncated"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-051",
    "normative_row_sha256": "d91c330ab7d906ee084b2c642c23752f249fc48c4a0130d9e285355d90d4cf8f",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.nfat_arch",
        "value": "MAX_DECODED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fe6aef7714d56709f355a9b078b0fcfe5fc8f192e71efb498ebf6b984739b173",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.nfat_arch"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-052",
    "normative_row_sha256": "5e0e97cf877403b2b8ebee5e3a669972f115a02cb225cacc222745ec31bb750d",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.fat.offset_size_overflow",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d5096c7c6ab1f44b98d7b6432f53cbe9ae6f630db36b0a95042c228e1eb087de",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.offset_size_overflow"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-053",
    "normative_row_sha256": "cdd89d21d633c167313a9b174bd33b10ab2445f00713fcbff9dd11960feabe9b",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.slice.out_of_bounds",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "bcc986e02eeed9ea18f6c9e4b39b54f7757386519f26e3d2453fe1357891ff9d",
      "required_targets": [
        "fixture.baseline",
        "macho.slice.out_of_bounds"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-054",
    "normative_row_sha256": "68140396259f8460fc9ba5a64cd7038bd2df10ca3c90140b2fa679ca0ec09d79",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.slice.overlap",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fd31b48bc300b748ac624076f23068929909a718d77d756b4bc87b9962d84eef",
      "required_targets": [
        "fixture.baseline",
        "macho.slice.overlap"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-055",
    "normative_row_sha256": "976c3005b1e3cf2f47d49df6080319dd8180ba6f86415f8d5b465183c06b5498",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.slice.alignment",
        "value": "INVALID_GT63_OR_MISALIGNED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fc51fad151a3d87d71edc8b4bdb3827cfcb3f2f10a6933b4e60f648adcb13ff4",
      "required_targets": [
        "fixture.baseline",
        "macho.slice.alignment"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-056",
    "normative_row_sha256": "9761e5ea8effa961573081af92e1c85a38ad7747ff587d089152ece9dd3adccf",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.cpu.subtype",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "00091bcff61ebfd23116551d3a36851a997f3921dc0e45dbec3b0571ee3f6400",
      "required_targets": [
        "fixture.baseline",
        "macho.cpu.subtype"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-057",
    "normative_row_sha256": "81d76eb1f901b003f7307f1402931d5ad584a5bb21aa47b160151ac3026d254b",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.cpu.subtype",
        "value": "1",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2f32435bedb68ba205162fd526044743ac1bac3e3508df9624c04e382a6b9f71",
      "required_targets": [
        "fixture.baseline",
        "macho.cpu.subtype"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-058",
    "normative_row_sha256": "71fe02ff202d521461a1512fc771914014d0d983651d12a859d7b41fe3675c2f",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.cpu.subtype",
        "value": "2",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "77c24c1a165951d868f03d808f7618f7571d4125e3991d5e1e1a74a3e3aa9cc6",
      "required_targets": [
        "fixture.baseline",
        "macho.cpu.subtype"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-059",
    "normative_row_sha256": "14a9ae49bcd384d08608b4c397e9aa5d0752bffdcc7323b92d56188e8105ceff",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.cpu.subtype",
        "value": "FEATURE_BIT_SET",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ee144822d3e514f149b4f0ef7398b4f8aabd6e3b184aa5adf7c3c66d374cdf8c",
      "required_targets": [
        "fixture.baseline",
        "macho.cpu.subtype"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-060",
    "normative_row_sha256": "dc6c69edbfb42e37e341c0b8e5cf21c4bb2f4ad285590e6a59465315d6fce078",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "THIN64",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.cpu.type",
        "value": "X86_64_ONLY",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "80303f427c6e29a2d0da86e7fd9f864ef7d45ea60c9a641035d2f6b7dc953ab3",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind",
        "macho.cpu.type"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-061",
    "normative_row_sha256": "29bc3e647d87a886d57679a24f0ead1e3f7c20c7a5e864a26f4a3152f566e94e",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.arm64_slice_count",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "20f08e3d566009bef1fe3744ebdab0f26e11f089956ca6b0df90a6e97de22209",
      "required_targets": [
        "fixture.baseline",
        "macho.arm64_slice_count"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-062",
    "normative_row_sha256": "c9ba1e4c6104ac8300f635db4d3423a487cbae13f9bd1fb162b1aeb1fc6e6123",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.arm64_slice_count",
        "value": "2",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "aef88daf871b99b29e591659497d774188826e43ac3262f1ca31d128d0147562",
      "required_targets": [
        "fixture.baseline",
        "macho.arm64_slice_count"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-063",
    "normative_row_sha256": "b4d5768ae97c247aa353872096b36534c274cbef2007548746972f7a8942eede",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "THIN64",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.outer_inner_cpu_match",
        "value": "false",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dd1a29046df2370714bbb8b4fc3efb1fefbed5338a091199e3850049a22ec8db",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind",
        "macho.outer_inner_cpu_match"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-064",
    "normative_row_sha256": "581dda9815db979a9ee846c40e4a1286425bba748b66d20d198a34e191cdd7ec",
    "domain": "Native container / slice",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_CONTAINER",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command_region",
        "value": "TRUNCATED_OR_MISALIGNED_OR_COUNT_MISMATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c9c8a99bb97fe8470c46133e0f74a8257d09baef837d7cbe439e104c27ff8884",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command_region"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-065",
    "normative_row_sha256": "fce6b72e0d6e625bfbc566ab6375dae1598ab4ee641da46ff95646039cb47519",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000001",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "42edf8c9fe8b6bc9c954b6e73d455566d211c4e46869d5e0a3f9766e5ed242bf",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-066",
    "normative_row_sha256": "03680cdcac9be9567da0757aa9b8d4a3e8625a66fd527b9fb7cfcee2e0358d2c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000002",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3ab18c62724baff962b286daf147793cdc4fdb97bf784166eb8f3ce63e7877a8",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-067",
    "normative_row_sha256": "8c9b4e4ceec7c104c2adaff909bb872568771671b5059d84c8c8c8c238fc1d34",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000003",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "579e673808aca64cbdeb1b382528a7c45812bb61d2d839f0dbcb196ff6401d96",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-068",
    "normative_row_sha256": "d81b9559a8846f2f4fa80f9ae0a8ba956b1454944fcc2f2f473e81361aaf705c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000004",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4d67682358a9a17b8105a4dc9a8602543d3343d0aa8023da5a3743cdc614ed02",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-069",
    "normative_row_sha256": "3531bf41bc364262154e274aabc4fc9aff8790e685fcb6e7a486b3d70f70e116",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000005",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8481d91be762aa59c28bdf9a8d9f1ed53f2a04d4477734a2553c1d206792504a",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-070",
    "normative_row_sha256": "5ce8566e453f7225ac6d53314d60e5588c8acca24550ffb49756e5f8474af673",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000006",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "67726e55bee81e61c527998773635df99e6d725b5817e874a143311ce80d985d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-071",
    "normative_row_sha256": "450eb331d34b5fa883f7628d5046ab167e309b09c46a690c00282f5ad5552958",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000007",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d25a9ab887a5c60cb6199111bc8ca46bad5371397b234ef4d73d21bdd0f8528f",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-072",
    "normative_row_sha256": "396b56505e44faa743ad04db74a011661af5c2cea2c4aa1ed7530928d939f7b7",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000008",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7b7041c42db461101c9b930c6b1f4c48a34eda683882d59b329bb19098db1348",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-073",
    "normative_row_sha256": "e7b165b67c12527d41d9f79fb28e73434a5a9f99eaf3eb71b87d77be8f270f4b",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000009",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8bccfb81d9a80744578d84741199ebbdafe1dab4c922c97a587d1e853dff0923",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-074",
    "normative_row_sha256": "d2b4ea36741fd868188f37ab8c3d9b8bb1b5b11aca938d141a8b2aa3536c43fd",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000a",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "746689cf268f755516e3b9b7427e077d3a29930d1a0d3a4890cd69387abdf15a",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-075",
    "normative_row_sha256": "7573fb025e3a296dbece47150fcc1257f5360fddc36e5ed16c4cf3a94ec3a8ec",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000b",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "51a979f56a8cad874b1ecf2e369646bb49b54fdb6877529a16c9e08466e8dfa6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-076",
    "normative_row_sha256": "309aedae30d335ca1a8ab14d53f7441fda8657d08ac8d58d993af916014c9f32",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000c",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c822257770e6be88afb52875c17a924e06d2f01dbf1f9478ee96ba93177b9649",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-077",
    "normative_row_sha256": "bcaac60fe0c98abc515797dabc45fd7937d08f3e0df183e6edcaad292a306bb1",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000d",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "122597eacdee55cc0bc50764826ebb6bb0f4bedd99ebc6b4be2a31ee857e9c3e",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-078",
    "normative_row_sha256": "26cb3db755d6fd63d5d2213d2de2bf4918e151963c9595ac8dee07f81c80322a",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000e",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "178abab89efe970a13e62de7045fc7c7b074e61df1c72a0fa3390facea3860a7",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-079",
    "normative_row_sha256": "657e15ab2b6fbcb7e1a5f446c64a634e812e61c375d720eeb409aba41c9ce2ec",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000f",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a6f892a4e647a1a834c54d4cde52f68b3aa47fcc4137e7e51a06a77a2997be4b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-080",
    "normative_row_sha256": "43ce8fb3463266e5858dc40fa33bccc09a6fe95731a80f027d82411dc475987d",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000010",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6fdde88c3ed1bddf4d16fbc508aea2691197f6784b8ec3e05dc53e7a26d0856d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-081",
    "normative_row_sha256": "0672f51080b7cb014799ae494f7c8a35c07315d247e8c67e6197093bc95981ca",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000011",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e128e4fb119553725c40bb568584e06357cdbcec83303b8a406870173a872155",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-082",
    "normative_row_sha256": "adac144d96563cc68687aa3773ad11032a5fc719d666daf548efbc36bea6edaf",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000012",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "68e504b3dc10d7bf729057af6fd062af56adb723d29c9ebcb49814a56d85ca87",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-083",
    "normative_row_sha256": "2f715b3078c8caff064fda3a240dfdd253a15ed1e4b6b47b7d7658d872a74285",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000013",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ec265e3f9cf73ffbf25278b9691fd4de2c23bb87a83247a3f7e341c035ab715b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-084",
    "normative_row_sha256": "af880ff5e746fe1dbdb415350cacec324c318af2b30083b612a38ad5178a612f",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000014",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "aaa9b08aa68e87ee435ffc7b98f5c1a509b199fe63c1b2c0df5c0bb1d527f8de",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-085",
    "normative_row_sha256": "e7104198d26366014d417380eb20ea0c6c9b44d0a086b2bbf0d7281d18de553f",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000015",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8e3b06ba1a778871ee180346dcfebffff9b2ecca9f9cc0a9c409e364389a2bbf",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-086",
    "normative_row_sha256": "a5a1c2a7e0330a4cd9920b0b30b2fdbe5edd8e1aa5c03b89b5b6684b5b80eb6b",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000016",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "95333ae03286b09039d678663062f4f168bfbaec9b81ac8cab8326c4ae6f3605",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-087",
    "normative_row_sha256": "44fa426d6bb5000631ec0c0b3460e634f53022c78c5d9844568e6e34ed240369",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000017",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e2a38a79cda25416b4a45a0b4568c8fa54dd14215c07a5f52fd2b64b33c28656",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-088",
    "normative_row_sha256": "38ad2bab6838a2fc39c3765e6f82469b5ff2f0c65e781aafa184a9118af175a4",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000018",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a6020be993b2f3c56ebfd1fc6b11b8c3701cd7d65826abfb58b49ecceb2ae6f7",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-089",
    "normative_row_sha256": "1785979f0e008660ac50495cfd00f23bab58439b3ca66040b60cf4c8b2e91f31",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000019",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "18e57aca309d2c7a54b4a30318b5f863fa8eb3a25f1b4141a936fc122ea2f5e6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-090",
    "normative_row_sha256": "e3ea792c60773a5d45706a23adcbbfa49c0fafbc140e685e0580c3e4b8956c98",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001a",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "48ecc5de1e0d604c5fea957ded36b2c3b6532e4c06690de7a1f41c0e15589199",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-091",
    "normative_row_sha256": "47e0351fa1a6e26c9b6c3e2cd910b4d5bba20aae5b15d31fda3ab37ca75c962b",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001b",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4425fb1bd9766cb2e6b354e3ec835385ce995fd55e241e440f3885f2de5863fe",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-092",
    "normative_row_sha256": "21b070a0df52b7df05339b69af4cd1e041f4e5ac590b8891bdb4455f06b65c92",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x8000001c",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dd6c8389498ed7205edb0d5232c8c479c44cf749e282a52e62424024bac93cc9",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-093",
    "normative_row_sha256": "23e43bc0f892947f14a754b560c031479bf0845bdab30c88c4c168fc392835e9",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001d",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9be808426cdea0a0fb8344f85c0db29666d7218aa92e8a8b586377be5872bee7",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-094",
    "normative_row_sha256": "5328dfce4a265ad488bfb87a2b2a336baf319c769fdc18ec0eaf02f9e9eb0366",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001e",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "58921df66dfd191a9331e95769f18d021e34cecc17b2dde4663a2dff545cff55",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-095",
    "normative_row_sha256": "ee22b49d7a5114256e186c623a85b6bdb053cc03d462cebe85c546f43d8e2bd6",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x8000001f",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2bc2322a19879ab906785dab1edf9b3c084c4c48f7bce9d57da6e79b073021d7",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-096",
    "normative_row_sha256": "b20d7462e76928eae8d472ee8b7b46ba612e1570cb216e3d072504afd4931c20",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000020",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ac754be28a05bfcf4a88d9625427d9e1409a8540de64fc202137eb46f745b047",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-097",
    "normative_row_sha256": "bcd83cbcd31d26bf6c71698c0d303869847f996267be2c14cae31bf3dab5de4c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000021",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0e6417fab52d0b6beedf91f7706cb1cd0dd099db12e2ab9158b95e17cf8fd0ee",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-098",
    "normative_row_sha256": "92ff5584849be9f1a88449e37ae3ed3d53368c97fbd89c25618d8c2cfdf0f108",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000022",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6ebd5bfef6f4a7ef49abb8c09681ac1134731f60bd4a92438ab9fa43e19d18c3",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-099",
    "normative_row_sha256": "b8fdf18572dec18573932819037e3c52cd7e7d735eff8c28e4cfe767c662790d",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000022",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7f178126eab7d00c2c69bfa97986809462a567f65aa31aa9db6cda96f0c90cf6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-100",
    "normative_row_sha256": "d055d18fcbe576a3917728b13989f12cb452f2f762139b35370ec8496872ce08",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000023",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "630a71added83f2127893136c40cabbef9e3aeba64f4758fd7de58186c227a6b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-101",
    "normative_row_sha256": "756908fb71ad71409c0821556029da3b157aaecdfa2dc39172a64b8938d3ac0e",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000024",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fcf6487dae15c6d80499e5c7c3a51f616263d5a082ec3174cf2fe7693575cb96",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-102",
    "normative_row_sha256": "bcc15434735f21538499553fc6eafc728dc97e51db0576b5b49277dbe30d2cdb",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000025",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "21996f8c12bead2bfdf864ad383880b42d0aab0f29504e8bf9c751ea4ab79ed0",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-103",
    "normative_row_sha256": "19abaae5823bd01bcbccc870eab9919a250d516b89932993cc68e86782c9476c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000026",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fdfd5c2f98ddc55bd4ff65eb79665d061d4dc215360c17a36300853761012611",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-104",
    "normative_row_sha256": "aeec544bbcd37a43f1cd241fa9018f014a2784882d133edae9ad43dd81248b45",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000027",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f827476167ff1f6ce73762fa2ee00677afd6dc809e19b88c3fcbbbc4125ff222",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-105",
    "normative_row_sha256": "0f7904366f49c54f54d9de1642ac07776efb4b9a2147f738395d79e15e355e44",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000028",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "53df71357d90542e4e9495da7dbca45d27d50c1bde7d35c17e5545c05991eb3f",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-106",
    "normative_row_sha256": "fd1a692fbe1850f18372e0d6345278d3e947dcc4d12d2a84b43f1f9de0784194",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000029",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4a2eea6cd6cffd80391f00949fb011ac8fae21ecfd3bd7146dbfb6a0fcc27bef",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-107",
    "normative_row_sha256": "d3a43454b67f160216fc8b17b45a038a57a9e022750de1480e87d8145031ac50",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002a",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e93247a3ed52d35c0b430240c6af2a82915c4fface203499d26324e35e3ccd60",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-108",
    "normative_row_sha256": "6883ba67fb0bedb704bd9fc1ca6a4f1cbb2dc22b4725e678732f8fa23112d381",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002b",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a89d3dc73577445619c9a04e2d04779383df7bee57d4b16b3e84c954d7801eb0",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-109",
    "normative_row_sha256": "6dfa717a126736cce701861744e912d956ed75508efeea3af67ad37dea8d459c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002c",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ff32deccab19aa2430d46597692c818fefe6e746010f64e4e745e45453f402ec",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-110",
    "normative_row_sha256": "086949cbe5bedb01913f6342dd6873dc27a06d7ad12aca2c5f64712e7ed802e6",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002d",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "17e89e39b4f8329177c862a86685859f0b597f8b91eb1a22e82357e0accfd264",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-111",
    "normative_row_sha256": "02f3de4bddb24a29233ef044f5adecaf8f6bca06ee4bcb8aa9c25da978c907b6",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002e",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9896db17b177c8e78e12ab567a67f92b4b72eef33d3198c1b81224a02ef041e5",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-112",
    "normative_row_sha256": "431b11f268604d9aa5266d3b8bd7b026f6369fb3040d51c35ddf9b0d48a43f77",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002f",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1fa2af037321fdc2a6d259fc6fdaebfcbe0e2633e8027832d51e9d938df81abe",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-113",
    "normative_row_sha256": "e16e577a7faac9b0d875b7d6b75ff33fe238e3674f7aa06205bf506398b87706",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000030",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4e1732d18405542dc4978a0cd4f209a24b090908be86c74a69c8529ac0da9743",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-114",
    "normative_row_sha256": "a1a554495f242189dd916160ad4b882f0dd9aa2caf365b2fa3ad3d9a2b04c820",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000031",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "39c76fc064c611b01888dec4d8c73c8d2ade97f6d5d8844888a9545576436898",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-115",
    "normative_row_sha256": "0a01f0b06988ceafa5f3893252927e8c364b6587067bc625683ccf0c9a11b222",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000032",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "aaa6917be3a30f80044679f26162b78502be5c6e5869ba724fe279ef1f64ee2d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-116",
    "normative_row_sha256": "91b3b7c9cd0d9c8d3058b6325a3806a0f55e3d583c83a2047370c229cc8cff82",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000033",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "383266e9129104a16cc10e014799281668b98a04516ccd51bcaf6210830b0653",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-117",
    "normative_row_sha256": "8e7a8a3e86cbd3200768a635457edf9e54882970981e0524cffdc1a523dd4ca7",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000034",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3eb56cd147697540906db9d725a146acf06bc08159d95e81cab9d83da35adc92",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-118",
    "normative_row_sha256": "cb49d71d15253c73f4cba96a075c7affe61f359f8c195599107d6c2c53926477",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000035",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e70bd26b3386a59a0c5a2aa416c396dc0c09ced9af06426e47865428bc3d726b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-119",
    "normative_row_sha256": "77b0bedc94f107bb0d59574dd1cca46274fda0b7a8bc941a3b5832999702b909",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "UNKNOWN_WITH_LC_REQ_DYLD",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4de2b5c8e8411fe8b0ccff43a9cc7420aea553aa3cd5904ceca32b00d8bf9943",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-120",
    "normative_row_sha256": "6bee3ecfffa1414ece96a471064d0afbc0be09d9ad4af4f27d22fb0e913d129c",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "UNKNOWN_WITHOUT_LC_REQ_DYLD",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dc7c63bb9ebd3e59e8f4e146d5fa363d9424f57b7cf23dfdee7f3d705c05931b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-121",
    "normative_row_sha256": "67701adc48f60dfce782902975b119109692f90903fe499a52177878168a0e05",
    "domain": "Load-command numeric policy",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_NUMERIC",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "EXTERNAL_SYMBOLIC_ABSENT_FROM_V1",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "51de252a3ace40923a4c23fe72add38eecc04f6486da5de330b266c30bd4a64d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-122",
    "normative_row_sha256": "2a3f48c8443174409a7ad841c345720e01caac36df0fe102e5446d7fe77020d7",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_GRAPH_EDGE",
        "target": "graph.edges",
        "value": "SEED->LAWFUL_DEP",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d308e6be71b1694b50ad1bedc9719c2a899af6a34c055af2af82e123f1c050b2",
      "required_targets": [
        "fixture.baseline",
        "graph.edges"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-123",
    "normative_row_sha256": "d57ac5748660a9e119883998699c5d9356caa2acaa1ee39f63a14d2cfe20dfa2",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "graph.edges",
        "value": "SEED->A|A->B",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9ffbd5e23229df4fca7db804eba3b4d7e290970bb35208d6d86d357df7e90e81",
      "required_targets": [
        "fixture.baseline",
        "graph.edges"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-124",
    "normative_row_sha256": "1c0bc84a311e32be7c48bb7f6f78bfde9a5463d7360bde21306f62357acc9312",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "graph.edges",
        "value": "SEED->D|SEED->A|A->D",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "81dca6bd91849b9095e484f1605d43c4a290a71886e7d3e4cd4d042bafe9c99c",
      "required_targets": [
        "fixture.baseline",
        "graph.edges"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-125",
    "normative_row_sha256": "85cba56d09105f810f77c595ca509be6fbabd4cff747187cd62796ece1a3c612",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "UNRESOLVED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d60246fad1ddc1c96b4703f105a37a738ae07e1fb9e8bc08a578037ce1974fb6",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-126",
    "normative_row_sha256": "b1c70d5afa2756646e0832e057b7fb5cc2d78a54f1c6283af90029c62e8dd2e9",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "AMBIGUOUS_TWO_TARGETS",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "502b84280087102596ed74ee0e52c669fd1e5106069fad361a35afb46594816e",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-127",
    "normative_row_sha256": "4c5fd4f54cbc77c50f33deca568ff028e21913bee7a8cbac6fd7dc49f18188cf",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "UNIQUE_LOADER_PATH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8f2972a0543c8f5d809ba12ad4702262e9a15bbdf6e7ef18e6a798d64119aea5",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-128",
    "normative_row_sha256": "b2c06bcc5d41796c52d415bd5695b25ad5896973054952d6c1abe5855f13a7da",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "UNIQUE_EXECUTABLE_PATH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "212379aff29ece5033fa936becf2e49b622ab95ccdbd192452c0b687dfb0889f",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-129",
    "normative_row_sha256": "c32051e067a8d7d6be206953516c011ca6622063bb68e8332b0c544df4c3e43f",
    "domain": "Mach-O graph",
    "builder_id": "adv_build_dependency_graph",
    "action_kind": "GRAPH_CONFIGURE_DEPENDENCY",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "UNIQUE_ORDERED_RPATH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a3ed67b486c2a15ca79d934d4b045ec351698e49643424cc748b2aa88401869f",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-130",
    "normative_row_sha256": "0469cf35b19feaf03e38c07807e20f75027196dd6aad85512f38de26c8a39d4b",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "graph.context.seeds",
        "value": "SEED_A|SEED_B",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7fe6458fd9d7e7e60abee1d09f230e99e51e16b314e2b7ef362fac030a8e94d9",
      "required_targets": [
        "fixture.baseline",
        "graph.context.seeds"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-131",
    "normative_row_sha256": "0d856e39162b2a72cded56d1598c4c2bfdd53604566bcc5ef8ecd49be56aa94b",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "SAME_ACROSS_CONTEXTS",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e946fbc0a741a9246b042cba49fc9d4cfe75f37a456f713840cfcd664d97a708",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-132",
    "normative_row_sha256": "115f9eeb07b7c581682e50c0bec18b6651e82b0524b61703d1d489c324d428cb",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.context.install_name",
        "value": "DIFFERENT_LAWFUL_TARGETS",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b06831af437d6423946face909a6fc6613e53225bd3f4d95bd0fc1da253dd31",
      "required_targets": [
        "fixture.baseline",
        "graph.context.install_name"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-133",
    "normative_row_sha256": "132e3472f794a7c896092033c6daeaaed88d57989166b99b43210c8edb0b45c3",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "graph.edges",
        "value": "A->B|B->A",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "efcb7e38b1f03c877ae8de400f4284c50955de84767d033f05ccd8f806024a00",
      "required_targets": [
        "fixture.baseline",
        "graph.edges"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-134",
    "normative_row_sha256": "633a1cbe24d4108178ecce85fa2e861a069f7229e3f1e593f5bdac54bae2ea1d",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_GRAPH_RESOLUTION",
        "target": "graph.edge",
        "value": "AMBIGUOUS_RPATH",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8571203ed689e99902093b32f5bf4dde76c53ce6497a45a572736054e726a5f3",
      "required_targets": [
        "fixture.baseline",
        "graph.edge"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-135",
    "normative_row_sha256": "ab78702c4a8458035a67eb2b6fa0c77753c9040b0ace75d83fd681a5dd116bba",
    "domain": "Context closure",
    "builder_id": "adv_build_context_graph",
    "action_kind": "GRAPH_CONFIGURE_CONTEXT",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "graph.enumeration.order",
        "value": "PERMUTED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b3a274343d4b57618a31b79fdfccfeb108ff204427b54ea033cddb01675723b2",
      "required_targets": [
        "fixture.baseline",
        "graph.enumeration.order"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-136",
    "normative_row_sha256": "0b69f9f0cf3126a71d767c1b66e84d76eeb5a9e0cd779cd4c3319ed0b08472ee",
    "domain": "TOCTOU",
    "builder_id": "adv_build_toctou_source",
    "action_kind": "TOCTOU_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_READ_BEHAVIOR",
        "target": "source.read_sequence",
        "value": "FIRST_BYTES_THEN_MUTATE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e73f6dc4dd113db611b3df87d216293ee790a83ceaf3211f9af8ef40dfa1139b",
      "required_targets": [
        "fixture.baseline",
        "source.read_sequence"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-137",
    "normative_row_sha256": "83c5b7539414065d11e40fdfaf117b96af9159e6a13000fe3afa5d54505e54cd",
    "domain": "TOCTOU",
    "builder_id": "adv_build_toctou_source",
    "action_kind": "TOCTOU_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_READ_BEHAVIOR",
        "target": "source.read_sequence",
        "value": "ONE_VERIFIER_OWNED_READ",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4cbc5abac036ac28803aae8152a1e0f33805de75503634a2afd3b91974d33a3c",
      "required_targets": [
        "fixture.baseline",
        "source.read_sequence"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-138",
    "normative_row_sha256": "0e309e411142073e41b8a5f77e025a77cba313c159a9190c503b8842c8648cd4",
    "domain": "TOCTOU",
    "builder_id": "adv_build_toctou_source",
    "action_kind": "TOCTOU_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_READ_BEHAVIOR",
        "target": "source.read_sequence",
        "value": "SECOND_READ_SUBSTITUTION_ATTEMPT",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e4f298cea84f680981d0ac951bc0b7574687c883fe503dd51a17611bb5764ec0",
      "required_targets": [
        "fixture.baseline",
        "source.read_sequence"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-139",
    "normative_row_sha256": "73214ebabfdb920e95b29276d6a07d42f0421f9bbd1661f55fa646eed0679c3f",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "domain.membership",
        "value": "M1R_NATIVE_MEMBER",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b7ab5f6a904b27617cd515ec8d4042c5083d70dedf35cca7d754bcc107ec8910",
      "required_targets": [
        "domain.membership",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-140",
    "normative_row_sha256": "81f4de932e7ce3116348fc99554c895587150333618e10c6c06ea6ce030891bc",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "domain.membership",
        "value": "LEXICAL_ONLY_NOT_PROFILE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dfb1e8fa51d5567bae141758012a52d294a34a28af3b48dca449c3fa3fcac797",
      "required_targets": [
        "domain.membership",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-141",
    "normative_row_sha256": "4e5eac20a01dab3a1c51a2de851d45ceefbad2659a3e5e59e4f3c30bd14c405d",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "domain.membership",
        "value": "GRAPH_REACHED_CELLAR",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "825ebb3d379de87913ab2f401908e499342b26580a0068e0f8aba57ecbe933b2",
      "required_targets": [
        "domain.membership",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-142",
    "normative_row_sha256": "f7d7d897382c1fed125118ec247c4c50eb827181281bb0716e855ac08c15eb91",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "domain.membership",
        "value": "UNREACHED_CELLAR",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "64aafbfd27feb3a3311e873ec723999ea3362c0dc5aa3f6174ed5ceec6f5f5b5",
      "required_targets": [
        "domain.membership",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-143",
    "normative_row_sha256": "2d0bc6b358a2284accfc9f847f24e4aecfd3d0045c2e9cc2358ca99c577c22c7",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "domain.membership",
        "value": "OUTSIDE_ALL_ALLOWED_DOMAINS",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "69a06e81a66365db93c111196cfe10c0447d691a9e2a2e86e2a34282e349400b",
      "required_targets": [
        "domain.membership",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-144",
    "normative_row_sha256": "eba2a9a379b09d0907dca4c9c8c5a9634d236e5c8b5f9c951a7371342f855dc5",
    "domain": "Domain",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "domain.permission_from_host_scan",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fac297ce8a2be90ec8c585f86683f434baaaff9c758227a6dea2d5ccc87032e9",
      "required_targets": [
        "domain.permission_from_host_scan",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-145",
    "normative_row_sha256": "af1d9c2c4418fd302cee86ff79a5bc4f3a677d2d43537928f970bc8d6923395c",
    "domain": "System",
    "builder_id": "adv_build_domain_graph",
    "action_kind": "DOMAIN_CONFIGURE_MEMBERSHIP",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "domain.canonical_target",
        "value": "/usr/lib",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a5eebc7fc64f9443d08a6dd2018bc03be4ce1b09896e07272d82b994a7b5b140",
      "required_targets": [
        "domain.canonical_target",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-146",
    "normative_row_sha256": "78e072880ebc42b41967078cb1243bda0bd495b3e3ecd81a08fab3b50eb96211",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "optional_seeds.registry",
        "value": "",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2415f2742a1ac16cdcb63affeb7090b6bd3e89f840b4f555fb9a5ecaa94502fb",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.registry"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-147",
    "normative_row_sha256": "0063dc297d647030b4d3842068d70ea39b92f6915570ad9cbe8a3500e388fe14",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "optional_seeds.registry",
        "value": "RUNTIME_INSERTED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "21e0b359379f3a69393d7f4d33b54312b54fb6f3046d32af8cffd50f54706f40",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.registry"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-148",
    "normative_row_sha256": "159702e2aa4551788f53e7d1aa54b0e1a19c317349c7c4b06b94bf224dbd9cfe",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "optional_seeds.names",
        "value": "mpg123|zstd",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8ff71302686a9af7c73f60d309f0185ec01dfeb9fc7bf65c37926ef8695e1d59",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.names"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-149",
    "normative_row_sha256": "545980c06ad7025efb71c5fab54883f6c95d98f102cb8dce6b3567952a6fc16c",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "optional_seeds.resolution",
        "value": "MISSING",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2297aeb47a6e78adcbe46fee0a27b17ce0bd8e1eab54ad1b08a5acfbd86ef981",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.resolution"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-150",
    "normative_row_sha256": "5f31cce76ddd6c124268031936f43bc75d480230130af996d288f6364c00d2d9",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "optional_seeds.resolution",
        "value": "AMBIGUOUS_MULTIPLE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "92b3771b4c14b034a65816b9350c6f3f3abfaa58bb4c56251fd522f2e67b2710",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.resolution"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-151",
    "normative_row_sha256": "e9706205dede87761ff0f719966ce5f8999ba317ee86236d77ad4ed79c9d0261",
    "domain": "Optional seeds",
    "builder_id": "adv_build_optional_seed",
    "action_kind": "OPTIONAL_SEEDS_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "optional_seeds.resolution",
        "value": "UNMODELLED_REQUIRED_COMPONENT",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "bd8effdfac3b560d289135a628163ffe84af0c544f45adfa95051c6e92825f86",
      "required_targets": [
        "fixture.baseline",
        "optional_seeds.resolution"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-152",
    "normative_row_sha256": "0026979a2b2f7f3f0655f09092e651123e27c1a1aa09c7c4bec592f7d72f47f9",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "inventory.indices",
        "value": "EXTRA",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b5e216622f8f999a15a0bd85764e01a6170790c7903183f1e7923e7b84cab733",
      "required_targets": [
        "fixture.baseline",
        "inventory.indices"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-153",
    "normative_row_sha256": "d2fd7a288f9972512e1ce3a78b04527820367259df2272be592195139eb74eac",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "REMOVE_ENTRY",
        "target": "inventory.indices",
        "value": "DERIVED_REQUIRED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0890677de02afaa6bd718e7c4c31f1e5f1392026f7b666434526c303d32c0139",
      "required_targets": [
        "fixture.baseline",
        "inventory.indices"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-154",
    "normative_row_sha256": "44931d2c52298f790ebcef272199c920ee94b869531dd0eb2c1d961b02e58a03",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "inventory.order",
        "value": "REVERSED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e3225bc7476813580229c503461cb8c011cb70336bf4dbd4055141a6659ec2b3",
      "required_targets": [
        "fixture.baseline",
        "inventory.order"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-155",
    "normative_row_sha256": "ce6cdf7d7c004c5e33b34f8dc81358d8369a1da9d4838f1a0636de1caf8c2c85",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "inventory.duplicate_identity",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1a3b4cc0edef452e4ea45f1a4c738b600a903133b0ac7beefdb44e52afb27038",
      "required_targets": [
        "fixture.baseline",
        "inventory.duplicate_identity"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-156",
    "normative_row_sha256": "b0fb071dc0abf78834f4b2fff55cb0f91eef1db54b201628afb1999a2ace41af",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "inventory.entries",
        "value": "1000",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6392bcf1d16884d520427adf8b70f1e575a236a06570fc6372345720a1d88a38",
      "required_targets": [
        "fixture.baseline",
        "inventory.entries"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-157",
    "normative_row_sha256": "7121ea6e270317525e718b218f52e4b7b3f5b9f7c696824fc42bf0c0febc27bf",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "inventory.family_membership",
        "value": "BOTH_REACHABLE_EXACT_M1R",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "61201ebec3f0c2dd36ae833811d9b3c12baf4c9de7d92b67a1092fa5c6f9c0fd",
      "required_targets": [
        "fixture.baseline",
        "inventory.family_membership"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-158",
    "normative_row_sha256": "2ea4934694bf07f3d65ae5cabb6640a3afd195eb9722b6618359e25b29eba223",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "inventory.proposal",
        "value": "SAME_IDENTITY_TWO_FAMILIES",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f29ee8ccb13d4aa49afccf81cb50b89308660304f74f88950c48128a81d2a72f",
      "required_targets": [
        "fixture.baseline",
        "inventory.proposal"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-159",
    "normative_row_sha256": "dd949f33d7be0235a3b16701e8c82e0ad51a7d1e8d3fe90457683f915792aedd",
    "domain": "Inventory",
    "builder_id": "adv_build_inventory_case",
    "action_kind": "INVENTORY_CONFIGURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "inventory.family",
        "value": "UNDETERMINED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0112e3e849bd00e5ec773b5a4f2906d8d9ba6fbb658f6beff80f8aa9747488b8",
      "required_targets": [
        "fixture.baseline",
        "inventory.family"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-160",
    "normative_row_sha256": "6b5133644514246d1d83ec6a1fd8edf88e0c5c2a354a93b24fb2e35afc1a688d",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "CALLABLE_MEASURER_PARAMETER",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_callable_measurer_parameter",
      "expected_state_sha256": "377651d3599d2980a011f775116523e40942b17d6d6c80f224033a663f4e846e",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-161",
    "normative_row_sha256": "cfce7706be32e426cfe8c98724255f2a2d38777ee0dca96b788ec95baee13016",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "SETTER_HOOK",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4910bff6eb5f10afd62f58f850736f93cf5fb863f878df8fbcf1f25267c5b283",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-162",
    "normative_row_sha256": "e92d71e741cdc046716b7b9db0c129482b06e1995973fbfd4311c2ce98f2b18d",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "FACTORY",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7c740fb22757c202ff5cdaa1329ead7c2830ff686253c856a518f366d9a79bb0",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-163",
    "normative_row_sha256": "2e66a64069058becb76680378741c1bd73a528dc490539a56b3999f88bb6abe5",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "REGISTRY",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8706e541d6d843d85d5adcb2e0acc449c7fd06a7f66a171b31f38b47b4551db1",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-164",
    "normative_row_sha256": "0a82f41e0ee04065326de539e08f2c229808b0f6d317f2b0369472a0d10ad420",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "CALLBACK_PLUGIN_MAP",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "03b0bf6bcac26e3910f445f11ca8e385c4a2190215ca079d37e481e3dfd42e5b",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-165",
    "normative_row_sha256": "45434ab666a479876b79283290935756b149c00000a701b472432fc79a513621",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "MUTABLE_GLOBAL",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5c5e7a40ca3bd79b17cae71f3648c1faa878e3f184dcfb2c244f9169c60ed852",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-166",
    "normative_row_sha256": "3ae875a5cb5309efcc9bd58cb511bdb37b1a710a20d57af51aac4cc8e8086438",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "MODULE_LOADER",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a8a144ba4821158c9c25604d681bc6ab4687be37d48762caa59834e5f4e42692",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-167",
    "normative_row_sha256": "f0a583d19f2d764f64e89f7cea20bdf41d4ab72ebd3e3767fa65f82261acb1f9",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "PRODUCTION_SOURCE_PATH",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "82e42282f6a0cbc795b41402e7560834bcc3cd73852002e835adce96d8e949c1",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-168",
    "normative_row_sha256": "6c77e25a6cc3de0f4553af39d90d8a562c12acc971893d10f9a4af7ae4d69553",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "ORDINARY_SYS_PATH",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "61f61f955270bb6b63ac1fffdaea8864fb6f7e22a44b10b99e07ff83ac2d035d",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-169",
    "normative_row_sha256": "35a385dc0aaaa4e63de7ce93e1e769d106dedccebf3bd9d17fed3ad4f3403544",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "DEPENDENCY_MANIFEST",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2c7258b5cd203f83111aeda5e84a41dfa7c098e11dbb2cbe5e5f731318f79287",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-170",
    "normative_row_sha256": "3735be696c30f516108e45402323beec272aacd2bcf419e2558c6b8d90cd1d21",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "REEXPORT",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "89d61281a9b3afe1d8f69378e8e6b6598f7d68e0f889673a6306ba19766ef312",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-171",
    "normative_row_sha256": "d13669eeb4576d46da606ff5011780fff4131fbc8bda755b63b08774f5f35d02",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "IMPORT_RESOLVES",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4fbc1b2489313740e5f0b3103f38b6077028edfddb5059bc56c0e3d45ca5af2d",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-172",
    "normative_row_sha256": "d582b04b869719c381bf535f4b123e0374b4915b1c1c96190fdfcfe0fc80f2e6",
    "domain": "Oracle isolation",
    "builder_id": "adv_build_oracle_source_fixture",
    "action_kind": "ORACLE_CONFIGURE_SOURCE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "INSERT_SOURCE_FORM",
        "target": "oracle.surface",
        "value": "TEST_PATH_ONLY_IMPORT_FAILS",
        "aux": null
      }
    ],
    "governing_callable_id": "measure_and_handoff_n4a",
    "probe_id": "probe_oracle_and_boundary",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "711a195d9b48b86ca252d1772e82335320b05970cd3c24f1cffa6c8936b89a85",
      "required_targets": [
        "fixture.baseline",
        "oracle.surface"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-173",
    "normative_row_sha256": "8fac4338999a4a321fd364cbfdd9b6087a530c613cedd026b3b2ede5c9f1c9cf",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "venv.root",
        "value": "RUN_SCOPED_VENV_ROOT_V1",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "venv.reservation",
        "value": "FRESH_EXCLUSIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0b9e3c3b609e0cd64f7c81ae44e6997b98347bd535aacaceb6f78e746d336e0c",
      "required_targets": [
        "fixture.baseline",
        "venv.reservation",
        "venv.root"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-174",
    "normative_row_sha256": "02e4a28df28fad8c3e03471321ec27fbb91f375c04c327cdaa8201b246f0fb86",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "venv.root",
        "value": "ALTERNATE_NOMINATED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b07e0c58587fcef71d78ec59e3928540f93121aa50c4845c79c059528e6a314e",
      "required_targets": [
        "fixture.baseline",
        "venv.root"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-175",
    "normative_row_sha256": "3201720677db03744c565a346be200197031c6777794d9203e85aeefe2e16e45",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "venv.namespace.preexisting",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d85d09678ce3b524188deef26da4221d3a9006af4e0832f47aab725cdfea6ade",
      "required_targets": [
        "fixture.baseline",
        "venv.namespace.preexisting"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-176",
    "normative_row_sha256": "e8297cd289f14860ab4b70111614b9bc0c00fa182596134c6c4c55ea442ccdca",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "venv.path_component",
        "value": "SYMLINK",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7a8526ca5be15290bc60f08643bf4e77591bc56447ea08c41ad3119c57ed657d",
      "required_targets": [
        "fixture.baseline",
        "venv.path_component"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-177",
    "normative_row_sha256": "33cd6713fef3a6806c750134b98d76a84bdd7630c22611bbe4c3b9ee88675950",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "venv.generation",
        "value": "REUSED",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c15b6b9376548bcc4c64676a9803237902ab4a47e3f478eb67dc07cd180d2ba5",
      "required_targets": [
        "fixture.baseline",
        "venv.generation"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-178",
    "normative_row_sha256": "34cd7a0bbb100886d5c4de0850110074e0b1b703cdd9d9c263d93f187af8c3c6",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "venv.generation",
        "value": "WRONG_GENERATION",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "17e9f165dc38e150fff3655720df03892e065627a3f70d36c62257757f5f34d3",
      "required_targets": [
        "fixture.baseline",
        "venv.generation"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-179",
    "normative_row_sha256": "35b6b073af620a1bba9e20d6458bc12e4bba0cc6b77e5da8a9e11966f5b73e56",
    "domain": "Generation-bound venv",
    "builder_id": "adv_build_generation_venv",
    "action_kind": "VENV_CONFIGURE_NAMESPACE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_PATH",
        "target": "venv.root",
        "value": "/private/tmp/non-derived-venv",
        "aux": null
      }
    ],
    "governing_callable_id": "derive_frozen_snapshots",
    "probe_id": "probe_snapshot_inventory",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c7b354359d3f384888b9f2536281579729fb96c96c853cb376ec574b4ec2dc88",
      "required_targets": [
        "fixture.baseline",
        "venv.root"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-180",
    "normative_row_sha256": "90810c0dbcb2803d7489d56e4959301e043f803910a179e32ff821c8d90e9aba",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "census.tree",
        "value": "pkg/a/b/c/native.bin",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5e72ddcb6e74d41af938f43649c7674fe3f9f3f0eb518bce165883dbbe1f0c1f",
      "required_targets": [
        "census.tree",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-181",
    "normative_row_sha256": "781251ea0d60a5630d08c5020c3f5a1e7f3f2cf4003d8579446963de5b2f9dc7",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "census.tree",
        "value": ".hidden/native.bin",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "cbcbc12d6b935cdedd35ae72c66a8132fa9e29492ff5d5ee96645bc8cbe6acc4",
      "required_targets": [
        "census.tree",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-182",
    "normative_row_sha256": "796908599299454942991012938705cecd1d08d3f3f504aeef7b5129d14ac15f",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "census.tree",
        "value": "arbitrary/native.bin",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "25cc068b5f4dda49cf54442c4f676096c51161ca5421fc3a089d3a0cbf36beb8",
      "required_targets": [
        "census.tree",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-183",
    "normative_row_sha256": "ed77011e548ea367f47d77e8aa43839dadc5299543393126c1ca4326d2d4c08d",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "census.tree",
        "value": "pkg/native.unhinted",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "eebaa720e254f0877b0a9a1e10929357b3ee52ee91e399dc8eab5a3676a53eeb",
      "required_targets": [
        "census.tree",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-184",
    "normative_row_sha256": "145eb54e0b8b879be032447b8a05fa415855e6065b2cf74c3afad7dbe549d2c0",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.enumerator.mode",
        "value": "KNOWN_DIRS_ONLY",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4159e6ce67f81403755b2d11d17deeb941de86145d835ff306f61fd1351074a6",
      "required_targets": [
        "census.enumerator.mode",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-185",
    "normative_row_sha256": "a4532edcbf0c128d0f871fcecc8d3eed92b153b9dfe65d351508ff948fb474a5",
    "domain": "Exhaustive enumeration",
    "builder_id": "adv_build_census_enumeration",
    "action_kind": "CENSUS_CONFIGURE_ENUMERATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "census.tree.unsupported",
        "value": "FIFO_SOCKET_DEVICE_OTHER",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "da12e48f599e504d080b0d0afa0d8513016e1176e6771e4d36d4f11a294af1c6",
      "required_targets": [
        "census.tree.unsupported",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-186",
    "normative_row_sha256": "9cd8dfc17c9ad07651219362aaa17ccdcd15ab2332e5acca4c3a1d71db12e24a",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SYMLINK_TARGET",
        "target": "census.link",
        "value": "MISSING_TARGET",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ab723dc58ed495ec8c9871406fa1a32a7dac753a65fdf0c75815003d688710ff",
      "required_targets": [
        "census.link",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-187",
    "normative_row_sha256": "a86095ac367378c3f011ac78c004cab3baf0924ced488c4b7e803391f173b181",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SYMLINK_TARGET",
        "target": "census.link",
        "value": "OUTSIDE_ROOTS",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6e26d38e74276c96a58c41cf35572bbc7238dba335ad4bb78a12e6a18585cf51",
      "required_targets": [
        "census.link",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-188",
    "normative_row_sha256": "ec48cb323b73c5dee2f4522885e8624b8b46a31d3c183ee03305fd2529f32fc2",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SYMLINK_TARGET",
        "target": "census.link",
        "value": "BASE_ROOT_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5d0ca39977ea939b8424a81b38d623573895b96d582f8718775c0cf5d3c0d4c0",
      "required_targets": [
        "census.link",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-189",
    "normative_row_sha256": "edf260670e5f643b82c39677ea3ec2ab7deeea92f4fad0062b4a8623f38801f3",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.aliases",
        "value": "ALIAS_A->TARGET|ALIAS_B->TARGET",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ec2db6a85390576ee14f4ce8d8d088aadd7d6762afe9f6365cad9027123a9970",
      "required_targets": [
        "census.aliases",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-190",
    "normative_row_sha256": "d03536c3a1e998172f3d38f8d85f51438c694e0105fc17a2824884518953bb46",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.root_relation",
        "value": "EQUAL_NESTED_OR_OVERLAP",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e52fc893be8c8d78a05e4e4e2855add29dbeb0f86e82bbe3d7d314cd8c25ce30",
      "required_targets": [
        "census.root_relation",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-191",
    "normative_row_sha256": "a0bc4a2398440dedcb1359d3fe0af1484081b36102919b83e83dfef30543a2ed",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.relative_paths",
        "value": "UNICODE_LOOKALIKE_A|UNICODE_LOOKALIKE_B",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "079ea10d75d42e98b27da7578d86e0c0fa7d4c0b908a9b2d8d43fcc318b09438",
      "required_targets": [
        "census.relative_paths",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-192",
    "normative_row_sha256": "651af4db9c308d722f0e2e3d5f7fa0dbdcca694e16a8334376075eb134a168ca",
    "domain": "Symlink / scope",
    "builder_id": "adv_build_census_symlink",
    "action_kind": "CENSUS_CONFIGURE_SYMLINK",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.relative_paths",
        "value": "CasePath|casepath",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "25f0a758f541454fefc558688e4528a07111ef5d2372e62639b59d51e5597cc2",
      "required_targets": [
        "census.relative_paths",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-193",
    "normative_row_sha256": "abc40379f25361162e9bd56894a16c60c7bfe4829fcaa3ba144b31fffcc69023",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.state",
        "value": "NOT_OBSERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "67aa28f4674adc4c00d87552e61b3506e2b1927e9cb12cd83e82396acfe071cc",
      "required_targets": [
        "fixture.baseline",
        "s4.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-194",
    "normative_row_sha256": "8bfc979e799ede906bf205a6cf1b04187fadb27a5ba59827dd6931edc2d9cf09",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.state",
        "value": "MEASURED_AND_OWNER_PINNED",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.keyset.mode",
        "value": "MEASURED_EXACT_WITH_DIGEST_AND_COUNT",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.profile_digest",
        "value": "FIXTURE_DIGEST",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "s4.profile_count",
        "value": "1",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c2b443b63c52a2f4c4d60e857808b115e60c32c74e2d5a2c68d88f856327e856",
      "required_targets": [
        "fixture.baseline",
        "s4.keyset.mode",
        "s4.profile_count",
        "s4.profile_digest",
        "s4.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-195",
    "normative_row_sha256": "374ce9534c22b4ed389fff93cdf68cb50354fb14a88496e68e167e3e1e3993f9",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "s4.object.duplicate_member",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d186369fd70d6d86630e832807ef13e08a2343b2b0b4f0e0fcf2ba87dde07c05",
      "required_targets": [
        "fixture.baseline",
        "s4.object.duplicate_member"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-196",
    "normative_row_sha256": "1a1bc658d060605ecd2287efd3dac7c7f17fda64436b7b985b0a660452ed2c21",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.key.naming",
        "value": "ALIAS",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f44e61d40def5275c562ef56dbb92395e1b51fad9688a4a4ab508a4974edefb3",
      "required_targets": [
        "fixture.baseline",
        "s4.key.naming"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-197",
    "normative_row_sha256": "41b53f0fe1435cc56cc89ff0169623075631e18b8fb7f581e00157ac8c3ad837",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "REMOVE_ENTRY",
        "target": "s4.keys",
        "value": "ONE_REQUIRED_KEY",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "18557500b0521459fe379e89bcad935a7588feb11c68ac8ee7a1eeacb9b4404d",
      "required_targets": [
        "fixture.baseline",
        "s4.keys"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-198",
    "normative_row_sha256": "a1889b71f0cb55e1c02e53513880c7f0f3adc5185ff17a527ed8539b71d3eb31",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "s4.mutation.family",
        "value": "WRONG_TYPE_EACH_FIELD",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "22be58b9554e3c4abeb9ba3956ad8bdf0d2762741a157548d811716680ae8bac",
      "required_targets": [
        "fixture.baseline",
        "s4.mutation.family"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-199",
    "normative_row_sha256": "23521ae17ac53bc67a6a50a5e1fd2ded8d4865dfaa99cffe1d321686bb805118",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.echo.truth_binding",
        "value": "CONFLICT",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6a58bcc5f7812dc91536f66178c528e2dc4fb6df9000a67ea638454d08c9587b",
      "required_targets": [
        "fixture.baseline",
        "s4.echo.truth_binding"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-200",
    "normative_row_sha256": "aa074f31f9f5975cf083a3ddf3ea216fbfc2e896f88d66cde0049cd232682b84",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "s4.state",
        "value": "NOT_OBSERVED",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "s4.keys",
        "value": "DIGEST_OR_COUNT",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "42c2eb7f027e889d38076dab6512c47817bbe80933768702dca1b36542890ae8",
      "required_targets": [
        "fixture.baseline",
        "s4.keys",
        "s4.state"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-201",
    "normative_row_sha256": "e7848a9efa917ac00169fdd26b141a5facf3890bbc069a67342e05519b19c248",
    "domain": "S4 exact key set",
    "builder_id": "adv_build_s4_echo",
    "action_kind": "S4_CONFIGURE_ECHO",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "REMOVE_ENTRY",
        "target": "s4.keys",
        "value": "DIGEST_OR_COUNT",
        "aux": null
      }
    ],
    "governing_callable_id": "validate_s4_a2r_m1r_echo",
    "probe_id": "probe_domain_evaluation",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f65265381b2356f5c378d3977dd28997dcbc04ead0269bc713075db7b3ef141b",
      "required_targets": [
        "fixture.baseline",
        "s4.keys"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-202",
    "normative_row_sha256": "82692d41699631361b8fc600a91258177ad33de2d8fe490d3e17f58bee45c763",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_RANGE",
        "target": "macho.fat.slice",
        "value": "START_BEFORE_METADATA_END",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c9b05e8980d961df01260a6a4336d14da542d33b3d770ee38a70ee0fc98e938b",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.slice"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-203",
    "normative_row_sha256": "5758950fe6b4e52e850dcf18c1964124c0f075c713dd44ee005af5f65bcbbb3b",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.slice.size",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8f2291c9cfbb510bea54ed694581f7bdc88993f1086039240661fbe4102360b8",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.slice.size"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-204",
    "normative_row_sha256": "0cfcdb4e6216f195ef29100eb97e730b966681220004e3f4200fdf26ac5b7478",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.nonselected.payload",
        "value": "OPAQUE_NON_MACHO_VALID_RANGE",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c016410d2371e2f54a70c5176cefc9afce49fc1267d34a578ecb1125e9072483",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.nonselected.payload"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-205",
    "normative_row_sha256": "c27a112cc64d0b98d23d7c157219d3fc432cc5bce4a20dc9efe5638e3cba7d07",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.slice_ranges",
        "value": "VALID_WITH_GAPS",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f8e287d483bd538a9b72594fe2448c4c624f6e37b583ed1af63e59dc7a1c08a0",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.slice_ranges"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-206",
    "normative_row_sha256": "a65237047f3a3c558194df3874b01026b81e2978404a7b08e7f0d575861c0c85",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.trailing_bytes",
        "value": "PRESENT",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "44c42ff55b9a7314b0b7a104a1388d913f1a046d5cc57f4c6e9168ddf356f574",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.trailing_bytes"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-207",
    "normative_row_sha256": "1ca6050e6a13588b6b62dee0e94c7bbb21fe5296caab40730188f3c829de4e2f",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.arithmetic",
        "value": "BIGINT_OVER_HOST_WORD",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3884a1e650af0121769a600437189fdabc458ab62a90df701f1b32d4b25debc9",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.arithmetic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-208",
    "normative_row_sha256": "918a3f35beb851ad1498866e09a38e1a7590e450be684d72888ce13bdd0864cb",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.fat.table_truncated",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b057718d2d2e3c1d8557041d077db3113bb09b48b06743e460912a677b816df",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.table_truncated"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-209",
    "normative_row_sha256": "211760f85a0435f55b976fbe70f5407123305f574f767dec5af775f67294f9c4",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.fat.slice_end_oob",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4718d767d7f636451cf34193367c597ce6e07111b68a6e14e1433f1000626073",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.slice_end_oob"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-210",
    "normative_row_sha256": "858e1168385c31f58fc67e50e1a5cb437c293267414d0392f3657c8e97bb5c60",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_FLAG",
        "target": "macho.fat.slice_overlap",
        "value": "true",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dbabe50ebf1f65f36a2f717e99b35e83ae627b1451d62fa0531e1801470226e1",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.slice_overlap"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-211",
    "normative_row_sha256": "8590cd57de3c7e14046397e6259dcaf5d60e31b4ec3442c8cdbd6137fa851d50",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat.align",
        "value": "64_OR_MISALIGNED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4b20172fea654ed6c97cefac02367f46a266a07599561358e6f9761c2f9fb102",
      "required_targets": [
        "fixture.baseline",
        "macho.fat.align"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-212",
    "normative_row_sha256": "d28e13d01865b770b89f1099262ab7430dd309912e62b43fad562472811ba673",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.fat64.reserved",
        "value": "1",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "02f247232c794ed5c08828fa615a4162798c90e115f74a3a964aa9318d20dc1f",
      "required_targets": [
        "fixture.baseline",
        "macho.fat64.reserved"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-213",
    "normative_row_sha256": "921db782fdfe326afc26642ddb18b2f0cb554bd313f0be949e82faf52279b4ea",
    "domain": "FAT structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "FAT_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.outer_inner_cpu_match",
        "value": "false",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "bdb3e5f686c535882f7f175f91a9daad4977c1a0660d080cc2e59acce53aff5d",
      "required_targets": [
        "fixture.baseline",
        "macho.outer_inner_cpu_match"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-214",
    "normative_row_sha256": "c0462c586766719be837a033a52456dea77ca1612b87ac601ac5bd3cdb9865d0",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000001",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "82ac22f585d95352bc76ac1821f915f2b24ae286feeda9cffdb2263f4c760ad2",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-215",
    "normative_row_sha256": "41c0d53e2b4dfcadf461f2676b70481d5ef3d6c57b912687e1aa3bd89c86db12",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000002",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "87a0f88b8883b87f88cde6bb86b12f31880efc5fa83e9d349b64ec79b2921238",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-216",
    "normative_row_sha256": "711581c02ec57a8d73102ae5da1d5118f3a97071b295597a11984c0c49fd3518",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000003",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6c09e8b2158bf63def1bd0bbd4fe7e32f70cf98addd79fe0279e8e16a6b89a14",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-217",
    "normative_row_sha256": "d1e28cccf9133ed30c61265495ab45c10bcdcbc82cf4820fe407dd2583697f47",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000004",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "361e6b21ab8ec6d9617e632f734938bea8683c957efb9db75500f3ec4cc27dae",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-218",
    "normative_row_sha256": "495604eb6125de55e50c3391e9334eba1d24c30f7271b0a5464a787360afae36",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000005",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "500a8e37cf15f5353e6bfb27e3bcb1a27a736466c7906151e7b4b93a7cde5fee",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-219",
    "normative_row_sha256": "8926db71ea46adef77e6662045a1e5e5a85767ca55626034103abea1dbf69129",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000008",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4d7824f84c1a4c6472c2ee16b3070b8d152e41e6ec19ac40592f97ebe9957a02",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-220",
    "normative_row_sha256": "e610fc4be6f66f12207bbcb1c26a8c8a7d0a01f58f661b9a10b3c5928d0536f0",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000b",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3fb206b3c261cfe20f2f4e606a8187e7ddd7d3cc5495c32aadfe917e8fbc6a7d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-221",
    "normative_row_sha256": "8c7d0baa0adf32eec65efa9c7f0572b79d9abd0480f6f1d53e2895303273db43",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000c",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5cca49996e1f8b514f42f4c070501c7b62db6aca56b7c348f325272c7510d393",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-222",
    "normative_row_sha256": "eb8c578b2d7bdddc788301f030b3946bd103f3b02fb93ca433b830aee3152764",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000d",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "32163d5aeee7c605c249c911f4a2ceae89537d08e11e5e43aa0365ee8caacd10",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-223",
    "normative_row_sha256": "cda29f39c48116d74de4df8b95a64c3c9de4d1b247b47728803845e4eeea70a9",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000e",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "30ecac601a0dee307e55e71e59879a6166260ee7a4f3eec5e43ccf4820ef28aa",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-224",
    "normative_row_sha256": "2b165f0c9005be385c0414cdf891e0f451156d66d4e1476de640fbd85770f84a",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000000f",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5ddff1ea1922701c0a0213df94e75d95502526439006e3f208aaf2eb834f306b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-225",
    "normative_row_sha256": "0d56a5e55fb15bed71fb13a101c13e63226590eac61b62f21e77b830279387df",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000011",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c21a25d06f91844225e42741c6fa2a4874269ef5a9d31c2e63428ef04e74efec",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-226",
    "normative_row_sha256": "76799f2b6ef87edaab4221dbb0b30df71c3a07e651c3f10a442a704fe8fbb9ca",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000016",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f907301b40fa5f7e731124c35dcded4f5712cd707fc9cb1fb9c7417a4a280dd6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-227",
    "normative_row_sha256": "19fad4d17fd6e7a3bbcc900f155d3c6904cff3c5452a1c2c5e0e6e9d3d8fdd96",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000017",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d73903af28837a803235077efe5fb61ce1517a02746821554ba729fa6018f683",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-228",
    "normative_row_sha256": "167a05b89dd9c66392c7ea241abc09ef6d1ee8bfff11fb83c80bec426eeb6e17",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000018",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d3de5262de6b279e67f2004b82bdcbeae205f57dd8d1a4eb8f8b656eec5276d6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-229",
    "normative_row_sha256": "d86d74e72891ebc06e21150619a4926a26935e50d1dca66bacab48041a3946b1",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000019",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "96a686fb5132089355312cd635e69ce463efeef290614552a8537211618cdf2e",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-230",
    "normative_row_sha256": "5108de5253355f0fc626a9739f408efb853e05e09cf5154e12f893871e1040cd",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001a",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "52e8f512b59f47400291ad48fb0d931b70012e2918371a0b524230db2a4c77be",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-231",
    "normative_row_sha256": "ca677c2e4228fdf441f9a698af3bf8c07cf96ae5f13045b61db2c56f33a5f90a",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001b",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "cf9dc28147e1395400266ca89a98f254660210e2f392e2286bb3242e179e789b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-232",
    "normative_row_sha256": "549c17a78ff91b52c963a1963b942daa2488b35bc422bb8afae31967ef53e8e2",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x8000001c",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "05748e2b826fd97083742af35515e673a58f73e2025ea630d257cbee7d5992d6",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-233",
    "normative_row_sha256": "5ef75f592f240c043944b1574856a720ad38fa8375fe997345986eebb658b4a2",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001d",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a93fdbd9220a17eeaabf1b8ee489d0c4b530680a91c70ad729a35a75c29126ca",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-234",
    "normative_row_sha256": "797042dc1849d4036538e1edb23a3f40fe49bab84630d3e5d60960abde19f226",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000001e",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ab05916bdcd384e0fc8e8dc6c4914c2aab8f989400368ecafb4275e6b09279f9",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-235",
    "normative_row_sha256": "5bf0b39e5ff80aeb110d2c65ac82c66cd04a31dccd9ce70b0d26c5b1f075868b",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x8000001f",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b740672d1530dba82ae3e756a60fd8aa69fbfd06f5ddadf0fb71fbf988342267",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-236",
    "normative_row_sha256": "47cb39aa3c3e96fb3e805649712af6c2dffb1319f7c380cece30fdbffb799f90",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000020",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "709d8625cfb2f6f997f05d385461d0d44042ebee1be9b7395686e39c3936b3ae",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-237",
    "normative_row_sha256": "2ad22e4803a87a04257921a614b775aa42cf75801a735fe11952f565e66bbc00",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000021",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3e97404e2e863242c47f215ef50e8ded7ea8a7109368cb5fbbfa485dabf80083",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-238",
    "normative_row_sha256": "79799d16c5e79287fea224c1547a99f81fc176239b4def945f0b6a7f0379bf66",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000022",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "c28e0c07bd7dc7d04f53b54dec6e09bd32a45dade0897b5529f4311c16650bd1",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-239",
    "normative_row_sha256": "4874560c2e6e37719eb48f895add2aa7a98139b9872f49660226024f24e76111",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000022",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2c2d628322d9bf3033041320ee24a470dc622eb4bc280bb7b9cc70da6ac0ee7d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-240",
    "normative_row_sha256": "ce747da4da9ae905a8aa6f6f0ea8c2e77ed5a31966f8ce519d0f8a9a6a806f19",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000023",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ee66a1a5855583b80f05372592320e57cc9caeedc8a4986970258c29f6c240c8",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-241",
    "normative_row_sha256": "3288e0c8d13cfd2f2f7ee39025e206e60db67f262575e40559b94ea84384288e",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000024",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5b6c7cc9e65bb7a468fe10c0ab0ecd9d7bf3972ee0e4f3a1560d15590132a33f",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-242",
    "normative_row_sha256": "ac5a361f2aac403974a416ef53e24b4a8caeee1736df519e7a69809422b56eef",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000025",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2cd6b341a46c6c1c10bdc3a4192563d0a2890f277433eb288b977de35491baa0",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-243",
    "normative_row_sha256": "b668eaff8f91c86186c99fc0a9ccc58e6ac4794ba8d03075afeb09ace3c537a9",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000026",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1bb1629f3cc787a6d897498f14cc03c2daec46f1ac0c614c7d81e45de9f53b22",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-244",
    "normative_row_sha256": "b82b4f3f302eac916b9d6fe60e756bc490035f22bac22a761ddf74492ca1ad5f",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000028",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "82578b1939d8730bc462e48ecd81c6091ed76b6cdfd223047a4a2b0eddb1ca02",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-245",
    "normative_row_sha256": "50993ce3b9fce2f513715f74632fae0c3f9ad72f72b63a07e10120a9ddb13756",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000029",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3257f84a5ab08ed0726ffc2157c48888e09d52984cc4305a05e09cab4dfccb44",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-246",
    "normative_row_sha256": "92c69c4e5164bc283bcedc59e1a3a1ba3d6bd0aeb653ac7c62b417b0b3ce6867",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002a",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2808a685564767feedfe9fdb6a5357ff880adfb054a3b6eb7b380b2cd6c41209",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-247",
    "normative_row_sha256": "94b017d79ac6006125b413c96c8e36ac614c55c2da8d4d66a8f0241d31f631b9",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002b",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8452c6abc18eec434348680d2e6353e7b21028314258ffa02b5a3e75dfdaa233",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-248",
    "normative_row_sha256": "e67d91566758bd03acb303c45719b3ff4da032b74adc55d41050a970f6ddc976",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002c",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "96d5de5d057028e33fa60e666afb1dd65b837eb51d14c9006a70ad6761fb19f3",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-249",
    "normative_row_sha256": "0252b36e92e9b5661ac7eb0331494f633ad8924d23d96b02ada63ab45bac6160",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002d",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA|NONZERO_PADDING_RESERVED",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "22c2bd0dc1a4dafc0ab431a5549cb96cf4e0fbe7ef0fddfd5c239c679ea058f2",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-250",
    "normative_row_sha256": "f50606d38150d3e1168dfaddc10f02a9778699fe164d0dadc3a6e0bcdab08b65",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002e",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "54f9944c6b217ee76db17adc0379fd663f3681c7675242ef6e05567655b4b308",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-251",
    "normative_row_sha256": "d31dd51dcbd4ea8bcfd9e1eb2c687277a5d67c695fab897c7d39f552440f05f4",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x0000002f",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "bb6f8c8a0636035d80ce9f285cfa02050ab5035b5deac7bf32f71ca4d2ddcbb5",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-252",
    "normative_row_sha256": "e7651f45922ef27100232a2df672da216ba5ca7337101821dc04e281208f7050",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000030",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "cd4fcdceeda6929c061bc47d1e2797ce6bec2246e15fb58edf67df4ab9ce1651",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-253",
    "normative_row_sha256": "333a1d804911a18035e4354c51ede9d220c735ab59fb6c2d85e417dcb92c2451",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000031",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "118bba8a1ecd6ab35703bd5fcf51ede05bfe8297cc977e7e6565192a6903e60d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-254",
    "normative_row_sha256": "cdbd1e3bf9701de87df4e69c7af64b6f29aeb5bfd74ff55163ee894823aed459",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x00000032",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|MALFORMED_FORMULA",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4a2967f24a332f592b059978e0f07fa51b3ed1a9d896501b9ed2a2cf8b60f6da",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-255",
    "normative_row_sha256": "8e8e2c05c2caf12714c5246869b302766a40f03a32fd4dfdca7259ff25fb5a74",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000033",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fd2b780f21bf79f53537c0d1f20df31079b782fcc78bd1c809cf6fd8c0140902",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-256",
    "normative_row_sha256": "0bf114bcaa0be349fd603045b132c4f6ce4c941216733afcc58e5b4f856c9c81",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.load_command.cmd",
        "value": "0x80000034",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OVERSIZED_TRAILING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8ef301d01021054f7af9078a266dcb687427ef9d6414f943bde6c6da08d2becb",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.cmd",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-257",
    "normative_row_sha256": "464f8c09a6218889d3d89742a399e86e743ef315c4a2e5c84bfb367f4aea4dc2",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|PAYLOAD_LT_24",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8a1a949d47ae06789149af9341c6949f8da26964676e4dc80872d48d46494ae0",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-258",
    "normative_row_sha256": "d7202a3245571b62348de5341c8f7dc19d58967016143bd6cbf00f3cecbb8206",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|NONZERO_PADDING_RESERVED|INVALID_STRING_OR_NUL_OR_PADDING",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "fb03f991e8a2e4b1513183da012fc3d7ed37f95015e994bdc4595617a4363cbc",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-259",
    "normative_row_sha256": "1b981ce688adfe3ba2f4535007811298a32e5c33c401b91cc5cc6438cdf06aa4",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|CMDSIZE_FORMULA_MISMATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2f02d9053978c5167a4ed1da2db2d50425d0c9ba45c57e4f9c59bc9a2597ad31",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-260",
    "normative_row_sha256": "f80301c59feec72b17ff3875ec62a7fd0e76ba02f96b9822558235f2cd532e8e",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|CMDSIZE_FORMULA_MISMATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2f02d9053978c5167a4ed1da2db2d50425d0c9ba45c57e4f9c59bc9a2597ad31",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-261",
    "normative_row_sha256": "92be0b2d61c5549a90fb4d43f89390ce4860a7a9e6001f8f4b998499ce75fc6d",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|OFFSET_NUL_PADDING_VIOLATION",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6d4cf0eb1c1e9ecc684e5e4f531aa82bad3f7481514f3f07bc6f4d415c35d43a",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-262",
    "normative_row_sha256": "0059a671a21def9b51c8e658f3c641b846cd53d8b43d68c29565e0108eabbb53",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|COMMAND_INTERVAL_OVERLAP_OR_GAP",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "84d6cb316dcb2d28579b1cd3713cd4e8f7bf0e648f5f3c95ba3e78c94dd74801",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-263",
    "normative_row_sha256": "819bdf6e6550ebbce0e0eadd7c488984bb8dbfcf3b2d64069b77df6e3767b316",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|NCMDS_MISMATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1c710d59ef76e27d1fa2a8960389a21d2816acfad5edb485dbb37f4bb27b395d",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-264",
    "normative_row_sha256": "4617127b41b306694af52d9c1023612d4e6360617eae679c7ca3a408fe4c58ca",
    "domain": "Load-command structural grammar",
    "builder_id": "adv_build_native_image",
    "action_kind": "LOAD_COMMAND_CONFIGURE_STRUCTURE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "macho.load_command.structural_variants",
        "value": "MINIMAL_VALID|UNDERSIZED|SIZEOFCMDS_MISMATCH",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "a6f0cc21e91e663ba1266cb224445801bab299fb2c986655817aeab8d11e365b",
      "required_targets": [
        "fixture.baseline",
        "macho.load_command.structural_variants"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-265",
    "normative_row_sha256": "28a153fcbf6fc518a2201852b1d9f7d90e19d0fd047e505dfee06d2b0715dc9f",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "resolver.symlinks",
        "value": "A->A",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "77dbf3f4fd259e06479c3b5dcb15ec9c3c9ae473c79682c04ebe2fbbb8655d68",
      "required_targets": [
        "fixture.baseline",
        "resolver.symlinks"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-266",
    "normative_row_sha256": "f8d44a388ab5c1310a4405d0d9f763ab937e1dc4c04a0917110a44514ef9235e",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "resolver.symlinks",
        "value": "A->B|B->A",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f623df28c6307cff32a02f2ae680108e857ee2edd5394a9ec333152e30798658",
      "required_targets": [
        "fixture.baseline",
        "resolver.symlinks"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-267",
    "normative_row_sha256": "b0ab4df69d011db08ba941a3590e6d236b6e4aa2e4d4d85995e9e98b619a5eda",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "resolver.symlinks",
        "value": "A->B|B->C|C->B",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "2139ffec635e505c1e3928f566eaeb36a679ecd0b91f4a777c374b096897a649",
      "required_targets": [
        "fixture.baseline",
        "resolver.symlinks"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-268",
    "normative_row_sha256": "97a2641d6848a0b56cf077be080ea4bd73f26ae8ec45956c185adf428a6f865d",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SYMLINK_TARGET",
        "target": "resolver.link",
        "value": "MISSING_TARGET",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "f3e4e9542dd59e9fcc428c00b43b58a7d8ebd35f00156626d59ff4a96e9fa3c0",
      "required_targets": [
        "fixture.baseline",
        "resolver.link"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-269",
    "normative_row_sha256": "9283e5ac08514e164b64594575afd04de9e870b845fb1845ecc8c3be3c966c10",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "resolver.intermediate_component",
        "value": "MISSING",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5d4c450e18ec4bac4014c54bc51b7d5589b36d99f81e124161dafe73c5f98c2f",
      "required_targets": [
        "fixture.baseline",
        "resolver.intermediate_component"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-270",
    "normative_row_sha256": "cd1596c03205763388b1217537d0aa2c53d191791a3c05e2bde71cb900bcb199",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "resolver.failure",
        "value": "PERMISSION_IO_CANONICALIZATION",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "18a1c7f15bd7270a80de331ca1e27a600adc57e0fc220c51495192251181624f",
      "required_targets": [
        "fixture.baseline",
        "resolver.failure"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-271",
    "normative_row_sha256": "161e06cc093b82b327da19d50e6f2c1383d780bb54a5c383af47aab84f8a62e7",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "resolver.target",
        "value": "UNSUPPORTED",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0b7c2d2758d0b6f6e4f47c51dc0cd54c1f0451523caf64ea3c3e590cda216415",
      "required_targets": [
        "fixture.baseline",
        "resolver.target"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-272",
    "normative_row_sha256": "4b504b1036b8546b4889653f5579c2e92bbd2a2db6b98a5fa91c79355cb3c0af",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "resolver.target",
        "value": "REGULAR_FILE_ONE_ROOT",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0b28a673ccff0090345644086ea6f1e8bc0484f8ff0a9f0f0b974a4f9d5c3a06",
      "required_targets": [
        "fixture.baseline",
        "resolver.target"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-273",
    "normative_row_sha256": "5be3caf72206fb36dd27a8d60c586bd60a2bb748186f683b0bdb89d650f49235",
    "domain": "PATH_CANONICALIZATION_V1",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_CANONICALIZATION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "resolver.target",
        "value": "REAL_DIRECTORY",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8f3d15c58e5e579f31f9d912c83d28149cf59308a3f839e5077e9eb444ad3d3a",
      "required_targets": [
        "fixture.baseline",
        "resolver.target"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-274",
    "normative_row_sha256": "3028de0d750e7d65d6314cf1218b87d57956d83b3df7725a5fc9831741c7c8db",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.required_expansions",
        "value": "31",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5ca505d0cb5e7071ecd340c0bc93cb1b68e05b7a1be5873774049607ea142b0c",
      "required_targets": [
        "fixture.baseline",
        "resolver.required_expansions"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-275",
    "normative_row_sha256": "bc66a1727862e768f32ad0fb46865a8a938368dec461c2cbd47123849a934d24",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.required_expansions",
        "value": "32",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e6c785547d68fc7b7f313c3261e01b2eec08b1b2bc4c6cad1696902322a775de",
      "required_targets": [
        "fixture.baseline",
        "resolver.required_expansions"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-276",
    "normative_row_sha256": "4cfc3076281da5178602e01e9ecc4e15319ff3ea614b69e97911040baa358f53",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.required_expansions",
        "value": "33",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7696936fa3c4ee7177599f6a18e065d37f16636a85bd0a4777283b7adf682c54",
      "required_targets": [
        "fixture.baseline",
        "resolver.required_expansions"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-277",
    "normative_row_sha256": "d211a2f1fcc5604cdcec4918976754105ff21a1a265b8b3bc7e66b0ddcbe6388",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "resolver.mutation",
        "value": "FRESH_PATH_EACH_HOP",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "252124240a15302413ba10b2c70d6c963ceb0b56d025d5a9e9363921d9cb9755",
      "required_targets": [
        "fixture.baseline",
        "resolver.mutation"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-278",
    "normative_row_sha256": "959848aad2d3b461c5f07116c6c00ff722b298127d095f22331eb1ef87838745",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.repeat_at_hop",
        "value": "5",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "802ee3926e9cfc6a2b2105cda20da6965c40439dce3478644e67968543a0c611",
      "required_targets": [
        "fixture.baseline",
        "resolver.repeat_at_hop"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-279",
    "normative_row_sha256": "67a4af055ae2e8c126e867547ed0c9ce704e04ad453ca80eecd59671abc96afd",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.host_limit",
        "value": "16",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "dce43b5673c644f57a83a48b6e1c510711c1d81a535a73981a766e4aed1d7558",
      "required_targets": [
        "fixture.baseline",
        "resolver.host_limit"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-280",
    "normative_row_sha256": "78b170fc2cdfa37caaab9dbcf4fc6a9cf2bf4ab2ebadda4da9ad6054d4f10080",
    "domain": "Resolver hop bound",
    "builder_id": "adv_build_canonical_path",
    "action_kind": "PATH_CONFIGURE_HOP_BOUND",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "resolver.host_limit",
        "value": "64",
        "aux": null
      }
    ],
    "governing_callable_id": "canonicalize_path_v1",
    "probe_id": "probe_canonicalization",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6860c20960753027c842750612b9cf49daa3bf10c6ea3457ff4d73ba0bf61cc5",
      "required_targets": [
        "fixture.baseline",
        "resolver.host_limit"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-281",
    "normative_row_sha256": "0213d2474bd8bbed6842a74d4fbff10b9e68341ee511c95b71e088b05796f6f6",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "ADD_ENTRY",
        "target": "census.b.namespace",
        "value": "INSERTED",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b87dbaf4be4ae34d8964774e4693b0bca23852f8d39b18ec5aa03fdfc0dde77e",
      "required_targets": [
        "census.b.namespace",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-282",
    "normative_row_sha256": "59ba32f263c9ec8a4afc05a4848a6712e7679571b1579672cb4a729767f6649d",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "REMOVE_ENTRY",
        "target": "census.b.namespace",
        "value": "BASELINE_ENTRY",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ca1df1615f339c61b36e2232f9885d82dd4f6d888026ca7bbcc847bfc926a733",
      "required_targets": [
        "census.b.namespace",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-283",
    "normative_row_sha256": "8e815b62e5ef8ed05b3895eb901e638475f45110b02d97da9d1b46cebd05aabf",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "RENAME_ENTRY",
        "target": "census.b.namespace",
        "value": "OLD->NEW",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8874ab29a30edc4faaa439cdfc4ac2630e8e71c39f94da4f1f424828f0ec36f7",
      "required_targets": [
        "census.b.namespace",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-284",
    "normative_row_sha256": "cb96388e4d503e18cded61ff89be1494d66e3a36aa789ecaa755e436e57c1833",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "census.b.entry",
        "value": "SYMLINK",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7b9987ee98709d6f09e7ba8a4b1aefe32b97e76e8c112f1636da6f724d5b9c92",
      "required_targets": [
        "census.b.entry",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-285",
    "normative_row_sha256": "fa1edf1bbcca3e5e4eec3a03d7a408c126211530ceb73b819a6d6f9a55bed42b",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_ENTRY_KIND",
        "target": "census.b.entry",
        "value": "REGULAR_FILE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "619199d9eb7f69cbcd7e0b829f155c030bd44d850b5c9c49da91c23b3251c7be",
      "required_targets": [
        "census.b.entry",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-286",
    "normative_row_sha256": "3e953c599c7f3501047382541333a13e608d55576b3429ec6f3c36082c6c4069",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SYMLINK_TARGET",
        "target": "census.b.link",
        "value": "DIFFERENT_TARGET",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1796f13d1f1711890bf770922a178a53857090ab75d01c582680f567c1a00fdc",
      "required_targets": [
        "census.b.link",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-287",
    "normative_row_sha256": "2000a085bef35f0bb36dfdd86826f29591502a21ecf448e0e1786c7815c0081a",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "census.b.native_bytes",
        "value": "DEADBEEF",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "eb57058be6fd68d8bbd874e5b9e521bba2fbaae88d16c3caf104b8b7c040731c",
      "required_targets": [
        "census.b.native_bytes",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-288",
    "normative_row_sha256": "90ab43638849a25ef8f5ca2f520760d01bbf61dbc005e629aefc9b24e3afb5ec",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE->NATIVE_MEMBER",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NATIVE_MEMBER->NON_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b44e1e07e910e8ca1e81750c17f7bf288a898f9e0b55daa09e65ff15edda34d",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-289",
    "normative_row_sha256": "1732409116b033f0ec479e5265ea768febc55d9574bd17a6742453571be8ce16",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE->NATIVE_MEMBER",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NATIVE_MEMBER->NON_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b44e1e07e910e8ca1e81750c17f7bf288a898f9e0b55daa09e65ff15edda34d",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-290",
    "normative_row_sha256": "92d08cd0d85ff47fef6aaaec31ff9911bf755baa3b67a3a1bffcfd3e53083556",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "RENAME_ENTRY",
        "target": "census.b.namespace",
        "value": "OLD->NEW",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8874ab29a30edc4faaa439cdfc4ac2630e8e71c39f94da4f1f424828f0ec36f7",
      "required_targets": [
        "census.b.namespace",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-291",
    "normative_row_sha256": "751249b517ede994c950955d86937e5a69d0a6e8ce1c541229e6b293ab8fb969",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE->NON_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "3ad08cd33e21627f70beb5bb21b253c236c4e9df6f158e823c08268278756ff4",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-292",
    "normative_row_sha256": "4a417dec4ae19643c230133aa02a4056ca8b15e2d7919c7c56891f50a488c5ab",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.a_b_relation",
        "value": "IDENTICAL",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4644a7c7cce8e109e586faf007a2f5f6d9836c7104d8b93cf76e3cff7562671c",
      "required_targets": [
        "census.a_b_relation",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-293",
    "normative_row_sha256": "fdfade4f9b83ac22b27f0034e0801701b23d0764ecc88b6c000e080f60f70460",
    "domain": "Stable census / classifier transition",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE|NON_NATIVE",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "census.b.ordinary_bytes",
        "value": "A1B2C3D4",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "1d1dc257cc3a0dc6d7af05e76a7171a4c3b7f2129f7212786384d79cf8ce5d24",
      "required_targets": [
        "census.b.ordinary_bytes",
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-294",
    "normative_row_sha256": "39d5f82ed26e86209f34326e62b8cc7d2b11715798b3027e8f1b1b97736fd281",
    "domain": "Stable census / classifier transition",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE->NATIVE_MEMBER",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NATIVE_MEMBER->NON_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b44e1e07e910e8ca1e81750c17f7bf288a898f9e0b55daa09e65ff15edda34d",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-295",
    "normative_row_sha256": "e98e3014eda57eabbf10e1243aea88f371fd0545518353a3e07011875e162101",
    "domain": "Stable census / classifier transition",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NON_NATIVE->NATIVE_MEMBER",
        "aux": null
      },
      {
        "opcode": "SET_SEQUENCE",
        "target": "census.classification",
        "value": "NATIVE_MEMBER->NON_NATIVE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6b44e1e07e910e8ca1e81750c17f7bf288a898f9e0b55daa09e65ff15edda34d",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-296",
    "normative_row_sha256": "2d1b51bb8e7d45b0386e55fdcec482fcd0fad75e69fb33d1f669a873e5c6ef68",
    "domain": "Stable census / classifier transition",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_BYTES_HEX",
        "target": "census.b.native_bytes",
        "value": "DEADBEEF",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "eb57058be6fd68d8bbd874e5b9e521bba2fbaae88d16c3caf104b8b7c040731c",
      "required_targets": [
        "census.b.native_bytes",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-297",
    "normative_row_sha256": "707f00281b885d4ceb996fdbe9d1353a2e98de54619504909c2abccd0436a32f",
    "domain": "Stable census / classifier transition",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_CLASSIFIER_TRANSITION",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.classification",
        "value": "UNSUPPORTED_MACHO_CANDIDATE",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "22c7c6bbf3b366d78abbf5dae75aa3840e8c448b9adcf58a0e837363c287d45d",
      "required_targets": [
        "census.classification",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-298",
    "normative_row_sha256": "6de18dd4de0c5e2d6a82a1da4d166fabd8c7780fe850c42a4de64f252f53a240",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.writer_capability",
        "value": "PROJECT_WRITER_RETAINED",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "5dc73171cf4bd566eb9f84e1499970cea0b01a01e97ffcd6cdc72744100d94ff",
      "required_targets": [
        "census.writer_capability",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-299",
    "normative_row_sha256": "48596e627c3120f6513797871f49e93197bb4357b4864e88aea6263606995574",
    "domain": "Stable census",
    "builder_id": "adv_build_stable_census",
    "action_kind": "CENSUS_CONFIGURE_STABLE",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "census.verifier_behavior",
        "value": "MUTATES_ROOT",
        "aux": null
      }
    ],
    "governing_callable_id": "capture_stable_census",
    "probe_id": "probe_census_trace",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "af8f0bc36f36af658dc4dc44d55266c959dd0fda812a0812adbd8c1d1b5371ae",
      "required_targets": [
        "census.verifier_behavior",
        "fixture.baseline"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-300",
    "normative_row_sha256": "0983128dde4b81f11234d5162808c56d2bc0eee16acfdf54b7350b272741f856",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9d28024f5a53d00c9dd626ff4bba29bce35af1b80f776c24127540d395802c1f",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-301",
    "normative_row_sha256": "57f1ade6d7e087188dcb28f27dd8e57fa86b8fbca2c03f83ba5dd024f107a554",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.slice.length",
        "value": "31",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9fdf90eb8e0a099ded19110044e1b5bedda579088f46624fd83b9a35dddaf85d",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic",
        "macho.slice.length"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-302",
    "normative_row_sha256": "550941abe7393deb75753812853a009aa2eec50ae1e5b9db9dfe652cd6cc8d38",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "NOT_0xfeedfacf",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "215be68ffe7d99d3a6966fe648ea33ae3af0508e1e2b60fbf2beff2eb3194025",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-303",
    "normative_row_sha256": "82531df879499ad03ea7e298f6c29e37461ae7490190d23198e8599017d9e3b3",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9d28024f5a53d00c9dd626ff4bba29bce35af1b80f776c24127540d395802c1f",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-304",
    "normative_row_sha256": "4dc678eae77f72454a49cf68b2c7dd3bcc5aa02966ebcab93e71419346630e50",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "2",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "4ef1db36763b3b0008b4d9b90c47e335c4ba611df53bd8f28624a6755b8a3d6b",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-305",
    "normative_row_sha256": "601a35008029427ed1f4105f7a14476fecd79f5acf75ac1d00d585712759c023",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "99",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "b94c4cf6bb279ee05a1d3ab961873195f63cbd567d2c0cb83723268fa7a855f4",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-306",
    "normative_row_sha256": "b3a709926cdce448de22b39c0257aafb3cb3c4f17312b7d65212877b538d1a26",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.command_region",
        "value": "EXCEEDS_SLICE",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "7630fb127f7f550f4c4d0e64b397835953bfc42ce9f9d09c02227e7f6eaf36d8",
      "required_targets": [
        "fixture.baseline",
        "macho.header.command_region",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-307",
    "normative_row_sha256": "e68758b76ce5a1e4e45e1915c0ca83e9866fb4da87a98420d6a8e55d9217553a",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.header.ncmds",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.header.sizeofcmds",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "ce1e1f294e4c2d0c4667ca02902e7a5a2f9ccdab7ae9aa481aeb67a22b79687f",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic",
        "macho.header.ncmds",
        "macho.header.sizeofcmds"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-308",
    "normative_row_sha256": "af976cf9f00464340fb051f187198f6bd0ddb0d39e5f1dd704f2fad5669e73ef",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.header.ncmds",
        "value": "1",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.header.sizeofcmds",
        "value": "0",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "247c75b11ef376332df8668b06a63596e0f2de3fef48c5f8566791479a55ce7c",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic",
        "macho.header.ncmds",
        "macho.header.sizeofcmds"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-309",
    "normative_row_sha256": "db86405a59777265db3741bdf72952a4413e6aaac5246b9db04292e4b69415bc",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.fake_command.offset",
        "value": "31",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "27e8f144b68d32b35ff8ac3442320177af53d202d53d39ce1acd91b32523037f",
      "required_targets": [
        "fixture.baseline",
        "macho.fake_command.offset",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-310",
    "normative_row_sha256": "aa00cd862dad35d34946262c927948f9715ca4126922aacd7d5be986c7f01d00",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_COUNT",
        "target": "macho.fake_command.offset",
        "value": "33",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "9052cd2d6c4e2d52ea0dbb5459e04368964bc3ca0df5630d5281eb1a66cb56c4",
      "required_targets": [
        "fixture.baseline",
        "macho.fake_command.offset",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-311",
    "normative_row_sha256": "7779f455ed83bb55ca73d79be8f05d8e45e7b0a169890012ea82dba109fdadfc",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "FAT_ARM64_NONZERO_OFFSET",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "d6ad33e8b0fae0ebfcfb22e6c6860950a2109624ab5320d149a3beaf1a4fe2c3",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-312",
    "normative_row_sha256": "ecd8ff74fe4291588298b4599ddd381162117ca44437e843c7e9393654212b80",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.container.kind",
        "value": "THIN64",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "0bf41177657e2c8828c786f2400a4682c7ff685ac1bc2db77d9623e72a468617",
      "required_targets": [
        "fixture.baseline",
        "macho.container.kind",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-313",
    "normative_row_sha256": "e74fc3ec5b771e80fe1d64571b66079979c6200709962e059363a84b6292314b",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.filetype",
        "value": "ARBITRARY_RAW",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "199015586868bf9ebe140a1aa277335c07497b3af5bd200e93bbf61c9dfc6cd9",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.filetype",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-314",
    "normative_row_sha256": "845ba234290ed2321880c4f71a99081fae74ea0dff6fb1d786a2dc6481c6c142",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.flags",
        "value": "ARBITRARY_RAW",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "e5da0d29983c7d1e7ed0781a6c0e62918f3a969291a6fe11a8a46acdfb66df82",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.flags",
        "macho.header.magic"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-315",
    "normative_row_sha256": "2bc589e6493dad08383053dcdfe665df3b823f202ab69b9c94f2e1ff94862616",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.reserved",
        "value": "ARBITRARY_RAW",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "6fa70397bec74204a635cef865a7db56fb25a1300c0ed4e42ccc599bcc5847e8",
      "required_targets": [
        "fixture.baseline",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.magic",
        "macho.header.reserved"
      ]
    }
  },
  {
    "row_id": "REV18-ADV-316",
    "normative_row_sha256": "4be960999693c0df6f7435ab9c533a284577da75fd3acd5683bfc8513c986caa",
    "domain": "Mach-O header64",
    "builder_id": "adv_build_native_image",
    "action_kind": "MACHO_CONFIGURE_HEADER64",
    "action_args": [
      {
        "opcode": "SET_SCALAR",
        "target": "fixture.baseline",
        "value": "VALID",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.magic",
        "value": "0xfeedfacf",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cputype",
        "value": "0x0100000c",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.cpusubtype",
        "value": "0",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.filetype",
        "value": "ARBITRARY_RAW",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.flags",
        "value": "ARBITRARY_RAW",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.header.reserved",
        "value": "ARBITRARY_RAW",
        "aux": null
      },
      {
        "opcode": "SET_SCALAR",
        "target": "macho.external_parser.result",
        "value": "REJECT_STRICTER_THAN_PROJECT",
        "aux": null
      }
    ],
    "governing_callable_id": "MACHO_NATIVE_CONTAINER_PARSE_V1",
    "probe_id": "probe_macho_parser",
    "post_mutation_invariant": {
      "observer_id": "observe_fixture_program_state",
      "expected_state_sha256": "8ecf5bfed1b11dcf334c8188f545ff14b72bd947fcfab028eb1a9bc3da17ec19",
      "required_targets": [
        "fixture.baseline",
        "macho.external_parser.result",
        "macho.header.cpusubtype",
        "macho.header.cputype",
        "macho.header.filetype",
        "macho.header.flags",
        "macho.header.magic",
        "macho.header.reserved"
      ]
    }
  }
]
~~~

The separate comparison truth is:

~~~json[
  {
    "row_id": "REV18-ADV-001",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "derive `PYTHON_BASE_RUNTIME_ROOT_V1`; root check passes, but Generation-B eligibility still blocked while baseline is `NOT_OBSERVED`"
  },
  {
    "row_id": "REV18-ADV-002",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-003",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-004",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "capability fixture passes; fixture baseline is test-only and grants no runtime authority"
  },
  {
    "row_id": "REV18-ADV-005",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-006",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-007",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-008",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "do not traverse; fail P25"
  },
  {
    "row_id": "REV18-ADV-009",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "included by byte/container recognition if otherwise supported"
  },
  {
    "row_id": "REV18-ADV-010",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "not a native-closure member merely by suffix"
  },
  {
    "row_id": "REV18-ADV-011",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "profile token/count/digest mismatch; fail P25"
  },
  {
    "row_id": "REV18-ADV-012",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "profile token/count/digest mismatch; fail P25"
  },
  {
    "row_id": "REV18-ADV-013",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "profile digest mismatch; fail P25"
  },
  {
    "row_id": "REV18-ADV-014",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-015",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "identical sorted serialization and profile digest"
  },
  {
    "row_id": "REV18-ADV-016",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "native-closure profile unchanged; no claim of full software-supply-chain integrity"
  },
  {
    "row_id": "REV18-ADV-017",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "Generation B ineligible: `BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`"
  },
  {
    "row_id": "REV18-ADV-018",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "derive one `HOMEBREW_FFMPEG_KEG_ROOT_V1` subject"
  },
  {
    "row_id": "REV18-ADV-019",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-020",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-021",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "locator accepted only after canonical root + identity checks"
  },
  {
    "row_id": "REV18-ADV-022",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25; authority does not update"
  },
  {
    "row_id": "REV18-ADV-023",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-024",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "echo-coherence capability passes; echo grants no authority"
  },
  {
    "row_id": "REV18-ADV-025",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "every omission fails P25"
  },
  {
    "row_id": "REV18-ADV-026",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-027",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "every wrong type fails P25"
  },
  {
    "row_id": "REV18-ADV-028",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-029",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "honest current-state representation; no place\u0068older digest/count"
  },
  {
    "row_id": "REV18-ADV-030",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-031",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "`M1R_NATIVE_CANDIDATE_CLASSIFIER_V1` returns exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-032",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-033",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-034",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-035",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-036",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `NON_NATIVE`; native parser not invoked"
  },
  {
    "row_id": "REV18-ADV-037",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "return exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25"
  },
  {
    "row_id": "REV18-ADV-038",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "return exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25"
  },
  {
    "row_id": "REV18-ADV-039",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "native parser is invoked; wrapper returns exactly `UNSUPPORTED_MACHO_CANDIDATE`; fail P25; never `NON_NATIVE`"
  },
  {
    "row_id": "REV18-ADV-040",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "native parser succeeds; wrapper returns exactly `NATIVE_MEMBER`"
  },
  {
    "row_id": "REV18-ADV-041",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "`MACHO_NATIVE_CONTAINER_PARSE_V1` fails exactly `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-042",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail exactly `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-043",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "parse succeeds under the closed project grammar"
  },
  {
    "row_id": "REV18-ADV-044",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail closed; parser result cannot be downgraded to ordinary `NON_NATIVE`"
  },
  {
    "row_id": "REV18-ADV-045",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "project result remains `REJECT_UNSUPPORTED`; external parser knowledge cannot widen authority"
  },
  {
    "row_id": "REV18-ADV-046",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "PASS if all remaining structure/commands are valid"
  },
  {
    "row_id": "REV18-ADV-047",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "inspect exactly that arm64 slice; PASS if graph valid"
  },
  {
    "row_id": "REV18-ADV-048",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "inspect exactly that arm64 slice; PASS if graph valid"
  },
  {
    "row_id": "REV18-ADV-049",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-050",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-051",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-052",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-053",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-054",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-055",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-056",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "supported"
  },
  {
    "row_id": "REV18-ADV-057",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "supported"
  },
  {
    "row_id": "REV18-ADV-058",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-059",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-060",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-061",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-062",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25; no preference selection"
  },
  {
    "row_id": "REV18-ADV-063",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-064",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-065",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-066",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-067",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-068",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-069",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-070",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-071",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-072",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-073",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-074",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-075",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-076",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "exactly one governed dependency edge with normal target-resolution law"
  },
  {
    "row_id": "REV18-ADV-077",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-078",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-079",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-080",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-081",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-082",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-083",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-084",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-085",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-086",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-087",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-088",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "exactly one governed dependency edge with normal target-resolution law"
  },
  {
    "row_id": "REV18-ADV-089",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-090",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-091",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-092",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-093",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-094",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-095",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "exactly one governed dependency edge with normal target-resolution law"
  },
  {
    "row_id": "REV18-ADV-096",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "exactly one governed dependency edge with normal target-resolution law"
  },
  {
    "row_id": "REV18-ADV-097",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-098",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-099",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-100",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "exactly one governed dependency edge with normal target-resolution law"
  },
  {
    "row_id": "REV18-ADV-101",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-102",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-103",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-104",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-105",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-106",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-107",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-108",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-109",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-110",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-111",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-112",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-113",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-114",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-115",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-116",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-117",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted with declared non-edge role and zero dependency edge"
  },
  {
    "row_id": "REV18-ADV-118",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-119",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-120",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`"
  },
  {
    "row_id": "REV18-ADV-121",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / `REJECT_UNSUPPORTED`; parser knowledge cannot widen policy"
  },
  {
    "row_id": "REV18-ADV-122",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "included exactly once"
  },
  {
    "row_id": "REV18-ADV-123",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "included by fixed-point closure"
  },
  {
    "row_id": "REV18-ADV-124",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "one global identity only after context agreement"
  },
  {
    "row_id": "REV18-ADV-125",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-126",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-127",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "deterministic PASS"
  },
  {
    "row_id": "REV18-ADV-128",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "deterministic PASS under carried originating context"
  },
  {
    "row_id": "REV18-ADV-129",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "deterministic PASS"
  },
  {
    "row_id": "REV18-ADV-130",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "evaluate both state contexts"
  },
  {
    "row_id": "REV18-ADV-131",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "one globally de-duplicated target"
  },
  {
    "row_id": "REV18-ADV-132",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-133",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "fixed-point PASS; no duplicate"
  },
  {
    "row_id": "REV18-ADV-134",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-135",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "byte-identical final inventory/order"
  },
  {
    "row_id": "REV18-ADV-136",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "hash/parse/materialized bytes remain the initial transient image"
  },
  {
    "row_id": "REV18-ADV-137",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "all derive from exactly one transient byte image"
  },
  {
    "row_id": "REV18-ADV-138",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 / substitution impossible under governed interface"
  },
  {
    "row_id": "REV18-ADV-139",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "Domain P/Python-family admission in capability fixture"
  },
  {
    "row_id": "REV18-ADV-140",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "no Domain-P authority; fail unless separately lawful under Domain H/system"
  },
  {
    "row_id": "REV18-ADV-141",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "Domain H admission"
  },
  {
    "row_id": "REV18-ADV-142",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-143",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-144",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-145",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "observed/classified system; no entitlement role"
  },
  {
    "row_id": "REV18-ADV-146",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "PASS"
  },
  {
    "row_id": "REV18-ADV-147",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-148",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "no authority; registry remains empty"
  },
  {
    "row_id": "REV18-ADV-149",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "resolver fails closed; fixture never becomes production authority"
  },
  {
    "row_id": "REV18-ADV-150",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "resolver fails closed; fixture never becomes production authority"
  },
  {
    "row_id": "REV18-ADV-151",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "generation ineligible pending owner-approved design revision"
  },
  {
    "row_id": "REV18-ADV-152",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-153",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-154",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-155",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-156",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-157",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "emitted once; Python family precedence"
  },
  {
    "row_id": "REV18-ADV-158",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "proposal grants no authority; verifier derives one family or fails P25"
  },
  {
    "row_id": "REV18-ADV-159",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-160",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-161",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-162",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-163",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-164",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-165",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-166",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-167",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-168",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-169",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-170",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-171",
    "expected_kind": "STATIC_REJECT",
    "expected_failure_code": null,
    "expected_detail": "row 5 negative scan fails"
  },
  {
    "row_id": "REV18-ADV-172",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "valid test-only isolation"
  },
  {
    "row_id": "REV18-ADV-173",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "locator/binding condition passes; remaining A2R/M1R checks still required"
  },
  {
    "row_id": "REV18-ADV-174",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25; nominated path is non-authoritative"
  },
  {
    "row_id": "REV18-ADV-175",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 on collision; do not adopt it"
  },
  {
    "row_id": "REV18-ADV-176",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-177",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-178",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-179",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-180",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "it is enumerated and included"
  },
  {
    "row_id": "REV18-ADV-181",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "it is enumerated and included"
  },
  {
    "row_id": "REV18-ADV-182",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "it is enumerated and included"
  },
  {
    "row_id": "REV18-ADV-183",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "byte policy determines membership; it is included if supported"
  },
  {
    "row_id": "REV18-ADV-184",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "capability fails P25; incomplete traversal is non-conforming"
  },
  {
    "row_id": "REV18-ADV-185",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-186",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-187",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-188",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "classify canonical target under `BASE_RUNTIME`; no venv alias row"
  },
  {
    "row_id": "REV18-ADV-189",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "collapse before serialization to one target-owning row"
  },
  {
    "row_id": "REV18-ADV-190",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 before traversal"
  },
  {
    "row_id": "REV18-ADV-191",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "preserve exact UTF-8 bytes as distinct pathname subjects; no normalization"
  },
  {
    "row_id": "REV18-ADV-192",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "preserve as distinct pathname subjects; no case folding"
  },
  {
    "row_id": "REV18-ADV-193",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "schema coherence passes; digest/count absent"
  },
  {
    "row_id": "REV18-ADV-194",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "schema capability passes only as synthetic fixture; no runtime authority"
  },
  {
    "row_id": "REV18-ADV-195",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 before schema validation"
  },
  {
    "row_id": "REV18-ADV-196",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-197",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-198",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-199",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-200",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-201",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-202",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-203",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-204",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "outer validation passes; payload is ignored and contributes no edge"
  },
  {
    "row_id": "REV18-ADV-205",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "permitted; gaps ignored"
  },
  {
    "row_id": "REV18-ADV-206",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "permitted; trailing bytes ignored"
  },
  {
    "row_id": "REV18-ADV-207",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "validity follows mathematical integers only; host-width behavior cannot change result"
  },
  {
    "row_id": "REV18-ADV-208",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-209",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-210",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-211",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-212",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-213",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-214",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-215",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-216",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-217",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-218",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-219",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-220",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-221",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-222",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-223",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-224",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-225",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-226",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-227",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-228",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-229",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-230",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-231",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-232",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-233",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-234",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-235",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-236",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-237",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-238",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-239",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-240",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `DEPENDENCY_EDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-241",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-242",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-243",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-244",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-245",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-246",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-247",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-248",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-249",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-250",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-251",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-252",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-253",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-254",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-255",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-256",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "minimal valid fixture is accepted with policy disposition `SUPPORTED_NONEDGE`; every malformed variant fails P25 before edge extraction"
  },
  {
    "row_id": "REV18-ADV-257",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25; no edge is emitted"
  },
  {
    "row_id": "REV18-ADV-258",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-259",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-260",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-261",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-262",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-263",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-264",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-265",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `SYMLINK_CYCLE`; fail P25; terminate without traversal"
  },
  {
    "row_id": "REV18-ADV-266",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `SYMLINK_CYCLE`; fail P25; terminate without host retry/ELOOP semantics"
  },
  {
    "row_id": "REV18-ADV-267",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `SYMLINK_CYCLE`; fail P25"
  },
  {
    "row_id": "REV18-ADV-268",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `DANGLING`; fail P25"
  },
  {
    "row_id": "REV18-ADV-269",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `DANGLING`; fail P25"
  },
  {
    "row_id": "REV18-ADV-270",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `CANONICALIZATION_FAILURE`; fail P25"
  },
  {
    "row_id": "REV18-ADV-271",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "resolver result exactly `RESOLVED_UNSUPPORTED_OBJECT`; fail P25"
  },
  {
    "row_id": "REV18-ADV-272",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "resolver result exactly `RESOLVED_REGULAR_FILE`; continue only under existing target-owning file-symlink law"
  },
  {
    "row_id": "REV18-ADV-273",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "resolver result exactly `RESOLVED_DIRECTORY`; directory-symlink law fails P25 and never traverses it"
  },
  {
    "row_id": "REV18-ADV-274",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "may continue to ordinary final regular-file classification if all other rules pass; `symlink_hops = 31`"
  },
  {
    "row_id": "REV18-ADV-275",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "may continue to ordinary final regular-file classification if all other rules pass; no 33rd expansion occurs"
  },
  {
    "row_id": "REV18-ADV-276",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "return exactly `CANONICALIZATION_FAILURE_HOP_LIMIT`; fail P25; do not expand target 33"
  },
  {
    "row_id": "REV18-ADV-277",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "terminate at the project-owned ceiling with `CANONICALIZATION_FAILURE_HOP_LIMIT`; no claim that external mutation was prevented"
  },
  {
    "row_id": "REV18-ADV-278",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "return exactly `SYMLINK_CYCLE`, not hop-limit failure"
  },
  {
    "row_id": "REV18-ADV-279",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "host limit is not project authority; an earlier host observation failure maps fail-closed through the existing canonicalization-failure family and does not redefine the project constant"
  },
  {
    "row_id": "REV18-ADV-280",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "project ceiling controls; expansion 33 is forbidden and returns `CANONICALIZATION_FAILURE_HOP_LIMIT`"
  },
  {
    "row_id": "REV18-ADV-281",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "Census A/B namespace sets differ; fail P25"
  },
  {
    "row_id": "REV18-ADV-282",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "Census A/B namespace sets differ; fail P25"
  },
  {
    "row_id": "REV18-ADV-283",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "Census A/B namespace sets differ; fail P25"
  },
  {
    "row_id": "REV18-ADV-284",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "entry-kind/namespace row differs; fail P25"
  },
  {
    "row_id": "REV18-ADV-285",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "entry-kind/namespace row differs; fail P25"
  },
  {
    "row_id": "REV18-ADV-286",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "raw target bytes and/or canonical target identity differs; fail P25"
  },
  {
    "row_id": "REV18-ADV-287",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "Census-B native stability digest differs; fail P25"
  },
  {
    "row_id": "REV18-ADV-288",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "classification transition; fail P25"
  },
  {
    "row_id": "REV18-ADV-289",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "classification transition; fail P25"
  },
  {
    "row_id": "REV18-ADV-290",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "namespace/root-scope rows differ; fail P25"
  },
  {
    "row_id": "REV18-ADV-291",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "allowed by M1R; namespace/classification stability passes; no full-content-integrity claim"
  },
  {
    "row_id": "REV18-ADV-292",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "stable-census capability passes; fixture grants no runtime/profile authority"
  },
  {
    "row_id": "REV18-ADV-293",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "may pass if namespace/classification obligations otherwise hold; ordinary non-native byte equality is not required"
  },
  {
    "row_id": "REV18-ADV-294",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-295",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-296",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-297",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 immediately"
  },
  {
    "row_id": "REV18-ADV-298",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "project-writer quiescence not established; fail P25 before successful capture"
  },
  {
    "row_id": "REV18-ADV-299",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "verifier-quiescence invariant violated; fail P25"
  },
  {
    "row_id": "REV18-ADV-300",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "`TABLE-MACHO-HEADER64-V1` accepts header; command region begins/ends at 32"
  },
  {
    "row_id": "REV18-ADV-301",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "invalid/truncated supported candidate; fail P25; never classify `NON_NATIVE`"
  },
  {
    "row_id": "REV18-ADV-302",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail project header/container policy"
  },
  {
    "row_id": "REV18-ADV-303",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-304",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-305",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25"
  },
  {
    "row_id": "REV18-ADV-306",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "fail P25 without host-integer overflow semantics"
  },
  {
    "row_id": "REV18-ADV-307",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accept empty command region; consumed command count and bytes are both exactly zero"
  },
  {
    "row_id": "REV18-ADV-308",
    "expected_kind": "EVIDENCE_FAILURE",
    "expected_failure_code": "DEPENDENCY_INVENTORY_DERIVATION_INVALID",
    "expected_detail": "exact command-count/byte-total law cannot both hold; fail P25"
  },
  {
    "row_id": "REV18-ADV-309",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "non-authoritative placement; walker still starts exactly at 32 and malformed project walk fails P25"
  },
  {
    "row_id": "REV18-ADV-310",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "non-authoritative placement; walker still starts exactly at 32 and malformed project walk fails P25"
  },
  {
    "row_id": "REV18-ADV-311",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "header origin is selected-slice-local 0; command walker begins selected-slice-local 32"
  },
  {
    "row_id": "REV18-ADV-312",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "file byte 0 is header origin; command walker begins file byte 32"
  },
  {
    "row_id": "REV18-ADV-313",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted as raw V1 metadata; no independent rejection"
  },
  {
    "row_id": "REV18-ADV-314",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted as raw V1 metadata; no independent rejection"
  },
  {
    "row_id": "REV18-ADV-315",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "accepted as raw V1 metadata; no independent rejection"
  },
  {
    "row_id": "REV18-ADV-316",
    "expected_kind": "PASS",
    "expected_failure_code": null,
    "expected_detail": "generic-parser result is non-normative; project result remains determined solely by V1 grammar"
  }
]
~~~

Implementation code may not parse normative case text to choose a mutation. It receives the already-frozen `AdversarialConstructionSpec`. The builder receives only `builder_id` and returns a neutral fixture. The action receives only `action_kind`, the listed `FixtureMutationOp` tuple and the fixture. Every operation is applied in order under the opcode semantics above. The mutation observer runs **before** the governing callable; it directly reads every touched target and requires the canonical state SHA-256 and required-target set in `post_mutation_invariant`. It never trusts an action receipt. Probe installation receives only `probe_id` and `governing_callable_id`. `AdversarialExecutionRequest` contains no expected kind/code/detail. Only the external comparator receives `AdversarialExpectation`. Every `expected_detail` is the exact trimmed `Required outcome` cell from the normative spec row. The probe must derive `observed_detail` solely from actual governing-call return/exception/state and may not read row expectation text; the comparator requires exact `observed_kind`, failure code and `observed_detail == expected_detail`.

Meta-tests independently replace builder, action, mutation observer, governing-call executor and result probe with no-op/echo/wrong-behavior forms; each must fail. Independent mutations of builder_id, action_kind, action_args, callable_id, probe_id, post_mutation_invariant and expected_result must each fail validation or execution. Count/id/hash equality alone cannot pass.

### 8.10 Closed static shell command/sink grammar

Task 15 remains STATIC ONLY: pytest plus `bash -n`; no Swift/build/codesign execution.

The final permitted script shape is exactly:

~~~bash
#!/bin/bash
set -euo pipefail
: "${GATE0_STAGE_B_FROZEN_S2:?non-empty required}"
: "${GATE0_STAGE_B_SEALED_DESTINATION:?non-empty required}"
: "${STAGE_B_SIGN_IDENTITY:?non-empty required}"
APP="$GATE0_STAGE_B_SEALED_DESTINATION"
BIN_PATH="$(/usr/bin/swift build -c release --package-path macos/stage_b --scratch-path "$APP/.swift-build" --show-bin-path)"
PRODUCT="$BIN_PATH/stage-b-sandbox-runner"
/bin/mkdir -p "$APP/Contents/MacOS"
/bin/cp -- macos/stage_b/Info.plist "$APP/Contents/Info.plist"
/bin/cp -- "$PRODUCT" "$APP/Contents/MacOS/StageBSandboxRunner"
/usr/bin/codesign --force --sign "$STAGE_B_SIGN_IDENTITY" --entitlements "$GATE0_STAGE_B_FROZEN_S2" --identifier org.centaurioun.video-intelligence-pipeline.gate0.stageb "$APP"
/usr/bin/codesign --verify --strict --verbose=4 "$APP"
/bin/echo "$APP"
~~~

The parser supports only: the exact shebang and `set` line above; the three exact non-empty guards; the three exact assignments APP/BIN_PATH/PRODUCT where BIN_PATH is the **only** permitted command substitution and its inner command must be SWIFT_BUILD; and the simple command families below. No redirection, pipeline, background operator, function, loop, conditional, eval/exec/source, glob, heredoc, process substitution, arithmetic expansion or additional command substitution is permitted.

~~~json[
  {
    "family": "SWIFT_BUILD",
    "executables": [
      "/usr/bin/swift"
    ],
    "context": "only as BIN_PATH command-substitution assignment",
    "argv_shape": [
      "build",
      "-c",
      "release",
      "--package-path",
      "macos/stage_b",
      "--scratch-path",
      "$APP/.swift-build",
      "--show-bin-path"
    ],
    "allowed_options": [
      "-c release",
      "--package-path macos/stage_b",
      "--scratch-path <path>",
      "--show-bin-path"
    ],
    "source_positions": [
      [
        6,
        "SEALED_DESTINATION_DERIVED"
      ]
    ],
    "sink_positions": [
      [
        6,
        "BUILD_DESTINATION"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "MKDIR",
    "executables": [
      "/bin/mkdir"
    ],
    "context": "simple command",
    "argv_shape": [
      "-p",
      "$APP/Contents/MacOS"
    ],
    "allowed_options": [
      "-p"
    ],
    "source_positions": [],
    "sink_positions": [
      [
        1,
        "DIRECTORY_DESTINATION"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "CP_INFO",
    "executables": [
      "/bin/cp"
    ],
    "context": "simple command",
    "argv_shape": [
      "--",
      "macos/stage_b/Info.plist",
      "$APP/Contents/Info.plist"
    ],
    "allowed_options": [
      "--"
    ],
    "source_positions": [
      [
        1,
        "SOURCE_LITERAL"
      ]
    ],
    "sink_positions": [
      [
        2,
        "COPY_DESTINATION"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "CP_PRODUCT",
    "executables": [
      "/bin/cp"
    ],
    "context": "simple command",
    "argv_shape": [
      "--",
      "$PRODUCT",
      "$APP/Contents/MacOS/StageBSandboxRunner"
    ],
    "allowed_options": [
      "--"
    ],
    "source_positions": [
      [
        1,
        "BUILD_PRODUCT_SOURCE"
      ]
    ],
    "sink_positions": [
      [
        2,
        "COPY_DESTINATION"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "CODESIGN_SIGN",
    "executables": [
      "/usr/bin/codesign"
    ],
    "context": "simple command",
    "argv_shape": [
      "--force",
      "--sign",
      "$STAGE_B_SIGN_IDENTITY",
      "--entitlements",
      "$GATE0_STAGE_B_FROZEN_S2",
      "--identifier",
      "org.centaurioun.video-intelligence-pipeline.gate0.stageb",
      "$APP"
    ],
    "allowed_options": [
      "--force",
      "--sign <identity>",
      "--entitlements <path>",
      "--identifier <exact literal>"
    ],
    "source_positions": [],
    "sink_positions": [
      [
        2,
        "CODESIGN_IDENTITY"
      ],
      [
        4,
        "CODESIGN_ENTITLEMENTS"
      ],
      [
        7,
        "CODESIGN_SUBJECT"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "CODESIGN_VERIFY",
    "executables": [
      "/usr/bin/codesign"
    ],
    "context": "simple command",
    "argv_shape": [
      "--verify",
      "--strict",
      "--verbose=4",
      "$APP"
    ],
    "allowed_options": [
      "--verify",
      "--strict",
      "--verbose=4"
    ],
    "source_positions": [],
    "sink_positions": [
      [
        3,
        "CODESIGN_SUBJECT"
      ]
    ],
    "aliases_may_feed_sinks": true
  },
  {
    "family": "ECHO",
    "executables": [
      "/bin/echo"
    ],
    "context": "final simple command only",
    "argv_shape": [
      "$APP"
    ],
    "allowed_options": [],
    "source_positions": [],
    "sink_positions": [
      [
        0,
        "STDOUT_REPORTED_PATH"
      ]
    ],
    "aliases_may_feed_sinks": true
  }
]
~~~

Every command family has exact executable spelling, option set, argv cardinality/order, source positions and sink positions. An argv token is path-bearing when it contains `/`, expands from APP/BIN_PATH/PRODUCT/frozen-S2, or occupies a declared path position. Every path-bearing argv must be classified by this table as exact source literal/source or exact sink; otherwise FAIL. Unknown simple command => FAIL. Unknown option => FAIL. Extra or missing argv => FAIL. Unsupported redirection => FAIL. Reordered argv => FAIL.

The parser itself derives the complete `ShellSink` set; callers cannot nominate sinks. Assignment aliases are followed transitively with unbound/cycle failure. Required reachability is: frozen S2 -> CODESIGN_ENTITLEMENTS; signing identity -> CODESIGN_IDENTITY; sealed destination -> BUILD_DESTINATION, DIRECTORY_DESTINATION, every COPY_DESTINATION, every CODESIGN_SUBJECT and STDOUT_REPORTED_PATH.

Static tests inject an alternate valid-looking `install` output command and an extra cp destination; each must be rejected rather than silently omitted from the sink graph.

## 9. Predicate and Tier-1 ownership

### 9.1 Exact Tier-1 rows in numeric order

| Row | Predicate(s) | Exact test name |
|---|---|---|
| 01 | P1 | `test_tier1_row01_authority_echo_coherence` |
| 02 | P3a/P3b | `test_tier1_row02_phase_aware_s1_binding` |
| 03 | P2 | `test_tier1_row03_generation_identity_tuple_and_reuse` |
| 04 | P4 | `test_tier1_row04_phase_aware_s2_signer_binding` |
| 05 | P5a/P5b | `test_tier1_row05_n4a_n4b_continuity_and_oracle_isolation` |
| 06 | P6 | `test_tier1_row06_n5_subject_is_exact_n4a_transient_application` |
| 07 | P7/P8 | `test_tier1_row07_exact_s8_and_type_strict_policy` |
| 08 | P9 | `test_tier1_row08_s11_policy_result_record` |
| 09 | P10 | `test_tier1_row09_entitlement_key_closure` |
| 10 | P11 | `test_tier1_row10_signing_identity_drift` |
| 11 | P12/P13 | `test_tier1_row11_projection_elision_and_privacy` |
| 12 | P14/P15 | `test_tier1_row12_reproducibility_and_nonvacuity` |
| 13 | P16/P17 | `test_tier1_row13_result_order_and_design_record` |
| 14 | P18a/P18b/P18c | `test_tier1_row14_anchor_bytes_immutability_digests` |
| 15 | P19 | `test_tier1_row15_p19_four_reference_arms` |
| 16 | P20/P21 | `test_tier1_row16_p20_p21_retention_and_additivity` |
| 17 | P24 | `test_tier1_row17_c2_envelope_acceptance` |
| 18 | P25 | `test_tier1_row18_p25_and_all_316_adversarial_rows` |
| 19 | P22 | `test_tier1_row19_phase_aware_p22_conjunction` |
| 20 | P23 | `test_tier1_row20_p23_self_excluding_coverage` |
| 21 | — | `test_tier1_row21_retained_evidence_reverification_only` |

This is actual row order 01..21; V4-N01 is closed. Row 21 names no predicate and remains outside P22.

### 9.2 Predicate ownership

Implementation ownership remains the accepted v3 mapping: P1 Task5; P2 Task5; P3a/P3b Tasks6/8/13; P4 Tasks8/13; P5a/P5b Tasks9/12; P6 Task10; P7/P8 Task10 plus row21; P9 Task12; P10 Task10; P11 Task9; P12/P13 Task9; P14/P15 Task12; P16/P17 Tasks11/12; P18a/b/c Tasks7/12; P19 Task11; P20/P21 Tasks11/12; P24 Task6; P25 Tasks2/3/6/13; P22/P23 Task13.

## 10. Final verification contracts

### 10.1 FV1 — exact plan-owned collection and exact execution

The exact expected V7 set is the §7 expansion: **960** unique node IDs, duplicate IDs zero. Execution command is exactly:

~~~bash
PYTHONPATH=src "$GATE0_PY" - <<'PY'
import hashlib
import os
import re
from pathlib import Path
import pytest
from tests.gate0.unit.evidence_dag_interface_manifest import load_plan_contract
from tests.gate0.unit.evidence_dag_fixtures import ExactOutcomeRecorder

CANONICAL_PLAN = "docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md"
plan_text = os.environ["G0_REV18_V7_PLAN_PATH"]
approved_blob = os.environ["G0_REV18_APPROVED_PLAN_BLOB"]
if plan_text != CANONICAL_PLAN:
    raise SystemExit("noncanonical V7 plan path")
if re.fullmatch(r"[0-9a-f]{40}", approved_blob) is None:
    raise SystemExit("invalid approved V7 plan blob")
plan_path = Path(plan_text)
plan_bytes = plan_path.read_bytes()
actual_blob = hashlib.sha1(
    b"blob " + str(len(plan_bytes)).encode("ascii") + b"\0" + plan_bytes
).hexdigest()
if actual_blob != approved_blob:
    raise SystemExit("approved V7 plan blob mismatch")

if pytest.__version__ != "8.3.3":
    raise SystemExit("pinned pytest 8.3.3 required")
plan = load_plan_contract(plan_path)
expected = plan.expand_expected_new_test_node_ids()
if len(expected) != 960 or len(set(expected)) != 960:
    raise SystemExit("FV1 inventory mismatch")
recorder = ExactOutcomeRecorder()
code = pytest.main(["-q", "-ra", *expected], plugins=[recorder])
snap = recorder.snapshot()
outcomes = snap["outcomes"]
if tuple(snap["pre_deselection_node_ids"]) != tuple(sorted(expected)):
    raise SystemExit("FV1 collection mismatch")
if tuple(snap["executed_node_ids"]) != tuple(sorted(expected)):
    raise SystemExit("FV1 execution mismatch")
if snap["deselected_node_ids"] or snap["collection_errors"]:
    raise SystemExit("FV1 deselection/collection error")
if len(outcomes) != 960 or any(outcomes[n] != "PASSED" for n in expected):
    raise SystemExit("FV1 terminal outcome mismatch")
if code != 0:
    raise SystemExit(code)
PY
~~~

The exact stdin block id is `FV1_PY`; bytes are the here-doc body including its final LF and excluding delimiter lines. Exact V7 body = **1847 octets**, SHA-256 `c2d804325b95e79abbcba08a2523888e6822125ca69e41aacbeb6cb64e3e217a`. FV1 proves canonical V7 path + externally approved Git-blob identity before reading plan truth, then requires collected set == executed set == exact 960, one terminal status per node, all 960 PASSED, zero failure/error/skip/xfail/xpass/deselection and no collection error.

### 10.2 FV2 — deterministic historical baseline

Load `.git/gate0-rev18-prechange-baseline-v4.json`, then rerun full `tests/gate0` with the **same §4.1 recorder**. Compare:
- exact pre-deselection historical collection;
- exact historical deselected node set;
- exact historical executed node set;
- exact `node_id -> terminal outcome`;
- collection-errors exact.

Current collection may differ from baseline only by the exact §7 960-node additive set. FV2 uses the corrected §4.1 pytest-8.3.3 recorder, so strict/non-strict XPASS classification cannot diverge between FV1 and FV2. Historical exception mapping is exactly `{}`. The synthetic hook-order regression must produce byte-identical recorder snapshots under both ordinary plugin registration orders because recorder collection is `tryfirst=True`.

### 10.3 FV3 — one plan-owned machine effect policy

There is exactly one normative effect-policy truth. The serialized object below and `EffectPolicy` in §5.2 have identical keys/order. The source contract in §10.3.1 interprets this object; it is not a second policy and contains no independent safe-symbol list.

~~~json
{
  "schema": "G0_REV18_V7_EFFECT_POLICY_V1",
  "production_roots": [
    "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
    "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
    "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
    "src/gate0/feasibility/macos_stage_b_evidence_git.py",
    "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
    "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
    "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
    "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
    "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
    "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
    "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
    "src/gate0/feasibility/macos_stage_b_evidence_references.py",
    "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
    "src/gate0/feasibility/macos_stage_b_evidence_results.py",
    "src/gate0/feasibility/macos_stage_b_evidence_package.py",
    "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
    "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
    "scripts/stage-b-evidence-dag.py"
  ],
  "safe_import_prefixes": [
    "argparse",
    "collections",
    "dataclasses",
    "enum",
    "functools",
    "hashlib",
    "hmac",
    "io",
    "itertools",
    "json",
    "math",
    "os",
    "pathlib",
    "plistlib",
    "re",
    "shlex",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "types",
    "typing",
    "uuid",
    "gate0.feasibility",
    "macos_stage_b_evidence_"
  ],
  "forbidden_network_prefixes": [
    "socket",
    "ssl",
    "urllib",
    "http.client",
    "requests",
    "aiohttp",
    "httpx",
    "ftplib",
    "smtplib",
    "imaplib",
    "poplib",
    "telnetlib",
    "xmlrpc.client",
    "websockets",
    "paramiko",
    "grpc",
    "boto3"
  ],
  "process_effect_rules": [
    "subprocess.*",
    "os.system",
    "os.popen",
    "os.posix_spawn",
    "os.posix_spawnp",
    "os.fork",
    "os.forkpty",
    "os.spawn*",
    "os.exec*",
    "asyncio.create_subprocess_exec",
    "asyncio.create_subprocess_shell"
  ],
  "traversal_effect_rules": [
    "os.walk",
    "os.fwalk",
    "os.scandir",
    "os.listdir",
    "glob.glob",
    "glob.iglob",
    "Path.glob",
    "Path.rglob",
    "Path.iterdir"
  ],
  "os_harmless_call_allowlist": [],
  "asyncio_harmless_call_allowlist": [],
  "path_harmless_call_allowlist": [
    "Path.as_posix",
    "Path.is_absolute",
    "Path.joinpath",
    "Path.relative_to",
    "Path.with_name",
    "Path.with_suffix"
  ],
  "path_constructor_policy": "CONSTRUCTION_ONLY_NO_EFFECT",
  "path_binding_resolution_policy": "Normalize pathlib.Path module aliases, direct Path import aliases, direct Path(...) call receivers, and simple local names assigned from Path(...); classify each resulting method call as Path.<method> before effect-policy lookup.",
  "path_unlisted_callable_policy": "EFFECT_UNKNOWN_FAIL_CLOSED",
  "multiprocessing_policy": "FAIL_CLOSED_IMPORT_OR_CALL",
  "allowed_process_leaves": [
    "macos_stage_b_evidence_git._run_git",
    "macos_stage_b_evidence_boundary._run_stage_b_build_process",
    "macos_stage_b_evidence_s8._run_codesign_entitlements"
  ],
  "allowed_traversal_leaf": "macos_stage_b_evidence_runtime._OSBackedCensusFS.list_entries -> os.scandir",
  "local_module_call_resolution_policy": "Resolve Import/ImportFrom under src/gate0/feasibility plus scripts/stage-b-evidence-dag.py; normalize module and direct-import aliases; build function-level local call edges; propagate PROCESS/NETWORK/TRAVERSAL/EFFECT_UNKNOWN to fixed point.",
  "unresolved_dynamic_local_edge_policy": "FAIL_CLOSED",
  "unknown_external_import_policy": "FAIL_CLOSED",
  "security_relevant_unlisted_call_policy": "EFFECT_UNKNOWN_FAIL_CLOSED",
  "shell_true_policy": "FAIL_CLOSED",
  "network_allowlist": []
}
~~~

`effect_policy_from_mapping` rejects missing, extra or renamed fields before scanning. FV8 compares exact field names/order/types. `OS_HARMLESS_CALL_ALLOWLIST` and `ASYNCIO_HARMLESS_CALL_ALLOWLIST` remain projections of the two empty machine fields. `PATH_HARMLESS_CALL_ALLOWLIST` is likewise only a projection of `path_harmless_call_allowlist`.

The exact Path harmless callable allowlist is limited to pure lexical operations: `Path.as_posix`, `Path.is_absolute`, `Path.joinpath`, `Path.relative_to`, `Path.with_name`, `Path.with_suffix`. No filesystem-observing Path method is grandfathered.

Path namespace closure is exact:

1. `Path(...)` construction is construction-only under `path_constructor_policy`;
2. `Path.method`, `pathlib.Path.method`, aliases, direct constructor receivers and simple local names assigned from `Path(...)` normalize to `Path.<method>`;
3. existing `Path.glob`, `Path.rglob`, `Path.iterdir` rules remain TRAVERSAL; only the existing CensusFS `list_entries -> os.scandir` leaf is approved;
4. exact members of `path_harmless_call_allowlist` are effect-free;
5. every other normalized `Path.*` callable, including `Path.walk` and `Path.exists`, is EFFECT_UNKNOWN/fail-closed;
6. local wrappers propagate TRAVERSAL/EFFECT_UNKNOWN to fixed point.

All accepted V6 process/network/default-deny semantics remain exact: forbidden-network closure with empty allowlist; subprocess/process rules; multiprocessing fail-closed; unlisted os/asyncio fail-closed; shell=True fail-closed; unknown external/unresolved dynamic fail-closed; exact three process leaves; one CensusFS traversal leaf.

### 10.3.1 Exact plan-owned production-scanner source contract

V7 closes V6R2-F02 with an exact source-region contract. Task 1 must place exactly one region in `tests/gate0/unit/evidence_dag_fixtures.py`:

`# BEGIN G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1` → exact bytes below → `# END G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1`.

The block is exactly **14929 UTF-8 octets** with SHA-256 `80eab8c6915a5c8d292416710e3f84327697b77d34eb2434125b622624b966a8`.

<!-- BEGIN EFFECT_SCANNER_SOURCE_CONTRACT_PY -->
~~~python
def scan_production_effects(policy: EffectPolicy) -> EffectScanResult:
    import ast
    from pathlib import Path

    def rule_matches(rule: str, symbol: str) -> bool:
        if rule.endswith("*"):
            return symbol.startswith(rule[:-1])
        return symbol == rule

    def canonical_module_name(path_text: str) -> str:
        return Path(path_text).stem

    local_roots = {
        canonical_module_name(path_text)
        for path_text in policy.production_roots
    }
    local_import_aliases: dict[str, str] = {}
    for path_text in policy.production_roots:
        canonical = canonical_module_name(path_text)
        local_import_aliases[canonical] = canonical
        if path_text.startswith("src/") and path_text.endswith(".py"):
            dotted_name = path_text[len("src/"):-len(".py")].replace("/", ".")
            local_import_aliases[dotted_name] = canonical

    def canonical_local_module(name: str) -> str | None:
        return local_import_aliases.get(name)

    def namespace_root(rule: str) -> str:
        return rule.rstrip("*").split(".", 1)[0]

    recognized_effect_roots = {
        *[namespace_root(rule) for rule in policy.process_effect_rules],
        *[namespace_root(rule) for rule in policy.traversal_effect_rules],
    }

    def is_safe_import(name: str) -> bool:
        root = name.split(".", 1)[0]
        return (
            canonical_local_module(name) is not None
            or root in recognized_effect_roots
            or any(
                name == prefix
                or name.startswith(prefix + ".")
                or (prefix.endswith("_") and name.startswith(prefix))
                for prefix in policy.safe_import_prefixes
            )
        )

    def classify(symbol: str, *, shell_true: bool) -> EffectKind | None:
        if shell_true and symbol.startswith("subprocess."):
            return EffectKind.EFFECT_UNKNOWN
        if any(
            symbol == prefix or symbol.startswith(prefix + ".")
            for prefix in policy.forbidden_network_prefixes
        ):
            return EffectKind.NETWORK
        if symbol.startswith("subprocess."):
            return EffectKind.PROCESS
        if any(rule_matches(rule, symbol) for rule in policy.process_effect_rules):
            return EffectKind.PROCESS
        if symbol == "multiprocessing" or symbol.startswith("multiprocessing."):
            return EffectKind.EFFECT_UNKNOWN
        if any(rule_matches(rule, symbol) for rule in policy.traversal_effect_rules):
            return EffectKind.TRAVERSAL
        if symbol.startswith("os."):
            if symbol in policy.os_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        if symbol.startswith("asyncio."):
            if symbol in policy.asyncio_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        if symbol.startswith("Path."):
            if symbol in policy.path_harmless_call_allowlist:
                return None
            return EffectKind.EFFECT_UNKNOWN
        root = symbol.split(".", 1)[0]
        if root not in local_roots and not is_safe_import(symbol):
            return EffectKind.EFFECT_UNKNOWN
        return None

    parsed: dict[str, tuple[str, ast.Module]] = {}
    module_aliases: dict[str, dict[str, str]] = {}
    import_findings: list[EffectScanFinding] = []

    for path_text in policy.production_roots:
        module_name = canonical_module_name(path_text)
        source = Path(path_text).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path_text)
        parsed[module_name] = (path_text, tree)
        aliases: dict[str, str] = {}

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    aliases[alias.asname or imported.split(".", 1)[0]] = (
                        canonical_local_module(imported) or imported
                    )
                    if any(
                        imported == prefix or imported.startswith(prefix + ".")
                        for prefix in policy.forbidden_network_prefixes
                    ):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.NETWORK,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
                    elif imported == "multiprocessing" or imported.startswith("multiprocessing."):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.EFFECT_UNKNOWN,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
                    elif not is_safe_import(imported):
                        import_findings.append(
                            EffectScanFinding(
                                kind=EffectKind.EFFECT_UNKNOWN,
                                module=module_name,
                                function="<module>",
                                symbol=imported,
                                line=node.lineno,
                            )
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_module = node.module
                for alias in node.names:
                    imported = f"{imported_module}.{alias.name}"
                    imported_module_target = canonical_local_module(imported)
                    imported_parent = canonical_local_module(imported_module)
                    if imported_module_target is not None:
                        aliases[alias.asname or alias.name] = imported_module_target
                    elif imported_parent is not None:
                        aliases[alias.asname or alias.name] = f"{imported_parent}.{alias.name}"
                    else:
                        aliases[alias.asname or alias.name] = imported
                if any(
                    imported_module == prefix or imported_module.startswith(prefix + ".")
                    for prefix in policy.forbidden_network_prefixes
                ):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.NETWORK,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )
                elif imported_module == "multiprocessing" or imported_module.startswith("multiprocessing."):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.EFFECT_UNKNOWN,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )
                elif not is_safe_import(imported_module):
                    import_findings.append(
                        EffectScanFinding(
                            kind=EffectKind.EFFECT_UNKNOWN,
                            module=module_name,
                            function="<module>",
                            symbol=imported_module,
                            line=node.lineno,
                        )
                    )

        module_aliases[module_name] = aliases

    direct_findings: dict[str, list[EffectScanFinding]] = {}
    local_edges: set[tuple[str, str]] = set()
    function_nodes: dict[str, tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = {}

    for module_name, (path_text, tree) in parsed.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_nodes[f"{module_name}.{node.name}"] = (path_text, node)
            elif isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        function_nodes[
                            f"{module_name}.{node.name}.{member.name}"
                        ] = (path_text, member)

    local_function_names = set(function_nodes)

    for function_key, (path_text, fn) in function_nodes.items():
        module_name = function_key.split(".", 1)[0]
        function_name = function_key.split(".", 1)[1]
        owner_key = function_key.rsplit(".", 1)[0]
        aliases = dict(module_aliases[module_name])
        path_bindings: set[str] = set()

        for node in ast.walk(fn):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    aliases[alias.asname or imported.split(".", 1)[0]] = (
                        canonical_local_module(imported) or imported
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    imported = f"{node.module}.{alias.name}"
                    imported_module_target = canonical_local_module(imported)
                    imported_parent = canonical_local_module(node.module)
                    if imported_module_target is not None:
                        aliases[alias.asname or alias.name] = imported_module_target
                    elif imported_parent is not None:
                        aliases[alias.asname or alias.name] = f"{imported_parent}.{alias.name}"
                    else:
                        aliases[alias.asname or alias.name] = imported

        def dotted(expr: ast.expr) -> str | None:
            if isinstance(expr, ast.Name):
                if expr.id in path_bindings:
                    return "Path"
                value = aliases.get(expr.id, expr.id)
                if value in {"pathlib.Path", "Path"}:
                    return "Path"
                return value
            if isinstance(expr, ast.Attribute):
                if isinstance(expr.value, ast.Call):
                    ctor = dotted(expr.value.func)
                    if ctor == "Path":
                        return f"Path.{expr.attr}"
                base = dotted(expr.value)
                if base:
                    if base == "pathlib" and expr.attr == "Path":
                        return "Path"
                    return f"{base}.{expr.attr}"
            return None

        for node in ast.walk(fn):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = [node.target] if isinstance(node, ast.AnnAssign) else list(node.targets)
            value = node.value
            if not isinstance(value, ast.Call):
                continue
            ctor = dotted(value.func)
            if ctor != "Path":
                continue
            for target in targets:
                if isinstance(target, ast.Name):
                    path_bindings.add(target.id)

        direct_findings.setdefault(function_key, [])
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            symbol = dotted(node.func)
            if not symbol:
                direct_findings[function_key].append(
                    EffectScanFinding(
                        kind=EffectKind.EFFECT_UNKNOWN,
                        module=module_name,
                        function=function_name,
                        symbol="<dynamic-call>",
                        line=node.lineno,
                    )
                )
                continue

            local_target = None
            if symbol in local_function_names:
                local_target = symbol
            elif "." not in symbol:
                candidate = f"{module_name}.{symbol}"
                if candidate in local_function_names:
                    local_target = candidate
            elif symbol.startswith("self.") or symbol.startswith("cls."):
                candidate = f"{owner_key}.{symbol.split('.', 1)[1]}"
                if candidate in local_function_names:
                    local_target = candidate
            if local_target is not None:
                local_edges.add((function_key, local_target))
                continue

            shell_true = any(
                kw.arg == "shell"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value is True
                for kw in node.keywords
            )
            kind = classify(symbol, shell_true=shell_true)
            if kind is not None:
                direct_findings[function_key].append(
                    EffectScanFinding(
                        kind=kind,
                        module=module_name,
                        function=function_name,
                        symbol=symbol,
                        line=node.lineno,
                    )
                )

    propagated: dict[str, list[EffectScanFinding]] = {
        key: list(value) for key, value in direct_findings.items()
    }
    changed = True
    while changed:
        changed = False
        for caller, callee in sorted(local_edges):
            known = {
                (x.kind, x.module, x.function, x.symbol, x.line)
                for x in propagated.setdefault(caller, [])
            }
            for finding in propagated.get(callee, []):
                marker = (
                    finding.kind,
                    finding.module,
                    finding.function,
                    finding.symbol,
                    finding.line,
                )
                if marker not in known:
                    propagated[caller].append(finding)
                    known.add(marker)
                    changed = True

    all_findings = [
        *import_findings,
        *[
            item
            for values in propagated.values()
            for item in values
        ],
    ]
    findings = {
        (item.kind, item.module, item.function, item.symbol, item.line): item
        for item in all_findings
    }
    return EffectScanResult(
        findings=tuple(
            findings[key]
            for key in sorted(
                findings,
                key=lambda x: (x[1], x[2], x[4], x[3], x[0].value),
            )
        ),
        resolved_local_edges=tuple(sorted(local_edges)),
    )
~~~
<!-- END EFFECT_SCANNER_SOURCE_CONTRACT_PY -->

Mechanical conformance is independent of implementation classification results:

- the exact controlled `FV_DRIVER_PY` extracts the block from the already blob-verified V7 plan, recomputes SHA-256, reads the implementation module, requires exactly one marker pair and byte-identical region;
- it parses the whole implementation module and requires exactly one top-level `scan_production_effects` definition with no other direct top-level binding/rebinding of that name;
- it independently compiles the **plan-owned scanner bytes** as a reference callable, normalizes both reference and implementation code objects while excluding filename/line-table noise, and requires exact bytecode/constant/name/variable/freevar/cellvar identity;
- it rejects implementation defaults/kwdefaults/closures not present in the plan-owned callable;
- it independently parses the sole effect-policy JSON from the already approved plan bytes, executes both the plan-owned reference scanner and implementation scanner over that same policy/current production-root source set, and requires exact result equality;
- it then independently rejects every reference finding except PROCESS at one of the exact three policy leaves or TRAVERSAL at the exact one CensusFS leaf; NETWORK and EFFECT_UNKNOWN always fail;
- only after those independent checks pass does it call implementation `verify_fv3`;
- an extra hard-coded safe symbol, renamed/extra safe-list constant, hidden special-case branch, dynamic callable-code replacement or other policy-preserving scanner-body widening cannot be certified merely because the widened symbol is absent from production roots;
- the source block obtains all behavior-defining safe sets/rules from the sole `EffectPolicy`; literal namespace names in the executable grammar only dispatch policy fields and do not create an independent safe allowance.

The unit helper `verify_effect_scanner_source_contract` mirrors the byte/AST law for TDD, but the controlled FV driver is the final independent oracle and never calls the implementation classifier to decide what reference behavior should be.

### 10.4 FV4 — argv + exact-stdin + exact-control-input controlled-run honesty

Pre-receipt FV4 requires no receipt and validates exact paired ledger schema/order, unique allowed-command matching, argv/cwd/selected environment, exact `required_control_keys`, exact START/END `control_inputs`, authorized base/blob, canonical V7 path and exact PRE phase, plus the preserved stdin/FV3/FV7/FV5/VCS/artifact checks.

Changing implementation base, plan path, approved-plan blob or PRE/POST phase while argv/stdin remain identical changes controlled command identity and fails. Missing/extra control-input keys fail.

Before plan-derived truth is consumed, exact FV1/shared-driver stdin independently computes actual V7 Git blob identity with `SHA1(b"blob " + ascii(len(bytes)) + b"\\0" + bytes)` and requires equality with external `G0_REV18_APPROVED_PLAN_BLOB`.

Post-receipt additionally requires exact POST phase and receipt agreement with ledger stdin/argv/control-input/VCS/artifact/static checks. Receipt text cannot override a contradiction.

### 10.5 FV5 — phase-exact changed paths

Before independent code review and after each accepted remediation, tracked changed paths from `G0_REV18_IMPLEMENTATION_BASE` **must equal** `PRE_RECEIPT_REQUIRED_CHANGED_PATHS` (44 paths). After the receipt commit they **must equal** `POST_RECEIPT_REQUIRED_CHANGED_PATHS` (45 paths). Proper subset and proper superset both fail.

### 10.6 FV6 — immutable protected surfaces

Require exact blobs:
- Rev18 spec `21e651503bff6dc2b369ad45923d16a3af8adf1c`;
- ruling `97c8c7e0ebddad715bf1002a44d71720965735d9`;
- owner approval `3f6230e8663e4267eddf7cada1608ea5396708b2`;
- v1 `18ba38319aa67ed0995cb2cc3f8d04937f188dcc`;
- v2 `e0eae8ea0a34a5f06c6d0d4e9ea11e62dc4ab1f2`;
- v3 `aa63f52007d1e3d8b80e4c03dc1bdd5cb14468e6`;
- v4 `fc5599caeaabe32878e1b56de75207265bad3b59`;
- v5 `7df69992b520def485eb4a1cda6b7f0fe8982fdd`.

`tests/gate0/conftest.py`, C² contracts, historical plans and every protected path outside §11 remain unchanged.

### 10.6.1 Exact FV2/FV3/FV4/FV5/FV6/FV8 driver

Run exactly:

~~~bash
PYTHONPATH=src "$GATE0_PY" - <<'PY'
import ast
import hashlib
import json
import os
import re
import types
from pathlib import Path
import tests.gate0.unit.evidence_dag_fixtures as fixturemod
from tests.gate0.unit.evidence_dag_interface_manifest import (
    verify_fv2, verify_fv3, verify_fv4, verify_fv5, verify_fv6, verify_fv8,
)

CANONICAL_PLAN = "docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md"
SCANNER_PATH = Path("tests/gate0/unit/evidence_dag_fixtures.py")
PLAN_BEGIN = "<!-- BEGIN EFFECT_SCANNER_SOURCE_CONTRACT_PY -->\n"
PLAN_END = "<!-- END EFFECT_SCANNER_SOURCE_CONTRACT_PY -->\n"
IMPL_BEGIN = "# BEGIN G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1\n"
IMPL_END = "# END G0_REV18_V7_EFFECT_SCANNER_SOURCE_CONTRACT_V1\n"
EXPECTED_SCANNER_SHA256 = "80eab8c6915a5c8d292416710e3f84327697b77d34eb2434125b622624b966a8"

plan_text = os.environ["G0_REV18_V7_PLAN_PATH"]
approved_blob = os.environ["G0_REV18_APPROVED_PLAN_BLOB"]
base = os.environ["G0_REV18_IMPLEMENTATION_BASE"]
phase = os.environ["G0_REV18_VERIFY_PHASE"]
if plan_text != CANONICAL_PLAN:
    raise SystemExit("noncanonical V7 plan path")
if re.fullmatch(r"[0-9a-f]{40}", approved_blob) is None:
    raise SystemExit("invalid approved V7 plan blob")
if re.fullmatch(r"[0-9a-f]{40}", base) is None:
    raise SystemExit("invalid implementation base")
if phase not in {"PRE_RECEIPT", "POST_RECEIPT"}:
    raise SystemExit("invalid verification phase")

plan = Path(plan_text)
plan_bytes = plan.read_bytes()
actual_blob = hashlib.sha1(
    b"blob " + str(len(plan_bytes)).encode("ascii") + b"\0" + plan_bytes
).hexdigest()
if actual_blob != approved_blob:
    raise SystemExit("approved V7 plan blob mismatch")

plan_source = plan_bytes.decode("utf-8")
if plan_source.count(PLAN_BEGIN) != 1 or plan_source.count(PLAN_END) != 1:
    raise SystemExit("scanner plan block marker mismatch")
plan_region = plan_source.split(PLAN_BEGIN, 1)[1].split(PLAN_END, 1)[0]
if not plan_region.startswith("~~~python\n") or not plan_region.endswith("~~~\n"):
    raise SystemExit("scanner plan block fence mismatch")
scanner_contract = plan_region[len("~~~python\n"):-len("~~~\n")].encode("utf-8")
if hashlib.sha256(scanner_contract).hexdigest() != EXPECTED_SCANNER_SHA256:
    raise SystemExit("scanner plan block digest mismatch")

impl_source = SCANNER_PATH.read_text(encoding="utf-8")
if impl_source.count(IMPL_BEGIN) != 1 or impl_source.count(IMPL_END) != 1:
    raise SystemExit("scanner implementation marker mismatch")
impl_region = impl_source.split(IMPL_BEGIN, 1)[1].split(IMPL_END, 1)[0].encode("utf-8")
if impl_region != scanner_contract:
    raise SystemExit("scanner implementation source mismatch")

tree = ast.parse(impl_source, filename=str(SCANNER_PATH))
defs = [
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    and node.name == "scan_production_effects"
]
if len(defs) != 1:
    raise SystemExit("scanner definition count mismatch")
for node in tree.body:
    if node is defs[0]:
        continue
    rebound = False
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        rebound = node.name == "scan_production_effects"
    elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        rebound = any(
            isinstance(target, ast.Name) and target.id == "scan_production_effects"
            for target in targets
        )
    elif isinstance(node, ast.Import):
        rebound = any(
            (alias.asname or alias.name.split(".", 1)[0]) == "scan_production_effects"
            for alias in node.names
        )
    elif isinstance(node, ast.ImportFrom):
        rebound = any(
            (alias.asname or alias.name) == "scan_production_effects"
            for alias in node.names
        )
    if rebound:
        raise SystemExit("scanner top-level rebind")

def code_signature(code):
    return (
        code.co_argcount,
        code.co_posonlyargcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_code,
        tuple(
            code_signature(value) if isinstance(value, types.CodeType) else value
            for value in code.co_consts
        ),
        code.co_names,
        code.co_varnames,
        code.co_freevars,
        code.co_cellvars,
    )

reference_namespace = {
    "EffectPolicy": fixturemod.EffectPolicy,
    "EffectKind": fixturemod.EffectKind,
    "EffectScanFinding": fixturemod.EffectScanFinding,
    "EffectScanResult": fixturemod.EffectScanResult,
}
exec(
    compile(scanner_contract.decode("utf-8"), "<approved-v7-scanner>", "exec"),
    reference_namespace,
)
reference_scanner = reference_namespace["scan_production_effects"]
implementation_scanner = fixturemod.scan_production_effects
if code_signature(implementation_scanner.__code__) != code_signature(reference_scanner.__code__):
    raise SystemExit("scanner callable code mismatch")
if implementation_scanner.__defaults__ is not None or implementation_scanner.__kwdefaults__ is not None:
    raise SystemExit("scanner callable defaults mismatch")
if implementation_scanner.__closure__ is not None:
    raise SystemExit("scanner callable closure mismatch")

policy_heading = "### 10.3 FV3 — one plan-owned machine effect policy\n"
policy_tail = plan_source.split(policy_heading, 1)[1]
policy_text = policy_tail.split("~~~json\n", 1)[1].split("\n~~~", 1)[0]
policy_mapping = json.loads(policy_text)
if policy_mapping["schema"] != "G0_REV18_V7_EFFECT_POLICY_V1":
    raise SystemExit("effect policy schema mismatch")
policy = types.SimpleNamespace(
    **{
        key: tuple(value) if isinstance(value, list) else value
        for key, value in policy_mapping.items()
    }
)
reference_result = reference_scanner(policy)
implementation_result = implementation_scanner(policy)

def result_signature(result):
    return (
        tuple(
            (
                finding.kind.value,
                finding.module,
                finding.function,
                finding.symbol,
                finding.line,
            )
            for finding in result.findings
        ),
        tuple(result.resolved_local_edges),
    )

if result_signature(implementation_result) != result_signature(reference_result):
    raise SystemExit("scanner implementation/reference behavior mismatch")

allowed_process = set(policy_mapping["allowed_process_leaves"])
allowed_traversal = policy_mapping["allowed_traversal_leaf"]
for finding in reference_result.findings:
    leaf = f"{finding.module}.{finding.function}"
    if finding.kind.value in {"NETWORK", "EFFECT_UNKNOWN"}:
        raise SystemExit(f"forbidden production effect:{finding.kind.value}:{leaf}:{finding.symbol}")
    if finding.kind.value == "PROCESS" and leaf not in allowed_process:
        raise SystemExit(f"unapproved process leaf:{leaf}")
    if (
        finding.kind.value == "TRAVERSAL"
        and f"{leaf} -> {finding.symbol}" != allowed_traversal
    ):
        raise SystemExit(f"unapproved traversal leaf:{leaf}:{finding.symbol}")

baseline = Path(".git/gate0-rev18-prechange-baseline-v4.json")
ledger = Path(".git/gate0-rev18-controlled-run-ledger-v3.jsonl")
before = Path(".git/gate0-rev18-pre-task1-worktree-v1.bin")
receipt = Path("docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md") if phase == "POST_RECEIPT" else None

verify_fv2(plan, baseline)
verify_fv3(plan)
verify_fv4(plan, ledger, before, phase, receipt, base, approved_blob)
verify_fv5(base, phase)
verify_fv6(Path(".").resolve())
verify_fv8(plan)
PY
~~~

The exact stdin block id is `FV_DRIVER_PY`; exact body = **7608 octets**, SHA-256 `f7672c1b3f01c99a80bd67929ce7c22b43e6c5e194b5cf6f36a4d2fb6eb8b8e5`. The driver has no fallback. It independently proves approved V7 plan identity, exact scanner source bytes, normalized callable code-object identity, reference/implementation result equality, and allowed-leaf policy compliance before FV3. PRE_RECEIPT uses `receipt=None`; POST_RECEIPT requires the exact receipt path and exact ledger/control-input/static/VCS agreement.

### 10.7 FV7 — static shell proof only

Run:
~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_stage_b_evidence_build_boundary.py -q
bash -n scripts/stage-b-build-app.sh
~~~
No Swift/build/codesign execution.

### 10.8 FV8 — complete machine shape

Extract only §§5.1–5.4 from the exact externally blob-approved frozen V7 plan. Compare exact runtime enum values/order; dataclass field names/order/types/frozen state; callable parameter names/order/annotations/returns/error/visibility; protocol module/name/classification/method names/order/parameter names/order/annotations/return annotations. Missing, extra or mismatched `CensusFS`, `EffectPolicy`, `CommandLedgerEvent`, `AllowedControlledCommand`, or `SyntheticForbiddenSourceForm` shape fails. FV8 also requires V7 Path-policy fields, `control_inputs`, `required_control_keys`, and every V7 callable signature exactly.

### 10.9 Repetition

Run FV1–FV8:
1. before independent code review;
2. after every accepted review remediation;
3. after Task-16 receipt commit.

The first two phases use PRE/FV4-pre semantics. The final phase uses POST/FV4-post semantics.

## 11. Exclusive writer ownership and phase-exact changed-path sets

| Task | Exclusive write paths |
|---|---|
| 1 | src/gate0/feasibility/macos_stage_b_evidence_constants.py; tests/gate0/unit/test_evidence_constants.py; tests/gate0/unit/evidence_dag_fixtures.py; tests/gate0/unit/evidence_dag_interface_manifest.py |
| 2 | src/gate0/feasibility/macos_stage_b_evidence_macho.py; tests/gate0/unit/test_evidence_macho.py |
| 3 | src/gate0/feasibility/macos_stage_b_evidence_runtime.py; tests/gate0/unit/test_evidence_runtime.py |
| 4 | src/gate0/feasibility/macos_stage_b_evidence_git.py; tests/gate0/unit/test_evidence_git.py |
| 5 | src/gate0/feasibility/macos_stage_b_evidence_authority.py; tests/gate0/unit/test_evidence_authority.py |
| 6 | src/gate0/feasibility/macos_stage_b_evidence_snapshot.py; tests/gate0/unit/test_evidence_snapshot.py |
| 7 | src/gate0/feasibility/macos_stage_b_evidence_anchor.py; tests/gate0/unit/test_evidence_anchor.py |
| 8 | src/gate0/feasibility/macos_stage_b_evidence_boundary.py; tests/gate0/unit/test_evidence_boundary.py; tests/gate0/unit/evidence_dag_oracle_manifest.py |
| 9 | src/gate0/feasibility/macos_stage_b_evidence_projection.py; src/gate0/feasibility/macos_stage_b_evidence_seal.py; tests/gate0/unit/test_evidence_projection.py; tests/gate0/unit/test_evidence_seal.py |
| 10 | src/gate0/feasibility/macos_stage_b_evidence_s8.py; tests/gate0/unit/test_evidence_s8.py |
| 11 | src/gate0/feasibility/macos_stage_b_evidence_references.py; src/gate0/feasibility/macos_stage_b_evidence_retention.py; tests/gate0/unit/test_evidence_references.py; tests/gate0/unit/test_evidence_retention.py |
| 12 | src/gate0/feasibility/macos_stage_b_evidence_results.py; src/gate0/feasibility/macos_stage_b_evidence_package.py; tests/gate0/unit/test_evidence_results.py; tests/gate0/unit/test_evidence_package.py |
| 13 | src/gate0/feasibility/macos_stage_b_evidence_gate.py; tests/gate0/unit/test_evidence_gate.py; tests/gate0/unit/test_evidence_adversarial.py; tests/gate0/unit/evidence_dag_adversarial_cases.py |
| 14 | src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py; scripts/stage-b-evidence-dag.py; tests/gate0/unit/test_evidence_orchestrator.py; tests/gate0/unit/test_stage_b_evidence_dag_cli.py |
| 15 | scripts/stage-b-build-app.sh; tests/gate0/unit/test_stage_b_evidence_build_boundary.py; .gitignore |
| 16 | docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md |

`tests/gate0/conftest.py` is not a writer path. V7 adds its 18 remediation tests/helpers only inside the already-owned Task-1 test/support surfaces and adds no implementation writer path; the accepted Task-13 source-form surfaces are unchanged. Re-expanding the final writer table gives 44 unique Task-1..15 paths and 45 unique Task-1..16 paths, duplicate writer paths zero; therefore the exact PRE=44 and POST=45 path lists remain valid after fresh V7 recomputation.

`PRE_RECEIPT_REQUIRED_CHANGED_PATHS` = exactly 44 paths:

~~~json
[
  ".gitignore",
  "scripts/stage-b-build-app.sh",
  "scripts/stage-b-evidence-dag.py",
  "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
  "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
  "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
  "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
  "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
  "src/gate0/feasibility/macos_stage_b_evidence_git.py",
  "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
  "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
  "src/gate0/feasibility/macos_stage_b_evidence_package.py",
  "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
  "src/gate0/feasibility/macos_stage_b_evidence_references.py",
  "src/gate0/feasibility/macos_stage_b_evidence_results.py",
  "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
  "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
  "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
  "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
  "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
  "tests/gate0/unit/evidence_dag_adversarial_cases.py",
  "tests/gate0/unit/evidence_dag_fixtures.py",
  "tests/gate0/unit/evidence_dag_interface_manifest.py",
  "tests/gate0/unit/evidence_dag_oracle_manifest.py",
  "tests/gate0/unit/test_evidence_adversarial.py",
  "tests/gate0/unit/test_evidence_anchor.py",
  "tests/gate0/unit/test_evidence_authority.py",
  "tests/gate0/unit/test_evidence_boundary.py",
  "tests/gate0/unit/test_evidence_constants.py",
  "tests/gate0/unit/test_evidence_gate.py",
  "tests/gate0/unit/test_evidence_git.py",
  "tests/gate0/unit/test_evidence_macho.py",
  "tests/gate0/unit/test_evidence_orchestrator.py",
  "tests/gate0/unit/test_evidence_package.py",
  "tests/gate0/unit/test_evidence_projection.py",
  "tests/gate0/unit/test_evidence_references.py",
  "tests/gate0/unit/test_evidence_results.py",
  "tests/gate0/unit/test_evidence_retention.py",
  "tests/gate0/unit/test_evidence_runtime.py",
  "tests/gate0/unit/test_evidence_s8.py",
  "tests/gate0/unit/test_evidence_seal.py",
  "tests/gate0/unit/test_evidence_snapshot.py",
  "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
  "tests/gate0/unit/test_stage_b_evidence_dag_cli.py"
]
~~~

`POST_RECEIPT_REQUIRED_CHANGED_PATHS` = exactly 45 paths:

~~~json
[
  ".gitignore",
  "docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md",
  "scripts/stage-b-build-app.sh",
  "scripts/stage-b-evidence-dag.py",
  "src/gate0/feasibility/macos_stage_b_evidence_anchor.py",
  "src/gate0/feasibility/macos_stage_b_evidence_authority.py",
  "src/gate0/feasibility/macos_stage_b_evidence_boundary.py",
  "src/gate0/feasibility/macos_stage_b_evidence_constants.py",
  "src/gate0/feasibility/macos_stage_b_evidence_gate.py",
  "src/gate0/feasibility/macos_stage_b_evidence_git.py",
  "src/gate0/feasibility/macos_stage_b_evidence_macho.py",
  "src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py",
  "src/gate0/feasibility/macos_stage_b_evidence_package.py",
  "src/gate0/feasibility/macos_stage_b_evidence_projection.py",
  "src/gate0/feasibility/macos_stage_b_evidence_references.py",
  "src/gate0/feasibility/macos_stage_b_evidence_results.py",
  "src/gate0/feasibility/macos_stage_b_evidence_retention.py",
  "src/gate0/feasibility/macos_stage_b_evidence_runtime.py",
  "src/gate0/feasibility/macos_stage_b_evidence_s8.py",
  "src/gate0/feasibility/macos_stage_b_evidence_seal.py",
  "src/gate0/feasibility/macos_stage_b_evidence_snapshot.py",
  "tests/gate0/unit/evidence_dag_adversarial_cases.py",
  "tests/gate0/unit/evidence_dag_fixtures.py",
  "tests/gate0/unit/evidence_dag_interface_manifest.py",
  "tests/gate0/unit/evidence_dag_oracle_manifest.py",
  "tests/gate0/unit/test_evidence_adversarial.py",
  "tests/gate0/unit/test_evidence_anchor.py",
  "tests/gate0/unit/test_evidence_authority.py",
  "tests/gate0/unit/test_evidence_boundary.py",
  "tests/gate0/unit/test_evidence_constants.py",
  "tests/gate0/unit/test_evidence_gate.py",
  "tests/gate0/unit/test_evidence_git.py",
  "tests/gate0/unit/test_evidence_macho.py",
  "tests/gate0/unit/test_evidence_orchestrator.py",
  "tests/gate0/unit/test_evidence_package.py",
  "tests/gate0/unit/test_evidence_projection.py",
  "tests/gate0/unit/test_evidence_references.py",
  "tests/gate0/unit/test_evidence_results.py",
  "tests/gate0/unit/test_evidence_retention.py",
  "tests/gate0/unit/test_evidence_runtime.py",
  "tests/gate0/unit/test_evidence_s8.py",
  "tests/gate0/unit/test_evidence_seal.py",
  "tests/gate0/unit/test_evidence_snapshot.py",
  "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
  "tests/gate0/unit/test_stage_b_evidence_dag_cli.py"
]
~~~

No Task 1–15 writer path is optional. FV5 compares exact set equality at the applicable phase; subset-only validation is forbidden.

## 12. Implementation tasks

Every behavior task uses test-driven development. No task may skip its RED observation.

### Task 1 — shared contracts, fixtures, corrected recorder/scanner support and plan-owned manifests

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_constants.py`
- Test: `tests/gate0/unit/test_evidence_constants.py`
- Test support: `tests/gate0/unit/evidence_dag_fixtures.py`
- Test support: `tests/gate0/unit/evidence_dag_interface_manifest.py`

Dependencies: none.

Concrete RED content includes every preserved V6 Task-1 test plus the V7 narrow-remediation falsifiers below. The accepted recorder/stdin tests are not deleted or weakened:

~~~python
def test_recorder_strict_xpass_pytest_8_3_3_actual_case(tmp_path):
    assert pytest.__version__ == "8.3.3"
    case = tmp_path / "test_strict_xpass.py"
    case.write_text(
        "import pytest\n"
        "@pytest.mark.xfail(strict=True, reason='v6-probe')\n"
        "def test_strict_xpass():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    recorder = ExactOutcomeRecorder()
    code = pytest.main([str(case), "-q"], plugins=[recorder])
    snap = recorder.snapshot()
    assert code == pytest.ExitCode.TESTS_FAILED
    assert tuple(snap["outcomes"].values()) == ("XPASSED",)

def test_effect_policy_serialized_fields_equal_effectpolicy_dataclass_fields(
    evidence_dag_plan_contract,
):
    mapping = evidence_dag_plan_contract.effect_policy_mapping()
    assert tuple(mapping) == tuple(EffectPolicy.__dataclass_fields__)
    assert effect_policy_from_mapping(mapping) == evidence_dag_plan_contract.effect_policy()

def test_fv3_refuses_missing_or_renamed_effect_policy_field(
    tmp_path, evidence_dag_plan_contract
):
    for mode, field in (
        ("DELETE", "shell_true_policy"),
        ("RENAME", "local_module_call_resolution_policy"),
    ):
        bad_plan = write_effect_policy_variant(
            tmp_path, evidence_dag_plan_contract, mode, field
        )
        with pytest.raises(TestContractError):
            verify_fv3(bad_plan)

def test_effect_scanner_subprocess_alias_is_process():
    result = scan_synthetic_effect_source(
        "from subprocess import run as r\ndef f():\n    return r(['true'])\n"
    )
    assert result.has_effect(EffectKind.PROCESS)

def test_effect_scanner_shell_true_fails_closed():
    result = scan_synthetic_effect_source(
        "import subprocess\ndef f():\n    return subprocess.run('true', shell=True)\n"
    )
    assert result.failed_closed is True

def test_effect_scanner_unlisted_os_callable_fails_closed():
    result = scan_synthetic_effect_source("import os\ndef f():\n    return os.getpid()\n")
    assert result.has_effect(EffectKind.EFFECT_UNKNOWN)
    assert result.failed_closed is True

def test_allowed_command_manifest_is_exact_and_unique(evidence_dag_plan_contract):
    records = evidence_dag_plan_contract.allowed_commands()
    assert len(records) == 70
    assert len({x.task_step_id for x in records}) == 70
    assert tuple(
        x.stdin_block_id for x in records if x.stdin_mode is StdinMode.EXACT_BYTES
    ) == ("PRETASK_BASELINE_PY", "FV1_PY", "FV_DRIVER_PY")

def test_command_manifest_stdin_digests_recompute_from_plan_blocks(
    evidence_dag_plan_contract,
):
    for allowed in evidence_dag_plan_contract.allowed_commands():
        if allowed.stdin_mode is StdinMode.NONE:
            assert allowed.expected_stdin_octets == 0
            assert allowed.expected_stdin_sha256 is None
            continue
        body = evidence_dag_plan_contract.stdin_block_bytes(allowed.stdin_block_id)
        assert len(body) == allowed.expected_stdin_octets
        assert hashlib.sha256(body).hexdigest() == allowed.expected_stdin_sha256

def test_command_ledger_same_argv_exact_stdin_passes(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    start, end = exact_ledger_pair_for(allowed)
    assert validate_command_event_pair(start, end, allowed, start.control_inputs) is True

def test_command_ledger_one_byte_changed_stdin_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    start, end = exact_ledger_pair_for(allowed)
    changed = dataclasses.replace(end, stdin_sha256="0" * 64)
    with pytest.raises(TestContractError):
        validate_command_event_pair(start, changed, allowed, start.control_inputs)

def test_command_ledger_same_argv_different_python_program_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    start, end = exact_ledger_pair_for(allowed)
    changed = dataclasses.replace(
        end,
        stdin_sha256=hashlib.sha256(b"raise SystemExit(0)\n").hexdigest(),
        stdin_octets=len(b"raise SystemExit(0)\n"),
    )
    with pytest.raises(TestContractError):
        validate_command_event_pair(start, changed, allowed, start.control_inputs)

def test_command_ledger_exact_stdin_mismatched_octet_count_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    start, end = exact_ledger_pair_for(allowed)
    changed = dataclasses.replace(end, stdin_octets=end.stdin_octets + 1)
    with pytest.raises(TestContractError):
        validate_command_event_pair(start, changed, allowed, start.control_inputs)

def test_command_ledger_start_end_stdin_mismatch_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    start, end = exact_ledger_pair_for(allowed)
    changed = dataclasses.replace(end, stdin_sha256="f" * 64)
    with pytest.raises(TestContractError):
        validate_command_event_pair(start, changed, allowed, start.control_inputs)

def test_command_ledger_none_with_nonzero_stdin_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("T01_RED")
    start, end = exact_ledger_pair_for(allowed)
    changed = dataclasses.replace(start, stdin_octets=1)
    with pytest.raises(TestContractError):
        validate_command_event_pair(changed, end, allowed, end.control_inputs)
~~~


V7-01, V7-02 and V7-03 add these exact singleton RED tests, all owned by `tests/gate0/unit/test_evidence_constants.py` and listed literally in §7:

~~~python
AUTH_BASE = "1" * 40
AUTH_PLAN_BLOB = "2" * 40
CANONICAL_V7_PLAN = (
    "docs/superpowers/plans/"
    "2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md"
)

def _mutate_control_input(
    events: tuple[CommandLedgerEvent, ...],
    task_step_id: str,
    key: str,
    value: str,
) -> tuple[CommandLedgerEvent, ...]:
    changed = []
    for event in events:
        if event.task_step_id != task_step_id:
            changed.append(event)
            continue
        changed.append(
            dataclasses.replace(
                event,
                control_inputs=tuple(
                    (name, value if name == key else current)
                    for name, current in event.control_inputs
                ),
            )
        )
    return tuple(changed)

def test_command_ledger_same_argv_stdin_different_implementation_base_fails(
    evidence_dag_plan_contract,
):
    events = exact_controlled_run_ledger_for(
        evidence_dag_plan_contract, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
    )
    changed = _mutate_control_input(
        events, "PRETASK_BASELINE_CAPTURE", "G0_REV18_IMPLEMENTATION_BASE", "3" * 40
    )
    with pytest.raises(TestContractError):
        validate_controlled_run_ledger(
            changed, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
        )

def test_command_ledger_same_argv_stdin_different_plan_path_fails(
    evidence_dag_plan_contract,
):
    events = exact_controlled_run_ledger_for(
        evidence_dag_plan_contract, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
    )
    changed = _mutate_control_input(
        events,
        "FV1_EXACT_TEST_SET",
        "G0_REV18_V7_PLAN_PATH",
        "docs/superpowers/plans/not-the-approved-v7.md",
    )
    with pytest.raises(TestContractError):
        validate_controlled_run_ledger(
            changed, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
        )

def test_approved_plan_identity_wrong_bytes_at_canonical_path_fails(tmp_path):
    plan_path = tmp_path / CANONICAL_V7_PLAN
    plan_path.parent.mkdir(parents=True)
    plan_path.write_bytes(b"unapproved plan bytes\n")
    with pytest.raises(TestContractError):
        verify_approved_plan_identity(tmp_path, plan_path, AUTH_PLAN_BLOB)

def test_command_ledger_pre_post_phase_mutation_fails(evidence_dag_plan_contract):
    events = exact_controlled_run_ledger_for(
        evidence_dag_plan_contract, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
    )
    changed = _mutate_control_input(
        events,
        "FV2_FV3_FV4_FV5_FV6_FV8_DRIVER",
        "G0_REV18_VERIFY_PHASE",
        "POST_RECEIPT",
    )
    with pytest.raises(TestContractError):
        validate_controlled_run_ledger(
            changed, "PRE_RECEIPT", AUTH_BASE, AUTH_PLAN_BLOB
        )

def test_command_ledger_start_end_control_input_mismatch_fails(
    evidence_dag_plan_contract,
):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    exact = (
        ("G0_REV18_V7_PLAN_PATH", CANONICAL_V7_PLAN),
        ("G0_REV18_APPROVED_PLAN_BLOB", AUTH_PLAN_BLOB),
    )
    start, end = exact_ledger_pair_for(allowed, exact)
    changed_end = dataclasses.replace(
        end,
        control_inputs=(
            ("G0_REV18_V7_PLAN_PATH", CANONICAL_V7_PLAN),
            ("G0_REV18_APPROVED_PLAN_BLOB", "3" * 40),
        ),
    )
    with pytest.raises(TestContractError):
        validate_command_event_pair(start, changed_end, allowed, exact)

def test_command_ledger_missing_required_control_input_fails(
    evidence_dag_plan_contract,
):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    exact = (
        ("G0_REV18_V7_PLAN_PATH", CANONICAL_V7_PLAN),
        ("G0_REV18_APPROVED_PLAN_BLOB", AUTH_PLAN_BLOB),
    )
    start, end = exact_ledger_pair_for(allowed, exact)
    missing = exact[:1]
    with pytest.raises(TestContractError):
        validate_command_event_pair(
            dataclasses.replace(start, control_inputs=missing),
            dataclasses.replace(end, control_inputs=missing),
            allowed,
            exact,
        )

def test_command_ledger_extra_control_input_fails(evidence_dag_plan_contract):
    allowed = evidence_dag_plan_contract.allowed_command("FV1_EXACT_TEST_SET")
    exact = (
        ("G0_REV18_V7_PLAN_PATH", CANONICAL_V7_PLAN),
        ("G0_REV18_APPROVED_PLAN_BLOB", AUTH_PLAN_BLOB),
    )
    start, end = exact_ledger_pair_for(allowed, exact)
    extra = exact + (("UNAUTHORIZED_CONTROL_INPUT", "x"),)
    with pytest.raises(TestContractError):
        validate_command_event_pair(
            dataclasses.replace(start, control_inputs=extra),
            dataclasses.replace(end, control_inputs=extra),
            allowed,
            exact,
        )

def test_path_walk_is_fail_closed():
    result = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return Path(p).walk()\n"
    )
    assert any(x.kind is EffectKind.EFFECT_UNKNOWN for x in result.findings)

def test_path_unlisted_callable_is_fail_closed():
    result = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return Path(p).exists()\n"
    )
    assert any(x.kind is EffectKind.EFFECT_UNKNOWN for x in result.findings)

def test_path_harmless_callable_requires_exact_allowlist_membership(
    evidence_dag_plan_contract,
):
    policy = evidence_dag_plan_contract.effect_policy()
    assert policy.path_harmless_call_allowlist == (
        "Path.as_posix",
        "Path.is_absolute",
        "Path.joinpath",
        "Path.relative_to",
        "Path.with_name",
        "Path.with_suffix",
    )
    good = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return Path(p).as_posix()\n"
    )
    bad = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return Path(p).exists()\n"
    )
    assert not good.findings
    assert any(x.kind is EffectKind.EFFECT_UNKNOWN for x in bad.findings)

def test_path_listed_traversal_outside_census_leaf_fails():
    result = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return tuple(Path(p).rglob('*'))\n"
    )
    assert any(x.kind is EffectKind.TRAVERSAL for x in result.findings)

def test_path_traversal_propagates_through_local_wrapper():
    result = scan_synthetic_effect_source(
        "from pathlib import Path\n"
        "def inner(p):\n    return Path(p).walk()\n"
        "def outer(p):\n    return inner(p)\n"
    )
    assert ("synthetic", "synthetic") not in result.resolved_local_edges
    assert any(caller.endswith(".outer") and callee.endswith(".inner")
               for caller, callee in result.resolved_local_edges)
    assert any(x.kind is EffectKind.EFFECT_UNKNOWN for x in result.findings)

def test_path_alias_import_has_same_classification():
    direct = scan_synthetic_effect_source(
        "from pathlib import Path\ndef f(p):\n    return Path(p).walk()\n"
    )
    alias = scan_synthetic_effect_source(
        "import pathlib as pl\ndef f(p):\n    return pl.Path(p).walk()\n"
    )
    direct_kinds = tuple(sorted(x.kind.value for x in direct.findings))
    alias_kinds = tuple(sorted(x.kind.value for x in alias.findings))
    assert direct_kinds == alias_kinds == ("EFFECT_UNKNOWN",)

def test_effect_scanner_source_contract_exact_region_is_required(tmp_path):
    plan_path = Path(CANONICAL_V7_PLAN)
    source = load_plan_contract(plan_path).effect_scanner_source_contract_bytes()
    scanner = write_scanner_contract_fixture(tmp_path, source)
    verify_effect_scanner_source_contract(plan_path, scanner)

def test_effect_scanner_source_contract_rejects_extra_safe_symbol(tmp_path):
    plan_path = Path(CANONICAL_V7_PLAN)
    source = load_plan_contract(plan_path).effect_scanner_source_contract_bytes()
    bad = source.replace(
        b'if symbol.startswith("Path."):\n',
        b'if symbol == "Path.hidden_safe":\n            return None\n'
        b'        if symbol.startswith("Path."):\n',
        1,
    )
    scanner = write_scanner_contract_fixture(tmp_path, bad)
    with pytest.raises(TestContractError):
        verify_effect_scanner_source_contract(plan_path, scanner)

def test_effect_scanner_source_contract_rejects_renamed_or_extra_safe_list(tmp_path):
    plan_path = Path(CANONICAL_V7_PLAN)
    source = load_plan_contract(plan_path).effect_scanner_source_contract_bytes()
    bad = source.replace(
        b"policy.path_harmless_call_allowlist",
        b"EXTRA_PATH_SAFE_LIST",
        1,
    )
    scanner = write_scanner_contract_fixture(tmp_path, bad)
    with pytest.raises(TestContractError):
        verify_effect_scanner_source_contract(plan_path, scanner)

def test_effect_scanner_source_contract_rejects_hidden_special_case_branch(tmp_path):
    plan_path = Path(CANONICAL_V7_PLAN)
    source = load_plan_contract(plan_path).effect_scanner_source_contract_bytes()
    bad = source.replace(
        b"def classify(symbol: str, *, shell_true: bool) -> EffectKind | None:\n",
        b"def classify(symbol: str, *, shell_true: bool) -> EffectKind | None:\n"
        b'        if symbol.endswith(".secret_exception"):\n'
        b"            return None\n",
        1,
    )
    scanner = write_scanner_contract_fixture(tmp_path, bad)
    with pytest.raises(TestContractError):
        verify_effect_scanner_source_contract(plan_path, scanner)

def test_effect_scanner_source_contract_rejects_widening_when_symbol_absent_from_roots(
    tmp_path,
):
    plan_path = Path(CANONICAL_V7_PLAN)
    contract = load_plan_contract(plan_path)
    source = contract.effect_scanner_source_contract_bytes()
    assert b"Path.hidden_safe" not in source
    for root in contract.effect_policy().production_roots:
        root_path = Path(root)
        if root_path.exists():
            assert "Path.hidden_safe" not in root_path.read_text(encoding="utf-8")
    bad = source.replace(
        b'if symbol.startswith("Path."):\n',
        b'if symbol == "Path.hidden_safe":\n            return None\n'
        b'        if symbol.startswith("Path."):\n',
        1,
    )
    scanner = write_scanner_contract_fixture(tmp_path, bad)
    with pytest.raises(TestContractError):
        verify_effect_scanner_source_contract(plan_path, scanner)
~~~

The final V7 inventory therefore adds exactly 18 singleton nodes: seven V7-01 control-input/plan-identity falsifiers, six V7-02 Path namespace falsifiers, and five V7-03 scanner-source-conformance falsifiers.

The preserved recorder family is exact: `ORDINARY_PASS`, `ORDINARY_ASSERTION_FAILURE`, `SETUP_ERROR`, `TEARDOWN_ERROR`, `COLLECTION_ERROR`, `ORDINARY_SKIP`, `EXPECTED_XFAIL`, `NONSTRICT_XPASS`, `DESELECTED`; duplicate terminal rejection is a separate singleton. `exercise_recorder_case` drives synthetic reports for those non-strict cases only. Strict XPASS is never faked by that helper; the test above executes real pytest 8.3.3.

The existing local-wrapper, forbidden-network, unknown-external and traversal tests are preserved. The process parameter family now additionally contains `os.posix_spawn`, `os.posix_spawnp`, `os.fork`, and `os.forkpty`. `test_allowed_command_manifest_is_exact_and_unique` requires unique `task_step_id` records and complete direct-command coverage. `test_command_manifest_stdin_digests_recompute_from_plan_blocks` reparses each EXACT_BYTES block, recomputes octets/SHA-256, and compares it to the manifest. The existing receipt-contradiction test is strengthened so a POST receipt cannot override a stdin mismatch.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_constants.py -q
~~~

Expected RED reason: the exact V6 implementation base has none of the V7 control-input fields/authorization binding, Path namespace-complete policy fields, approved-plan identity helper, or plan-owned scanner source-conformance contract. The preserved V6 tests remain RED there for their original missing implementation surfaces.

Minimal implementation:
- implement every §5 enum/dataclass/test-support type and the exact §4.1 recorder;
- implement plan parser methods `enum_values`, `protocol`, `expand_expected_new_test_node_ids`, `unbound_fixture_references`, `effect_policy_mapping`, `effect_policy`, `allowed_commands`, `allowed_command`, `stdin_block_bytes`, `effect_scanner_source_contract_bytes`, and exact block extraction;
- implement §6 helpers with lazy imports for production modules owned by later tasks;
- implement only the §10.3 machine policy and place the exact §10.3.1 scanner source bytes between the required markers; no scanner-authored fallback/safe list;
- implement §4.2 event-pair/manifest validation, including exact stdin count/digest plus exact required-control key/value binding and capture-before-child-execution;
- implement ledger/path/artifact validators from §§4/10/11;
- parse only the externally blob-approved canonical V7 plan as expected truth; do not import an implementation-authored expected inventory;
- keep `tests/gate0/conftest.py` unchanged.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_constants.py -q
~~~

Expected GREEN result: all Task-1 nodes pass; accepted V6 recorder/stdin tests remain green; V7-01 rejects every base/path/blob/phase/control mismatch; V7-02 rejects unlisted Path calls and propagates wrapper/alias effects; V7-03 rejects every implementation-only scanner widening; the exact V7 inventory expands to 960 unique nodes with duplicate count zero.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_constants.py tests/gate0/unit/test_evidence_constants.py tests/gate0/unit/evidence_dag_fixtures.py tests/gate0/unit/evidence_dag_interface_manifest.py
git commit -m "feat(gate0): add Revision-18 evidence contracts"
~~~

### Task 2 — project-owned Mach-O parser and structural fixture families

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_macho.py`
- Test: `tests/gate0/unit/test_evidence_macho.py`

Dependencies: Task 1.

Concrete RED content:

~~~python
def test_header64_exact_layout():
    image=make_thin_arm64(ncmds=0,commands=b"")
    parsed=MACHO_NATIVE_CONTAINER_PARSE_V1(image)
    assert parsed.header.magic==0xFEEDFACF
    assert parsed.selected_slice_length==32

@pytest.mark.parametrize("command_value",ACCEPTED_COMMAND_VALUES,ids=lambda v:f"0x{v:08x}")
def test_every_accepted_command_has_executable_minimal_fixture(command_value):
    observed=exercise_command_fixture(build_minimal_command_fixture(command_value))
    assert observed.accepted is True

@pytest.mark.parametrize("command_value",REJECTED_COMMAND_VALUES,ids=lambda v:f"0x{v:08x}")
def test_every_rejected_numeric_policy_row_fails(command_value):
    with pytest.raises(EvidenceDagError) as exc:
        exercise_command_fixture(struct.pack("<II",command_value,8))
    assert exc.value.code is EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID

@pytest.mark.parametrize("case",STRUCTURAL_COMMAND_CASES,ids=lambda c:c.case_id)
def test_load_command_structure(case):
    observed=exercise_command_fixture(build_structural_case_bytes(case))
    if case.variant=="VALID":
        assert observed.accepted is True
    else:
        assert observed.failure_code is EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID

@pytest.mark.parametrize("case",HEADER64_CASES,ids=lambda c:c.case_id)
def test_header64_policy_row(case):
    assert execute_header64_case(case)==case.expected_success

@pytest.mark.parametrize("case",FAT_STRUCTURE_CASES,ids=lambda c:c.case_id)
def test_fat_structure_case(case):
    assert execute_fat_structure_case(case)==case.expected_success
~~~

For every one of the 43 accepted structural rows, define deterministic parameter ids VALID, UNDERSIZED, FORMULA_OR_TRAILING and NONZERO_RESERVED_OR_PADDING when the normative row contains required zero bytes. Each case invokes production parser and checks the exact accepted disposition or exact P25 failure.

FAT cases are separate deterministic nodes for metadata truncation, zero size, mathematical bounds, overlap, alignment, FAT64 reserved, selected inner/outer mismatch, opaque non-selected payload, gaps and trailing bytes.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_macho.py -q
~~~

Expected RED reason: macos_stage_b_evidence_macho import failure.

Minimal implementation: explicit bytes-only mathematical-integer parser matching Revision-18 container, Header64, 54 numeric and 43 structural rows. No external parser, otool, /usr/bin/file or host inspection.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_macho.py -q
~~~

Expected GREEN result: all Task-2 nodes pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_macho.py tests/gate0/unit/test_evidence_macho.py
git commit -m "feat(gate0): add closed Mach-O parser"
~~~

### Task 3 — M1R wrapper, path resolver, expectation-free stable census and native manifest

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_runtime.py`
- Test: `tests/gate0/unit/test_evidence_runtime.py`

Dependencies: Tasks 1,2.

Concrete RED content:

~~~python
def test_censusfs_protocol_is_fv8_machine_truth(evidence_dag_plan_contract):
    assert exact_protocol_shape(CensusFS) == evidence_dag_plan_contract.protocol("CensusFS")

@pytest.mark.parametrize("subaction", ["INSERT", "REMOVE", "RENAME", "KIND_CHANGE"])
def test_census19_each_mutation_independently_fails(subaction):
    spec = census_construction("CENSUS-19")
    assert not any(name.startswith("expected") for name in spec.__dataclass_fields__)
    one = dataclasses.replace(spec, subaction_ids=(subaction,))
    observations = execute_stable_census_construction(one)
    assert len(observations) == 1
    assert observations[0].subaction_id == subaction
    assert observations[0].governing_call_count == 1
    assert observations[0].mutation_observed is True
    expected = expectation_for_subaction(census_expectation("CENSUS-19"), subaction)
    assert compare_stable_census(observations, expected)

@pytest.mark.parametrize(
    "cheat",
    ["NO_OP_EXECUTOR", "SYNTHESIZED_TRACE", "NO_GOVERNING_CALL", "NO_MUTATION"],
)
def test_census_executor_cheat_is_detected(cheat):
    assert run_census_cheat_falsifier(cheat) is False
~~~

The same file retains the frozen resolver/native RED families: 31/32/33 hop law and repeat precedence; RR18-2-N01 exact 0/1/2/3 with native-parser count zero; both roots exhaustive; lstat-before-follow; zero directory-symlink traversal; independent A/B enumeration; classifier identity; Census-A native byte ownership; non-native/native transitions; native digest/retarget failures; transient-state nonserialization; exact native-manifest serialization and all overflow negatives.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_runtime.py -q
~~~

Expected RED reason: runtime module and split census execution support do not exist.

Minimal implementation:
- implement M1R one-argument classifier and exact path/native rules;
- implement `CensusFS` with exactly the §5.4 five-method protocol;
- `_OSBackedCensusFS.list_entries` is the sole bounded traversal leaf and uses `os.scandir` only on its already-validated directory;
- implement §8.3 construction execution without any expectation parameter;
- CENSUS-19 constructs four fresh fixtures and invokes real `capture_stable_census` four times.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_runtime.py -q
~~~

Expected GREEN result: all Task-3 nodes pass; no census executor can satisfy a row by echoing expectations.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_runtime.py tests/gate0/unit/test_evidence_runtime.py
git commit -m "feat(gate0): add stable native census"
~~~

### Task 4 — bounded Git object plumbing and fixed repository-root discovery

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_git.py`
- Test: `tests/gate0/unit/test_evidence_git.py`

Dependencies: Task 1.

Concrete RED content:

~~~python
def test_blob_read_uses_committed_object_not_worktree(evidence_dag_tmp_git_repo):
    commit = evidence_dag_tmp_git_repo.commit_file("x.txt", b"committed")
    evidence_dag_tmp_git_repo.write_worktree("x.txt", b"mutated")
    assert read_blob_at(commit, "x.txt") == b"committed"

def test_repository_root_discovery_leaf_is_private_zero_argument():
    assert tuple(inspect.signature(gitmod._discover_repository_root_from_module_location).parameters) == ()
    assert tuple(inspect.signature(verify_repository_context).parameters) == (
        "authority", "evaluation_commit",
    )

def test_verified_context_uses_real_verifier_at_exact_s7_commit(
    evidence_dag_tmp_git_repo,
    evidence_dag_s7_anchor,
    evidence_dag_verified_repository_context,
):
    ctx = evidence_dag_verified_repository_context
    assert ctx.canonical_root == evidence_dag_tmp_git_repo.root
    assert ctx.evaluation_commit == evidence_dag_s7_anchor.commit_sha
~~~

The existing exact-instance copy/manual-reconstruction/alternate-clean-root/symlink-root/root-replacement negatives remain.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_git.py -q
~~~

Expected RED reason: Git evidence module is absent.

Minimal implementation:
- one private `_run_git` process leaf;
- one private zero-argument `_discover_repository_root_from_module_location` leaf;
- `verify_repository_context` always calls that leaf and offers no production root selector;
- bounded Git object/type/ancestry/additivity/generation checks and exact-instance registration;
- test-process monkeypatch may replace only the private leaf; production API/signature is unchanged.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_git.py -q
~~~

Expected GREEN result: all Task-4 nodes pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_git.py tests/gate0/unit/test_evidence_git.py
git commit -m "feat(gate0): add evidence Git plumbing"
~~~

### Task 5 — verifier authority, exact P2 and S3/S4 coherence

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_authority.py`
- Test: `tests/gate0/unit/test_evidence_authority.py`

Dependencies: Tasks 1,4.

Concrete RED content:

~~~python
@pytest.mark.parametrize("field",(
    "base_controller_commit","applicable_spec_blob","applicable_plan_blob","generation_ordinal",
))
def test_generation_identity_mutates_with_each_normative_input(evidence_dag_authority,field):
    baseline=derive_generation_identity(evidence_dag_authority)
    value=getattr(evidence_dag_authority,field)
    replacement=value+1 if field=="generation_ordinal" else mutate_lower_hex(value)
    assert derive_generation_identity(replace(evidence_dag_authority,**{field:replacement}))!=baseline

@pytest.mark.parametrize("case",P2_INVALID_CASES,ids=lambda case:case.case_id)
def test_p2_invalid_preconditions_fail_before_hash(monkeypatch,case):
    calls=0
    def forbidden(payload:bytes)->str:
        nonlocal calls
        calls+=1
        raise AssertionError
    monkeypatch.setattr(authority_mod,"_sha256_generation_identity_payload",forbidden)
    with pytest.raises(EvidenceDagError) as exc:
        derive_generation_identity(case.authority)
    assert exc.value.code is EvidenceFailureCode.GENERATION_IDENTITY_COLLISION
    assert calls==0
~~~

P2_INVALID_CASES is exactly §8.1: empty, uppercase, non-hex, wrong length, encoded length > u16, ordinal 0, negative, non-integer, 2**64 and larger than u64.

Additional RED nodes:

- applicable plan blob comes only from fixed path docs/superpowers/plans/2026-09-14-gate0-stage-b-c2-v3-implementation-plan.md at controller commit;
- ordinal equals distinct reachable committed identities + 1;
- candidate committed-identity reuse rejected;
- every S3 authority echo mutated independently;
- S4 NOT_OBSERVED exact key set;
- synthetic future MEASURED_AND_OWNER_PINNED exact key set;
- missing, extra, duplicate, alias, wrong-type and independently conflicting S4 values fail P25.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_authority.py -q
~~~

Expected RED reason: authority module import failure.

Minimal implementation: preserve v2 H byte-for-byte; derive Git values only through Task 4; no producer echo defines a tuple member; malformed P2 input is rejected before hashing; P19 future-controller separation remains intact.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_authority.py -q
~~~

Expected GREEN result: all Task-5 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_authority.py tests/gate0/unit/test_evidence_authority.py
git commit -m "feat(gate0): add verifier authority and P2 identity"
~~~

### Task 6 — canonical S1/S2/S3/S4 snapshots and dependency closure

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_snapshot.py`
- Test: `tests/gate0/unit/test_evidence_snapshot.py`

Dependencies: Tasks 2,3,4,5.

Concrete RED content:

~~~python
def test_producer_dependency_lists_do_not_define_s1(evidence_dag_snapshot):
    producer=replace(
        evidence_dag_snapshot.producer_inputs,
        argv=("--tool-dependency=/attacker/tool","--python-dependency=/attacker/python"),
    )
    result=derive_frozen_snapshots(evidence_dag_snapshot.verifier_inputs,producer)
    assert b"/attacker/tool" not in result.s1.data
    assert b"/attacker/python" not in result.s1.data

def test_census_a_first_bytes_drive_parse_digest_materialization(evidence_dag_snapshot):
    derive_frozen_snapshots(evidence_dag_snapshot.verifier_inputs,evidence_dag_snapshot.producer_inputs)
    assert evidence_dag_snapshot.mutable_native_source.read_count==1
~~~

Additional RED nodes prove context-sensitive fixed point, Domain P/H/system, empty optional registry, family/order determinism, P24 execution_mode/target_safety reference acceptance and no target-safety predicate resurrection.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_snapshot.py -q
~~~

Expected RED reason: snapshot module import failure.

Minimal implementation:

- deterministic context-sensitive fixed point;
- one immutable byte image per admitted source;
- same-byte materialization;
- verifier-derived dependency inventory;
- private production host-observation call sites named exactly:
  _derive_dependency_inventory_from_host(verifier_inputs)->tuple[DependencyInventoryEntry,...]
  _read_host_native_image(path)->bytes
- render_s2_from_s1 accepts the exact FrozenArtifact S1 and returns FrozenArtifact S2.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_snapshot.py -q
~~~

Expected GREEN result: all Task-6 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_snapshot.py tests/gate0/unit/test_evidence_snapshot.py
git commit -m "feat(gate0): add verifier frozen snapshots"
~~~

### Task 7 — S7 exact anchor and one-repository authority lineage

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_anchor.py`
- Test: `tests/gate0/unit/test_evidence_anchor.py`

Dependencies: Tasks 1,4,6.

Concrete RED content:

~~~python
def test_s7_exact_set_parent_and_reread(evidence_dag_s7_anchor):
    assert len(evidence_dag_s7_anchor.anchored) == 4
    assert {x.repository_path for x in evidence_dag_s7_anchor.anchored} == {
        "S1.json", "S2.plist", "S3.json", "S4.json",
    }

def test_verified_context_and_s7_share_exact_tmp_repo_lineage(
    evidence_dag_tmp_git_repo,
    evidence_dag_s7_anchor,
    evidence_dag_verified_repository_context,
    evidence_dag_anchored_s1,
):
    assert evidence_dag_verified_repository_context.canonical_root == evidence_dag_tmp_git_repo.root
    assert evidence_dag_verified_repository_context.evaluation_commit == evidence_dag_s7_anchor.commit_sha
    assert evidence_dag_anchored_s1.repository_context is evidence_dag_verified_repository_context

@pytest.mark.parametrize("mutation", ["missing", "extra", "changed", "wrong_parent"])
def test_anchor_mutations_fail(mutation):
    assert anchor_mutation_fixture(mutation).passed is False
~~~

`evidence_dag_s7_anchor` is a test-support commit constructed directly in the same `TmpGitRepo`; it does not require the production Task-7 anchor writer. The verified-context fixture then patches only the fixed private root-discovery leaf and invokes the real Task-4 verifier at that exact S7 commit. No cwd/global seam exists.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_anchor.py -q
~~~

Expected RED reason: anchor resolution module is absent.

Minimal implementation: exact S7 closed set/parent/reread plus `resolve_anchored_s1` only from the registered context and verified S7; read exact S1 Git blob, construct FrozenArtifact internally, register exact AnchoredS1Handle, reject equal-value/copy/reconstruction before boundary use.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_anchor.py -q
~~~

Expected GREEN result: all Task-7 nodes pass on the single temp-repository/S7/context lineage.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_anchor.py tests/gate0/unit/test_evidence_anchor.py
git commit -m "feat(gate0): add exact S7 anchor"
~~~

### Task 8 — N4a origin boundary, opaque handles, path/env safety and expectation-free oracle proof

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_boundary.py`
- Test: `tests/gate0/unit/test_evidence_boundary.py`
- Test support: `tests/gate0/unit/evidence_dag_oracle_manifest.py`

Dependencies: Tasks 1,4,5,6,7.

Concrete RED content:

~~~python
def test_n4a_retained_primitive_exactly_five_fields():
    assert tuple(f.name for f in fields(N4ABoundaryPrimitive)) == (
        "format", "renderer_input_sha256", "renderer_input_octets",
        "signer_entitlements_sha256", "signer_entitlements_octets",
    )

@pytest.mark.parametrize("request", ORACLE_INSPECTION_REQUESTS, ids=lambda x: x.surface_id)
def test_oracle_request_is_observed_then_compared(request):
    assert "expected" not in request.__dataclass_fields__
    observation = inspect_oracle_request(request)
    assert compare_oracle_observation(observation, oracle_expectation_for(request.surface_id))

@pytest.mark.parametrize(
    "mechanism",
    sorted({x.mechanism for x in ORACLE_INSPECTION_REQUESTS}, key=lambda x: x.value),
)
def test_oracle_mechanism_positive_falsifier(mechanism):
    request, tree = positive_falsifier_for(mechanism)
    observation = inspect_oracle_request_against_tree(request, tree)
    assert observation_has_forbidden_match(observation)

def test_oracle_inspector_cannot_echo_expectation():
    assert oracle_echo_inspector_falsifier() is False
~~~

Retain all v4 exact-instance handle forgery/replay negatives, renderer-S2 continuity, empty-origin exact seven-variable env, private-S2/destination replacement checks, raw destination/signing seed prohibition and exact five-field N4a primitive.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_boundary.py -q
~~~

Expected RED reason: boundary/oracle modules are absent.

Minimal implementation:
- frozen exact-instance N4a boundary and context/handle provenance;
- §8.7 request-only inspector plus separate comparator;
- B03/B09/B10/B11 use call/import/reachability graph;
- every mechanism family has a positive falsifier;
- inspector never receives expectation.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_boundary.py -q
~~~

Expected GREEN result: all Task-8 nodes pass; no Swift/build/codesign process executes.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_boundary.py tests/gate0/unit/test_evidence_boundary.py tests/gate0/unit/evidence_dag_oracle_manifest.py
git commit -m "feat(gate0): add N4a verifier boundary"
~~~

### Task 9 — privacy projection and S9 seal

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_projection.py`
- Create: `src/gate0/feasibility/macos_stage_b_evidence_seal.py`
- Test: `tests/gate0/unit/test_evidence_projection.py`
- Test: `tests/gate0/unit/test_evidence_seal.py`

Dependencies: Tasks 2,4,7,8.

Concrete RED content:

~~~python
def test_n4b_parent_and_additive_projection(evidence_dag_s7_anchor,evidence_dag_n4a_result):
    seal=seal_n4b(evidence_dag_s7_anchor,evidence_dag_n4a_result.seal_capability)
    assert commit_parent(seal.commit_sha)==evidence_dag_s7_anchor.commit_sha

def test_project_signed_image_returns_typed_projection(evidence_dag_signed_image):
    assert isinstance(project_signed_image(evidence_dag_signed_image),SignedImageProjection)

def test_requirements_and_cms_are_elided_with_only_lawful_digests(evidence_dag_signed_image):
    projection:SignedImageProjection=project_signed_image(evidence_dag_signed_image)
    assert projection.requirements_bytes is None
    assert projection.cms_bytes is None
    assert dict(projection.special_slot_state)[-4]==bytes(32)
    assert dict(projection.special_slot_state)[-6]==bytes(32)
~~~

Additional RED nodes:

- first fresh seal capability succeeds once;
- duplicate/current copy, second use and stale duplicate fail before B;
- exact projection paths only;
- Requirements and CMS bytes absent, their exact two digest measurements retained;
- −4 and −6 all-zero structural state outside P20;
- each prohibited declared/textual personal class rejected;
- CodeDirectory team identifier treated truthfully as structural residual, never falsely claimed absent;
- B tree contains no B self SHA/tree identity.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_projection.py tests/gate0/unit/test_evidence_seal.py -q
~~~

Expected RED reason: projection/seal module imports fail.

Minimal implementation: exact Revision-18 privacy-reduced projection, single-use N4b capability, B parent S7, exact five-field primitive serialization, P12/P13 enforcement and no complete-app retention.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_projection.py tests/gate0/unit/test_evidence_seal.py -q
~~~

Expected GREEN result: all Task-9 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_projection.py src/gate0/feasibility/macos_stage_b_evidence_seal.py tests/gate0/unit/test_evidence_projection.py tests/gate0/unit/test_evidence_seal.py
git commit -m "feat(gate0): add privacy-reduced S9 seal"
~~~

### Task 10 — positive N5 exact-S8 extraction and type-strict policy

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_s8.py`
- Test: `tests/gate0/unit/test_evidence_s8.py`

Dependencies: Tasks 6,8,9.

Concrete RED content:

~~~python
def test_n5_positive_exact_bytes(monkeypatch,evidence_dag_n4a_result):
    exact=b"<?xml version='1.0'?><plist><dict/></plist>\n"
    calls=0
    def leaf(application):
        nonlocal calls
        calls+=1
        return subprocess.CompletedProcess(
            ("/usr/bin/codesign","-d","--entitlements",":-",str(application._subject_path)),
            0,exact,b"",
        )
    monkeypatch.setattr(s8mod,"_run_codesign_entitlements",leaf)
    assert extract_s8_from_n4a_application(
        evidence_dag_n4a_result.transient_application
    )==exact
    assert calls==1
~~~

Exact-type negative table:

| Case | Required result |
|---|---|
| wrong generation | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| stale lifecycle | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| already consumed | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| shallow/deep copied exact instance before first N5 use | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| manually reconstructed exact type with copied token/guard | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| substituted private subject | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |
| commit-B path encoded as subject | SIGNED_BYTES_NOT_VERIFIER_DERIVED; leaf count 0 |

Additional RED nodes:

- extractor signature exactly one parameter named application;
- wrong Python type refused but not counted as forgery proof;
- fixed private leaf argv exactly /usr/bin/codesign -d --entitlements :- PRIVATE_SUBJECT;
- CLI cannot select app/bundle path;
- stdout retained byte-for-byte with no decode/trim/re-serialization;
- parsed exact S8 equals parsed retained embedded entitlement payload;
- Boolean true differs from integer 1;
- arrays differ from scalars;
- string/non-string mismatch fails;
- exact renderer-defined array order;
- missing key, extra key and path widening fail;
- each of four prohibited network entitlement keys fails.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_s8.py -q
~~~

Expected RED reason: S8 module import failure.

Minimal implementation: validate verifier-owned handle provenance before private leaf; fixed codesign extraction subject from handle only; exact stdout retention; expected policy reconstructed only from exact S1 and frozen renderer/schema semantics.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_s8.py -q
~~~

Expected GREEN result: all Task-10 tests pass; real codesign never executes.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_s8.py tests/gate0/unit/test_evidence_s8.py
git commit -m "feat(gate0): add verifier-owned N5 S8 extraction"
~~~

### Task 11 — P19 four reference arms and P20 closed two-mode retention

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_references.py`
- Create: `src/gate0/feasibility/macos_stage_b_evidence_retention.py`
- Test: `tests/gate0/unit/test_evidence_references.py`
- Test: `tests/gate0/unit/test_evidence_retention.py`

Dependencies: Tasks 4,5,9,10.

Concrete RED content:

~~~python
@pytest.mark.parametrize("reference_class",list(ReferenceClass))
def test_each_p19_class_resolves_exactly_one_arm(reference_class):
    reference,context,arm=build_reference_case(reference_class)
    result=resolve_p19_reference(reference,context)
    assert result.passed is True
    assert result.resolved_arm==arm

def test_p20_closed_constant_exact_members():
    assert MEASUREMENT_ONLY_DIGEST_KEYS==frozenset({
        "requirements_blob_sha256","cms_signature_blob_sha256",
    })

def test_foreign_digest_cannot_be_mode_b(evidence_dag_retention):
    assignment=assign_p20_retention(
        evidence_dag_retention.foreign_digest_value,
        evidence_dag_retention.context,
    )
    evaluation=evaluate_p20_retention(assignment,evidence_dag_retention.context)
    assert evaluation.passed is False
    assert evaluation.failure_code is EvidenceFailureCode.EVIDENCE_NOT_RETAINED
~~~

Additional RED nodes:

- P19 arm d substitutes reviewer/sibling/later refs and fails;
- each arm-d tuple component independently falsified;
- exact authority bytes/decision id/P17 digest checked;
- RetentionContext has no measurement-only key set field;
- caller/config/artifact attempts to inject a third/foreign key have no production input surface;
- Mode B requires closed membership, P12 lawful elision and proven absent preimage;
- retained preimage forces Mode A;
- −4/−6 structural state never enters RecordedEvidenceValue;
- P20 has exactly two modes.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_references.py tests/gate0/unit/test_evidence_retention.py -q
~~~

Expected RED reason: reference/retention module imports fail.

Minimal implementation: exact four P19 classes/arms and module-owned immutable two-member MEASUREMENT_ONLY_DIGEST_KEYS. No caller/context/config selector exists.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_references.py tests/gate0/unit/test_evidence_retention.py -q
~~~

Expected GREEN result: all Task-11 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_references.py src/gate0/feasibility/macos_stage_b_evidence_retention.py tests/gate0/unit/test_evidence_references.py tests/gate0/unit/test_evidence_retention.py
git commit -m "feat(gate0): add P19 P20 closure"
~~~

### Task 12 — result serializers, reproducibility and S13 package

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_results.py`
- Create: `src/gate0/feasibility/macos_stage_b_evidence_package.py`
- Test: `tests/gate0/unit/test_evidence_results.py`
- Test: `tests/gate0/unit/test_evidence_package.py`

Dependencies: Tasks 1,7,10,11.

Concrete RED content:

~~~python
def test_s11_serializes_supplied_gate_result_without_evaluating(evidence_dag_result_builder):
    synthetic=Tier1GateResult(
        Tier1Phase.GENERATION_REASSERTION,
        False,
        (Tier1RowResult(
            19,Tier1RowKind.AGGREGATE,("P22",),False,
            EvidenceFailureCode.GENERATION_B_TIER1_GATE_UNMET,
        ),),
    )
    record=json.loads(
        serialize_s11(evidence_dag_result_builder.s11_inputs,synthetic).decode("utf-8")
    )
    assert record["tier1_gate_state"]=="FAIL"

def test_s10_before_s12_is_refused(evidence_dag_result_builder):
    with pytest.raises(EvidenceDagError) as exc:
        evidence_dag_result_builder.create_s10_before_s12()
    assert exc.value.code is EvidenceFailureCode.RESULT_MANIFEST_NOT_FINAL
~~~

Additional RED nodes:

- S11 records supplied actual typed gate state and no hidden evaluator;
- exact S11 before S12 before S10 order;
- S10 excludes itself and S13 commit SHA;
- P17 exact decision id and exact authority byte digest;
- S13 parent S9;
- S13 adds exact S8/S11/S12/S10;
- MDRT empty for S7..S9, S9..S13 and S7..S13;
- every pre-existing S7/S9 path byte-identical in S13.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_results.py tests/gate0/unit/test_evidence_package.py -q
~~~

Expected RED reason: result/package module imports fail.

Minimal implementation: serializers accept already-computed Task-1 Tier1GateResult; no Task-13 evaluator dependency; exact result order, self-exclusion and additive package contract.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_results.py tests/gate0/unit/test_evidence_package.py -q
~~~

Expected GREEN result: all Task-12 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_results.py src/gate0/feasibility/macos_stage_b_evidence_package.py tests/gate0/unit/test_evidence_results.py tests/gate0/unit/test_evidence_package.py
git commit -m "feat(gate0): add result and package artifacts"
~~~

### Task 13 — 21-row Tier-1 gate, row-21 retained re-verification and 316 concrete mutation programs

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_gate.py`
- Test: `tests/gate0/unit/test_evidence_gate.py`
- Test: `tests/gate0/unit/test_evidence_adversarial.py`
- Test support: `tests/gate0/unit/evidence_dag_adversarial_cases.py`

Dependencies: Tasks 1 through 12.

Concrete RED content preserves the v5 316-row execution/anti-echo tests and adds the closed source-form registry checks:

~~~python
def test_source_form_registry_missing_used_form_fails():
    used = used_insert_source_form_ids(NORMATIVE_ADVERSARIAL_CONSTRUCTIONS)
    with pytest.raises(TestContractError):
        validate_source_form_registry(SYNTHETIC_FORBIDDEN_SOURCE_FORMS[:-1], used)

def test_source_form_registry_duplicate_id_fails():
    used = used_insert_source_form_ids(NORMATIVE_ADVERSARIAL_CONSTRUCTIONS)
    duplicate = SYNTHETIC_FORBIDDEN_SOURCE_FORMS + (SYNTHETIC_FORBIDDEN_SOURCE_FORMS[0],)
    with pytest.raises(TestContractError):
        validate_source_form_registry(duplicate, used)

def test_insert_source_form_unknown_id_fails():
    with pytest.raises(TestContractError):
        source_form_for("UNKNOWN")

def test_all_13_used_source_form_ids_resolve_exactly_once():
    used = used_insert_source_form_ids(NORMATIVE_ADVERSARIAL_CONSTRUCTIONS)
    registry_ids = tuple(x.source_form_id for x in SYNTHETIC_FORBIDDEN_SOURCE_FORMS)
    assert len(used) == 13
    assert len(registry_ids) == 13
    assert set(used) == set(registry_ids)
    assert len(set(registry_ids)) == 13
    validate_source_form_registry(SYNTHETIC_FORBIDDEN_SOURCE_FORMS, used)

def test_no_unknown_source_form_id_remains():
    used = used_insert_source_form_ids(NORMATIVE_ADVERSARIAL_CONSTRUCTIONS)
    assert "UNKNOWN" not in used

def test_row160_callable_measurer_parameter_is_mechanically_observed():
    construction = construction_for_id("REV18-ADV-160")
    assert construction.normative_row_sha256 == "6b5133644514246d1d83ec6a1fd8edf88e0c5c2a354a93b24fb2e35afc1a688d"
    insert = [op for op in construction.action_args if op.opcode is FixtureMutationOpcode.INSERT_SOURCE_FORM]
    assert len(insert) == 1
    assert insert[0].value == "CALLABLE_MEASURER_PARAMETER"
    assert construction.post_mutation_invariant.expected_state_sha256 == "377651d3599d2980a011f775116523e40942b17d6d6c80f224033a663f4e846e"
    fixture = build_adversarial_fixture(construction.builder_id)
    fixture = apply_adversarial_action(construction.action_kind, construction.action_args, fixture)
    assert observe_post_mutation(fixture, construction.post_mutation_invariant)

def test_row160_wrong_source_form_fails_property_observer():
    expected = source_form_for("CALLABLE_MEASURER_PARAMETER")
    wrong = source_form_for("SETTER_HOOK")
    fixture = insert_source_form_into_neutral_fixture(wrong)
    assert observe_source_form_property(fixture, expected) is False

def test_row160_source_without_callable_measurer_parameter_fails():
    expected = source_form_for("CALLABLE_MEASURER_PARAMETER")
    broken = dataclasses.replace(
        expected,
        utf8_text="def production_boundary(payload):\n    return payload\n",
    )
    fixture = insert_source_form_into_neutral_fixture(broken)
    assert observe_source_form_property(fixture, expected) is False
~~~

The preserved 316-row governing-behavior test remains expectation-separated: neutral builder -> typed mutation ops -> direct post-mutation observation -> probe -> real governing callable/static inspection -> external comparator. No construction-stage helper receives `AdversarialExpectation`.

`insert_source_form_into_neutral_fixture` is a Task-13 test helper owned by `evidence_dag_adversarial_cases.py`; it inserts exactly the registry record's frozen bytes into a neutral synthetic fixture and never reads an expectation. Its use is limited to the two source-form property falsifiers above. The production Gate implementation never imports the source-form registry.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_gate.py tests/gate0/unit/test_evidence_adversarial.py -q
~~~

Expected RED reason: gate/adversarial modules, the 316 construction manifest and the closed source-form registry/observers are absent.

Minimal implementation:
- table-driven Tier-1 01–21 with row-19 conjunction and P23 self-excluding closure;
- row 21 repository-only retained evidence path;
- load exact §8.9 construction/expectation manifests and exact unchanged 13-record source-form registry from the frozen V7 plan;
- builders are neutral; action interpreter applies `FixtureMutationOp` records exactly in listed order;
- `INSERT_SOURCE_FORM` performs exact unique registry lookup, materializes exact UTF-8 bytes, runs the registry observer and refuses unknown/duplicate ids;
- row160 uses only `CALLABLE_MEASURER_PARAMETER`; its specialized observer proves the callable `measurer` parameter AST property before the governing call;
- mutation observer directly reads touched fixture state before the real governing call;
- no implementation code translates normative case text into mutation semantics.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_gate.py tests/gate0/unit/test_evidence_adversarial.py -q
~~~

Expected GREEN result: all Task-13 nodes pass; all 13 used source-form ids resolve exactly once; row160 mechanically instantiates and observes the callable `measurer` parameter; exactly 316 normative row identities execute real governing behavior after independently verified mutation.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_gate.py tests/gate0/unit/test_evidence_gate.py tests/gate0/unit/test_evidence_adversarial.py tests/gate0/unit/evidence_dag_adversarial_cases.py
git commit -m "feat(gate0): add complete Tier-1 gate"
~~~

### Task 14 — orchestrator and non-live CLI

**Files:**
- Create: `src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py`
- Modify/Create: `scripts/stage-b-evidence-dag.py`
- Test: `tests/gate0/unit/test_evidence_orchestrator.py`
- Test: `tests/gate0/unit/test_stage_b_evidence_dag_cli.py`

Dependencies: Tasks 7,8,9,10,11,12,13.

Concrete RED content:

~~~python
def test_orchestrator_records_exact_actual_gate_result(evidence_dag_orchestrator):
    gate=evidence_dag_orchestrator.evaluate_generation_gate()
    s11=evidence_dag_orchestrator.serialize_s11_with(gate)
    assert json.loads(s11)["tier1_gate_state"]==("PASS" if gate.passed else "FAIL")

def test_cli_has_no_n5_subject_retargeting_argument(evidence_dag_cli_parser):
    options={o for a in evidence_dag_cli_parser._actions for o in a.option_strings}
    assert options.isdisjoint({"--app","--bundle","--signed-app","--app-path","--bundle-path"})
~~~

Additional RED nodes reject N4b before N4a, N6 before N5, N7 before S10 and every Generation-B entry while baseline is NOT_OBSERVED.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_orchestrator.py tests/gate0/unit/test_stage_b_evidence_dag_cli.py -q
~~~

Expected RED reason: orchestrator/CLI imports fail.

Minimal implementation: implement exact §5 EvidenceDagOrchestrator fields/method signatures; it sequences typed outputs and passes exact Task-13 Tier1GateResult to Task-12 serializer. CLI provides only static-check, tier1-preentry and verify-package; it has no build/sign/live/Generation-B command and no N5 subject selector.

GREEN command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_evidence_orchestrator.py tests/gate0/unit/test_stage_b_evidence_dag_cli.py -q
~~~

Expected GREEN result: all Task-14 tests pass.

Exact commit:

~~~bash
git add src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py scripts/stage-b-evidence-dag.py tests/gate0/unit/test_evidence_orchestrator.py tests/gate0/unit/test_stage_b_evidence_dag_cli.py
git commit -m "feat(gate0): add evidence DAG orchestration"
~~~

### Task 15 — closed static shell boundary and unconditional scratch ignore

**Files:**
- Modify/Create: `scripts/stage-b-build-app.sh`
- Test: `tests/gate0/unit/test_stage_b_evidence_build_boundary.py`
- Modify: `.gitignore`

Dependencies: Tasks 8,14.

No test executes the shell script, Swift or codesign.

Concrete RED content:

~~~python
@pytest.mark.parametrize("family", list(ShellCommandFamily))
def test_shell_family_derives_complete_sinks(family, evidence_dag_script_text):
    contract = parse_stage_b_shell_contract(evidence_dag_script_text)
    assert derived_family_sinks(contract, family) == plan_family_rule(family).sink_positions

def test_shell_alternate_output_command_rejected(evidence_dag_script_text):
    injected = evidence_dag_script_text + "\n/bin/install -m 755 source /tmp/alternate-output\n"
    with pytest.raises(ShellContractError):
        parse_stage_b_shell_contract(injected)

def test_shell_extra_destination_argv_rejected(evidence_dag_script_text):
    injected = evidence_dag_script_text.replace(
        '/bin/cp -- "$PRODUCT" "$APP/Contents/MacOS/StageBSandboxRunner"',
        '/bin/cp -- "$PRODUCT" "$APP/Contents/MacOS/StageBSandboxRunner" "$APP/extra"',
    )
    with pytest.raises(ShellContractError):
        parse_stage_b_shell_contract(injected)
~~~

Additional RED nodes require unknown command, unknown path-bearing option, unsupported redirection and unclassified path-bearing argv to fail.

RED command:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_stage_b_evidence_build_boundary.py -q
~~~

Expected RED reason: frozen-base shell contains discovery/render/output fallbacks, extra extraction/redirection and no closed sink classifier.

Minimal implementation: make `scripts/stage-b-build-app.sh` byte-for-byte the final §8.10 script; add exactly `.stage-b-build/` to root `.gitignore`. Parser accepts only the §8.10 shape and derives all sinks itself.

GREEN commands:

~~~bash
PYTHONPATH=src "$GATE0_PY" -m pytest tests/gate0/unit/test_stage_b_evidence_build_boundary.py -q
bash -n scripts/stage-b-build-app.sh
~~~

Expected GREEN result: static tests pass and `bash -n` exits zero; no Swift/build/codesign process executes.

Exact commit:

~~~bash
git add scripts/stage-b-build-app.sh tests/gate0/unit/test_stage_b_evidence_build_boundary.py .gitignore
git commit -m "refactor(gate0): bind static Stage-B build boundary"
~~~

### Task 16 — repeatable FV1–FV8, independent code review and implementation receipt

**File:** `docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md`

Dependencies: Tasks 14,15. This task exists only for a later explicitly authorized implementation run.

Before any Task-1 implementation command, the future controller MUST possess two literal values supplied by the later explicit implementation authorization / owner approval:

- `AUTHORIZED_IMPLEMENTATION_BASE_SHA` — exact lowercase 40-hex authorized implementation base;
- `AUTHORIZED_V7_PLAN_BLOB` — exact lowercase 40-hex Git blob of the independently approved V7 plan.

The controller must not discover, infer, substitute, or self-author either value. Fail closed before implementation if either is absent or malformed.

Exact future setup:

~~~bash
: "${AUTHORIZED_IMPLEMENTATION_BASE_SHA:?explicit authorization must supply AUTHORIZED_IMPLEMENTATION_BASE_SHA}"
: "${AUTHORIZED_V7_PLAN_BLOB:?explicit authorization must supply AUTHORIZED_V7_PLAN_BLOB}"
case "$AUTHORIZED_IMPLEMENTATION_BASE_SHA" in (*[!0-9a-f]*|'') exit 64;; esac
case "$AUTHORIZED_V7_PLAN_BLOB" in (*[!0-9a-f]*|'') exit 64;; esac
test "${#AUTHORIZED_IMPLEMENTATION_BASE_SHA}" -eq 40
test "${#AUTHORIZED_V7_PLAN_BLOB}" -eq 40
export G0_REV18_V7_PLAN_PATH=docs/superpowers/plans/2026-09-23-gate0-rev18-evidence-dag-implementation-plan-v7.md
export G0_REV18_APPROVED_PLAN_BLOB="$AUTHORIZED_V7_PLAN_BLOB"
export G0_REV18_IMPLEMENTATION_BASE="$AUTHORIZED_IMPLEMENTATION_BASE_SHA"
export G0_REV18_VERIFY_PHASE=PRE_RECEIPT
~~~

For each direct controlled command, capture all `required_control_keys` **before START**, emit those exact captured values in `CommandLedgerEvent.control_inputs`, and pass those same captured values into the child environment. Environment rereads after START are forbidden for required control inputs.

Then execute FV1–FV8 exactly as frozen in §10: §10.1 FV1; §10.6.1 FV2/FV3/FV4/FV5/FV6/FV8; §10.7 static FV7. PRE_RECEIPT FV4 receives `receipt_path=None` and may not access a receipt.

After every PRE check passes:
1. request independent code review on that exact implementation candidate;
2. consume review with `receiving-code-review`; unexpected failures route to `systematic-debugging`;
3. after each accepted remediation rerun FV1–FV8 with exact PRE control inputs;
4. write the receipt with candidate SHA, baseline digest, FV1–FV8 results, reviewer identity/disposition, exact PRE path set, authorization-provided implementation base, authorization-provided approved V7 plan blob, and all activity fields;
5. commit only the receipt:

~~~bash
git add docs/agent-runs/run-20260923-gate0-rev18-implementation-v1/implementation-receipt.md
git commit -m "docs(gate0): record Revision-18 implementation verification"
~~~

6. set `G0_REV18_VERIFY_PHASE=POST_RECEIPT`; capture the POST value before START; rerun FV1–FV8. FV4 requires POST receipt/control-input/stdin/artifact/static/VCS agreement and FV5 exact POST changed-path equality.

Expected GREEN result: every FV passes in each required phase without provisioning, dependency installation, build/sign execution, profile-freeze measurement, Generation B, live Stage B, provider/model activity, protected media, or any authorization widening.

## 13. Task graph and acyclicity

Exact dependencies:
- Task 1: none
- Task 2: 1
- Task 3: 1,2
- Task 4: 1
- Task 5: 1,4
- Task 6: 2,3,4,5
- Task 7: 1,4,6
- Task 8: 1,4,5,6,7
- Task 9: 2,4,7,8
- Task 10: 6,8,9
- Task 11: 4,5,9,10
- Task 12: 1,7,10,11
- Task 13: 1,2,3,4,5,6,7,8,9,10,11,12
- Task 14: 7,8,9,10,11,12,13
- Task 15: 8,14
- Task 16: 14,15

Topological order 1..16 is valid; every edge points backward in that order. §11 writer paths remain pairwise disjoint and `tests/gate0/conftest.py` is absent from the write set. Rolling-frontier parallelism is allowed only after all declared predecessors complete and only for disjoint writers.

## 14. Improved Six-Cycle self-refinement before freeze

### Cycle 1 — Authority / Facts

Verify and record as VERIFIED/PENDING/NOT_OBSERVED/BLOCKED:

- exact V6 predecessor subject `290f09b6363d963ce5b2b8cb699100f3a1ad78ba` and plan blob `8f324fe3951b307b4f634346cff37552d2ef38d8`;
- moderator convergence `f7fb6ecc60ea0b135f7bde87c301f2f47309060f` / `b49b59c505382a27eaadb4918d96fe49c72166a1`;
- moderator intake and all three reviewer memo blobs;
- Revision-18 spec/ruling/final-owner blobs;
- exact branch ancestry from the V6 review subject;
- current authorization/evidence state, with implementation and restricted runtime activity still unauthorized.

### Cycle 2 — Internal Consistency

Search final V7 bytes for:

- stale active V6 plan-path variables or V6 execution instructions;
- stale 942/200 inventory claims outside historical V6 facts;
- contradictory selected-environment/control-input descriptions;
- duplicated effect-policy truth;
- inconsistent PRE/POST phase semantics;
- stale stdin/scanner hashes or octet counts;
- stale task dependencies/writer ownership;
- machine-type/serialized-object/prose mismatches.

Historical V1–V6 identities and the intentionally unchanged V6 source-form registry schema remain historical evidence, not active V7 execution truth.

### Cycle 3 — Mechanical Contract Closure

Mechanically prove:

- every behavior-defining verifier input actually consumed by PRETASK/FV1/FV_DRIVER is bound in exact `control_inputs`;
- required control values are captured before START and the same captured values are passed to the child;
- canonical V7 path plus external approved-plan Git blob prevents canonical-looking path → alternate bytes;
- START/END and FV4 bind implementation base, approved plan identity and exact phase;
- Path namespace classification is machine-carried and single-valued;
- `EffectPolicy` type fields == serialized object keys/order exactly;
- the sole policy remains the only safe-behavior truth;
- the plan-owned scanner source region is independently byte/digest/AST-conformance checked before FV3;
- no undefined helper or implementation discretion remains in V7-01/V7-02/V7-03.

### Cycle 4 — Executability / TDD / Adversarial Falsification

Verify each Task 1–15 RED → minimal GREEN → regression → exact git-add → exact commit sequence and mechanically expand §7. Attempt at minimum:

- plan-path retarget;
- canonical path with wrong approved plan bytes;
- wrong implementation base;
- PRE/POST phase mutation;
- same argv/stdin with changed control input;
- START/END control mismatch;
- missing required control input;
- extra unauthorized control input;
- `Path.walk`;
- another unlisted `Path.*` callable;
- exact harmless Path allowlist member;
- listed traversal outside exact CensusFS leaf;
- local wrapper and alias/import Path traversal;
- extra scanner-only safe symbol;
- renamed/extra scanner safe-list constant;
- hidden scanner special-case branch;
- scanner-body widening when widened symbol is absent from production roots;
- preserved stale-handle, no-op, expectation-echo and source-form falsifiers.

### Cycle 5 — Security / Evidence / Provenance / No Widening

Verify no V7 change authorizes profile-freeze measurement, venv provisioning, dependency download/install, host inspection, process/network/provider activity, build/sign, Generation B, live Stage B, protected media, runtime-policy approval or Gate promotion.

Keep exactly:

`PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`

`GENERATION_B_ELIGIBILITY=BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`

### Cycle 6 — Convergence / Minimal Next Action

Deduplicate findings and repair only V7-01/V7-02/V7-03 plus directly necessary inventory/hash/manifest/prose updates. Recompute test inventory, controlled-command manifest, exact stdin bodies, PRE/POST writer sets, task graph/cycle status and duplicate writers. If no material plan issue remains, create the author verification memo, commit the substantive candidate, and only then create a metadata-only freeze record for targeted independent V7 review.

## 15. Plan-review acceptance checklist

Independent targeted V7 review must attempt to falsify:

1. V7 descends exactly from V6 review subject `290f09b6363d963ce5b2b8cb699100f3a1ad78ba`; V1–V6 are immutable.
2. Moderator convergence, Revision-18 spec/ruling/final-owner blobs are exact.
3. Command manifest has exactly 70 unique task-step records and exactly three EXACT_BYTES commands.
4. PRETASK_BASELINE_PY remains V6-exact: 3741 octets / `988f93f310ff698872539012a0f60cc2516a4dc82a380fda425832170ef9d9b5`.
5. FV1_PY and FV_DRIVER_PY octet/digest values recompute from the final V7 bytes.
6. `CommandLedgerEvent.control_inputs` and `AllowedControlledCommand.required_control_keys` are exact machine fields.
7. identical argv/stdin + changed implementation base rejects.
8. identical argv/stdin + changed plan path rejects.
9. canonical V7 path + unapproved bytes rejects against external approved V7 Git blob.
10. PRE↔POST phase mutation rejects.
11. START/END control-input mismatch rejects.
12. missing required or extra unauthorized control input rejects.
13. required control inputs are capture-before-START and same captured values are passed to child.
14. FV1/shared driver independently prove approved V7 plan identity before consuming plan truth.
15. `EffectPolicy` type names/order exactly equal sole serialized policy keys/order.
16. os/asyncio harmless allowlists remain empty; multiprocessing/security-unlisted/shell/network/default-deny fields remain exact.
17. Path harmless allowlist is exact, policy-carried and pure lexical only.
18. `Path.walk` and another unlisted Path callable become EFFECT_UNKNOWN/fail-closed.
19. exact listed Path traversal outside CensusFS leaf becomes TRAVERSAL/fail-closed.
20. alias/import/local-wrapper Path effects classify/propagate identically.
21. scanner source block count/digest recompute from final V7 plan.
22. FV_DRIVER independently rejects extra safe symbol, renamed/extra safe-list constant, hidden branch and any scanner-body widening before production-root contents matter.
23. scanner-source conformance never calls the implementation classifier as its oracle.
24. pytest 8.3.3 strict/non-strict XPASS, XFAIL, FAILED, ERROR, SKIPPED, duplicate-terminal and V5-06 baseline semantics remain unchanged.
25. exact 13-entry source-form registry, used-id equality, row160 source/hash/outcome and expectation separation remain unchanged.
26. VerifiedRepositoryContext, AnchoredS1, exact-instance handles, empty-origin environment, M1R, RR18-2-N01, native serialization, 32-hop precedence, Mach-O 8/54/43, five-field N4a, P20 and row21 remain intact.
27. §7 expands to singleton=218, parameter families=24, parameterized=742, total=960, unique=960, duplicates=0.
28. FV1 exact collected set == executed set == all 960 plan-owned nodes and all terminal outcomes are PASSED.
29. FV2 uses the same corrected recorder and exact historical/additive-set law.
30. PRE/POST writer sets remain exact 44/45 paths; receipt is sole POST-only path.
31. task graph is acyclic and duplicate writer paths=0.
32. Tasks 1–15 are TDD-complete and contain no undefined helper/fixture.
33. placeholder scan is clean.
34. `PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`.
35. `GENERATION_B_ELIGIBILITY=BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`.
36. no implementation or restricted runtime activity occurred during V7 authoring.

## 16. Planning-turn terminal state

`PYTHON_NATIVE_CLOSURE_BASELINE=NOT_OBSERVED`

`GENERATION_B_ELIGIBILITY=BLOCKED_ON_FUTURE_PROFILE_FREEZE_BASELINE`

`IMPLEMENTATION_AUTHORIZED=NO`

`IMPLEMENTATION_EXECUTED=NO`

`PROFILE_FREEZE_MEASUREMENT_EXECUTED=NO`

`VENV_PROVISIONING_EXECUTED=NO`

`DEPENDENCY_INSTALL_EXECUTED=NO`

`BUILD_SIGN_EXECUTED=NO`

`GENERATION_B_EXECUTED=NO`

`LIVE_STAGE_B_EXECUTED=NO`

`PROVIDER_MODEL_ACTIVITY=NO`

`PROTECTED_MEDIA_TOUCHED=NO`

`INDEPENDENT_CERTIFICATION_CLAIMED=NO`

Author-side V7 remediation may stop only at:

`READY_FOR_INDEPENDENT_PLAN_REVIEW`

Independent review and any later implementation authorization remain separate acts.
