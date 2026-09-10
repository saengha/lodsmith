import json
from pathlib import Path

from addon.cli import main
from addon.recipe_loader import load_all
from addon.set_loader import load_all_sets


ROOT = Path(__file__).resolve().parent.parent
RECIPES = str(ROOT / "recipes")
SETS = str(ROOT / "sets")


def test_cli_list(capsys):
    assert main(["--recipes", RECIPES, "list"]) == 0
    out = capsys.readouterr().out
    assert "crate\tCrate\t72" in out
    assert "lantern" in out


def test_cli_validate(capsys):
    assert main(["--recipes", RECIPES, "--sets", SETS, "validate"]) == 0
    out = capsys.readouterr().out
    assert "ok\tcrate" in out
    assert "ok\tset:tavern" in out
    recipes = load_all(ROOT / "recipes")
    sets = load_all_sets(ROOT / "sets")
    assert f"{len(recipes)} recipes ok, {len(sets)} sets ok, 0 failed" in out


def test_cli_compile_json(capsys):
    assert main(["--recipes", RECIPES, "compile", "stool"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["parent_name"] == "lodsmith.stool"
    assert payload["estimated_tris"] == 60
    assert payload["poly_ok"] is True


def test_cli_plan(capsys):
    assert main(["--recipes", RECIPES, "--sets", SETS, "plan", "loot chest"]) == 0
    out = capsys.readouterr().out
    assert "chest" in out


def test_cli_plan_korean_set(capsys):
    assert main(["--recipes", RECIPES, "--sets", SETS, "plan", "선술집"]) == 0
    out = capsys.readouterr().out
    assert "set\ttavern" in out


def test_cli_compose(capsys):
    assert main(["--recipes", RECIPES, "--sets", SETS, "compose", "yard"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["id"] == "yard"
    assert payload["estimated_tris"] > 0
    fences = [item for item in payload["items"] if item["recipe"] == "fence_post"]
    assert len(fences) == 4
    assert fences[0]["scale"] == 1.0


def test_cli_missing_recipe(capsys):
    assert main(["--recipes", RECIPES, "compile", "nope"]) == 1
    err = capsys.readouterr().err
    assert "missing recipe" in err
