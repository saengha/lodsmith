from pathlib import Path

from addon.compile import compile_recipe
from addon.recipe_loader import CUBE_TRIS, load_all, load_recipe


ROOT = Path(__file__).resolve().parent.parent


def test_compile_crate_names_and_budget():
    recipe = load_recipe(ROOT / "recipes" / "crate.json")
    compiled = compile_recipe(recipe)
    assert compiled.parent_name == "lodsmith.crate"
    assert compiled.poly_ok
    assert compiled.estimated_tris == 72
    names = [part.object_name for part in compiled.parts]
    assert names[0] == "crate.floor"
    assert "crate.lid" in names
    assert compiled.to_dict()["recipe_id"] == "crate"


def test_every_shipped_recipe_compiles():
    recipes = load_all(ROOT / "recipes")
    assert len(recipes) >= 13
    for recipe in recipes:
        compiled = compile_recipe(recipe)
        assert compiled.recipe_id == recipe.id
        assert compiled.parent_name == f"lodsmith.{recipe.id}"
        assert compiled.estimated_tris == CUBE_TRIS * len(recipe.parts)
        assert compiled.estimated_tris == recipe.target_tris
        assert compiled.poly_ok
        object_names = [part.object_name for part in compiled.parts]
        assert len(object_names) == len(set(object_names))
        for part, source in zip(compiled.parts, recipe.parts, strict=True):
            assert part.object_name == f"{recipe.id}.{source.name}"
            assert part.size == source.size
            assert part.location == source.location
            assert part.rotation_deg == source.rotation_deg
            assert part.color == source.color
