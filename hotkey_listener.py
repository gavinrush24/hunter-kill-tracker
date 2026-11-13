"""A global hotkey: works even while another window (the game) has focus.

The actual key listening is done by pynput, which runs the callbacks on its own
background thread. So on_hotkey must NOT touch the UI; the app passes a function
that just puts a KillEvent on its queue.
"""


def key_name(key):
    """Turn a pynput key into a plain lowercase name like 'f8' or 'k'.

    pynput gives special keys (F8, Home, ...) as Key members with a .name,
    and normal keys as KeyCode objects with a .char. Returns None if neither.
    """
    name = getattr(key, "name", None)
    if name:
        return name.lower()
    char = getattr(key, "char", None)
    if char:
        return char.lower()
    return None


class HotkeyMatcher:
    """Decides when a key press counts as one hotkey press.

    Holding a key down makes the OS repeat the press many times a second,
    which would log a pile of kills. So the hotkey only fires again after
    the key has been released.
    """

    def __init__(self, hotkey):
        self.hotkey = hotkey.lower()
        self._held = False

    def press(self, key):
        """Call on every key press. Returns True if the hotkey should fire."""
        if key_name(key) != self.hotkey:
            return False
        if self._held:
            return False
        self._held = True
        return True

    def release(self, key):
        """Call on every key release."""
        if key_name(key) == self.hotkey:
            self._held = False


class HotkeyListener:
    """Listens for one hotkey system-wide and calls on_hotkey() when it's pressed."""

    def __init__(self, hotkey, on_hotkey):
        self.hotkey = hotkey
        self._matcher = HotkeyMatcher(hotkey)
        self._on_hotkey = on_hotkey
        self._listener = None

    def start(self):
        """Start listening. Raises an exception if keyboard hooks aren't available."""
        if self._listener is not None:
            return
        # Imported here, not at the top: pynput fails to import on machines
        # without a keyboard backend, and that shouldn't break the whole app.
        from pynput import keyboard

        self._listener = keyboard.Listener(
            on_press=self._handle_press, on_release=self._matcher.release
        )
        self._listener.daemon = True  # don't keep the app alive after the window closes
        self._listener.start()

    def stop(self):
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _handle_press(self, key):
        if self._matcher.press(key):
            self._on_hotkey()
