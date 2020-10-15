import logging
import re
from typing import Tuple

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from arknights.gacha import ArknightsBanner

banner = ArknightsBanner("default")
with_pity = True
stars = ["", "☆", "☆", "☆", "☆", "★", "⭐"]


def format_gacha_result(pulls: list) -> str:
    return "\n".join(
        f"{ stars[pull['rarity']] * pull['rarity']} {pull['class']} {pull['cn_name']}"
        for pull in pulls)


def pull10(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    _, args_string = argv
    pulls = banner.pull10(with_pity)
    username = update.effective_user.username
    msg = f"<b>@{username}</b> 的十连寻访结果: \n{format_gacha_result(pulls)}"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=msg,
                             parse_mode=ParseMode.HTML)


def set_banner(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    success = banner.set_banner(argv[1])
    msg = {0: f"卡池已设置为<b>{argv[1]}</b>", -1: "卡池设置失败"}[success]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=msg,
                             parse_mode=ParseMode.HTML)


def set_pity(val: bool, *args) -> None:
    global with_pity
    with_pity = val


def pity_on(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    set_pity(True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="已开启保底",
                             parse_mode=ParseMode.HTML)


def pity_off(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    set_pity(False)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="已关闭保底",
                             parse_mode=ParseMode.HTML)


def show_banners(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    msg = "<b>可选卡池列表</b>" + "\n".join(b.name for b in banner.banner)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="已关闭保底",
                             parse_mode=ParseMode.HTML)
