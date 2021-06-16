import logging
from typing import Any, Callable, Iterable, Optional, Union

from telegram import Update
from telegram.ext import CallbackContext, Dispatcher, Filters, MessageHandler

CommandCallback = Callable[[Update, CallbackContext, tuple[str]], None]
FilterReturns = Optional[tuple[Update, CallbackContext, tuple[str, str, str,
                                                              str]]]
FilterCallback = Callable[[Update, CallbackContext, tuple[str]], FilterReturns]


class DotCommandError(Exception):
    """Base class for all DotCommand errors"""


class DotCommandDispatcher:
    def __init__(
        self,
        dispatcher: Dispatcher,
        default: Optional[CommandCallback] = None,
    ) -> None:
        self._default = default
        self._commands = dict()

        def _default(
            update: Update,
            context: CallbackContext,
            argv: tuple[str, str],
        ) -> None:
            command, args_string = argv
            logging.info(
                f"received Unknown dot command {command=}, {args_string=}")
            # msg = (f"Unknown dot command: "
            #        f"<b>.{command}</b> <i>{args_string}</i>\n"
            #        "Usage: <b>[.。](command)</b> <i>(arguments)*</i>")
            # context.bot.send_message(
            #     chat_id=update.effective_chat.id,
            #     text=msg,
            #     parse_mode=ParseMode.HTML,
            # )

        if not self._default:
            self._default = _default

        self._filter = None
        self._command_filters = dict()

        def dot_command_handler(update: Update, context: CallbackContext):
            matches = context.matches
            assert isinstance(matches, list)
            command, args_string = matches[0].groups()
            print(f"received dot command: {command} {args_string}")
            filtered = None
            if self._filter:
                filtered = self._filter(update,
                                        context,
                                        argv=(command, args_string))
            if filtered:
                update, command, argv = filtered
                command, args_string = argv
            else:
                return
            command_handler = self._commands.get(command)
            if command_handler:
                command_handler(update, context, argv=(command, args_string))
            else:
                print(f"argv: {command=}, {args_string=}")
                self._default(update, context, argv=(command, args_string))

        self._dot_command_pattern = (r"(?:^[\.。](?P<command>\S+)\s?)"
                                     r"(?:(?P<args>.*)\s*)")
        dispatcher.add_handler(
            MessageHandler(Filters.regex(self._dot_command_pattern),
                           dot_command_handler))

    def add_command(
        self,
        name: Union[str, Iterable],
        command_callback: Callable[[Update, CallbackContext, tuple[str]],
                                   None],
    ) -> None:
        if isinstance(name, str):
            self._commands[name] = command_callback
        elif isinstance(name, Iterable):
            for _name in name:
                self._commands[_name] = command_callback

    def remove_command(self, name: str) -> None:
        del self._commands[name]

    def set_filter(self, callback: FilterCallback) -> None:
        self._filter = callback

    def add_command_filter(
        self,
        command: str,
        callback: FilterCallback,
    ) -> None:
        # TODO
        raise NotImplementedError
