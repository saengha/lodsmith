from pathlib import Path

import pytest

from addon.recipe_loader import RecipeError, load_all
from addon.set_loader import load_all_sets, load_set, validate_sets


ROOT = Path(__file__).resolve().parent.parent


def test_load_tavern_set_has_table_and_stools():
    prop_set = load_set(ROOT / "sets" / "tavern.json")
    assert prop_set.id == "tavern"
    ids = [item.recipe_id for item in prop_set.items]
    assert ids.count("stool") == 3
    assert "table" in ids
    assert "mug" in ids


def test_yard_repeat_expands_fence():
    prop_set = load_set(ROOT / "sets" / "yard.json")
    fences = [item for item in prop_set.items if item.recipe_id == "fence_post"]
    assert len(fences) == 4
    assert fences[1].location[0] == pytest.approx(1.2)


def test_crate_stack_repeats_crates():
    prop_set = load_set(ROOT / "sets" / "crate_stack.json")
    crates = [item for item in prop_set.items if item.recipe_id == "crate"]
    assert len(crates) == 3
    assert crates[0].location[2] == pytest.approx(0.14)
    assert crates[1].location[2] == pytest.approx(0.65)


def test_load_all_sets_skips_schema_and_has_unique_ids():
    catalog = load_all_sets(ROOT / "sets")
    ids = [item.id for item in catalog]
    assert len(ids) == len(set(ids))
    assert "set" not in ids


def test_set_filename_must_match_id(tmp_path: Path):
    path = tmp_path / "named.json"
    path.write_text(
        '{"id":"other","name":"Other","items":[{"recipe":"crate","location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="filename stem"):
        load_set(path)


def test_all_sets_resolve_against_catalog():
    recipes = load_all(ROOT / "recipes")
    catalog = load_all_sets(ROOT / "sets")
    assert {item.id for item in catalog} >= {
        "tavern",
        "warehouse",
        "yard",
        "camp",
        "market",
        "entrance",
        "crate_stack",
        "wellside",
        "facade",
    }
    validate_sets(catalog, recipes)


def test_unknown_recipe_in_set(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text(
        '{"id":"bad","name":"Bad","items":[{"recipe":"nope","location":[0,0,0]}]}',
        encoding="utf-8",
    )
    recipes = load_all(ROOT / "recipes")
    with pytest.raises(RecipeError, match="unknown recipe"):
        validate_sets((load_set(path),), recipes)


def test_load_set_rejects_blocked_id(tmp_path: Path):
    path = tmp_path / "untitled.json"
    path.write_text(
        '{"id":"untitled","name":"Nope","items":[{"recipe":"crate","location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="reserved or blocked"):
        load_set(path)


def test_placement_scale_and_rotation(tmp_path: Path):
    path = tmp_path / "tiny.json"
    path.write_text(
        '{"id":"tiny","name":"Tiny","items":[{"recipe":"crate","location":[1,0,0],'
        '"rotation_deg":[0,0,90],"scale":0.5}]}',
        encoding="utf-8",
    )
    item = load_set(path).items[0]
    assert item.scale == 0.5
    assert item.rotation_deg[2] == 90
    recipes = load_all(ROOT / "recipes")
    validate_sets((load_set(path),), recipes)
