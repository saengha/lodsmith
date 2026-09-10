from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Iterable

ALLOWED_PRIMITIVES = frozenset({"cube"})


class RecipeError(ValueError):
    """Invalid recipe JSON."""


@dataclass(frozen=True)
class Part:
    name: str
    primitive: str
    size: tuple[float, float, float]
    location: tuple[float, float, float]


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    target_tris: int
    parts: tuple[Part, ...]
    description: str = ""


def recipes_dir(start: Path | None = None) -> Path:
    """Repo-root `recipes/` next to `blender_manifest.toml`."""
    here = start if start is not None else Path(__file__).resolve()
    root = here.parent.parent if start is None else start
    return root / "recipes"


def load_recipe(path: Path) -> Recipe:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecipeError(f"{path.name}: invalid JSON ({exc})") from exc
    if not isinstance(raw, dict):
        raise RecipeError(f"{path.name}: root must be an object")
    return _parse_recipe(raw, path.stem)


def load_all(directory: Path | None = None) -> tuple[Recipe, ...]:
    folder = directory if directory is not None else recipes_dir()
    if not folder.is_dir():
        raise RecipeError(f"recipes directory missing: {folder}")
    recipes = []
    for path in sorted(folder.glob("*.json")):
        recipes.append(load_recipe(path))
    ids = [recipe.id for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise RecipeError("duplicate recipe id")
    return tuple(recipes)


def _parse_recipe(raw: dict[str, Any], fallback_id: str) -> Recipe:
    recipe_id = _require_str(raw, "id") or fallback_id
    name = _require_str(raw, "name")
    if not name:
        raise RecipeError("name is required")
    target_tris = raw.get("target_tris")
    if not isinstance(target_tris, int) or target_tris <= 0:
        raise RecipeError("target_tris must be a positive int")
    parts_raw = raw.get("parts")
    if not isinstance(parts_raw, list) or len(parts_raw) == 0:
        raise RecipeError("parts must be a non-empty list")
    parts = tuple(_parse_part(item, index) for index, item in enumerate(parts_raw))
    description = raw.get("description")
    if description is not None and not isinstance(description, str):
        raise RecipeError("description must be a string")
    return Recipe(
        id=recipe_id,
        name=name,
        target_tris=target_tris,
        parts=parts,
        description=description or "",
    )


def _parse_part(raw: Any, index: int) -> Part:
    if not isinstance(raw, dict):
        raise RecipeError(f"parts[{index}] must be an object")
    name = _require_str(raw, "name")
    if not name:
        raise RecipeError(f"parts[{index}].name is required")
    primitive = _require_str(raw, "primitive")
    if primitive not in ALLOWED_PRIMITIVES:
        raise RecipeError(
            f"parts[{index}].primitive must be one of {sorted(ALLOWED_PRIMITIVES)}"
        )
    size = _vec3(raw.get("size"), f"parts[{index}].size")
    location = _vec3(raw.get("location"), f"parts[{index}].location")
    return Part(name=name, primitive=primitive, size=size, location=location)


def _require_str(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if value is None:
        return ""
    if not isinstance(value, str) or not value.strip():
        raise RecipeError(f"{key} must be a non-empty string")
    return value.strip()


def _vec3(value: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        raise RecipeError(f"{label} must be [x, y, z]")
    items = list(value)
    if len(items) != 3:
        raise RecipeError(f"{label} must be [x, y, z]")
    try:
        return (float(items[0]), float(items[1]), float(items[2]))
    except (TypeError, ValueError) as exc:
        raise RecipeError(f"{label} must be three numbers") from exc
