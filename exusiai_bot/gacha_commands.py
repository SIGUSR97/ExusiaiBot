import logging
import re
from typing import Tuple

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from ..arknights.gacha import GachaBanner

banner = GachaBanner()
with_pity = False

def format_gacha_result(pulls: list) -> str:
    pass


def pull10(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    _, args_string = argv
    pulls = banner.pull10(with_pity)


def set_banner(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    pass
