#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
INPUT_ROOT="${INPUT_ROOT:?INPUT_ROOT is required}"
OUTPUT_ROOT="${OUTPUT_ROOT:?OUTPUT_ROOT is required}"
RUN_ID="${RUN_ID:?RUN_ID is required}"
RUN_DIR="$OUTPUT_ROOT/$RUN_ID"
STAGE="${1:?stage is required}"

test -x /usr/bin/bwrap || { echo 'SANDBOX_ATTESTATION' >&2; exit 20; }
test -x /usr/bin/python3.11 || { echo 'SANDBOX_ATTESTATION' >&2; exit 20; }
# The helper owns the validated argv contract: --die-with-parent --unshare-net
# --clearenv --ro-bind --bind --dev /dev --proc /proc --setenv PATH /usr/bin:/bin
# and /usr/bin/python3.11; helper binds GATE0_SANDBOX_ATTESTATION_JSON and PYTHONPATH.
export PYTHONPATH="$REPO_ROOT/src"
exec /usr/bin/python3.11 -m gate0.launcher_attestation "$REPO_ROOT" "$INPUT_ROOT" "$OUTPUT_ROOT" "$RUN_ID" "$STAGE" "$RUN_DIR"
