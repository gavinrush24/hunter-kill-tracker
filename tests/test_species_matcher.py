from maps import get_species_for_map
from species_matcher import clean_text, match_species

LAYTON = get_species_for_map("Layton Lake District")


def test_exact_name():
    assert match_species("Moose", LAYTON) == "Moose"


def test_case_does_not_matter():
    assert match_species("BLACK BEAR", LAYTON) == "Black Bear"


def test_hyphens_and_spaces_are_treated_the_same():
    assert match_species("white tailed jackrabbit", LAYTON) == "White-tailed Jackrabbit"


def test_digits_misread_as_letters():
    assert match_species("Whitetai1 Deer", LAYTON) == "Whitetail Deer"
    assert match_species("Mo0se", LAYTON) == "Moose"


def test_small_typo():
    assert match_species("Roosvelt Elk", LAYTON) == "Roosevelt Elk"


def test_name_among_other_harvest_screen_text():
    text = "HARVEST\nWhitetail Deer\nMale  84.2 kg\nTrophy rating 160.4\nScore: 1,200"
    assert match_species(text, LAYTON) == "Whitetail Deer"


def test_longer_name_wins_over_a_name_inside_it():
    species = ["Deer", "Whitetail Deer"]
    assert match_species("Whitetail Deer", species) == "Whitetail Deer"


def test_species_from_another_map_is_not_matched():
    assert match_species("Eurasian Lynx", LAYTON) is None


def test_garbage_and_empty_text_give_none():
    assert match_species("", LAYTON) is None
    assert match_species("   \n  ", LAYTON) is None
    assert match_species("@#%$ 1234 ~~~", LAYTON) is None
    assert match_species("Settings  Map  Inventory", LAYTON) is None


def test_clean_text_keeps_lines_and_strips_symbols():
    assert clean_text("  Black-Bear!! \n\n 84.2 kg ") == "black bear\nb kg"
