from typing import Callable, Tuple, Union, Iterable
from telegram import parsemode
from telegram.ext import Dispatcher, CallbackContext, MessageHandler, Filters
from telegram import Update, ParseMode


class DotCommandDispatcher:
    def __init__(
        self,
        dispatcher: Dispatcher,
        default: Callable[[Update, CallbackContext, Tuple[str]], None] = None,
    ) -> None:
        self._default = default
        self._commands = dict()

        # yapf: disable
        def default(update: Update,
                    context: CallbackContext,
                    argv: Tuple[str],
        ) -> None:
            command, args_string = argv
            msg = (
                f"Unknown dot command: "
                f"<b>.{command}</b> <i>{args_string}</i>\n"
                 "Usage: <b>[.。](command)</b> <i>(arguments)*</i>"
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg, parse_mode=ParseMode.HTML,
            )
        if not self._default:
            self._default = default

        def dot_command_handler(update: Update, context: CallbackContext):
            command, args_string = context.matches[0].groups()
            print(f"received dot command: {command} {args_string}")
            # print(f"{self._commands=}")
            command_handler = self._commands.get(command)
            if command_handler:
                command_handler(update, context,
                                        argv=(command, args_string))
            else:
                print(f"argv: {command=}, {args_string=}")
                self._default(update, context, argv=(command, args_string))


        self._dot_command_pattern = r"(?:^[\.。](?P<command>[\u4e00-\u9fa5a-zA-Z0-9]+)\s?)(?:(?P<args>.*)\s*)"
        dispatcher.add_handler(MessageHandler(Filters.regex(self._dot_command_pattern),
                               dot_command_handler))
        # yapf: enable

    def add_command(
        self,
        name: Union[str, Iterable],
        command_callback: Callable[[Update, CallbackContext, Tuple[str]],
                                   None],
    ) -> None:
        if isinstance(name, str):
            self._commands[name] = command_callback
        elif isinstance(name, Iterable):
            for _name in name:
                self._commands[_name] = command_callback

    def remove_command(self, name: str) -> None:
        del self._commands[name]
