from kill_events import KillEvent, resolve_target

MAP = "Layton Lake District"


def test_hotkey_event_uses_the_focused_animal():
    event = KillEvent(source="hotkey")
    assert resolve_target(event, MAP, "Moose") == (MAP, "Moose")


def test_hotkey_event_is_ignored_when_no_animal_is_focused():
    event = KillEvent(source="hotkey")
    assert resolve_target(event, MAP, None) is None


def test_event_with_a_species_uses_that_species():
    event = KillEvent(source="ocr", species="Black Bear")
    assert resolve_target(event, MAP, "Moose") == (MAP, "Black Bear")


def test_event_with_a_species_works_without_a_focused_animal():
    event = KillEvent(source="ocr", species="Black Bear")
    assert resolve_target(event, MAP, None) == (MAP, "Black Bear")


def test_nothing_is_logged_without_a_selected_map():
    event = KillEvent(source="ocr", species="Black Bear")
    assert resolve_target(event, None, "Moose") is None
