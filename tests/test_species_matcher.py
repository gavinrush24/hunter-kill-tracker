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


# --- Cases found in the code review ------------------------------------------

REVONTULI = get_species_for_map("Revontuli Coast")  # has Moose and three kinds of goose
HIRSCHFELDEN = get_species_for_map("Hirschfelden Hunting Reserve")  # Red Deer and Roe Deer


def test_goose_is_never_read_as_moose():
    for text in ["Goose", "Loose", "Mouse", "Greylaq\nGoose", "Snovv\nGoose", "Tundra Bcan\nGoose\nMale\n2.1 kg"]:
        assert match_species(text, REVONTULI) != "Moose", text


def test_a_name_wrapped_onto_two_lines_is_matched():
    assert match_species("Tundra Bcan\nGoose\nMale\n2.1 kg", REVONTULI) == "Tundra Bean Goose"
    assert match_species("Greylaq\nGoose", REVONTULI) == "Greylag Goose"


def test_text_equally_close_to_two_animals_gives_none():
    assert match_species("Rod Deer", HIRSCHFELDEN) is None


def test_clear_misreads_of_similar_names_still_match():
    assert match_species("Red Deer", HIRSCHFELDEN) == "Red Deer"
    assert match_species("Roe Deer", HIRSCHFELDEN) == "Roe Deer"
    assert match_species("Ring-Neckcd Pheasant", HIRSCHFELDEN) == "Ring-Necked Pheasant"


def test_short_names_need_a_near_exact_match():
    tar_map = get_species_for_map("Sundarpatan")
    assert match_species("Tar", tar_map) is None
    assert match_species("Tahr", tar_map) == "Tahr"
