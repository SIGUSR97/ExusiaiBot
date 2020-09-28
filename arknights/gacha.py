from abc import ABC, abstractmethod
from typing import Any
from .probability_tree import ProbabilityNode
import json


class GachaBanner(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def pull(self) -> Any:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class ArknightsBanner(GachaBanner):
    SIX_STAR_RATE = 0.02
    FIVE_STAR_RATE = 0.08
    FOUR_STAR_RATE = 0.50
    THREE_STAR_RATE = 0.40
    RATE_UP = 0.50

    def __init__(
        self,
        name: str,
        rateups: dict = {},
    ) -> None:
        self.name = name
        self.rateups = rateups

        self.rng = ProbabilityNode()

        self.rng.add_child(
            ProbabilityNode(name="SIX_STAR", probability=0.02)
        )

    def pull(self) -> Any:
        return self._rng_root.choice_recursive()

    def __str__(self) -> str:
        pass


if __name__ == "__main__":
    banner = ArknightsBanner("test", rateups={})
    for i in range(10):
        print(banner.pull())
