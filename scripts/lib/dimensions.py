"""Read the dimension registry.

Small on purpose. The value is not the code, it is that every consumer asks the
same file instead of carrying its own list — see the header of
`dimensions.toml` for what the drift between four copies cost.

`datasets/*/metric.py` is the exception and keeps a literal copy, because the
dataset manifest publishes that file on its own and it has to run detached from
this repository. `scripts/validate-rubric` fails when the copy diverges.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import tomllib

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "dimensions.toml"


@lru_cache(maxsize=1)
def registry() -> dict:
    if not REGISTRY_PATH.is_file():
        raise SystemExit(
            f"{REGISTRY_PATH} is missing. It is the single definition of the "
            f"dimensions; without it a consumer would fall back to a private "
            f"list, which is the failure this file exists to prevent."
        )
    return tomllib.loads(REGISTRY_PATH.read_text())


def all_ids() -> list[str]:
    return [d["id"] for d in registry()["dimension"]]


def ids_for(applies_to: str) -> list[str]:
    return [d["id"] for d in registry()["dimension"] if d["applies_to"] == applies_to]


def open_dimensions() -> list[str]:
    """The eight an open forward review grades unless a case narrows them."""
    return ids_for("open")


def met_threshold() -> float:
    return float(registry()["met_threshold"])


def order(ids) -> list[str]:
    """Registry order for the given ids, unknown ones last and alphabetical."""
    known = all_ids()
    present = set(ids)
    return [i for i in known if i in present] + sorted(present - set(known))
