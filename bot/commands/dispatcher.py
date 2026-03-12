import inspect
import shlex
from pathlib import Path
from typing import Any, get_type_hints

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory, InMemoryHistory

from bot.config import DEFAULT_HISTORY_FILE
from bot.utils.file_utils import ensure_file_exists
from .errors import ForbiddenCommandArgumentError, InvalidCommandArgumentsError
from .registry import CommandsRegistry

CommandArgs = tuple[str, ...]
CommandContext = dict[str, Any]


class CommandsDispatcher:
    def __init__(self, registry: CommandsRegistry, history_file: Path = DEFAULT_HISTORY_FILE) -> None:
        self.__registry = registry
        self.__history = CommandsDispatcher.__initialize_history(history_file)
        possible_commands = self.__registry.get_all_command_names()
        self.__completer = WordCompleter(possible_commands, sentence=True)

    @staticmethod
    def __initialize_history(history_file: Path) -> FileHistory | InMemoryHistory:
        try:
            absolute_history_path = history_file.absolute()
            ensure_file_exists(absolute_history_path)
            return FileHistory(str(absolute_history_path))
        except Exception as e:
            print(f"Failed to initialize history file: {e}, fallback to session history")
            return InMemoryHistory()

    def input_command(self, prompt_text: str) -> tuple[str | None, list[str]]:
        user_input = prompt(prompt_text, completer=self.__completer, history=self.__history).strip()
        if not user_input:
            return None, []

        try:
            parts = shlex.split(user_input)
        except ValueError:
            raise ValueError(
                "Unbalanced quotes in input. Please close any open quotes and try again"
            )

        command, *args = parts
        command = command.lower()
        return command, args

    def run_command(self, command_name: str, *args: str, **kwargs: Any) -> None:
        command = self.__registry.get(command_name)
        command_args: dict[str, Any] = {}

        sig = inspect.signature(command.func)
        hints = get_type_hints(command.func)

        for param_name, _ in sig.parameters.items():
            param_type = hints.get(param_name)

            # Check args quantity & inject them
            if param_type == CommandArgs:
                required_args_n = len(command.required_args)
                optional_args_n = len(command.optional_args)
                min_args_n = required_args_n
                max_args_n = required_args_n + optional_args_n

                if max_args_n == 0 and len(args) > 0:
                    raise InvalidCommandArgumentsError(
                        f"Command '{command_name}' does not expect any args"
                    )
                elif not (min_args_n <= len(args) <= max_args_n):
                    raise InvalidCommandArgumentsError(
                        (
                            f"Command '{command_name}' requires {min_args_n} args"
                            if min_args_n == max_args_n
                            else f"Command '{command_name}' requires {min_args_n} (+{max_args_n} optional) args"
                        ),
                        required_args=command.required_args,
                        optional_args=command.optional_args,
                    )

                optional_defaults = (None,) * (max_args_n - len(args))
                command_args[param_name] = args + optional_defaults

            # Inject context
            if param_type == CommandContext:
                command_args[param_name] = kwargs

            # Forbid all other arguments
            if param_type != CommandArgs and param_type != CommandContext:
                raise ForbiddenCommandArgumentError(
                    f"Argument '{param_name}' with '{param_type}' type is not allowed."
                )

        command.func(**command_args)
