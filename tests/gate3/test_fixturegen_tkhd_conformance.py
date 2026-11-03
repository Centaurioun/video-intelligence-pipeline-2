from __future__ import annotations

import struct

import pytest

from gate3 import fixturegen


def _boxes(data: bytes, start: int = 0, end: int | None = None):
    end = len(data) if end is None else end
    pos = start
    while pos + 8 <= end:
        size = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4 : pos + 8]
        header = 8
        if size == 1:
            if pos + 16 > end:
                return
            size = struct.unpack_from(">Q", data, pos + 8)[0]
            header = 16
        elif size == 0:
            size = end - pos
        if size < header or pos + size > end:
            return
        yield pos, kind, header, size
        pos += size


def _descend(data: bytes, parents: tuple[bytes, ...]):
    start, end = 0, len(data)
    for parent in parents:
        found = next((b for b in _boxes(data, start, end) if b[1] == parent), None)
        assert found is not None, f"missing {parent!r}"
        start = found[0] + found[2]
        end = found[0] + found[3]
    return list(_boxes(data, start, end))


def _tkhd(data: bytes, track_index: int = 0):
    traks = [b for b in _descend(data, (b"moov",)) if b[1] == b"trak"]
    trak = traks[track_index]
    children = list(_boxes(data, trak[0] + trak[2], trak[0] + trak[3]))
    box = next(b for b in children if b[1] == b"tkhd")
    payload = box[0] + box[2]
    return box, payload


def _fields(data: bytes, track_index: int = 0):
    box, p = _tkhd(data, track_index)
    return box, struct.unpack_from(">IIIII", data, p + 4), data[p]


def _single(**kwargs) -> bytes:
    return fixturegen.build_mp4(media_timescale=1000, sample_deltas=(40, 40), **kwargs)


def test_r_f1_generated_tkhd_has_nonzero_track_id():
    box, fields, _ = _fields(_single())
    assert box[3] == 92
    assert fields[2] == 1


def test_r_f2_generated_tkhd_has_zero_modification_time():
    _, fields, _ = _fields(_single())
    assert fields[1] == 0


def test_r_f3_declared_duration_occupies_tkhd_duration_field():
    _, fields, _ = _fields(_single(declared_duration=120))
    assert fields[4] == 120


def test_r_f4_multi_track_ids_are_distinct_and_sequential():
    data = fixturegen.build_multi_trak_mp4(media_timescale=1000, traks=[
        {"media_timescale": 1000, "sample_deltas": (40,), "handler": b"vide"},
        {"media_timescale": 48000, "sample_deltas": (1024,), "handler": b"soun"},
    ])
    ids = tuple(_fields(data, i)[1][2] for i in range(2))
    assert ids == (1, 2)


def test_r_f5_adversarial_fixture_builders_emit_declared_shapes():
    assert fixturegen.build_no_tkhd_mp4()
    short = fixturegen.build_short_tkhd_mp4()
    assert any(b[1] == b"tkhd" and b[3] < 92 for b in _descend(short, (b"moov", b"trak")))
    zero = fixturegen.build_zero_size_tkhd_mp4()
    box, _ = _tkhd(zero)
    assert struct.unpack_from(">I", zero, box[0])[0] == 0
    large = fixturegen.build_large_size_tkhd_mp4()
    box, fields, _ = _fields(large)
    assert struct.unpack_from(">I", large, box[0])[0] == 1 and fields[2] == 1
    version2 = fixturegen.build_tkhd_version_2_mp4()
    assert _fields(version2)[2] == 2
    duplicate = fixturegen.build_duplicate_track_id_mp4()
    assert tuple(_fields(duplicate, i)[1][2] for i in range(2)) == (1, 1)
    reversed_ids = fixturegen.build_reversed_track_ids_mp4()
    assert tuple(_fields(reversed_ids, i)[1][2] for i in range(2)) == (2, 1)
    timingless = fixturegen.build_timingless_trak_mp4()
    assert any(b[1] == b"tkhd" for b in _descend(timingless, (b"moov", b"trak")))
    assert not any(b[1] == b"stts" for b in _descend(timingless, (b"moov", b"trak", b"mdia", b"minf", b"stbl")))
    assert "no_tkhd" in fixturegen.RECIPES
    assert fixturegen.build_recipe("no_tkhd") == fixturegen.build_no_tkhd_mp4()


def test_r_f5_extended_size_tkhd_preserves_parent_box_boundaries():
    data = fixturegen.build_large_size_tkhd_mp4()
    moov = next(b for b in _boxes(data) if b[1] == b"moov")
    trak = next(b for b in _boxes(data, moov[0] + moov[2], moov[0] + moov[3]) if b[1] == b"trak")
    children = list(_boxes(data, trak[0] + trak[2], trak[0] + trak[3]))
    tkhd = next(b for b in children if b[1] == b"tkhd")
    mdia = next(b for b in children if b[1] == b"mdia")
    assert tkhd[0] + tkhd[3] == mdia[0]
    assert trak[0] + trak[3] == max(child[0] + child[3] for child in children)
    assert moov[0] + moov[3] == max(child[0] + child[3] for child in _boxes(data, moov[0] + moov[2], moov[0] + moov[3]))


def test_r_f5_recipe_builder_is_usable_through_public_generate_fixture(tmp_path):
    import hashlib

    result = fixturegen.generate_fixture("no_tkhd", tmp_path, out_name="no-tkhd.mp4")
    blob = (tmp_path / "no-tkhd.mp4").read_bytes()
    assert result["fixture"] == "no_tkhd"
    assert result["sha256"] == hashlib.sha256(blob).hexdigest()
    assert result["byte_count"] == len(blob)



@pytest.mark.parametrize("recipe_name", [
    "no_tkhd", "short_tkhd", "zero_size_tkhd", "large_size_tkhd",
    "tkhd_version_2", "duplicate_track_id", "reversed_track_ids", "timingless_trak",
])
def test_r_f5_adversarial_recipes_are_consumable_by_generate_fixture(tmp_path, recipe_name):
    import hashlib

    result = fixturegen.generate_fixture(recipe_name, tmp_path, out_name=f"{recipe_name}.mp4")
    blob = (tmp_path / f"{recipe_name}.mp4").read_bytes()
    assert result["fixture"] == recipe_name
    assert result["sha256"] == hashlib.sha256(blob).hexdigest()
    assert result["byte_count"] == len(blob)
    expected = {
        "duplicate_track_id": (1000, (40,), 40),
        "reversed_track_ids": (1000, (40,), 40),
        "timingless_trak": (1000, (), 80),
    }.get(recipe_name, (1000, (40, 40), 80))
    timescale, deltas, duration = expected
    assert fixturegen.RECIPES[recipe_name]["media_timescale"] == timescale
    assert tuple(fixturegen.RECIPES[recipe_name]["sample_deltas"]) == deltas
    timing_bytes = fixturegen._mdhd(timescale, duration)
    if recipe_name != "timingless_trak":
        timing_bytes = fixturegen._stts(deltas) + timing_bytes
    assert result["container_sha256_of_stts"] == hashlib.sha256(timing_bytes).hexdigest()
