# Gate-0 T00–T11 synthetic implementation receipt

## Scope and boundary

This receipt records local, synthetic verification for the bounded Gate-0
implementation authorized by Issue #12. No real archive or media run, model
download, model/provider inference, cloud call, external network egress,
Google Drive materialization, or later Gate 1–3 execution was performed.
Those runtime, model-feasibility, archive-scale, and host-enforcement facts
remain `NOT_OBSERVED`.

The run contract retains exactly 13 persisted result artifacts. The canonical
control input `config/gate0/default.json`, schemas, fixtures, logs, temporary
files, and this receipt are not runtime result artifacts. `policy.json` is not
a result artifact and is not accepted as a second policy control path.

## Observed checks

The following evidence was observed in the Issue #12 implementation lanes and
revalidated by the T11 lane where noted:

| Area | Evidence state |
| --- | --- |
| T00 configuration/lock contract | ACCEPTED and canonical from Issue #11; downstream regression checks remained green |
| T01 IDs, canonical serialization, envelopes, and 13-artifact schemas | ACCEPTED and canonical from Issue #11; downstream regression checks remained green |
| T02 inventory/authorization | focused and cumulative synthetic tests passed in its lane |
| T03 split/labels | focused and cumulative synthetic tests passed in its lane |
| T04 policy/egress | synthetic policy/egress checks passed; host runtime enforcement remains `NOT_OBSERVED` |
| T05 temporal extraction | seven-fixture temporal oracle checks passed; real decoder/media behavior remains `NOT_OBSERVED` |
| T06 representation arms | synthetic metadata/semantic seams passed; model feasibility/inference remains `NOT_OBSERVED` |
| T07 ranking | deterministic synthetic ranking checks passed |
| T08 evaluation/report | synthetic metrics/decision checks passed; malformed mapping/origin/time-base/uncertainty evidence now fails closed as protocol-invalid and report metrics are digest/owner bound |
| T09 lifecycle/rollback | synthetic retry, invalidation, retention, and rollback checks passed |
| T10 repeatability/CLI/verifier | synthetic repeatability and verifier checks passed; partial or malformed comparison maps fail with exit 20; legal non-repeat stages remain explicit `NOT_OBSERVED`; host enforcement remains `NOT_OBSERVED` |
| T11 acceptance projections | exact seven-entry catalog, six minimum roles, closed 13-artifact inventory, no duplicate policy path, and receipt-boundary checks passed |

The T11 acceptance test is a projection over checked-in contracts and
synthetic inputs. It does not claim that real runtime execution occurred.

Final integrated-main observations at SHA `071b5d9`:

- `.venv-gate0/bin/python --version`: Python 3.11.9; pytest 8.3.3; `pip check` reported no broken requirements.
- `PYTHONPATH=src .venv-gate0/bin/python -m pytest tests/gate0 -q`: `143 passed`.
- Full synthetic Gate-0 verifier with deny-network, schemas, structural foreign keys, exact artifact count, secrets, redaction, prohibited-artifact, no-provider, repeatability, and comparison-closure flags: all PASS; `artifact_count=13`.
- `git diff --check`: PASS; `bash scripts/verify-workspace.sh`: PASS.
- Whole-branch recertification: policy/security PASS; specification and determinism/test certifiers NEEDS_WORK on remaining launcher process-boundary attestation and verifier/stage-order contract gaps. No further remediation generation was authorized.

## Reproducibility

Use the repository-local Python 3.11.9 environment and no package
installation or network access:

```text
PYTHONPATH=src .venv-gate0/bin/python -m pytest tests/gate0/integration/test_synthetic_acceptance.py -q
PYTHONPATH=src .venv-gate0/bin/python -m pytest tests/gate0 -q
PYTHONPATH=src .venv-gate0/bin/python scripts/verify-gate0.py --schemas --foreign-keys --artifact-count=13 --synthetic-only
```

The final pushed-state check remains a synchronization property and is
recorded in the Issue #12 ledger after the non-force push. Host bwrap/Python
process-boundary execution, model/provider feasibility, and real archive/media
execution remain `NOT_OBSERVED`.

## Issue #14 launcher evidence closure

The bounded Issue #14 continuation closed only the Amendment-1 CERT-B launcher
evidence blockers. No package, provider, network, real-media, later-gate, or
destructive operation was performed.

`CERTIFIED_CANDIDATE_SHA = e9a51b955900e8a2d0bc4bd9d28c95cadda8a45b`

- B1 has eight durable mutation tests covering security/control flag, mount
  mode, mount order, environment binding, interpreter invocation, CLI shape,
  and both config-bound digests. All eight were baseline-GREEN characterization
  tests because the existing validator already rejected each mutation.
- B3 has observed RED -> minimal GREEN -> regression for explicit final
  observed argv/mount digest equality with transported attestation and config.
- B2 has observed RED -> minimal GREEN -> regression for the injectable exec
  seam receiving exactly the last successfully validated final argv.
- Focused launcher/config/preflight regression: `32 passed`; full Gate-0
  regression: `179 passed`; synthetic and semantic candidate verifiers: PASS;
  `py_compile`, `git diff --check`, and workspace verification: PASS.

Fresh certification dispositions from the exact candidate:

- CERT-A: PASS — preservation/spec, ordered-stage behavior, semantic closure,
  exact 13-artifact contract, and approved config/schema state.
- CERT-B: PASS — complete B1/B2/B3 Amendment-1 evidence and main-path identity.
- CERT-C: PASS — fail-closed policy/security and scope preservation.

Actual Linux bwrap/Python child process-boundary execution is `NOT_OBSERVED`
because the required host binaries/runtime are unavailable in this environment;
the synthetic fail-closed evidence remains valid. This receipt does not
authorize Pilot 1, later gates, provider/cloud calls, model downloads, or real
archive/media execution.
