import sys
from pathlib import Path


def app_folder():
    """The folder holding the user's files (data and badges).

    When packaged as an .exe this is the folder the .exe sits in.
    When run normally it is the project folder.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent