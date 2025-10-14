"""
Contains paths that may be set by users to override default behaviour.

Contains constants and small utility functions to make the demos more robust and easier to follow.
"""

import pickle
from pathlib import Path

from framcore.events import send_event, set_event_handler

from framdemo.EventHandler import EventHandler

# this makes demo output better
set_event_handler(EventHandler())

DATASET_SOURCE = None
DEMO_FOLDER = Path.resolve(Path(__file__)).parent.parent / "demo_folder"

JULIA_PATH_EXE = None
JULIA_PATH_ENV = DEMO_FOLDER / "julia_env"
JULIA_PATH_DEPOT = DEMO_FOLDER / "julia_depot"

def display(message: str, obj: object = None, digits_round: int = 1) -> None:
    """Send an object to EventHandler for display."""
    send_event(None, "display", message=message, object=obj, digits_round=digits_round)


def load(path: Path) -> object:
    """Read object from pickle file."""
    with Path.open(path, "rb") as f:
        return pickle.load(f)


def save(obj: object, path: Path) -> None:
    """Write object to pickle file at given path."""
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with Path.open(path, "wb") as f:
        pickle.dump(obj, f)
