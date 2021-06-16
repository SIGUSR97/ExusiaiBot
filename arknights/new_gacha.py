from typing import Optional


class Gacha:
    def __init__(self, banner_name: Optional[str] = None) -> None:
        self.load_banner(banner_name)

    def load_banner(self, banner_name: Optional[str]) -> None:
        pass