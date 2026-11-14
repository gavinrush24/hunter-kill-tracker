from harvest_dedupe import HarvestDeduper


def run(frames, **settings):
    """Feed a list of frames (species or None) to a new deduper; return what was logged."""
    deduper = HarvestDeduper(**settings)
    return [logged for logged in map(deduper.update, frames) if logged is not None]


def test_frames_with_no_match_never_log():
    assert run([None] * 10) == []


def test_a_harvest_screen_held_for_many_frames_logs_once():
    assert run(["Moose"] * 40) == ["Moose"]


def test_a_single_frame_is_not_enough_to_log():
    assert run([None, "Moose", None, None]) == []


def test_one_misread_frame_does_not_log_the_wrong_animal():
    assert run(["Roe Deer", "Red Deer", "Red Deer", "Red Deer"]) == ["Red Deer"]


def test_a_one_frame_ocr_dropout_does_not_count_the_harvest_twice():
    # Screen up for a long time with a dropout well into it.
    frames = ["Moose"] * 25 + [None] + ["Moose"] * 10
    assert run(frames) == ["Moose"]


def test_a_short_gap_does_not_count_the_harvest_twice():
    frames = ["Moose"] * 5 + [None] * 3 + ["Moose"] * 5
    assert run(frames) == ["Moose"]


def test_two_harvests_close_together_are_both_logged():
    frames = ["Mallard Duck"] * 4 + [None] * 4 + ["Mallard Duck"] * 4
    assert run(frames) == ["Mallard Duck", "Mallard Duck"]


def test_two_different_animals_are_both_logged():
    frames = ["Moose"] * 4 + [None] * 4 + ["Black Bear"] * 4
    assert run(frames) == ["Moose", "Black Bear"]


def test_frame_counts_can_be_changed():
    frames = ["Moose", None, "Moose"]
    assert run(frames, confirm_frames=1, clear_frames=1) == ["Moose", "Moose"]
