class CommandError(Exception):
    pass


class CommandAlreadyExistsError(CommandError):
    pass


class CommandNotFoundError(CommandError):
    pass


class ForbiddenCommandArgumentError(CommandError):
    pass


class InvalidCommandArgumentsError(CommandError):
    def __init__(
        self,
        message: str,
        *,
        required_args: list[str] | None = None,
        optional_args: list[str] | None = None,
    ) -> None:
        """Initialise with an error message and optional argument metadata.

        Args:
            message: Human-readable description of the argument error.
            required_args: Names of required arguments that were missing or
                invalid.
            optional_args: Names of optional arguments that were invalid.
        """
        self.required_args = required_args or []
        self.optional_args = optional_args or []
        super().__init__(message)

    @property
    def required_args_str(self) -> str:
        """Return a human-readable, comma-and-'and'-joined list of required argument names.

        Returns:
            A formatted string of required argument names.
        """
        return self._format_args(self.required_args)

    @property
    def optional_args_str(self) -> str:
        """Return a human-readable, comma-and-'and'-joined list of optional argument names.

        Returns:
            A formatted string of optional argument names.
        """
        return self._format_args(self.optional_args)

    @staticmethod
    def _format_args(args: list[str]) -> str:
        """Join a list of argument names into a readable English phrase.

        Args:
            args: List of argument name strings to format.

        Returns:
            An empty string when *args* is empty, the single name when there is
            only one entry, or a comma-separated phrase with "and" before the
            last name for multiple entries.
        """
        if len(args) > 1:
            return ", ".join(args[:-1]) + " and " + args[-1]
        elif len(args) == 1:
            return args[0]
        else:
            return ""
