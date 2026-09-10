"""Write a valid recipe or set stub. Contributors edit JSON, not Python."""

from __future__ import annotations

import json
from pathlib import Path

from .naming import catalog_id_error
from .recipe_loader import CUBE_TRIS, RecipeError, load_all
from .set_loader import load_all_sets


def write_recipe(
    folder: Path,
    recipe_id: str,
    *,
    name: str = "",
) -> Path:
    recipe_id = recipe_id.strip()
    reason = catalog_id_error(recipe_id)
    if reason:
        raise RecipeError(f"id {reason}")
    path = folder / f"{recipe_id}.json"
    if path.exists():
        raise RecipeError(f"{path.name} already exists")
    display = name.strip() or recipe_id.replace("_", " ").title()
    parts = [
        {
            "name": "body",
            "primitive": "cube",
            "size": [0.4, 0.4, 0.4],
            "location": [0, 0, 0.2],
            "color": "#7a5429",
        },
        {
            "name": "lid",
            "primitive": "cube",
            "size": [0.42, 0.42, 0.04],
            "location": [0, 0, 0.42],
            "color": "#8c6239",
        },
    ]
    payload = {
        "id": recipe_id,
        "name": display,
        "description": f"TODO: describe {display} with separate named parts.",
        "tags": ["props"],
        "target_tris": CUBE_TRIS * len(parts),
        "parts": parts,
    }
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_set(
    folder: Path,
    set_id: str,
    recipe_ids: tuple[str, ...],
    *,
    recipes_folder: Path,
    name: str = "",
) -> Path:
    set_id = set_id.strip()
    reason = catalog_id_error(set_id)
    if reason:
        raise RecipeError(f"id {reason}")
    if not recipe_ids:
        raise RecipeError("set needs at least one recipe id")
    known = {recipe.id for recipe in load_all(recipes_folder)}
    missing = [item for item in recipe_ids if item not in known]
    if missing:
        raise RecipeError(f"unknown recipe: {', '.join(missing)}")
    if folder.is_dir():
        existing = {item.id for item in load_all_sets(folder)}
        if set_id in existing:
            raise RecipeError(f"{set_id}.json already exists")
    path = folder / f"{set_id}.json"
    if path.exists():
        raise RecipeError(f"{path.name} already exists")
    display = name.strip() or set_id.replace("_", " ").title()
    items = [
        {"recipe": recipe_id, "location": [index * 1.4, 0, 0]}
        for index, recipe_id in enumerate(recipe_ids)
    ]
    payload = {
        "id": set_id,
        "name": display,
        "description": f"TODO: arrange {', '.join(recipe_ids)}.",
        "tags": ["props"],
        "items": items,
    }
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def parse_recipe_list(raw: str) -> tuple[str, ...]:
    parts = [item.strip() for item in raw.split(",") if item.strip()]
    if not parts:
        raise RecipeError("provide at least one recipe id")
    for item in parts:
        reason = catalog_id_error(item)
        if reason:
            raise RecipeError(f"not a slug: {item} ({reason})")
    return tuple(parts)
