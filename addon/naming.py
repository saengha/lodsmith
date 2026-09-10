"""Stable object names for recipes and compiled props."""

from __future__ import annotations

import re

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

# Short denylist for catalog ids and part names. Underscores are ignored
# (c_u_b_e == cube). Maintainers close anything else without debate; do not
# grow this into a profanity encyclopedia.
BLOCKED_SLUGS = frozenset(
    {
        "addon",
        "addons",
        "admin",
        "ass",
        "asshole",
        "bitch",
        "blender",
        "bpy",
        "chatgpt",
        "cock",
        "collection",
        "copilot",
        "cube",
        "cunt",
        "cursor",
        "default",
        "dick",
        "example",
        "fag",
        "faggot",
        "false",
        "fuck",
        "fucking",
        "github",
        "hitler",
        "json",
        "kkk",
        "lodsmith",
        "maintainer",
        "mesh",
        "nazi",
        "new",
        "nigga",
        "nigger",
        "none",
        "nsfw",
        "null",
        "object",
        "official",
        "openai",
        "operator",
        "penis",
        "porn",
        "pussy",
        "python",
        "rape",
        "recipe",
        "recipes",
        "retard",
        "root",
        "saengha",
        "sample",
        "scene",
        "schema",
        "set",
        "sets",
        "sex",
        "sexy",
        "shit",
        "slut",
        "temp",
        "test",
        "tests",
        "tmp",
        "todo",
        "troll",
        "true",
        "undefined",
        "untitled",
        "whore",
        "xxx",
    }
)


def is_slug(value: str) -> bool:
    return bool(NAME_PATTERN.fullmatch(value))


def compact_slug(value: str) -> str:
    """Strip underscores so cheap padding cannot dodge the denylist."""
    return value.replace("_", "")


def catalog_id_error(value: str) -> str | None:
    """Why `value` is not allowed as a recipe/set id, or None if it is."""
    if not is_slug(value):
        return "must be a lowercase slug (a-z, 0-9, _)"
    key = compact_slug(value)
    if len(key) < 2 or key.isdigit():
        return "must be at least two characters (not digits-only)"
    if key in BLOCKED_SLUGS:
        return "is reserved or blocked"
    return None


def is_catalog_id(value: str) -> bool:
    return catalog_id_error(value) is None


def part_name_error(value: str) -> str | None:
    """Why `value` is not allowed as a part name or tag, or None if it is."""
    if not is_slug(value):
        return "must be a lowercase slug (a-z, 0-9, _)"
    if compact_slug(value) in BLOCKED_SLUGS:
        return "is reserved or blocked"
    return None


def parent_name(recipe_id: str) -> str:
    return f"lodsmith.{recipe_id}"


def part_object_name(recipe_id: str, part_name: str) -> str:
    return f"{recipe_id}.{part_name}"


def recipe_id_from_parent(name: str) -> str | None:
    prefix = "lodsmith."
    if not name.startswith(prefix):
        return None
    recipe_id = name[len(prefix) :]
    if not is_catalog_id(recipe_id):
        return None
    return recipe_id
