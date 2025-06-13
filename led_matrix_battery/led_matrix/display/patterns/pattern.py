from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Tuple


@dataclass(frozen=True)
class Pattern:
    """
    A class representing an LED Matrix pattern.

    Attributes:
        name (str):
            The name of the pattern.

        action (Callable[..., None]):
            The function to be called when displaying this pattern.

        args (Tuple[Any, ...]):
            Positional arguments for the `action` function.

        kwargs (Dict[str, Any]):
            Keyword arguments for the `action` function.
    """
    name:   str
    action: Callable[..., None]
    args:   Tuple[Any, ...]     = field(default_factory=tuple)
    kwargs: Dict[str, Any]      = field(default_factory=dict)

