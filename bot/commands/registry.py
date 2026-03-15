from typing import Any, Callable, NamedTuple

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .errors import CommandAlreadyExistsError, CommandNotFoundError

CommandArgs = tuple[str, ...]
CommandContext = dict[str, Any]


class Command(NamedTuple):
    is_primary: bool
    name: str
    aliases: list[str]
    func: Callable
    required_args: list[str]
    optional_args: list[str]
    description: str | None

    @property
    def signature(self) -> str:
        """Build a human-readable usage signature for the command.

        Returns:
            A string in the form ``name <req1> <req2> [opt1]``, showing
            required arguments in angle brackets and optional ones in square
            brackets.
        """
        reqs = " ".join(f"<{a}>" for a in self.required_args)
        opts = " ".join(f"[{a}]" for a in self.optional_args)
        return " ".join(part for part in [self.name, reqs, opts] if part)

    def __str__(self) -> str:
        """Return a plain-text summary of the command.

        Returns:
            A multi-line string containing the signature, description, aliases,
            and argument lists.
        """
        lines = [
            self.signature,
            f"  {self.description or 'No description provided.'}",
        ]

        if self.aliases:
            lines.append(f"  Aliases: {', '.join(self.aliases)}")
        if self.required_args:
            lines.append(f"  Required args: {', '.join(self.required_args)}")
        if self.optional_args:
            lines.append(f"  Optional args: {', '.join(self.optional_args)}")

        return "\n".join(lines)

    def __rich__(self) -> Panel:
        """Render a rich-formatted panel for the command.

        Returns:
            A :class:`rich.panel.Panel` containing a grid with usage, description,
            aliases, and argument details.
        """
        table = Table.grid(padding=(0, 1))

        table.add_column(style="bold cyan", no_wrap=True)
        table.add_column()

        table.add_row("Usage:", Text(self.signature))
        table.add_row(
            "Description:",
            Text(self.description or "No description provided."),
        )
        if self.aliases:
            table.add_row("Aliases:", Text(", ".join(self.aliases)))
        if self.required_args:
            table.add_row("Required:", Text(", ".join(self.required_args)))
        if self.optional_args:
            table.add_row("Optional:", Text(", ".join(self.optional_args)))

        return Panel(
            table,
            title=Text(self.name, style="bold white"),
            title_align="left",
            border_style="dim",
            expand=False,
        )


class CommandsRegistry:
    def __init__(self) -> None:
        """Initialise an empty commands registry."""
        self.__registry: dict[str, Command] = {}

    def register(
        self,
        *command_names: str,
        args: list[str] | None = None,
        optional_args: list[str] | None = None,
        description: str | None = None,
    ) -> Callable:
        """Return a decorator that registers a function under one or more command names.

        The first name in *command_names* is treated as the primary name; every
        subsequent name becomes an alias.

        Args:
            *command_names: One or more names (and aliases) for the command.
                At least one name must be provided.
            args: Names of required positional arguments.
            optional_args: Names of optional positional arguments.
            description: Short human-readable description shown in help output.

        Returns:
            A decorator that registers the wrapped callable and returns it
            unchanged.

        Raises:
            CommandAlreadyExistsError: If any of *command_names* is already
                registered.
        """
        def decorator(func: Callable) -> Callable:
            for name in command_names:
                if name in self.__registry:
                    raise CommandAlreadyExistsError(
                        f"Command '{name}' is already registered."
                    )
                self.__registry[name] = Command(
                    is_primary=name == command_names[0],
                    name=name,
                    aliases=[n for n in command_names if n != name],
                    func=func,
                    required_args=args or [],
                    optional_args=optional_args or [],
                    description=description,
                )
            return func

        return decorator

    def get(self, command_name: str) -> Command:
        """Retrieve a registered command by name.

        Args:
            command_name: The primary name or alias of the command to look up.

        Returns:
            The :class:`Command` registered under *command_name*.

        Raises:
            CommandNotFoundError: If no command is registered under
                *command_name*.
        """
        command = self.__registry.get(command_name)
        if not command:
            raise CommandNotFoundError(f"Command '{command_name}' is not registered.")
        return command

    def get_all_command_names(self) -> list[str]:
        """Return all registered command names (including aliases).

        Returns:
            A list of every key currently in the registry.
        """
        return list(self.__registry.keys())

    def get_primary_commands(self) -> list[Command]:
        """Return only the primary (non-alias) commands.

        Returns:
            A list of :class:`Command` objects where ``is_primary`` is ``True``.
        """
        return [cmd for cmd in self.__registry.values() if cmd.is_primary]
