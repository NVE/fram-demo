"""Custom event handler to control display of demo output."""

import inspect
from copy import deepcopy
from pathlib import Path

class EventHandler:
    """Handle events from framcore.events.send_event."""

    def handle_event(self, sender: object, event_type: str, **kwargs: dict[str, object]) -> None:
        """Try to handle event using rich.print. Use Python.print otherwise."""
        name = self._get_sender_name(sender)
        try:
            self._handle_event_using_rich(name, event_type, **kwargs)
        except Exception:
            if name:
                print(name, event_type, kwargs)
            else:
                print(event_type, kwargs)

    def _get_sender_name(self, sender: object) -> str:
        if inspect.isbuiltin(sender) or sender is None:
            return ""
        is_func = False
        try:
            path = Path(inspect.getfile(type(sender)))
        except Exception:
            path = Path(inspect.getfile(sender))
            is_func = True
        package = None
        for parent in path.parents:
            if parent.name in ["framcore", "framdemo", "framdata", "framjules"]:
                package = parent.name
                break
        name = sender.__name__ if is_func else type(sender).__name__

        try:
            if not is_func:
                caller_method_name = inspect.stack()[5].function
                name = f"{name}.{caller_method_name}"
        except Exception:
            pass

        return f"{name}" if package is None else f"{package}.{name}"

    def _handle_event_using_rich(
        self,
        sender_name: str,
        event_type: str,
        **kwargs: dict[str, object],
    ) -> None:
        import rich  # noqa: PLC0415

        sender_color = "#5DE2E7"
        sender_string = f"[{sender_color}]{sender_name}: [/{sender_color}]" if sender_name else ""

        if event_type in ["info", "debug", "warning", "error"]:
            color = {
                "info": "yellow",
                "debug": "green",
                "warning": "magenta",
                "error": "red",
            }[event_type]
            message = kwargs["message"]

            rich.print(f"[bold {color}]{event_type}: [/bold {color}]{sender_string}{message}")
            return

        if event_type == "display":
            color = "cyan"
            message = kwargs["message"]
            obj = kwargs["object"]
            obj = "" if obj is None else obj
            if isinstance(obj, dict):
                digits_round = kwargs.get("digits_round", 3)
                obj = self._try_prettify(obj, digits_round)
            rich.print(f"[bold {color}]{event_type}: [/bold {color}]{sender_string}{message}", obj)
            return

        color = "cyan"
        rich.print(f"[bold {color}]{event_type}: [/bold {color}]{sender_string}", kwargs)

    def _try_prettify(self, obj: dict, digits_round: int) -> dict:
        if self._has_len_1(obj):
            copied_obj = deepcopy(obj)
            try:
                self._convert_len_1_to_float(copied_obj, digits_round)
                return copied_obj
            except Exception:
                pass
        return obj

    def _has_len_1(self, obj: object) -> bool:
        if isinstance(obj, dict):
            for some_value in obj.values():
                return self._has_len_1(some_value)
            return False
        return self._is_len_1(obj)

    def _is_len_1(self, obj: object) -> bool:
        try:
            return len(obj) == 1
        except Exception:
            return False

    def _convert_len_1_to_float(self, obj: object, digits_round: int) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    self._convert_len_1_to_float(value, digits_round)
                else:
                    obj[key] = round(float(value[0]), digits_round)
