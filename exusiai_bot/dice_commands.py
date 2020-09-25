import logging
import re
from typing import Tuple

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from .dice import *
from .dot_command import FilterReturns

dice = Dice(
    max_line_length=47,
    max_repeats=10,
    max_throws=100,
    max_sides=1000,
)


def dice_handler(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    print(f"dice argv: {argv}")
    _, args = argv
    args = args.split()

    usage_tip = ("Roll 命令 用法:\n"
                 "<b>.r</b> <i>(重复次数#)投掷次数[dD]骰子面数"
                 "([xX*]骰子倍率)([+-]骰子补偿)</i>")
    send_tip = False
    dice_code = purpose = None

    if len(args) == 1:
        dice_code, = args
        if not Dice.test_dice_code(dice_code):
            send_tip = True
    elif len(args) == 2:
        for arg in args:
            if Dice.test_dice_code(arg):
                dice_code = arg
            else:
                purpose = arg
        if not dice_code:
            send_tip = True
    else:
        send_tip = True

    if send_tip:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=usage_tip,
                                 parse_mode=ParseMode.HTML)
        return
    msg = None
    try:
        dice.roll(dice_code)
    except RepeatsValueError as e:
        if e.repeats == 0:
            msg = "wdnmd不扔骰子就滚"
        else:
            msg = "？想累死我"
    except ThrowsValueError as e:
        if e.throws == 0:
            msg = "wdnmd不扔骰子就滚"
        else:
            msg = "这么多骰子你怎么不出钱买？"
    except SidesValueError as e:
        if e.sides == 0:
            msg = "你倒是整个0面骰子出来啊kora"
        else:
            msg = "这是骰子？这tm是个球！"
    else:
        username = update.effective_user.username
        purpose = purpose if purpose else ''
        formatter = ("<b>@{username}</b> 掷骰<i>{purpose}</i>: "
                     "{dice_code}={break}{result}")
        msg = dice.get_message(formatter=formatter,
                               formatter_data={
                                   "username": username,
                                   "purpose": purpose
                               })
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=msg,
                             parse_mode=ParseMode.HTML)


def dot_rd_handler(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    cmd, args_string = argv
    dice_handler(update, context, (cmd, args_string + " 1D100"))


def dot_command_filter(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> FilterReturns:
    command, args_string = argv
    match = re.match(r"(?:r(.+))", command)
    logging.info(f"filter received command: {command} {args_string}, {match.group()=}")
    if match and Dice.test_dice_code(match.group()):
        return update, context, ("r", f"{match.string} {args_string}")
    return update, context, argv


if __name__ == "__main__":
    dice = Dice()
    dice.roll("5#30d100*5+2")
    print(dice.get_message())
