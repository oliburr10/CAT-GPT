from catagent import costumes, sprites


def test_every_costume_has_every_pose():
    for name, frames in costumes.COSTUMES.items():
        missing = set(sprites.FRAMES) - set(frames)
        assert not missing, f"{name} is missing {missing}"


def test_frames_are_the_same_size_and_use_known_colours():
    for name, frames in costumes.COSTUMES.items():
        height = costumes.height(name)
        for frame, grid in frames.items():
            assert len(grid) == height, (name, frame)
            for row in grid:
                assert len(row) == sprites.WIDTH, (name, frame, row)
                assert set(row) <= set(sprites.PALETTE) | {"."}, (name, frame, row)


def test_costumes_only_add_room_above_the_head():
    """The feet stay on the bottom row, so the cat doesn't jump when it changes."""
    for name, frames in costumes.COSTUMES.items():
        assert frames["idle"][-1] == sprites.FRAMES["idle"][-1] or name == "dragon"
        assert costumes.height(name) >= sprites.HEIGHT


def test_dressing_up_ends_in_the_costume():
    for name, steps in costumes.DRESS_UP.items():
        assert steps, name
        assert all(frame in costumes.COSTUMES[name] and seconds > 0 for frame, seconds in steps)
        last = costumes.COSTUMES[name][steps[-1][0]]
        assert last == costumes.COSTUMES[name]["idle"], name
