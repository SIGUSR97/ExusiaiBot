import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Union
from functools import partial
from collections import defaultdict
from random import choice

import arrow

from probability_tree import ProbabilityNode
from utils import (get_banners_info, get_operators_info, save_banners_info,
                   save_operators_info)


class NoneExistantBanner(Exception):
    pass


class GachaBanner(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def pull(self) -> Any:
        pass


class ArknightsBanner(GachaBanner):
    SIX_STAR_RATE = 0.02
    FIVE_STAR_RATE = 0.08
    FOUR_STAR_RATE = 0.50
    THREE_STAR_RATE = 0.40
    RATEUP = 0.50

    OPERATORS_INFO_FILEPATH = "../assets/arknights/operators_less.json"
    BANNERS_FILEPATH = "../assets/arknights/banners.json"
    NUM2WORD = {
        1: "ONE",
        2: "TWO",
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6: "SIX",
    }

    def __init__(
        self,
        name: str,
        rateups: dict = {},
        end_time: Optional[str] = None,
    ) -> None:
        self.name = name
        self.end_time = end_time
        self.rateups = rateups

        self._load_banner(False)

    def pull(self) -> Any:
        return choice(self.rng.choice_recursive().value)

    def pull10(
        self,
        with_pity: bool = False,
    ) -> list:
        flag = True
        result = []
        for _ in range(9 + (not with_pity)):
            pull = self.pull()
            result.append(pull)
            if pull["rarity"] >= 5:
                flag = False
        if with_pity and flag:
            self.rng.set_children_probabilities({
                "FIVE_STAR": 0.98,
                "SIX_STAR": 0.02,
                "FOUR_STAR": 0,
                "THREE_STAR": 0,
            })
            result.append(self.pull())
            self.rng.reset_children_recursive()
        return result

    def _load_banner(self, update: bool = False) -> None:
        if update:
            save_operators_info(less=True)
            save_banners_info
        path = Path(self.OPERATORS_INFO_FILEPATH)
        with path.open("r", encoding="utf-8") as f:
            self.operators = json.loads(f.read())
        self.operators_dict = {op["cn_name"]: op for op in self.operators}
        path = Path(self.BANNERS_FILEPATH)
        with path.open("r", encoding="utf-8") as f:
            self.banners = json.loads(f.read())

        self.set_banner(self.name)

    def set_banner(self, banner_name: str, default: bool = True) -> None:
        banner_ = None
        ret = 0
        for banner in self.banners:
            if banner["name"] == banner_name:
                banner_ = banner

        if not banner_:
            if default:
                banner_ = {
                    "name":
                    self.name,
                    "time":
                    self.end_time
                    if self.end_time else arrow.get().format("YYYYMMDD"),
                    "rateups":
                    self.rateups,
                }
            else:
                raise NoneExistantBanner
            ret = -1

        self.banner = banner_

        self._load_available_operators()

        self._load_rateups(self.banner["rateups"])
        self._load_probability_tree()

        return ret

    def _load_available_operators(self) -> None:
        filter_ = partial(
            self._filter,
            rarity=">0",
            approach="标准寻访",
            before_date=self.banner["time"],
        )

        self.available_operators = list(filter(filter_, self.operators))
        self.available_operators_dict = {
            op["cn_name"]: op
            for op in self.available_operators
        }

    def _load_rateups(self, rateups: list) -> None:
        self.rateups = defaultdict(list)
        for name in rateups:
            if self.available_operators_dict.get(name):
                self.available_operators.remove(
                    self.available_operators_dict[name])
                del self.available_operators_dict[name]
            op = self.operators_dict[name]
            self.rateups[op["rarity"]].append(op)

    def _load_probability_tree(self) -> None:
        self.N_STARS_POOL = {
            i: list(
                filter(partial(self._filter, rarity=i),
                       self.available_operators))
            for i in range(3, 7)
        }
        self.N_STARS_RATE = {
            3: self.THREE_STAR_RATE,
            4: self.FOUR_STAR_RATE,
            5: self.FIVE_STAR_RATE,
            6: self.SIX_STAR_RATE,
        }

        self.rng = ProbabilityNode()

        for i in range(3, 7):
            self.rng.add_child(
                name=f"{self.NUM2WORD[i]}_STAR",
                probability=self.N_STARS_RATE[i],
                value=self.N_STARS_POOL[i],
            )

        for k, v in self.rateups.items():
            parent_name = f"{self.NUM2WORD[k]}_STAR"
            self.rng.get_child_by_name(parent_name).add_child(
                name=f"RATEUP_{self.NUM2WORD[k]}_STAR",
                probability=self.RATEUP,
                value=v,
            )
            self.rng.get_child_by_name(parent_name).add_child(
                name=f"{self.NUM2WORD[k]}_STAR",
                probability=1 - self.RATEUP,
                value=self.N_STARS_POOL[k],
            )

    def _filter(
        self,
        op: dict,
        rarity: Union[str, int] = ">0",
        approach: str = "标准寻访",
        before_date: str = "99991230",
    ) -> bool:
        rarity_condition = None
        try:
            rarity_condition = eval(f"op['rarity']{rarity}")
        except SyntaxError:
            rarity_condition = op["rarity"] == int(rarity)

        return rarity_condition and approach in op["approach"] and arrow.get(
            before_date) >= arrow.get(op["release_time"])


def format_gacha_result(pulls: list) -> str:
    return "\n".join(
        f"{'⭐' * pull['rarity']} {pull['class']} {pull['cn_name']}"
        for pull in pulls)


if __name__ == "__main__":
    from pprint import pprint
    banner = ArknightsBanner("test")
    pprint(banner.pull10(True))
    banner.set_banner("地生五金")
    pprint(banner.banner)
    pprint(banner.pull10(True))
    print(format_gacha_result(banner.pull10(True)))

    # for i in range(10):
    #     print(banner.pull())
    # banner._load_operator_pool(True)
    # from pprint import pprint
    # pprint(banner.operators)
