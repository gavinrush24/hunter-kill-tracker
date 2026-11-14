import pytest

import storage


@pytest.fixture(autouse=True)
def data_file(tmp_path, monkeypatch):
    # Point storage at a temporary file so the real data/tracker.json
    # is never touched. pytest deletes tmp_path after the run.
    path = tmp_path / "tracker.json"
    monkeypatch.setattr(storage, "DATA_FILE", path)
    monkeypatch.setattr(storage, "_session", {})
    monkeypatch.setattr(storage, "_recovery_message", None)
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

# --- Damaged or unreadable files -------------------------------------------


@pytest.mark.parametrize(
    "contents",
    [b"", b'{"Layt', b"not json at all", b"[]", b"null", b'"text"', b"\xff\xfe\x81"],
)
def test_damaged_file_is_kept_aside_and_the_app_starts_empty(data_file, contents):
    data_file.write_bytes(contents)
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 0
    backups = list(data_file.parent.glob("tracker.corrupt-*.json"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == contents
    assert not data_file.exists()
    assert storage.pop_recovery_message() is not None
    assert storage.pop_recovery_message() is None  # only reported once


def test_counting_works_again_after_a_damaged_file(data_file):
    data_file.write_bytes(b'{"Layt')
    assert storage.add_kill("Layton Lake District", "Moose") == 1
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 1


def test_a_file_that_cant_be_read_raises_instead_of_being_wiped(data_file):
    # A folder where the file should be: reading it fails like a locked file would.
    data_file.mkdir()
    with pytest.raises(OSError):
        storage.load_data()
    assert data_file.is_dir()


def test_no_recovery_message_for_a_healthy_file():
    storage.add_kill("Layton Lake District", "Moose")
    storage.load_data()
    assert storage.pop_recovery_message() is None


# --- Safe saving ------------------------------------------------------------


def test_a_save_cut_off_halfway_leaves_the_old_file_intact(data_file, monkeypatch):
    storage.add_kill("Layton Lake District", "Moose")
    before = data_file.read_bytes()

    def crash_partway(data, f, **kwargs):
        f.write('{"Layt')
        raise KeyboardInterrupt("power cut")

    with monkeypatch.context() as patch:
        patch.setattr(storage.json, "dump", crash_partway)
        with pytest.raises(KeyboardInterrupt):
            storage.add_kill("Layton Lake District", "Moose")
    assert data_file.read_bytes() == before
    assert storage.get_entry("Layton Lake District", "Moose")["kills"] == 1


def test_non_ascii_names_survive_a_save_and_load(data_file):
    data_file.write_text('{"Tòrr nan Sithean": {"Red Deer": {"kills": 3}}}', encoding="utf-8")
    assert storage.get_entry("Tòrr nan Sithean", "Red Deer")["kills"] == 3
    storage.save_data(storage.load_data())
    assert storage.get_entry("Tòrr nan Sithean", "Red Deer")["kills"] == 3
