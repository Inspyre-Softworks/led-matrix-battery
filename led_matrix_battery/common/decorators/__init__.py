import functools
from typing import Any, Callable, Optional, Type


def freeze_setter(attr_name: Optional[str] = None, 
                  exception: Type[Exception] = AttributeError,
                  allow_none_reassignment: bool = False,
                  treat_none_as_unset: bool = True):
    """
    Function decorator for a @<prop>.setter that raises if you try to set again.

    This decorator prevents reassigning a property after it's been set once.

    Parameters:
        attr_name (str, optional):
            The name of the property to freeze. If not provided, 
            it will be derived from the setter name.

        exception (Exception class, optional):
            The exception to raise on reassignment. Defaults to AttributeError.

        allow_none_reassignment (bool, optional):
            If True, allows setting the property to None even if it's already set.
            Defaults to False.

        treat_none_as_unset (bool, optional):
            If True, None values are considered as unset, allowing the property
            to be set if its current value is None. Defaults to True.

    Example:
        ```python
        class MyClass:
            def __init__(self):
                self._value = None

            @property
            def value(self):
                return self._value

            @value.setter
            @freeze_setter()
            def value(self, new_value):
                self._value = new_value

        obj = MyClass()
        obj.value = 42  # Works fine
        obj.value = 100  # Raises AttributeError: Cannot reassign MyClass.value
        ```
    """
    def decorator(setter: Callable) -> Callable:
        name = setter.__name__
        private = attr_name or f'_{name}'

        @functools.wraps(setter)
        def wrapper(self, new: Any) -> Any:
            current_value = getattr(self, private, None)

            # Check if we're trying to reassign
            if (not treat_none_as_unset or current_value is not None) and \
               not (allow_none_reassignment and new is None):
                raise exception(
                    f'Cannot reassign {self.__class__.__name__}.{name} '
                    f'(current value: {current_value!r})'
                )

            return setter(self, new)

        return wrapper

    return decorator
