from functools import partial
from threading import Timer
from typing import TypedDict, Union

from telegram import Bot
from telegram.message import Message


class TimedMessage(TypedDict):
    timer: Timer
    message: Message


def send_timed_message(
    bot: Bot,
    chat_id: Union[int, str],
    text: str,
    timeout: int = 5000,
) -> TimedMessage:
    msg = bot.send_message(chat_id=chat_id, text=text)
    assert isinstance(msg, Message)
    del_msg = partial(bot.delete_message,
                      chat_id=chat_id,
                      message_id=msg.message_id)
    timer = Timer(timeout / 1000, del_msg)
    timer.start()

    return {"timer": timer, "message": msg}
