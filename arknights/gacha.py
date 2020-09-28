import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .probability_tree import ProbabilityNode
from .utils import get_operator_infos


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

    OPERATOR_INFO_FILEPATH = "../assets/arknights/operators.json"

    def __init__(
        self,
        name: str,
        rateups: dict = {},
    ) -> None:
        self.name = name
        self.rateups = rateups

        self.rng = ProbabilityNode()

        self.rng.add_child(
            ProbabilityNode(
                name="SIX_STAR",
                probability=self.SIX_STAR_RATE,
            ))
        self.rng.add_child(
            ProbabilityNode(
                name="FIVE_STAR",
                probability=self.FIVE_STAR_RATE,
            ))
        self.rng.add_child(
            ProbabilityNode(
                name="FOUR_STAR",
                probability=self.FOUR_STAR_RATE,
            ))
        self.rng.add_child(
            ProbabilityNode(
                name="THREE_STAR",
                probability=self.THREE_STAR_RATE,
            ))

        for k, v in self.rateups.items():
            self.rng.get_child_by_name(k).add_child(
                ProbabilityNode(name=f"RATEUP_{k}",
                                probability=self.RATEUP,
                                value=v))
            self.rng.get_child_by_name(k).add_child(
                ProbabilityNode(
                    name=k,
                    probability=1 - self.RATEUP,
                ))

    def pull(self) -> Any:
        return self.rng.choice_recursive()

    def _load_operator_pool(self, update: bool = False) -> None:
        info = []
        path = Path(self.OPERATOR_INFO_FILEPATH)
        if update:
            with path.open("w") as f:
                f.write(json.dumps(get_operator_infos()))
        with path.open("r") as f:
            self.operators = json.loads(f.read())
        

if __name__ == "__main__":
    banner = ArknightsBanner("test", rateups={})
    for i in range(10):
        print(banner.pull())
