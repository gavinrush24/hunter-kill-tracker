import pytest

import storage


@pytest.fixture(autouse=True)
def data_file(tmp_path, monkeypatch):
    # Point storage at a temporary file so the real data/tracker.json
    # is never touched. pytest deletes tmp_path after the run.
    path = tmp_path / "tracker.json"
    monkeypatch.setattr(storage, "DATA_FILE", path)
    monkeypatch.setattr(storage, "_session", {})
    return path


def test_entry_is_all_zeros_when_nothing_is_saved():
    assert storage.get_entry("Layton Lake District", "Moose") == {
        "kills": 0,
        "diamonds": 0,
        "pinned": False,
    }


def test_add_kill_increases_and_saves_the_count():
    assert storage.add_kill("Layton Lake District", "Moose") == 1
    assert storage.add_kill("Layton Lake District", "Moose") == 2
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 2


def test_remove_kill_decreases_the_count():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_kill("Layton Lake District", "Moose")
    assert storage.remove_kill("Layton Lake District", "Moose") == 1


def test_kills_never_go_below_zero():
    assert storage.remove_kill("Layton Lake District", "Moose") == 0
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 0


def test_add_and_remove_diamond():
    storage.add_diamond("Layton Lake District", "Moose")
    storage.add_diamond("Layton Lake District", "Moose")
    assert storage.remove_diamond("Layton Lake District", "Moose") == 1


def test_diamonds_never_go_below_zero():
    assert storage.remove_diamond("Layton Lake District", "Moose") == 0


def test_kills_and_diamonds_are_tracked_separately():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_diamond("Layton Lake District", "Moose")
    entry = storage.get_entry("Layton Lake District", "Moose")
    assert entry["kills"] == 1
    assert entry["diamonds"] == 1


def test_same_animal_on_two_maps_has_separate_counts():
    storage.add_kill("Hirschfelden Hunting Reserve", "Red Deer")
    storage.add_kill("Hirschfelden Hunting Reserve", "Red Deer")
    storage.add_kill("Parque Fernando", "Red Deer")
    assert storage.get_entry("Hirschfelden Hunting Reserve", "Red Deer")["kills"] == 2
    assert storage.get_entry("Parque Fernando", "Red Deer")["kills"] == 1


def test_unknown_animal_raises_and_saves_nothing(data_file):
    with pytest.raises(ValueError):
        storage.add_kill("Hirschfelden Hunting Reserve", "Lion")
    assert not data_file.exists()


def test_toggle_pin_switches_on_and_off():
    assert storage.toggle_pin("Layton Lake District", "Moose") is True
    assert storage.get_entry("Layton Lake District", "Moose")["pinned"] is True
    assert storage.toggle_pin("Layton Lake District", "Moose") is False
    assert storage.get_entry("Layton Lake District", "Moose")["pinned"] is False

def test_reset_sets_kills_and_diamonds_to_zero_and_keeps_pin():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_diamond("Layton Lake District", "Moose")
    storage.toggle_pin("Layton Lake District", "Moose")
    storage.reset_animal("Layton Lake District", "Moose")
    assert storage.get_entry("Layton Lake District", "Moose") == {
        "kills": 0,
        "diamonds": 0,
        "pinned": True,
    }

def test_session_starts_at_zero():
    assert storage.get_session("Layton Lake District", "Moose") == {
        "kills": 0,
        "diamonds": 0,
    }


def test_session_counts_kills_and_diamonds_logged():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_diamond("Layton Lake District", "Moose")
    assert storage.get_session("Layton Lake District", "Moose") == {
        "kills": 2,
        "diamonds": 1,
    }


def test_removing_a_kill_lowers_the_session_count():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_kill("Layton Lake District", "Moose")
    storage.remove_kill("Layton Lake District", "Moose")
    assert storage.get_session("Layton Lake District", "Moose")["kills"] == 1


def test_session_never_goes_below_zero_for_kills_from_before_the_session():
    storage.add_kill("Layton Lake District", "Moose")
    storage.add_kill("Layton Lake District", "Moose")
    storage._session.clear()  # pretend the app was just reopened
    storage.remove_kill("Layton Lake District", "Moose")
    assert storage.get_session("Layton Lake District", "Moose")["kills"] == 0
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 1


def test_session_is_tracked_per_animal():
    storage.add_kill("Layton Lake District", "Moose")
    assert storage.get_session("Layton Lake District", "Coyote")["kills"] == 0


def test_reset_clears_the_session_too():
    storage.add_kill("Layton Lake District", "Moose")
    storage.reset_animal("Layton Lake District", "Moose")
    assert storage.get_session("Layton Lake District", "Moose") == {
        "kills": 0,
        "diamonds": 0,
    }