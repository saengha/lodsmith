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
    assert len(recipe.parts) >= 2
    names = [part.name for part in recipe.parts]
    assert "lid" in names
    assert "floor" in names
    for part in recipe.parts:
        assert part.primitive == "cube"
        assert len(part.size) == 3
        assert len(part.location) == 3


def test_load_all_includes_crate():
    recipes = load_all(ROOT / "recipes")
    assert any(recipe.id == "crate" for recipe in recipes)


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
    path = tmp_path / "tris.json"
    path.write_text(
        '{"id":"t","name":"T","target_tris":0,"parts":[{"name":"x","primitive":"cube","size":[1,1,1],"location":[0,0,0]}]}',
        encoding="utf-8",
    )
    with pytest.raises(RecipeError, match="target_tris"):
        load_recipe(path)
