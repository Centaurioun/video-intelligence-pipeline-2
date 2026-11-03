"""Build a Gate-0 *media* input root from real, locally generated MP4 fixtures.

The synthetic fixture root (``tests/gate0/fixtures/synthetic-input``) carries no
media at all, so the media-input branch of the pipeline could not be exercised
end to end.  This module generates real MP4 files at test time with
``tests/gate0/media/generated_media.py`` (ffmpeg/``testsrc2``), points four
declared revisions at four distinct files, and writes the
``media-corpus.json`` contract that ``gate0.media_experiment.load_media_corpus``
accepts.

What is reused verbatim (never hand-authored):

* ``synthetic-labels.json`` and ``synthetic-query-vectors.json`` come from the
  existing synthetic-input generator, so the media revisions reuse exactly the
  synthetic revision ids (``rev_eval_sunrise``/``rev_eval_office``/
  ``rev_eval_night``/``rev_dev_probe``) and the join keeps working;
* the corpus ``relations`` list is copied from the generated synthetic corpus.

What is media-specific:

* each revision maps onto a real generated file, so every locator is unique;
* ``rev_dev_probe`` is a byte-for-byte copy of ``media/cfr_25.mp4`` (the same
  content under a second occurrence, not a re-encode);
* ``generation`` records the generator module, the fixture specifications and
  the real ``ffmpeg``/``ffprobe`` version banner lines measured at build time.

The builder is deterministic and idempotent (same inputs -> byte-identical
JSON), uses only the standard library, and never writes absolute paths.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

_MODULE_PATH = Path(__file__).resolve()
# <repo>/tests/gate0/fixtures/generated-media/build_media_corpus.py
_REPO_ROOT = _MODULE_PATH.parents[4]
_MEDIA_TEST_ROOT = _REPO_ROOT / "tests/gate0/media"
_SYNTHETIC_INPUT_ROOT = _REPO_ROOT / "tests/gate0/fixtures/synthetic-input"

for _path in (str(_MEDIA_TEST_ROOT), str(_SYNTHETIC_INPUT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import generate  # noqa: E402  (synthetic-input generator: labels/vectors/relations)
import generated_media  # noqa: E402  (real MP4 fixture harness; ffmpeg-backed)

MEDIA_CORPUS_FILE = "media-corpus.json"
MEDIA_CORPUS_SCHEMA_VERSION = "gate0.media-corpus.v1"
MEDIA_CORPUS_KIND = "generated_synthetic_media_not_experiment_evidence"

EVALUATION_REVISIONS = ("rev_eval_sunrise", "rev_eval_office", "rev_eval_night")
DEVELOPMENT_REVISION = "rev_dev_probe"

#: revision id -> locator relative to the input root (every locator is unique).
REVISION_LOCATORS = {
    "rev_eval_sunrise": "media/cfr_30.mp4",
    "rev_eval_office": "media/cfr_25.mp4",
    "rev_eval_night": "media/bframes.mp4",
    "rev_dev_probe": "media/dev_cfr_25.mp4",
}

#: (source, destination) copy that gives the development revision distinct bytes
#: under a distinct occurrence without re-encoding.
_DEV_COPY = ("media/cfr_25.mp4", "media/dev_cfr_25.mp4")

#: generated fixtures recorded in ``generation`` (used by the revisions above and
#: by the negative tests: vfr_concat + the three corrupt fixtures).
_RECORDED_FIXTURES = ("cfr_25", "cfr_30", "bframes", "vfr_concat")
_RECORDED_CORRUPT = tuple(generated_media.CORRUPT_FIXTURES)

_RELATION_PREFIX = "rel_"


def _declared_spec(name: str) -> dict[str, Any]:
    spec = generated_media.SPECS[name]
    return {
        "name": spec.name,
        "kind": spec.kind,
        "width": spec.width,
        "height": spec.height,
        "declared_frame_count": spec.declared_frame_count,
        "declared_nominal_rate": list(spec.declared_nominal_rate) if spec.declared_nominal_rate else None,
        "has_audio": spec.has_audio,
        "video_stream_index": spec.video_stream_index,
        "notes": spec.notes,
    }


def _tool_banner(executable: str) -> str:
    try:
        result = subprocess.run(
            [executable, "-version"], capture_output=True, text=True, check=False, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[0] if lines else "unavailable"


def _canonical_relations(relations: Iterable[Iterable[str]]) -> list[list[str]]:
    """Copy the synthetic relation edges into the corpus' canonical orientation.

    ``load_media_corpus`` requires each undirected edge to be stored as
    ``[left, right]`` with ``left < right``; the synthetic corpus stores its
    single edge in declaration order, so the edge *set* is preserved while each
    edge is oriented canonically.
    """
    canonical: list[list[str]] = []
    for edge in relations:
        pair = sorted(str(item) for item in edge)
        if pair not in canonical:
            canonical.append(pair)
    return sorted(canonical)


def _relation_ids(relations: list[list[str]]) -> dict[str, list[str]]:
    ids: dict[str, list[str]] = {}
    for left, right in relations:
        relation_id = f"{_RELATION_PREFIX}{left}_{right}"
        for revision_id in (left, right):
            ids.setdefault(revision_id, []).append(relation_id)
    return ids


def _revision_entry(
    revision_id: str,
    *,
    locator: str,
    split: str,
    window_count: int,
    selected_stream_index: int | None,
    relation_ids: list[str],
) -> dict[str, Any]:
    return {
        "revision_id": revision_id,
        "occurrence_id": f"occ_{revision_id}",
        "content_id": f"content_{revision_id}",
        "locator": locator,
        "relation_ids": list(relation_ids),
        "split": split,
        "window_count": int(window_count),
        "selected_stream_index": selected_stream_index,
    }


def _write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_media_input(
    destination: Path | str,
    *,
    revision_overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> Path:
    """Generate real media fixtures and write a valid media input root.

    ``destination`` is the ``--input-root`` directory.  The function creates
    ``destination/media/*.mp4``, ``destination/media-corpus.json``,
    ``destination/synthetic-labels.json`` and
    ``destination/synthetic-query-vectors.json``, then returns the path to the
    corpus document.

    ``revision_overrides`` exists for the fail-closed integration tests: it
    replaces individual revision fields (for example ``locator`` or
    ``window_count``) on top of the deterministic defaults.
    """
    destination = Path(destination)
    destination = destination if destination.is_absolute() else destination.resolve()
    media_dir = destination / "media"
    destination.mkdir(parents=True, exist_ok=True)

    generated_media.generate_all(media_dir)
    source_name, copy_name = _DEV_COPY
    shutil.copyfile(media_dir / Path(source_name).name, media_dir / Path(copy_name).name)

    synthetic_corpus = generate.build_corpus()
    labels = generate.build_labels()
    query_vectors = generate.build_query_vectors(labels)
    _write_json(destination / generate.LABELS_FILE, labels)
    _write_json(destination / generate.QUERY_VECTORS_FILE, query_vectors)

    relations = _canonical_relations(synthetic_corpus.get("relations", ()))
    relation_ids = _relation_ids(relations)

    overrides = {
        str(revision_id): dict(changes)
        for revision_id, changes in (revision_overrides or {}).items()
    }
    unknown = sorted(set(overrides) - set(REVISION_LOCATORS))
    if unknown:
        raise ValueError(f"unknown revision override(s): {unknown}")

    revisions: list[dict[str, Any]] = []
    for revision_id, default_locator in REVISION_LOCATORS.items():
        changes = overrides.get(revision_id, {})
        split = "EVALUATION" if revision_id in EVALUATION_REVISIONS else "DEVELOPMENT"
        entry = _revision_entry(
            revision_id,
            locator=str(changes.pop("locator", default_locator)),
            split=str(changes.pop("split", split)),
            window_count=int(changes.pop("window_count", 1)),
            selected_stream_index=changes.pop("selected_stream_index", None),
            relation_ids=changes.pop("relation_ids", relation_ids.get(revision_id, [])),
        )
        if changes:
            raise ValueError(f"unsupported override field(s) for {revision_id}: {sorted(changes)}")
        revisions.append(entry)

    generation = {
        "generator_module": "tests/gate0/media/generated_media.py",
        "fixture_builder": "tests/gate0/fixtures/generated-media/build_media_corpus.py",
        "ffmpeg_version": _tool_banner("ffmpeg"),
        "ffprobe_version": _tool_banner("ffprobe"),
        "fixture_specs": [_declared_spec(name) for name in _RECORDED_FIXTURES],
        "corrupt_fixtures": list(_RECORDED_CORRUPT),
        "development_copy": {
            "source": _DEV_COPY[0],
            "destination": _DEV_COPY[1],
            "method": "byte_copy_no_reencode",
        },
    }

    document = {
        "schema_version": MEDIA_CORPUS_SCHEMA_VERSION,
        "corpus_kind": MEDIA_CORPUS_KIND,
        "generation": generation,
        "evaluation_revisions": sorted(EVALUATION_REVISIONS),
        "development_revision": DEVELOPMENT_REVISION,
        "relations": relations,
        "revisions": sorted(revisions, key=lambda row: str(row["revision_id"])),
    }
    corpus_path = destination / MEDIA_CORPUS_FILE
    _write_json(corpus_path, document)
    return corpus_path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="media input root to create")
    args = parser.parse_args(list(argv) if argv is not None else None)
    corpus_path = build_media_input(Path(args.destination))
    print(f"media_corpus={corpus_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
