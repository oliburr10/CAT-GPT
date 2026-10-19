import json

import pytest

from catagent import clipboard
from catagent.clipboard import ClipboardError


def test_first_run_makes_a_project():
    assert clipboard.ensure_project() == clipboard.DEFAULT_PROJECT
    assert clipboard.projects() == [clipboard.DEFAULT_PROJECT]


def test_folders_and_clips_are_real_files(notes_dir):
    clipboard.make_project("Math 1")
    week = clipboard.make_folder("Math 1", "", "Week 1")
    questions = clipboard.make_folder("Math 1", week, "Questions")
    path = clipboard.save_clip("Math 1", questions, {"kind": "solution", "title": "$\\operatorname{Trace}(AB) = \\operatorname{Trace}(BA)$", "notes": {}})

    assert path == "Week 1/Questions/Trace(AB) = Trace(BA).json"
    saved = json.loads((notes_dir / "Math 1" / path).read_text())
    assert saved["kind"] == "solution" and saved["id"] and saved["created"]
    assert clipboard.tree("Math 1") == [{
        "type": "folder", "name": "Week 1", "path": "Week 1", "children": [{
            "type": "folder", "name": "Questions", "path": "Week 1/Questions", "children": [{
                "type": "clip", "name": saved["title"], "kind": "solution", "path": path, "created": saved["created"],
            }],
        }],
    }]


def test_folders_sort_naturally():
    clipboard.make_project("P")
    for name in ("Week 10", "Week 2", "Exams", "Week 1"):
        clipboard.make_folder("P", "", name)
    assert [f["name"] for f in clipboard.tree("P")] == ["Exams", "Week 1", "Week 2", "Week 10"]


def test_same_title_gets_a_new_name_but_same_clip_is_replaced():
    clipboard.make_project("P")
    first = clipboard.save_clip("P", "", {"kind": "idea", "title": "Plan", "id": "a"})
    again = clipboard.save_clip("P", "", {"kind": "idea", "title": "Plan", "id": "a", "text": "updated"})
    other = clipboard.save_clip("P", "", {"kind": "idea", "title": "Plan", "id": "b"})
    assert first == again == "Plan.json"
    assert other == "Plan 2.json"
    assert clipboard.read_clip("P", "Plan.json")["text"] == "updated"


def test_empty_id_gets_a_real_one():
    clipboard.make_project("P")
    path = clipboard.save_clip("P", "", {"kind": "note", "title": "x", "id": None, "created": None})
    clip = clipboard.read_clip("P", path)
    assert clip["id"] and clip["created"]


def test_move_and_delete():
    clipboard.make_project("P")
    clipboard.make_folder("P", "", "A")
    clipboard.make_folder("P", "", "B")
    path = clipboard.save_clip("P", "A", {"kind": "note", "title": "x"})
    moved = clipboard.move_clip("P", path, "B")
    assert moved == "B/x.json"
    assert clipboard.move_clip("P", moved, "B") == moved
    with pytest.raises(ClipboardError):
        clipboard.read_clip("P", path)
    clipboard.delete_clip("P", moved)
    assert [n["children"] for n in clipboard.tree("P")] == [[], []]


def test_folder_with_clips_is_not_deleted():
    clipboard.make_project("P")
    clipboard.make_folder("P", "", "A")
    clipboard.save_clip("P", "A", {"kind": "note", "title": "keep me"})
    with pytest.raises(ClipboardError, match="still has clips"):
        clipboard.delete_folder("P", "A")
    clipboard.make_folder("P", "", "Empty")
    clipboard.delete_folder("P", "Empty")


@pytest.mark.parametrize("bad", ["../outside", "A/../../outside", "/etc"])
def test_paths_cannot_leave_the_project(bad):
    clipboard.make_project("P")
    clipboard.make_folder("P", "", "A")
    with pytest.raises(ClipboardError):
        clipboard.make_folder("P", bad, "x")
    with pytest.raises(ClipboardError):
        clipboard.save_clip("P", bad, {"kind": "note", "title": "x"})


def test_names_are_cleaned_and_checked():
    assert clipboard.safe_name("  a/b:c  ") == "a-b-c"
    assert clipboard.safe_name("..hidden") == "hidden"
    with pytest.raises(ClipboardError):
        clipboard.safe_name("   ")
    clipboard.make_project("P")
    clipboard.make_folder("P", "", "Week 1")
    with pytest.raises(ClipboardError, match="already exists"):
        clipboard.make_folder("P", "", "Week 1")
    with pytest.raises(ClipboardError):
        clipboard.save_clip("P", "", {"kind": "poem", "title": "x"})


def test_broken_files_are_skipped(notes_dir):
    clipboard.make_project("P")
    (notes_dir / "P" / "junk.json").write_text("not json")
    (notes_dir / "P" / "other.json").write_text('{"some": "other app"}')
    (notes_dir / "P" / ".DS_Store").write_text("")
    assert clipboard.tree("P") == []


def test_current_project_is_shared_and_saved():
    clipboard.make_project("Math 1")
    clipboard.make_project("Physics")
    assert clipboard.current_project() == "Math 1"   # the first one, until you pick
    clipboard.set_current_project("Physics")
    assert clipboard.current_project() == "Physics"
    with pytest.raises(ClipboardError):
        clipboard.set_current_project("Nope")
