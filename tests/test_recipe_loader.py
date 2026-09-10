from pathlib import Path

import pytest

from addon.recipe_loader import RecipeError, load_all, load_recipe, recipes_dir


ROOT = Path(__file__).resolve().parent.parent


def test_recipes_dir_points_at_repo_recipes():
    assert recipes_dir() == ROOT / "recipes"


def test_load_crate_recipe():
    recipe = load_recipe(ROOT / "recipes" / "crate.json")
    assert recipe.id == "crate"
    assert recipe.name == "Crate"
    assert recipe.target_tris == 72
    assert "storage" in recipe.tags
    names = [part.name for part in recipe.parts]
    assert "lid" in names
    assert "floor" in names
    for part in recipe.parts:
        assert part.primitive == "cube"
        assert len(part.size) == 3
        assert len(part.location) == 3
        assert part.color is not None
        assert part.color.startswith("#")


def test_load_all_skips_schema_and_has_unique_ids():
    recipes = load_all(ROOT / "recipes")
    ids = [recipe.id for recipe in recipes]
    assert len(ids) == len(set(ids))
    assert "recipe" not in ids
    assert {"crate", "barrel", "chest", "lantern", "stool"} <= set(ids)


def test_filename_must_match_id(tmp_path: Path):
    path = tmp_path / "crate.json"
    path.write_text(
        '{"id":"other","name":"Other","target_tris":12,"parts":[{"name":"x","primitive":"cube","size":[1,1,1],"location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="filename stem"):
        load_recipe(path)


def test_rotation_defaults_to_zero():
    recipe = load_recipe(ROOT / "recipes" / "crate.json")
    assert recipe.parts[0].rotation_deg == (0.0, 0.0, 0.0)


def test_rejects_unknown_primitive(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text(
        '{"id":"bad","name":"Bad","target_tris":12,"parts":[{"name":"x","primitive":"uv_sphere","size":[1,1,1],"location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="primitive"):
        load_recipe(path)


def test_rejects_empty_parts(tmp_path: Path):
    path = tmp_path / "empty.json"
    path.write_text(
        '{"id":"empty","name":"Empty","target_tris":1,"parts":[]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="parts"):
        load_recipe(path)


def test_rejects_bad_target_tris(tmp_path: Path):
    path = tmp_path / "tiny.json"
    path.write_text(
        '{"id":"tiny","name":"T","target_tris":0,"parts":[{"name":"x","primitive":"cube","size":[1,1,1],"location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="target_tris"):
        load_recipe(path)


def test_rejects_wrong_cube_budget(tmp_path: Path):
    path = tmp_path / "tiny.json"
    path.write_text(
        '{"id":"tiny","name":"T","target_tris":12,"parts":['
        '{"name":"a","primitive":"cube","size":[1,1,1],"location":[0,0,0]},'
        '{"name":"b","primitive":"cube","size":[1,1,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="24"):
        load_recipe(path)


def test_rejects_duplicate_part_names(tmp_path: Path):
    path = tmp_path / "dup.json"
    path.write_text(
        '{"id":"dup","name":"Dup","target_tris":24,"parts":['
        '{"name":"wall","primitive":"cube","size":[1,1,1],"location":[0,0,0]},'
        '{"name":"wall","primitive":"cube","size":[1,1,1],"location":[1,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="unique"):
        load_recipe(path)


def test_rejects_bad_part_slug(tmp_path: Path):
    path = tmp_path / "slug.json"
    path.write_text(
        '{"id":"slug","name":"Slug","target_tris":12,"parts":['
        '{"name":"Wall Front","primitive":"cube","size":[1,1,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="slug"):
        load_recipe(path)


def test_rejects_bad_color(tmp_path: Path):
    path = tmp_path / "tint.json"
    path.write_text(
        '{"id":"tint","name":"Tint","target_tris":12,"parts":['
        '{"name":"x","primitive":"cube","size":[1,1,1],"location":[0,0,0],"color":"brown"}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="#RRGGBB"):
        load_recipe(path)


def test_rejects_non_positive_size(tmp_path: Path):
    path = tmp_path / "flat.json"
    path.write_text(
        '{"id":"flat","name":"Flat","target_tris":12,"parts":['
        '{"name":"x","primitive":"cube","size":[1,0,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="positive"):
        load_recipe(path)


def test_load_recipe_rejects_blocked_id(tmp_path: Path):
    path = tmp_path / "cube.json"
    path.write_text(
        '{"id":"cube","name":"Cube","target_tris":12,"parts":['
        '{"name":"body","primitive":"cube","size":[1,1,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="reserved or blocked"):
        load_recipe(path)


def test_load_recipe_rejects_padded_reserved_id(tmp_path: Path):
    path = tmp_path / "c_u_b_e.json"
    path.write_text(
        '{"id":"c_u_b_e","name":"Nope","target_tris":12,"parts":['
        '{"name":"body","primitive":"cube","size":[1,1,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="reserved or blocked"):
        load_recipe(path)


def test_load_recipe_rejects_blocked_part_name(tmp_path: Path):
    path = tmp_path / "stool_tall.json"
    path.write_text(
        '{"id":"stool_tall","name":"Tall stool","target_tris":12,"parts":['
        '{"name":"untitled","primitive":"cube","size":[1,1,1],"location":[0,0,0]}'
        "]}",
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="reserved or blocked"):
        load_recipe(path)


def test_shipped_good_ids_still_load():
    for recipe_id in ("crate", "anvil", "firepit"):
        recipe = load_recipe(ROOT / "recipes" / f"{recipe_id}.json")
        assert recipe.id == recipe_id


def test_normalizes_color_hex(tmp_path: Path):
    path = tmp_path / "tint.json"
    path.write_text(
        '{"id":"tint","name":"Tint","target_tris":12,"parts":['
        '{"name":"x","primitive":"cube","size":[1,1,1],"location":[0,0,0],"color":"#AABBCC"}'
        "]}",
        encoding="utf-8",
    )
    recipe = load_recipe(path)
    assert recipe.parts[0].color == "#aabbcc"
