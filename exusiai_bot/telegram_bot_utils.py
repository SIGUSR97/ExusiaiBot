from contextlib import contextmanager
from functools import partial
from threading import Timer
from typing import Union

from telegram import Bot


def send_timed_message(
    bot: Bot,
    chat_id: Union[int, str],
    text: str,
    timeout: int = 5000,
) -> dict:
    msg = bot.send_message(chat_id=chat_id, text=text)
    del_msg = partial(bot.delete_message,
                      chat_id=chat_id,
                      message_id=msg.message_id)
    timer = Timer(timeout / 1000, del_msg)
    timer.start()

    return {"timer": timer, "message": msg}
