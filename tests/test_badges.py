import pytest

import badges


@pytest.fixture(autouse=True)
def badges_folder(tmp_path, monkeypatch):
    # A temporary badges folder and an empty cache, so real badges are never used.
    monkeypatch.setattr(badges, "BADGES_FOLDER", tmp_path)
    monkeypatch.setattr(badges, "_cache", {})
    return tmp_path


def test_missing_badge_gives_none():
    assert badges.get_badge_image("Moose", 64) is None


def test_damaged_badge_gives_none_instead_of_crashing(badges_folder):
    (badges_folder / "moose.png").write_bytes(b"this is not a png")
    assert badges.get_badge_image("Moose", 64) is None


def test_a_real_badge_loads(badges_folder):
    from PIL import Image

    Image.new("RGBA", (8, 8), "orange").save(badges_folder / "black-bear.png")
    assert badges.get_badge_image("Black Bear", 64) is not None
