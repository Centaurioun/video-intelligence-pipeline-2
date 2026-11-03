# Functional vertical-slice synthetic fixtures

These files are test-only timing recipes. They are not Gate-0 result artifacts,
source media, model inputs, or production corpus data. A test may call
`materialize_fixture(recipe, tmp_path)` from `materialize.py`; the generated
descriptor is disposable and must remain below the test's temporary directory.

## Recipe contract

Each recipe records a single synthetic video stream and its presentation-order
PTS sequence. `time_base` is the exact rational mapping from integer PTS ticks
to seconds. `tail_duration_ticks` is explicit because the final sample's
duration cannot be inferred from a following PTS. `duration_ticks` and
`duration_seconds` are derived values included as an oracle.

The CFR recipe is the four-second control used by the vertical slice:

* `pts_ticks = [0, 13, 25, 38, 50, 63, 75, 88]`
* `time_base = 1/25`
* final sample duration = 12 ticks, giving 100 ticks / 25 Hz = 4 seconds

At the eight 2-FPS target offsets (`0, 1/2, ..., 7/2`), selection is the
first presentation-order frame satisfying `target <= PTS < 4`; the expected
frame IDs are recorded in the recipe. This is an integer-rational predicate,
not `seconds * nominal_fps`.

The VFR recipe preserves the approved non-uniform presentation sequence
(`0, 40, 80, 160, 280` at a `1/1000` timebase) and an explicit 500-tick tail.
It is intentionally short and is used to prove that source-native PTS are
carried through the adapter. The expected deltas are `[40, 40, 80, 120]` ms;
the 80/120 ms gaps are the discriminating non-uniformity.

No semantic timestamp in these recipes is a cut or export instruction. Any
interval derived by a test remains candidate evidence until the measured
source-native PTS/timebase refinement step accepts it.
