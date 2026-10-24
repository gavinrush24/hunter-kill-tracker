from stats import diamond_rate_text


def test_no_diamonds_yet_shows_none_yet():
    assert diamond_rate_text(120, 0) == "None yet"


def test_formats_rate_as_kills_per_diamond():
    assert diamond_rate_text(300, 6) == "1 every 50.00"


def test_rounds_to_two_decimal_places():
    assert diamond_rate_text(100, 3) == "1 every 33.33"