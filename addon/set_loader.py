"""Declarative prop sets: several recipes with offsets. No bpy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Iterable

from .naming import catalog_id_error, part_name_error
from .recipe_loader import Recipe, RecipeError, recipes_dir


@dataclass(frozen=True)
class Placement:
    recipe_id: str
    location: tuple[float, float, float]
    rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: float = 1.0


@dataclass(frozen=True)
class PropSet:
    id: str
    name: str
    items: tuple[Placement, ...]
    description: str = ""
    tags: tuple[str, ...] = ()

    @property
    def recipe_ids(self) -> tuple[str, ...]:
        return tuple(item.recipe_id for item in self.items)


def sets_dir(start: Path | None = None) -> Path:
    if start is None:
        return recipes_dir().parent / "sets"
    return start / "sets"


def load_set(path: Path) -> PropSet:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecipeError(f"{path.name}: invalid JSON ({exc})") from exc
    if not isinstance(raw, dict):
        raise RecipeError(f"{path.name}: root must be an object")
    return _parse_set(raw, path.stem)


def load_all_sets(directory: Path | None = None) -> tuple[PropSet, ...]:
    folder = directory if directory is not None else sets_dir()
    if not folder.is_dir():
        raise RecipeError(f"sets directory missing: {folder}")
    loaded = []
    for path in sorted(folder.glob("*.json")):
        if path.name.endswith(".schema.json"):
            continue
        loaded.append(load_set(path))
    ids = [item.id for item in loaded]
    if len(ids) != len(set(ids)):
        raise RecipeError("duplicate set id")
    return tuple(loaded)


def validate_sets(
    catalog: tuple[PropSet, ...],
    recipes: tuple[Recipe, ...],
) -> None:
    known = {recipe.id for recipe in recipes}
    for prop_set in catalog:
        if not prop_set.items:
            raise RecipeError(f"{prop_set.id}: items must be non-empty")
        for item in prop_set.items:
            if item.recipe_id not in known:
                raise RecipeError(
                    f"{prop_set.id}: unknown recipe {item.recipe_id!r}"
                )


def estimated_set_tris(prop_set: PropSet, recipes: tuple[Recipe, ...]) -> int:
    by_id = {recipe.id: recipe for recipe in recipes}
    return sum(by_id[item.recipe_id].target_tris for item in prop_set.items)


def _parse_set(raw: dict[str, Any], fallback_id: str) -> PropSet:
    set_id = _require_str(raw, "id") or fallback_id
    if set_id != fallback_id:
        raise RecipeError(
            f"{fallback_id}.json: id {set_id!r} must match the filename stem"
        )
    reason = catalog_id_error(set_id)
    if reason:
        raise RecipeError(f"{fallback_id}.json: id {reason}")
    name = _require_str(raw, "name")
    if not name:
        raise RecipeError("name is required")
    items_raw = raw.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        raise RecipeError("items must be a non-empty list")
    items: list[Placement] = []
    for index, item in enumerate(items_raw):
        items.extend(_parse_item(item, index))
    description = raw.get("description")
    if description is not None and not isinstance(description, str):
        raise RecipeError("description must be a string")
    tags = _parse_tags(raw.get("tags"))
    return PropSet(
        id=set_id,
        name=name,
        items=tuple(items),
        description=description or "",
        tags=tags,
    )


def _parse_item(raw: Any, index: int) -> tuple[Placement, ...]:
    if not isinstance(raw, dict):
        raise RecipeError(f"items[{index}] must be an object")
    recipe_id = raw.get("recipe")
    if not isinstance(recipe_id, str) or not recipe_id.strip():
        raise RecipeError(f"items[{index}].recipe must be a slug")
    recipe_id = recipe_id.strip()
    reason = catalog_id_error(recipe_id)
    if reason:
        raise RecipeError(f"items[{index}].recipe {reason}")
    location = _vec3(raw.get("location", [0, 0, 0]), f"items[{index}].location")
    rotation = _vec3(
        raw.get("rotation_deg", [0, 0, 0]), f"items[{index}].rotation_deg"
    )
    repeat = raw.get("repeat", 1)
    if not isinstance(repeat, int) or repeat < 1 or repeat > 32:
        raise RecipeError(f"items[{index}].repeat must be an int 1..32")
    offset = _vec3(raw.get("offset", [0, 0, 0]), f"items[{index}].offset")
    scale = raw.get("scale", 1)
    if not isinstance(scale, (int, float)) or float(scale) <= 0:
        raise RecipeError(f"items[{index}].scale must be a positive number")
    scale_f = float(scale)
    placed = []
    for step in range(repeat):
        placed.append(
            Placement(
                recipe_id=recipe_id,
                location=(
                    location[0] + offset[0] * step,
                    location[1] + offset[1] * step,
                    location[2] + offset[2] * step,
                ),
                rotation_deg=rotation,
                scale=scale_f,
            )
        )
    return tuple(placed)


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
