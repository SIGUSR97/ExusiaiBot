from abc import ABC, abstractmethod


class GachaBanner(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass


class ArknightsBanner(GachaBanner):
    SIX_STAR_RATE = 0.02
    FIVE_STAR_RATE = 0.10
    def __init__(
        self,
        name: str,
        rateups: dict,
    ) -> None:
        pass
