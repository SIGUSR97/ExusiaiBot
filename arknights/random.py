from __future__ import annotations
from typing import Any, Callable, Generic, Optional, Union, TypeVar
from typing_extensions import TypedDict
import random
from pydantic import BaseModel

Number = Union[int, float]
RNGType = Callable[[], Number]


class Node(TypedDict):
    value: Any
    weight: Number
    id: str
    children: Optional[list[Node]]

class _Node(BaseModel):
    value: Any
    weight: Number
    id: str
    children: Optional[list[_Node]]


def create_node(node: Node) -> PNode[Any]:
    node_ = PNode(node["value"], node["weight"])
    children = node["children"]
    if children:
        for child in children:
            node_.add_child(child["value"], child["weight"])
    return node_


class ProbabilityTree:
    root: PNode[Any]

    def __init__(self, tree: Node) -> None:
        self.root = self._load_tree(tree)

    def _load_tree(self, tree: Node) -> PNode[Any]:
        return create_node(tree)

    def __call__(self) -> Any:
        pass


tree = ProbabilityTree({
    "value": "test",
    "weight": 1,
    "id": "test",
    "children": []
})

dummy = lambda *_, **__: None
T = TypeVar("T")
class PNode(Generic[T]):
    value: T
    children: list[PNode[T]]
    weight: Number
    rng: RNGType
    on_success: Callable[[PNode[T]], Any]
    on_fail: Callable[[PNode[T]], Any]

    def __init__(
        self,
        value: T,
        weight: float,
        *,
        rng: RNGType = random.random,
        on_success: Optional[Callable[[PNode[T]], Any]] = None,
        on_fail: Optional[Callable[[PNode[T]], Any]] = None,
    ) -> None:
        self.weight = weight
        self.value = value
        self.children = []
        self.rng = rng
        self.on_success = on_success or dummy
        self.on_fail = on_fail or dummy

    def add_child(self, value: T, weight: float):
        self.children.append(PNode(value, weight))

    def clear_children(self):
        self.children.clear()

    def next(self) -> Optional[PNode[T]]:
        if len(self.children) == 1: return self.children[0]
        total_weight = sum(w.weight for w in self.children)
        rand = self.rng() * total_weight
        sum = 0
        for child in self.children:
            sum += child.weight
            if rand < sum:
                child.on_success(child)
                return child
            child.on_fail(child)

    def __call__(self) -> Optional[PNode[T]]:
        node = self.next()
        while node is not None:
            node = node.next()
        return node
