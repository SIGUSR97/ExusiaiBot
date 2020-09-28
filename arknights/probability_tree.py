from typing import Any, List, TypedDict, Union
from numpy import random


class ProbabilityNodeChild(TypedDict):
    probability: float
    item: Any


class ProbabilityNode:
    rng = random.default_rng()

    def __init__(
        self,
        children: List[ProbabilityNodeChild],
    ) -> None:
        self.children = children

    def choice(self) -> Any:
        return self.rng.choice(
            self.children,
            p=[i["probability"] for i in self.children],
        )["item"]

    def choice_recursive(self) -> Any:
        result = self.choice()
        if isinstance(result, ProbabilityNode):
            return result.choice_recursive()
        else:
            return result

    


if __name__ == "__main__":
    root = ProbabilityNode(children=[{
        "probability": 0.5,
        "item": "a"
    }, {
        "probability": 0.3,
        "item": "b"
    }, {
        "probability":
        0.2,
        "item":
        ProbabilityNode(children=[
            {
                "probability": 0.5,
                "item": "aa"
            },
            {
                "probability": 0.5,
                "item": "bb"
            },
        ])
    }])

    print(root.choice_recursive())
