from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Type


def _default_token_to_method(token: str) -> str:
    """Convert a command token like 'FILE_UPLOAD_AT' to a method name 'file_upload_at'."""
    return token.lower()


def make_simulator(
    handler_class: Type[Any],
    token_to_method: Optional[Callable[[str], str]] = None,
    on_missing: str = "raise",
) -> Callable[[Iterable[Sequence[Any]]], List[Any]]:
    """Create a simulator function for a given handler class.

    - handler_class: class with methods matching command tokens (e.g., file_upload, file_get,...)
    - token_to_method: optional function to map tokens to method names; defaults to lowercase
    - on_missing: 'raise' to error on unknown command; 'skip' to ignore

    Returns a function with signature: simulate_coding_framework(list_of_lists) -> List[Any]
    Each command is a sequence like ["FILE_UPLOAD", name, size]. The simulator dispatches to
    handler.method(*args) and appends the return value to the outputs list.
    """

    token_mapper = token_to_method or _default_token_to_method

    def simulate_coding_framework(list_of_lists: Iterable[Sequence[Any]]) -> List[Any]:
        handler = handler_class()
        outputs: List[Any] = []
        for command in list_of_lists:
            if not command:
                continue
            token = str(command[0])
            args = list(command[1:])
            method_name = token_mapper(token)
            method = getattr(handler, method_name, None)
            if method is None:
                if on_missing == "skip":
                    continue
                raise AttributeError(f"Unknown command '{token}' mapped to missing method '{method_name}'")
            result = method(*args)
            outputs.append(result)
        return outputs

    return simulate_coding_framework


