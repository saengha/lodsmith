from addon.geometry import UNIT_CUBE_FACES, UNIT_CUBE_VERTS, cube_vertices_local


def test_unit_cube_topology():
    assert len(UNIT_CUBE_VERTS) == 8
    assert len(UNIT_CUBE_FACES) == 6
    for face in UNIT_CUBE_FACES:
        assert len(face) == 4
        assert len(set(face)) == 4


def test_identity_keeps_unit_verts():
    verts = cube_vertices_local((1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    assert verts == UNIT_CUBE_VERTS


def test_scale_stretches_axes():
    verts = cube_vertices_local((2.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    xs = {round(vert[0], 6) for vert in verts}
    assert xs == {-1.0, 1.0}


def test_z_rotation_90_swaps_xy():
    verts = cube_vertices_local((1.0, 1.0, 1.0), (0.0, 0.0, 90.0))
    # (0.5, -0.5, -0.5) -> (0.5, 0.5, -0.5)
    mapped = {(round(x, 6), round(y, 6), round(z, 6)) for x, y, z in verts}
    assert (0.5, 0.5, -0.5) in mapped
    assert (-0.5, 0.5, -0.5) in mapped
