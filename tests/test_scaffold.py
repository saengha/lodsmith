from pathlib import Path

import pytest

from addon.cli import main
from addon.recipe_loader import RecipeError, load_recipe
from addon.scaffold import parse_recipe_list, write_recipe, write_set
from addon.set_loader import load_set


ROOT = Path(__file__).resolve().parent.parent


def test_write_recipe_is_valid(tmp_path: Path):
    path = write_recipe(tmp_path, "stool_tall", name="Tall stool")
    recipe = load_recipe(path)
    assert recipe.id == "stool_tall"
    assert recipe.name == "Tall stool"
    assert recipe.target_tris == 24
    assert len(recipe.parts) == 2


def test_write_recipe_refuses_existing(tmp_path: Path):
    write_recipe(tmp_path, "dup")
    with pytest.raises(RecipeError, match="already exists"):
        write_recipe(tmp_path, "dup")


def test_write_recipe_refuses_blocked_ids(tmp_path: Path):
    for recipe_id in ("cube", "test", "untitled", "lodsmith", "c_u_b_e", "x"):
        with pytest.raises(RecipeError, match="reserved or blocked|two characters"):
            write_recipe(tmp_path, recipe_id)
        assert not (tmp_path / f"{recipe_id}.json").exists()
    path = write_recipe(tmp_path, "anvil", name="Anvil")
    assert load_recipe(path).id == "anvil"
    firepit = write_recipe(tmp_path, "firepit")
    assert load_recipe(firepit).id == "firepit"


def test_write_set_refuses_blocked_id(tmp_path: Path):
    with pytest.raises(RecipeError, match="reserved or blocked"):
        write_set(
            tmp_path,
            "test",
            ("crate",),
            recipes_folder=ROOT / "recipes",
        )


def test_write_set_uses_shipped_recipes(tmp_path: Path):
    path = write_set(
        tmp_path,
        "dock",
        ("crate", "barrel"),
        recipes_folder=ROOT / "recipes",
        name="Dock",
    )
    prop_set = load_set(path)
    assert prop_set.id == "dock"
    assert [item.recipe_id for item in prop_set.items] == ["crate", "barrel"]


def test_write_set_rejects_unknown_recipe(tmp_path: Path):
    with pytest.raises(RecipeError, match="unknown recipe"):
        write_set(
            tmp_path,
            "nope",
            ("not_a_prop",),
            recipes_folder=ROOT / "recipes",
        )


def test_parse_recipe_list():
    assert parse_recipe_list("crate, barrel") == ("crate", "barrel")
    with pytest.raises(RecipeError):
        parse_recipe_list("Crate")
    with pytest.raises(RecipeError, match="reserved or blocked"):
        parse_recipe_list("cube")


def test_cli_new_recipe(tmp_path: Path, capsys):
    assert (
        main(
            [
                "--recipes",
                str(tmp_path),
                "new",
                "recipe",
                "box_small",
                "--name",
                "Small box",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "wrote" in out
    assert (tmp_path / "box_small.json").is_file()


def test_cli_new_set(tmp_path: Path, capsys):
    assert (
        main(
            [
                "--recipes",
                str(ROOT / "recipes"),
                "--sets",
                str(tmp_path),
                "new",
                "set",
                "dock",
                "crate",
                "barrel",
                "--name",
                "Dock",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "wrote" in out
    assert (tmp_path / "dock.json").is_file()


def test_cli_new_recipe_refuses_blocked(tmp_path: Path, capsys):
    assert (
        main(["--recipes", str(tmp_path), "new", "recipe", "cube"])
        == 1
    )
    err = capsys.readouterr().err
    assert "reserved or blocked" in err
    assert not (tmp_path / "cube.json").is_file()


def test_cli_new_set_use_flag(tmp_path: Path):
    assert (
        main(
            [
                "--recipes",
                str(ROOT / "recipes"),
                "--sets",
                str(tmp_path),
                "new",
                "set",
                "pier",
                "--use",
                "crate,pallet",
            ]
        )
        == 0
    )
    assert (tmp_path / "pier.json").is_file()
