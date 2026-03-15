from typing import Any


class Field:
    def __init__(self, value: Any) -> None:
        """Initialise the field with an arbitrary value.

        Args:
            value: The initial value to store in this field.
        """
        self.value = value

    def __str__(self) -> str:
        """Return the string representation of the stored value.

        Returns:
            The result of calling ``str()`` on the stored value.
        """
        return str(self.value)
