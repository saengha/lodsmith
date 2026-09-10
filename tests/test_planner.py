from pathlib import Path

from addon.planner import _SET_SYNONYMS, _SYNONYMS, plan, tokenize
from addon.recipe_loader import load_all
from addon.set_loader import load_all_sets


ROOT = Path(__file__).resolve().parent.parent


def _catalog():
    return load_all(ROOT / "recipes"), load_all_sets(ROOT / "sets")


def test_tokenize_lowercases_and_splits():
    assert tokenize("Wooden Barrel!") == frozenset({"wooden", "wood", "barrel"})


def test_plan_keg_ranks_barrel_family():
    recipes, sets = _catalog()
    hits = plan("a wooden keg", recipes, sets)
    assert hits
    assert hits[0].id in {"barrel", "barrel_open"}


def test_plan_tavern_prefers_set():
    recipes, sets = _catalog()
    hits = plan("tavern", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "tavern"


def test_plan_korean_tavern_prefers_set():
    recipes, sets = _catalog()
    hits = plan("선술집", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "tavern"


def test_plan_exact_id_boost():
    recipes, sets = _catalog()
    hits = plan("signpost", recipes, sets, limit=3)
    assert hits[0].id == "signpost"


def test_plan_empty_prompt_is_empty():
    recipes, sets = _catalog()
    assert plan("   ", recipes, sets) == ()


def test_plan_market_prefers_set():
    recipes, sets = _catalog()
    hits = plan("market stall", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "market"


def test_plan_korean_entrance():
    recipes, sets = _catalog()
    hits = plan("출입구", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "entrance"


def test_every_catalog_id_has_synonyms():
    recipes, sets = _catalog()
    assert {recipe.id for recipe in recipes} == set(_SYNONYMS)
    assert {prop_set.id for prop_set in sets} == set(_SET_SYNONYMS)


def test_plan_window_ranks_window():
    recipes, sets = _catalog()
    hits = plan("window pane", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "window"


def test_plan_korean_window_not_door():
    recipes, sets = _catalog()
    hits = plan("창문", recipes, sets)
    assert hits[0].id == "window"


def test_plan_wagon_ranks_cart():
    recipes, sets = _catalog()
    hits = plan("wooden wagon", recipes, sets)
    assert hits[0].id == "cart"


def test_plan_crate_stack_prefers_set():
    recipes, sets = _catalog()
    hits = plan("crate stack", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "crate_stack"


def test_plan_korean_wellside():
    recipes, sets = _catalog()
    hits = plan("우물가", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "wellside"


def test_plan_facade_prefers_set():
    recipes, sets = _catalog()
    hits = plan("facade", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "facade"


def test_plan_korean_chair_not_stool():
    recipes, sets = _catalog()
    hits = plan("의자", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "chair"


def test_plan_korean_anvil():
    recipes, sets = _catalog()
    hits = plan("모루", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "anvil"


def test_plan_korean_firepit():
    recipes, sets = _catalog()
    hits = plan("모닥불", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "firepit"


def test_plan_dont_exec_bpy_ranks_crate():
    recipes, sets = _catalog()
    hits = plan("don't exec bpy", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "crate"


def test_plan_72_tris_ranks_crate():
    recipes, sets = _catalog()
    hits = plan("72 tris", recipes, sets)
    assert hits[0].kind == "recipe"
    assert hits[0].id == "crate"


def test_plan_smithy_prefers_set():
    recipes, sets = _catalog()
    hits = plan("smithy", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "smithy"


def test_plan_inn_prefers_set():
    recipes, sets = _catalog()
    hits = plan("inn", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "inn"


def test_plan_korean_smithy():
    recipes, sets = _catalog()
    hits = plan("대장간", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "smithy"


def test_plan_korean_inn():
    recipes, sets = _catalog()
    hits = plan("여관", recipes, sets)
    assert hits[0].kind == "set"
    assert hits[0].id == "inn"


def test_plan_korean_new_recipe_vocab():
    recipes, sets = _catalog()
    mapping = {
        "침대": "bed",
        "텐트": "tent",
        "병": "bottle",
        "책": "book",
        "망치": "hammer",
        "가마솥": "cauldron",
    }
    for prompt, recipe_id in mapping.items():
        hits = plan(prompt, recipes, sets)
        assert hits, prompt
        assert hits[0].kind == "recipe", prompt
        assert hits[0].id == recipe_id, (prompt, hits[0].id)
