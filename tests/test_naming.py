from pathlib import Path

from addon.colors import hex_to_rgb, is_hex_color, normalize_hex
from addon.naming import (
    BLOCKED_SLUGS,
    catalog_id_error,
    compact_slug,
    is_catalog_id,
    is_slug,
    parent_name,
    part_name_error,
    part_object_name,
    recipe_id_from_parent,
)
from addon.recipe_loader import load_all
from addon.set_loader import load_all_sets


ROOT = Path(__file__).resolve().parent.parent


def test_hex_roundtrip():
    assert is_hex_color("#AaBbCc")
    assert normalize_hex("#AABBCC") == "#aabbcc"
    r, g, b = hex_to_rgb("#ffffff")
    assert (r, g, b) == (1.0, 1.0, 1.0)
    assert hex_to_rgb("#000000") == (0.0, 0.0, 0.0)
    assert not is_hex_color("white")
    assert not is_hex_color("#fff")


def test_naming_helpers():
    assert is_slug("crate_open")
    assert not is_slug("Crate")
    assert not is_slug("1crate")
    assert parent_name("crate") == "lodsmith.crate"
    assert part_object_name("crate", "lid") == "crate.lid"
    assert recipe_id_from_parent("lodsmith.crate_open") == "crate_open"
    assert recipe_id_from_parent("Cube") is None
    assert recipe_id_from_parent("lodsmith.cube") is None


def test_good_catalog_ids():
    for recipe_id in ("crate", "anvil", "firepit", "crate_open", "fence_post"):
        assert is_catalog_id(recipe_id)
        assert catalog_id_error(recipe_id) is None


def test_catalog_id_rejects_short_and_reserved():
    assert catalog_id_error("t") is not None
    assert catalog_id_error("x") is not None
    assert catalog_id_error("a_") is not None
    assert compact_slug("c_u_b_e") == "cube"
    for blocked in ("cube", "untitled", "test", "lodsmith", "blender", "bpy", "new"):
        assert catalog_id_error(blocked) is not None
        assert catalog_id_error(blocked) == "is reserved or blocked"
    assert catalog_id_error("c_u_b_e") == "is reserved or blocked"
    assert catalog_id_error("t_e_s_t") == "is reserved or blocked"
    assert not is_catalog_id("Crate")


def test_part_names_reject_blocked_words():
    assert part_name_error("lid") is None
    assert part_name_error("horn") is None
    assert part_name_error("x") is None
    assert part_name_error("cube") == "is reserved or blocked"
    assert part_name_error("Wall") is not None


def test_shipped_ids_are_not_on_the_blocklist():
    recipes = load_all(ROOT / "recipes")
    sets = load_all_sets(ROOT / "sets")
    for recipe in recipes:
        assert compact_slug(recipe.id) not in BLOCKED_SLUGS, recipe.id
        assert is_catalog_id(recipe.id), recipe.id
        for part in recipe.parts:
            assert part_name_error(part.name) is None, f"{recipe.id}.{part.name}"
        for tag in recipe.tags:
            assert part_name_error(tag) is None, f"{recipe.id} tag {tag}"
    for prop_set in sets:
        assert is_catalog_id(prop_set.id), prop_set.id
