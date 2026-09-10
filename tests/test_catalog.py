from pathlib import Path
import json

from addon.recipe_loader import load_all, load_recipe
from addon.set_loader import load_all_sets


ROOT = Path(__file__).resolve().parent.parent


def test_every_recipe_json_loads():
    recipes = load_all(ROOT / "recipes")
    assert {recipe.id for recipe in recipes} >= {"crate", "barrel"}
    for recipe in recipes:
        assert recipe.tags, recipe.id
        assert len(recipe.parts) >= 2, recipe.id
        assert recipe.target_tris == 12 * len(recipe.parts)


def test_every_set_json_loads():
    catalog = load_all_sets(ROOT / "sets")
    assert {item.id for item in catalog} >= {"tavern", "yard"}
    assert catalog


def test_recipe_files_are_objects_with_matching_id():
    for path in sorted((ROOT / "recipes").glob("*.json")):
        if path.name.endswith(".schema.json"):
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["id"] == path.stem
        load_recipe(path)


def test_set_files_are_objects_with_matching_id():
    for path in sorted((ROOT / "sets").glob("*.json")):
        if path.name.endswith(".schema.json"):
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["id"] == path.stem
