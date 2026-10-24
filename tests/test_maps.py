import pytest

from maps import MAPS, get_map_names, get_species_for_map, is_valid_species


def test_returns_maps_in_file_order():
    assert get_map_names()[0] == "Hirschfelden Hunting Reserve"


@pytest.mark.parametrize("map_name", get_map_names())
def test_every_map_has_animals(map_name):
    assert len(get_species_for_map(map_name)) > 0


@pytest.mark.parametrize("map_name", get_map_names())
def test_no_animal_is_listed_twice_on_one_map(map_name):
    species_list = MAPS[map_name]
    assert len(species_list) == len(set(species_list))


def test_returns_animals_for_a_map():
    assert "Whitetail Deer" in get_species_for_map("Layton Lake District")


def test_animal_on_its_map_is_valid():
    assert is_valid_species("Layton Lake District", "Moose")


def test_animal_from_another_map_is_not_valid():
    assert not is_valid_species("Hirschfelden Hunting Reserve", "Lion")


def test_unknown_map_is_not_valid():
    assert not is_valid_species("Nowhere", "Moose")