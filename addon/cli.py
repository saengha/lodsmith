"""Command line for listing, validating, compiling, and planning recipes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compile import compile_recipe
from .planner import plan
from .recipe_loader import RecipeError, load_all, load_recipe, recipes_dir
from .set_loader import (
    estimated_set_tris,
    load_all_sets,
    load_set,
    validate_sets,
)
from .scaffold import parse_recipe_list, write_recipe, write_set


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lodsmith",
        description="Validate and compile lodsmith recipes without Blender.",
    )
    parser.add_argument(
        "--recipes",
        type=Path,
        default=None,
        help="Recipes directory (defaults to repo recipes/)",
    )
    parser.add_argument(
        "--sets",
        type=Path,
        default=None,
        help="Sets directory (defaults to sibling sets/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Print shipped recipe ids")
    sub.add_parser("sets", help="Print shipped set ids")
    sub.add_parser("validate", help="Load every recipe and set")

    compile_parser = sub.add_parser("compile", help="Print a compiled scene graph as JSON")
    compile_parser.add_argument("recipe_id")

    compose_parser = sub.add_parser("compose", help="Print set placements as JSON")
    compose_parser.add_argument("set_id")

    plan_parser = sub.add_parser("plan", help="Rank recipes and sets for a local prompt")
    plan_parser.add_argument("prompt")
    plan_parser.add_argument("--limit", type=int, default=8)

    new_parser = sub.add_parser("new", help="Write a valid recipe or set stub")
    new_sub = new_parser.add_subparsers(dest="new_kind", required=True)
    new_recipe = new_sub.add_parser("recipe", help="Write recipes/<id>.json")
    new_recipe.add_argument("id")
    new_recipe.add_argument("--name", default="")
    new_set = new_sub.add_parser("set", help="Write sets/<id>.json")
    new_set.add_argument("id")
    new_set.add_argument(
        "recipe_ids",
        nargs="*",
        metavar="RECIPE",
        help="Existing recipe ids (default: crate)",
    )
    new_set.add_argument("--name", default="")
    new_set.add_argument(
        "--use",
        default="",
        help="Comma-separated recipe ids (alternative to positional ids)",
    )

    args = parser.parse_args(argv)
    folder = args.recipes if args.recipes is not None else recipes_dir()
    set_folder = args.sets if args.sets is not None else folder.parent / "sets"

    try:
        if args.command == "list":
            return _cmd_list(folder)
        if args.command == "sets":
            return _cmd_sets(set_folder)
        if args.command == "validate":
            return _cmd_validate(folder, set_folder)
        if args.command == "compile":
            return _cmd_compile(folder, args.recipe_id)
        if args.command == "compose":
            return _cmd_compose(folder, set_folder, args.set_id)
        if args.command == "plan":
            return _cmd_plan(folder, set_folder, args.prompt, args.limit)
        if args.command == "new":
            return _cmd_new(args, folder, set_folder)
    except RecipeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _cmd_list(folder: Path) -> int:
    for recipe in load_all(folder):
        print(f"{recipe.id}\t{recipe.name}\t{recipe.target_tris}")
    return 0


def _cmd_sets(folder: Path) -> int:
    if not folder.is_dir():
        print("error: sets directory missing", file=sys.stderr)
        return 1
    for prop_set in load_all_sets(folder):
        print(f"{prop_set.id}\t{prop_set.name}\t{len(prop_set.items)}")
    return 0


def _cmd_validate(folder: Path, set_folder: Path) -> int:
    recipes = load_all(folder)
    failed = 0
    for recipe in recipes:
        compiled = compile_recipe(recipe)
        status = "ok" if compiled.poly_ok else "FAIL"
        if not compiled.poly_ok:
            failed += 1
        print(
            f"{status}\t{recipe.id}\t{len(recipe.parts)} parts\t"
            f"{compiled.estimated_tris}/{recipe.target_tris} tris"
        )
    if set_folder.is_dir():
        catalog = load_all_sets(set_folder)
        validate_sets(catalog, recipes)
        for prop_set in catalog:
            tris = estimated_set_tris(prop_set, recipes)
            print(f"ok\tset:{prop_set.id}\t{len(prop_set.items)} props\t{tris} tris")
        print(f"{len(recipes) - failed} recipes ok, {len(catalog)} sets ok, {failed} failed")
    else:
        print(f"{len(recipes) - failed} ok, {failed} failed")
    return 1 if failed else 0


def _cmd_compile(folder: Path, recipe_id: str) -> int:
    path = folder / f"{recipe_id}.json"
    if not path.is_file():
        print(f"error: missing recipe {path}", file=sys.stderr)
        return 1
    compiled = compile_recipe(load_recipe(path))
    print(json.dumps(compiled.to_dict(), indent=2))
    return 0


def _cmd_compose(folder: Path, set_folder: Path, set_id: str) -> int:
    path = set_folder / f"{set_id}.json"
    if not path.is_file():
        print(f"error: missing set {path}", file=sys.stderr)
        return 1
    recipes = load_all(folder)
    prop_set = load_set(path)
    validate_sets((prop_set,), recipes)
    payload = {
        "id": prop_set.id,
        "name": prop_set.name,
        "estimated_tris": estimated_set_tris(prop_set, recipes),
        "items": [
            {
                "recipe": item.recipe_id,
                "location": list(item.location),
                "rotation_deg": list(item.rotation_deg),
                "scale": item.scale,
            }
            for item in prop_set.items
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_plan(folder: Path, set_folder: Path, prompt: str, limit: int) -> int:
    recipes = load_all(folder)
    sets = load_all_sets(set_folder) if set_folder.is_dir() else ()
    if sets:
        validate_sets(sets, recipes)
    hits = plan(prompt, recipes, sets, limit=limit)
    if not hits:
        print("no matching recipe")
        return 1
    for hit in hits:
        print(
            f"{hit.score}\t{hit.kind}\t{hit.id}\t{hit.name}\t{','.join(hit.matched)}"
        )
    return 0


def _cmd_new(args, folder: Path, set_folder: Path) -> int:
    if args.new_kind == "recipe":
        path = write_recipe(folder, args.id, name=args.name)
        print(f"wrote {path}")
        print("next: edit parts, then python -m addon validate")
        return 0
    if args.new_kind == "set":
        if args.use.strip():
            recipe_ids = parse_recipe_list(args.use)
        elif args.recipe_ids:
            recipe_ids = parse_recipe_list(",".join(args.recipe_ids))
        else:
            recipe_ids = ("crate",)
        path = write_set(
            set_folder,
            args.id,
            recipe_ids,
            recipes_folder=folder,
            name=args.name,
        )
        print(f"wrote {path}")
        print("next: edit locations, then python -m addon compose", args.id)
        return 0
    print("error: use new recipe or new set", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
