from contextlib import contextmanager
from threading import Timer
from typing import Optional, Union
from telegram import Bot
from functools import partial


def send_timed_message(bot: Bot, chat_id: Union[int, str], text: str,
                       timeout: int=5000):
    msg = bot.send_message(chat_id=chat_id, text=text)
    del_msg = partial(bot.delete_message,
                      chat_id=chat_id,
                      message_id=msg.message_id)
    timer = Timer(timeout / 1000, del_msg)
    timer.start()
