from abc import ABC, abstractmethod
from typing import Any
from probability_tree import ProbabilityNode
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

        branches = []
        # self._banner_root = ProbabilityNode(children=[])
        branches.append({
            "probability":
            self.SIX_STAR_RATE,
            "item":
            ProbabilityNode(children=[
                {
                    "probability": self.RATE_UP,
                    "item": "RATE_UP_SIX_STAR",
                },
                {
                    "probability": 1 - self.RATE_UP,
                    "item": "SIX_STAR",
                },
            ]) if self.rateups.get("SIX_STAR") else "SIX_STAR"
        })
        branches.append({
            "probability":
            self.FIVE_STAR_RATE,
            "item":
            ProbabilityNode(children=[
                {
                    "probability": self.RATE_UP,
                    "item": "RATE_UP_FIVE_STAR",
                },
                {
                    "probability": 1 - self.RATE_UP,
                    "item": "FIVE_STAR",
                },
            ]) if self.rateups.get("FIVE_STAR") else "FIVE_STAR"
        })
        branches.append({
            "probability":
            self.FOUR_STAR_RATE,
            "item":
            ProbabilityNode(children=[
                {
                    "probability": self.RATE_UP,
                    "item": "RATE_UP_FOUR_STAR",
                },
                {
                    "probability": 1 - self.RATE_UP,
                    "item": "FOUR_STAR",
                },
            ]) if self.rateups.get("FOUR_STAR") else "FOUR_STAR"
        })
        branches.append({
            "probability":
            self.THREE_STAR_RATE,
            "item":
            ProbabilityNode(children=[
                {
                    "probability": self.RATE_UP,
                    "item": "RATE_UP_THREE_STAR",
                },
                {
                    "probability": 1 - self.RATE_UP,
                    "item": "THREE_STAR",
                },
            ]) if self.rateups.get("THREE_STAR") else "THREE_STAR"
        })

        self._rng_root = ProbabilityNode(children=branches)

    def pull(self) -> Any:
        return self._rng_root.choice_recursive()

    def __str__(self) -> str:
        pass


if __name__ == "__main__":
    banner = ArknightsBanner("test", rateups={})
    for i in range(10):
        print(banner.pull())
