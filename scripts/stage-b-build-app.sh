#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_ROOT="${STAGE_B_BUILD_ROOT:-$ROOT/.stage-b-build}"
IDENTITY="${STAGE_B_SIGN_IDENTITY:-}"
[[ -n "$IDENTITY" ]] || { echo "BLOCKED_STAGE_B_STABLE_SIGNING_IDENTITY" >&2; exit 20; }
DISCOVERY="${STAGE_B_DISCOVERY:-$BUILD_ROOT/host-discovery.json}"
ENTITLEMENTS="${STAGE_B_ENTITLEMENTS:-$BUILD_ROOT/StageBSandboxRunner.entitlements}"
APP="$BUILD_ROOT/StageBSandboxRunner.app"
mkdir -p "$BUILD_ROOT"
python3 "$ROOT/scripts/stage-b-discover-host.py" --output "$DISCOVERY" --worktree "$ROOT" --output-root "${STAGE_B_OUTPUT_ROOT:-$BUILD_ROOT/output}"
python3 "$ROOT/scripts/stage-b-render-entitlements.py" --discovery "$DISCOVERY" --output "$ENTITLEMENTS" --output-root "${STAGE_B_OUTPUT_ROOT:-$BUILD_ROOT/output}"
BIN_PATH="$(swift build -c release --package-path "$ROOT/macos/stage_b" --show-bin-path)"
PRODUCT="$BIN_PATH/stage-b-sandbox-runner"
[[ -x "$PRODUCT" ]] || { echo "STAGE_B_BUILD_PRODUCT_MISSING:$PRODUCT" >&2; exit 21; }
mkdir -p "$APP/Contents/MacOS"
cp "$ROOT/macos/stage_b/Info.plist" "$APP/Contents/Info.plist"
cp "$PRODUCT" "$APP/Contents/MacOS/StageBSandboxRunner"
/usr/bin/codesign --force --sign "$IDENTITY" --entitlements "$ENTITLEMENTS" --identifier org.centaurioun.video-intelligence-pipeline.gate0.stageb "$APP"
/usr/bin/codesign --verify --strict --verbose=4 "$APP"
/usr/bin/codesign -dvvv --entitlements :- "$APP" > "$BUILD_ROOT/codesign-entitlements.txt" 2>&1
/usr/bin/codesign -d -r- "$APP" > "$BUILD_ROOT/designated-requirement.txt" 2>&1
echo "$APP"
