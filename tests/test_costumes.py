import pytest

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


@pytest.mark.parametrize("text, costume", [
    ("Change costumes", "random"), ("change costume randomly", "random"), ("random costume", "random"),
    ("please change your costume!", "random"),
    ("change into dragon", "dragon"), ("Change into a Dragon", "dragon"), ("turn into a green dragon", "dragon"),
    ("put on the dragon costume", "dragon"),
    ("change into wizard", "wizard"), ("dress up as a wizard", "wizard"), ("wear the wizard hat", "wizard"),
    ("change back to normal", "ginger"), ("back to normal", "ginger"), ("change into ginger", "ginger"),
])
def test_costume_commands(text, costume):
    assert costumes.parse_request(text) == costume


@pytest.mark.parametrize("text", [
    "change into a unicorn", "fix the dragon class in game.py", "surprise me",
    "change the costume of the main character in my story to a dragon please because it is cooler",
])
def test_other_messages_go_to_the_agent(text):
    assert costumes.parse_request(text) is None


def test_random_never_picks_the_costume_already_on():
    for current in costumes.COSTUMES:
        assert all(costumes.pick("random", current) != current for _ in range(30))
    assert costumes.pick("wizard", "wizard") == "wizard"
