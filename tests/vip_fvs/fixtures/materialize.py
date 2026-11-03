"""Test-only materialization for the checked-in FVS timing recipes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

FIXTURE_ROOT = Path(__file__).resolve().parent


def load_recipe(recipe: str | Path) -> dict:
    path = Path(recipe)
    if path.name not in {"cfr_4s_shape.json", "vfr_nonuniform.json"}:
        path = FIXTURE_ROOT / f"{recipe}.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def materialize_fixture(recipe: str | Path, tmp_path: str | Path) -> Path:
    """Write a disposable, digest-bound source descriptor under ``tmp_path``.

    This deliberately writes JSON metadata rather than media bytes. Consumers
    inject a decoder/source seam and must use the recipe's integer PTS/timebase.
    """
    descriptor = load_recipe(recipe)
    target = Path(tmp_path) / f"{descriptor['fixture_id']}.source.json"
    canonical = json.dumps(descriptor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = {"recipe": descriptor, "content_sha256": hashlib.sha256(canonical.encode()).hexdigest()}
    target.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return target


materialize_recipe = materialize_fixture
