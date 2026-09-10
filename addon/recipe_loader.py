from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Iterable

from .colors import is_hex_color, normalize_hex
from .naming import catalog_id_error, part_name_error

ALLOWED_PRIMITIVES = frozenset({"cube"})
CUBE_TRIS = 12


class RecipeError(ValueError):
    """Invalid recipe JSON."""


@dataclass(frozen=True)
class Part:
    name: str
    primitive: str
    size: tuple[float, float, float]
    location: tuple[float, float, float]
    rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    color: str | None = None


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    target_tris: int
    parts: tuple[Part, ...]
    description: str = ""
    tags: tuple[str, ...] = ()


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
        if path.name == "schema.json" or path.name.endswith(".schema.json"):
            continue
        recipes.append(load_recipe(path))
    ids = [recipe.id for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise RecipeError("duplicate recipe id")
    return tuple(recipes)


def _parse_recipe(raw: dict[str, Any], fallback_id: str) -> Recipe:
    recipe_id = _require_str(raw, "id") or fallback_id
    if recipe_id != fallback_id:
        raise RecipeError(
            f"{fallback_id}.json: id {recipe_id!r} must match the filename stem"
        )
    reason = catalog_id_error(recipe_id)
    if reason:
        raise RecipeError(f"{fallback_id}.json: id {reason}")
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
    part_names = [part.name for part in parts]
    if len(part_names) != len(set(part_names)):
        raise RecipeError("parts[].name must be unique")
    expected_tris = CUBE_TRIS * len(parts)
    if target_tris != expected_tris:
        raise RecipeError(
            f"target_tris must be {expected_tris} for {len(parts)} cube parts "
            f"({CUBE_TRIS} tris each)"
        )
    description = raw.get("description")
    if description is not None and not isinstance(description, str):
        raise RecipeError("description must be a string")
    tags = _parse_tags(raw.get("tags"))
    return Recipe(
        id=recipe_id,
        name=name,
        target_tris=target_tris,
        parts=parts,
        description=description or "",
        tags=tags,
    )


def _parse_tags(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise RecipeError("tags must be a list of slugs")
    tags = []
    for index, item in enumerate(raw):
        if not isinstance(item, str):
            raise RecipeError(f"tags[{index}] must be a lowercase slug")
        tag = item.strip()
        reason = part_name_error(tag)
        if reason:
            raise RecipeError(f"tags[{index}] {reason}")
        tags.append(tag)
    if len(tags) != len(set(tags)):
        raise RecipeError("tags must be unique")
    return tuple(tags)


def _parse_part(raw: Any, index: int) -> Part:
    if not isinstance(raw, dict):
        raise RecipeError(f"parts[{index}] must be an object")
    name = _require_str(raw, "name")
    if not name:
        raise RecipeError(f"parts[{index}].name is required")
    reason = part_name_error(name)
    if reason:
        raise RecipeError(f"parts[{index}].name {reason}")
    primitive = _require_str(raw, "primitive")
    if primitive not in ALLOWED_PRIMITIVES:
        raise RecipeError(
            f"parts[{index}].primitive must be one of {sorted(ALLOWED_PRIMITIVES)}"
        )
    size = _vec3(raw.get("size"), f"parts[{index}].size")
    if any(component <= 0 for component in size):
        raise RecipeError(f"parts[{index}].size must be three positive numbers")
    location = _vec3(raw.get("location"), f"parts[{index}].location")
    rotation = raw.get("rotation_deg", [0, 0, 0])
    rotation_deg = _vec3(rotation, f"parts[{index}].rotation_deg")
    color = _parse_color(raw.get("color"), f"parts[{index}].color")
    return Part(
        name=name,
        primitive=primitive,
        size=size,
        location=location,
        rotation_deg=rotation_deg,
        color=color,
    )


def _parse_color(raw: Any, label: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not is_hex_color(raw):
        raise RecipeError(f"{label} must be #RRGGBB")
    return normalize_hex(raw)


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
