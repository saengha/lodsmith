"""Compile a recipe into a bpy-free scene graph."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .naming import parent_name, part_object_name
from .recipe_loader import CUBE_TRIS, Recipe


@dataclass(frozen=True)
class CompiledPart:
    object_name: str
    part_name: str
    primitive: str
    size: tuple[float, float, float]
    location: tuple[float, float, float]
    rotation_deg: tuple[float, float, float]
    color: str | None
    estimated_tris: int


@dataclass(frozen=True)
class CompiledProp:
    recipe_id: str
    recipe_name: str
    parent_name: str
    description: str
    tags: tuple[str, ...]
    parts: tuple[CompiledPart, ...]
    target_tris: int
    estimated_tris: int

    @property
    def poly_ok(self) -> bool:
        return self.estimated_tris == self.target_tris

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["poly_ok"] = self.poly_ok
        return data


def estimated_tris_for_part(primitive: str) -> int:
    if primitive == "cube":
        return CUBE_TRIS
    return 0


def compile_recipe(recipe: Recipe) -> CompiledProp:
    parts = tuple(
        CompiledPart(
            object_name=part_object_name(recipe.id, part.name),
            part_name=part.name,
            primitive=part.primitive,
            size=part.size,
            location=part.location,
            rotation_deg=part.rotation_deg,
            color=part.color,
            estimated_tris=estimated_tris_for_part(part.primitive),
        )
        for part in recipe.parts
    )
    estimated = sum(part.estimated_tris for part in parts)
    return CompiledProp(
        recipe_id=recipe.id,
        recipe_name=recipe.name,
        parent_name=parent_name(recipe.id),
        description=recipe.description,
        tags=recipe.tags,
        parts=parts,
        target_tris=recipe.target_tris,
        estimated_tris=estimated,
    )
