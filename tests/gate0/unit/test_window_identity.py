"""Window identity must survive more than one source revision in one run."""
from __future__ import annotations

from gate0.adapters.decoder import DecodedFrame
from gate0.inventory import RevisionRef
from gate0.temporal import sample_targets


def _revision(revision_id: str) -> RevisionRef:
    return RevisionRef(revision_id, revision_id, "synthetic", 0, "config")


def _frames() -> tuple[DecodedFrame, ...]:
    frames = []
    for ordinal in range(16):
        seconds = ordinal / 2
        frames.append(
            DecodedFrame(
                raw_pts_ticks=int(seconds * 90000),
                time_base_num=1,
                time_base_den=90000,
                decoder_ordinal=ordinal,
                presentation_order=ordinal,
                selected_frame_id=f"frame_{ordinal}",
                pixels=b"",
            )
        )
    return tuple(frames)


def test_window_ids_are_unique_across_source_revisions_in_one_run():
    rows = []
    for revision_id in ("rev_alpha", "rev_beta"):
        rows.extend(sample_targets(_revision(revision_id), _frames(), window_count=2))

    pairs = [(row.window_id, row.tick) for row in rows]
    assert len(pairs) == len(set(pairs)), "window_id/tick must be unique across revisions in one run"
    assert all(row.window_id.startswith(f"{row.mapping_ref.split('_map_')[0]}_window_") for row in rows)
    assert {row.window_id for row in rows} == {
        "rev_alpha_window_0", "rev_alpha_window_1", "rev_beta_window_0", "rev_beta_window_1",
    }
