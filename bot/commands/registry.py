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
        reqs = " ".join(f"<{a}>" for a in self.required_args)
        opts = " ".join(f"[{a}]" for a in self.optional_args)
        return " ".join(part for part in [self.name, reqs, opts] if part)

    def __str__(self) -> str:
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
        self.__registry: dict[str, Command] = {}

    def register(
        self,
        *command_names: str,
        args: list[str] | None = None,
        optional_args: list[str] | None = None,
        description: str | None = None,
    ) -> Callable:
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
        command = self.__registry.get(command_name)
        if not command:
            raise CommandNotFoundError(f"Command '{command_name}' is not registered.")
        return command

    def get_all_command_names(self) -> list[str]:
        return list(self.__registry.keys())

    def get_primary_commands(self) -> list[Command]:
        return [cmd for cmd in self.__registry.values() if cmd.is_primary]
