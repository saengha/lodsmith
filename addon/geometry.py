"""Cube geometry used by the Blender builder. No bpy."""

from __future__ import annotations

from math import cos, radians, sin

# Unit cube centered at origin. Matches bpy.ops.mesh.primitive_cube_add(size=1).
UNIT_CUBE_VERTS: tuple[tuple[float, float, float], ...] = (
    (-0.5, -0.5, -0.5),
    (-0.5, -0.5, 0.5),
    (-0.5, 0.5, -0.5),
    (-0.5, 0.5, 0.5),
    (0.5, -0.5, -0.5),
    (0.5, -0.5, 0.5),
    (0.5, 0.5, -0.5),
    (0.5, 0.5, 0.5),
)

UNIT_CUBE_FACES: tuple[tuple[int, int, int, int], ...] = (
    (0, 1, 3, 2),
    (4, 6, 7, 5),
    (0, 4, 5, 1),
    (2, 3, 7, 6),
    (0, 2, 6, 4),
    (1, 5, 7, 3),
)

Vec3 = tuple[float, float, float]
Mat3 = tuple[Vec3, Vec3, Vec3]


def _matmul3(matrix: Mat3, vec: Vec3) -> Vec3:
    return (
        matrix[0][0] * vec[0] + matrix[0][1] * vec[1] + matrix[0][2] * vec[2],
        matrix[1][0] * vec[0] + matrix[1][1] * vec[1] + matrix[1][2] * vec[2],
        matrix[2][0] * vec[0] + matrix[2][1] * vec[1] + matrix[2][2] * vec[2],
    )


def _mat_mul(left: Mat3, right: Mat3) -> Mat3:
    right_cols = tuple(
        (right[0][column], right[1][column], right[2][column]) for column in range(3)
    )
    out_cols = tuple(_matmul3(left, column) for column in right_cols)
    return (
        (out_cols[0][0], out_cols[1][0], out_cols[2][0]),
        (out_cols[0][1], out_cols[1][1], out_cols[2][1]),
        (out_cols[0][2], out_cols[1][2], out_cols[2][2]),
    )


def euler_xyz_matrix(rx: float, ry: float, rz: float) -> Mat3:
    """Blender XYZ Euler: v' = Rz @ Ry @ Rx @ v."""
    cx, sx = cos(rx), sin(rx)
    cy, sy = cos(ry), sin(ry)
    cz, sz = cos(rz), sin(rz)
    rx_m: Mat3 = ((1.0, 0.0, 0.0), (0.0, cx, -sx), (0.0, sx, cx))
    ry_m: Mat3 = ((cy, 0.0, sy), (0.0, 1.0, 0.0), (-sy, 0.0, cy))
    rz_m: Mat3 = ((cz, -sz, 0.0), (sz, cz, 0.0), (0.0, 0.0, 1.0))
    return _mat_mul(rz_m, _mat_mul(ry_m, rx_m))


def cube_vertices_local(
    size: tuple[float, float, float],
    rotation_deg: tuple[float, float, float],
) -> tuple[Vec3, ...]:
    """Scale then rotate a unit cube. Object origin stays at the part center."""
    rotation = euler_xyz_matrix(
        radians(rotation_deg[0]),
        radians(rotation_deg[1]),
        radians(rotation_deg[2]),
    )
    sx, sy, sz = size
    verts = []
    for vx, vy, vz in UNIT_CUBE_VERTS:
        scaled = (vx * sx, vy * sy, vz * sz)
        verts.append(_matmul3(rotation, scaled))
    return tuple(verts)
