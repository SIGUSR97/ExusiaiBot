from typing import Union
from decimal import Decimal


Number = Union[Decimal, int, float]


class SharedWeight:
    def __init__(self, total: Number) -> None:
        pass

from arknights.utils import save_banners_info

save_banners_info()