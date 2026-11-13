from types import SimpleNamespace

from hotkey_listener import HotkeyMatcher, key_name

# Stand-ins for pynput's key objects, so these tests don't need a keyboard backend.
F8 = SimpleNamespace(name="f8")
F9 = SimpleNamespace(name="f9")
LETTER_K = SimpleNamespace(name=None, char="K")


def test_key_name_of_a_special_key():
    assert key_name(F8) == "f8"


def test_key_name_of_a_letter_is_lowercase():
    assert key_name(LETTER_K) == "k"


def test_key_name_of_an_unknown_key_is_none():
    assert key_name(SimpleNamespace(name=None, char=None)) is None


def test_pressing_the_hotkey_fires():
    assert HotkeyMatcher("F8").press(F8) is True


def test_other_keys_do_not_fire():
    assert HotkeyMatcher("f8").press(F9) is False


def test_holding_the_key_only_fires_once():
    matcher = HotkeyMatcher("f8")
    assert matcher.press(F8) is True
    # The OS repeats the press while the key is held down.
    assert matcher.press(F8) is False
    assert matcher.press(F8) is False


def test_fires_again_after_release():
    matcher = HotkeyMatcher("f8")
    matcher.press(F8)
    matcher.release(F8)
    assert matcher.press(F8) is True


def test_releasing_another_key_does_not_reset():
    matcher = HotkeyMatcher("f8")
    matcher.press(F8)
    matcher.release(F9)
    assert matcher.press(F8) is False
