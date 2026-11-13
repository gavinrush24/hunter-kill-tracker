from harvest_dedupe import HarvestDeduper


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make_deduper():
    clock = FakeClock()
    return HarvestDeduper(cooldown=10.0, clock=clock), clock


def test_frames_with_no_match_never_fire():
    deduper, clock = make_deduper()
    for _ in range(5):
        assert deduper.update(None) is None
        clock.now += 0.5


def test_a_harvest_screen_held_for_many_frames_fires_once():
    deduper, clock = make_deduper()
    results = []
    for _ in range(20):
        results.append(deduper.update("Moose"))
        clock.now += 0.5
    assert results.count("Moose") == 1
    assert results[0] == "Moose"


def test_fires_again_for_the_next_harvest_after_the_cooldown():
    deduper, clock = make_deduper()
    assert deduper.update("Moose") == "Moose"
    clock.now = 3.0
    assert deduper.update(None) is None
    clock.now = 15.0
    assert deduper.update("Moose") == "Moose"


def test_does_not_fire_again_inside_the_cooldown():
    deduper, clock = make_deduper()
    assert deduper.update("Moose") == "Moose"
    clock.now = 2.0
    deduper.update(None)  # OCR flickered for one frame
    clock.now = 2.5
    assert deduper.update("Moose") is None


def test_a_different_species_after_the_cooldown_fires_without_a_gap():
    deduper, clock = make_deduper()
    assert deduper.update("Moose") == "Moose"
    clock.now = 12.0
    assert deduper.update("Black Bear") == "Black Bear"
