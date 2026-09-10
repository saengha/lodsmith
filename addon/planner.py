"""Map a local prompt onto shipped recipes and sets. No network, no LLM."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .prompting import expand_prompt
from .recipe_loader import Recipe
from .set_loader import PropSet

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "for",
        "to",
        "with",
        "on",
        "in",
        "at",
        "one",
        "is",
        "it",
    }
)

_SYNONYMS: dict[str, frozenset[str]] = {
    "crate": frozenset({"box", "chest", "container", "shipping", "lid", "tris", "bpy", "exec"}),
    "crate_open": frozenset({"open", "empty", "bin"}),
    "crate_battens": frozenset({"batten", "reinforced", "strip"}),
    "crate_lid_ajar": frozenset({"ajar", "open", "tilted", "lid"}),
    "barrel": frozenset({"keg", "cask", "drum", "tavern"}),
    "barrel_open": frozenset({"keg", "open", "empty"}),
    "pallet": frozenset({"skid", "shipping", "warehouse"}),
    "bench": frozenset({"seat", "park", "plank"}),
    "stool": frozenset({"seat", "bar", "tavern"}),
    "table": frozenset({"desk", "tavern", "plank"}),
    "lantern": frozenset({"lamp", "light", "torch", "cage"}),
    "fence_post": frozenset({"fence", "rail", "post", "yard"}),
    "signpost": frozenset({"sign", "board", "post", "road"}),
    "chest": frozenset({"loot", "treasure", "box", "lock"}),
    "mug": frozenset({"cup", "drink", "tavern"}),
    "candle": frozenset({"light", "wax", "flame", "tavern"}),
    "sack": frozenset({"bag", "grain", "warehouse"}),
    "shelf": frozenset({"wall", "board", "tavern"}),
    "door": frozenset({"gate", "entrance", "frame", "architecture"}),
    "torch": frozenset({"flame", "sconce", "wall", "light"}),
    "bucket": frozenset({"pail", "water", "camp"}),
    "window": frozenset({"pane", "sill", "glass", "shutter", "architecture"}),
    "ladder": frozenset({"rung", "climb", "rail"}),
    "cart": frozenset({"wagon", "handcart", "wheels", "cargo"}),
    "well": frozenset({"water", "village", "stone", "curb"}),
    "bed": frozenset({"mattress", "sleep", "pillow", "headboard"}),
    "chair": frozenset({"seat", "backrest", "sit", "furniture"}),
    "anvil": frozenset({"forge", "horn", "smith", "iron"}),
    "firepit": frozenset({"campfire", "coals", "flame", "ring"}),
    "tent": frozenset({"canvas", "shelter", "camp", "flap"}),
    "bottle": frozenset({"cork", "glass", "flask", "drink"}),
    "book": frozenset({"tome", "pages", "spine", "lore"}),
    "hammer": frozenset({"mallet", "peen", "smith", "tool"}),
    "cauldron": frozenset({"pot", "stew", "cook", "kettle"}),
}

_SET_SYNONYMS: dict[str, frozenset[str]] = {
    "tavern": frozenset({"pub", "bar", "alehouse", "taproom"}),
    "warehouse": frozenset({"depot", "storage", "docks", "shipping"}),
    "yard": frozenset({"fence", "garden", "outdoor", "road"}),
    "camp": frozenset({"campsite", "trail", "night", "fire"}),
    "market": frozenset({"stall", "shop", "vendor", "bazaar"}),
    "entrance": frozenset({"door", "gate", "entry", "architecture"}),
    "crate_stack": frozenset({"stack", "pile", "shipping", "warehouse"}),
    "wellside": frozenset({"village", "well", "water", "yard"}),
    "facade": frozenset({"wall", "windows", "frontage", "architecture"}),
    "smithy": frozenset({"forge", "blacksmith", "anvil", "workshop"}),
    "inn": frozenset({"lodging", "guest", "room", "bedchamber"}),
}


@dataclass(frozen=True)
class PlanHit:
    kind: str
    id: str
    name: str
    score: int
    matched: tuple[str, ...]

    @property
    def recipe_id(self) -> str:
        return self.id


_STEM = {
    "wooden": "wood",
    "boxes": "box",
    "barrels": "barrel",
    "crates": "crate",
    "doors": "door",
    "torches": "torch",
    "windows": "window",
    "carts": "cart",
    "wells": "well",
    "ladders": "ladder",
    "wagons": "wagon",
    "beds": "bed",
    "chairs": "chair",
    "anvils": "anvil",
    "tents": "tent",
    "bottles": "bottle",
    "books": "book",
    "hammers": "hammer",
    "cauldrons": "cauldron",
}


def tokenize(text: str) -> frozenset[str]:
    found = [
        token
        for token in _TOKEN.findall(expand_prompt(text).lower())
        if token not in _STOP and len(token) > 1
    ]
    extra = [_STEM[token] for token in found if token in _STEM]
    return frozenset(found + extra)


def _tokens_of(*words: object) -> set[str]:
    tokens: set[str] = set()
    for word in words:
        tokens.update(tokenize(str(word)))
    return tokens


def _recipe_haystack(recipe: Recipe) -> frozenset[str]:
    return frozenset(
        _tokens_of(
            recipe.id,
            recipe.id.replace("_", " "),
            recipe.name,
            recipe.description,
            *recipe.tags,
            *(part.name for part in recipe.parts),
            *(_SYNONYMS.get(recipe.id, ())),
        )
    )


def _set_haystack(prop_set: PropSet) -> frozenset[str]:
    return frozenset(
        _tokens_of(
            prop_set.id,
            prop_set.name,
            prop_set.description,
            *prop_set.tags,
            *prop_set.recipe_ids,
            *(_SET_SYNONYMS.get(prop_set.id, ())),
        )
    )


def _score(tokens: frozenset[str], hay: frozenset[str], item_id: str, tags: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    overlap = tokens & hay
    score = len(overlap)
    slug = item_id.replace(" ", "_")
    if slug in tokens or item_id in tokens:
        score += 4
    for tag in tags:
        if tag in tokens:
            score += 2
    return score, tuple(sorted(overlap))


def plan(
    prompt: str,
    recipes: tuple[Recipe, ...],
    sets: tuple[PropSet, ...] = (),
    *,
    limit: int = 8,
) -> tuple[PlanHit, ...]:
    tokens = tokenize(prompt)
    if not tokens:
        return ()
    hits: list[PlanHit] = []
    for recipe in recipes:
        score, matched = _score(tokens, _recipe_haystack(recipe), recipe.id, recipe.tags)
        if score <= 0:
            continue
        hits.append(
            PlanHit(
                kind="recipe",
                id=recipe.id,
                name=recipe.name,
                score=score,
                matched=matched,
            )
        )
    for prop_set in sets:
        score, matched = _score(
            tokens, _set_haystack(prop_set), prop_set.id, prop_set.tags
        )
        if prop_set.id in tokens or any(tag in tokens for tag in prop_set.tags):
            score += 3
        if score <= 0:
            continue
        hits.append(
            PlanHit(
                kind="set",
                id=prop_set.id,
                name=prop_set.name,
                score=score,
                matched=matched,
            )
        )
    hits.sort(key=lambda hit: (-hit.score, hit.kind != "set", hit.id))
    return tuple(hits[:limit])
