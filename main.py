import hashlib
import logging
import os
import sys
from typing import Tuple

import arrow
from numpy.random import SeedSequence, default_rng
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Updater

from exusiai_bot.dice_commands import (dice_handler, dot_command_filter,
                                       dot_rd_handler, bobing)
from exusiai_bot.dot_command import DotCommandDispatcher
from exusiai_bot.telegram_bot_utils import send_timed_message
from exusiai_bot.gacha_commands import pull10, set_banner, pity_on, pity_off, show_banners, update_banner

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXY_URL = "http://127.0.0.1:10012"
PORT = int(os.getenv("PORT", 5000))

request_kwargs = {"proxy_url": PROXY_URL}

updater = Updater(
    token=TELEGRAM_BOT_TOKEN,
    use_context=True,
    #request_kwargs=request_kwargs,
)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    print("command: /start")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi!")


def test(update: Update, context: CallbackContext):
    print('command: /test')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm a bot, please talk to me!")
    send_timed_message(bot=context.bot,
                       chat_id=update.effective_chat.id,
                       text="test",
                       timeout=5000)


def error_handler(update: Update, context: CallbackContext):
    print(f'{context.error=}')
    raise context.error


def dot_jrrp_handler(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    username = update.effective_user.username
    temp = f"{username}{arrow.utcnow().to('utf-8').isocalendar()}"
    hash_ = int(hashlib.md5(temp.encode()).hexdigest(), 16) % sys.maxsize
    # logging.info(f"in jrrp_handler: {temp=}, {hash_=}")
    rp = default_rng(SeedSequence(hash_)).integers(0, 100, endpoint=True)
    chat_id = update.effective_chat.id
    msg = f"@{username} 今天的人品值是：**{rp}**。"
    context.bot.send_message(chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('test', test))
dispatcher.add_error_handler(error_handler)
dot_dispatcher = DotCommandDispatcher(dispatcher=dispatcher)
dot_dispatcher.add_command("jrrp", dot_jrrp_handler)
dot_dispatcher.add_command("r", dice_handler)
dot_dispatcher.add_command("rd", dot_rd_handler)
dot_dispatcher.add_command("博饼", bobing)
dot_dispatcher.set_filter(dot_command_filter)

dot_dispatcher.add_command(["十连寻访", "十连"], pull10)
dot_dispatcher.add_command("设置卡池", set_banner)
dot_dispatcher.add_command("开启保底", pity_on)
dot_dispatcher.add_command("关闭保底", pity_off)
dot_dispatcher.add_command("卡池列表", show_banners)
dot_dispatcher.add_command("更新卡池", update_banner)

if os.getenv("PRODUCTION", 'False').lower() in ['true', '1']:
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
    )
    updater.bot.setWebhook(
        f"https://exusiai-bot.herokuapp.com/{TELEGRAM_BOT_TOKEN}")

else:
    updater.start_polling()

logging.info("Exusiai Bot started")
logging.info("アップルパイ！🥧")
updater.idle()
