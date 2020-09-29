import re
from typing import Union

from numpy import ndarray
from numpy.random import default_rng


class DiceError(Exception):
    """Base class for dice exceptions"""


class DiceCodeSyntaxError(DiceError):
    """Raised when dice code is invalid"""
    def __init__(
        self,
        dice_code: int,
        message: str = "Invalid dice code: {}",
    ) -> None:
        self.dice_code = dice_code
        self.message = message.format(self.dice_code)
        super().__init__(self.message)


class RepeatsValueError(DiceError):
    """Raised when repeats not in range of [1, max_repeats]"""
    def __init__(
        self,
        repeats: int,
        max_repeats: int,
        message: str = "{} repeats is not in range of [1, {}]",
    ) -> None:
        self.max_repeats = max_repeats
        self.repeats = repeats
        self.message = message.format(self.repeats, self.max_repeats)
        super().__init__(self.message)


class ThrowsValueError(DiceError):
    """Raised when throws not in range of [1, max_throws]"""
    def __init__(
        self,
        throws: int,
        max_throws: int,
        message: str = "{} throws is not in range of [1, {}]",
    ) -> None:
        self.max_throws = max_throws
        self.throws = throws
        self.message = message.format(self.throws, self.max_throws)
        super().__init__(self.message)


class SidesValueError(DiceError):
    """Raised when sides not in range of [1, max_sides]"""
    def __init__(
        self,
        sides: int,
        max_sides: int,
        message: str = "{} sides is not in range of [1, {}]",
    ) -> None:
        self.sides = sides
        self.max_sides = max_sides
        self.message = message.format(self.sides, self.max_sides)
        super().__init__(self.message)


class DiceNotRolledError(DiceError):
    """Raised when get_message is called when dice is not rolled"""
    def __init__(
        self,
        message: str = "Connot generate message before dice is rolled"
    ) -> None:
        self.message = message
        super().__init__(self.message)


class Dice:
    DICE_CODE_PAT = (
        r"(?:(?P<repeats>[0-9]+)#)?"
        r"(?:(?P<throws>[0-9]+)[dD](?P<sides>[0-9]+))"
        r"(?:[\*xX](?P<multiplier>[0-9]+))?"
        r"(?P<bonus>[\+-][0-9])?"
    ) # yapf: disable
    dice_code_regex = re.compile(DICE_CODE_PAT)
    default_formatter = "{dice_code}=\n{result}"
    rng = default_rng()
    rolled = False

    def __init__(
        self,
        max_line_length: int = 47,
        max_repeats: int = 10,
        max_throws: int = 100,
        max_sides: int = 1000,
        filler: str = "...",
    ) -> None:
        self.max_line_length = max_line_length
        self.max_repeats = max_repeats
        self.max_throws = max_throws
        self.max_sides = max_sides
        self.filler = filler

    def roll(self, dice_code: str):
        matched = self.dice_code_regex.fullmatch(dice_code)
        if not matched:
            raise DiceCodeSyntaxError(dice_code)
        self.dice_code = dice_code
        dice_options = {
            k: int(v) if v else v
            for k, v in matched.groupdict().items()
        }
        self._validate_and_set_dice_options(dice_options)

        throws = self.throws
        sides = self.sides
        repeats = self.repeats

        self.rolls = self.rng.integers(
            1,
            sides,
            size=(repeats, throws),
            endpoint=True,
        )
        if repeats == 1:
            self.rolls = self.rolls.flatten()

        self.rolled = True

    @classmethod
    def test_dice_code(
        cls,
        dice_code: str,
    ) -> bool:
        return cls.dice_code_regex.fullmatch(dice_code) is not None

    def get_message(
        self,
        formatter: str = default_formatter,
        formatter_data: dict = {},
    ) -> str:
        if not self.rolled: raise DiceNotRolledError()
        result = self._get_rolls_string()
        break_formatter = "{break}"
        formatted = formatter.format(
            **{
                "result": result,
                "repeats": self.repeats,
                "throws": self.throws,
                "sides": self.sides,
                "multiplier": self.multiplier,
                "bonus": self.bonus,
                "dice_code": self.dice_code,
                "break": break_formatter,
            }, **formatter_data)
        # break_ = "\n" if len(
        #     formatted) >= self.max_line_length - len("{break}") else ""
        res = ""
        for line in formatted.splitlines():
            if break_formatter in line:
                untagged_line = re.subn(r"</?\w+?>", "", line)
                break_ = "\n" if self.repeats > 1 or len(
                    untagged_line
                ) >= self.max_line_length - len(break_formatter) else ""
                res = f"{res}\n{line.format(**{'break': break_})}"
            else:
                res = f"{res}\n{line}"
        formatted = res
        # print(f"{break_=}, {len(formatted)=}")
        return formatted

    def _get_rolls_string(self) -> str:
        if self.repeats == 1:
            return self._get_roll_expression(
                nums=self.rolls,
                multiplier=self.multiplier,
                bonus=self.bonus,
            )
        else:
            return "\n".join([
                self._get_roll_expression(
                    nums=roll,
                    multiplier=self.multiplier,
                    bonus=self.bonus,
                ) for roll in self.rolls
            ])

    def _get_roll_expression(
        self,
        nums: ndarray,
        multiplier: Union[int, None],
        bonus: Union[int, None],
    ) -> str:
        result_exp = "+".join(map(str, nums))
        mult_part = bonus_part = sum_part = ""
        if multiplier is not None:
            mult_part = f"*{multiplier}"
            result_exp = f"({result_exp})"
        else:
            multiplier = 1
        if bonus is not None:
            bonus_part = f"+{bonus}"
        else:
            bonus = 1
        if len(nums) > 1 or mult_part or bonus_part:
            result = nums.sum() * multiplier + bonus
            sum_part = f"={result}"
        result_exp = f"{result_exp}{mult_part}{bonus_part}"
        if len(f"{result_exp}{sum_part}") > self.max_line_length:
            length = self.max_line_length - len(sum_part)
            result_exp = (
                f"{result_exp[:length // 2 - len(self.filler)]}"
                f"{self.filler}{result_exp[-(length // 2 + (length & 1)):]}")
        return f"{result_exp}{sum_part}"

    def _validate_and_set_dice_options(
        self,
        dice_options: dict,
    ) -> None:
        throws = dice_options["throws"]
        sides = dice_options["sides"]

        repeats = dice_options["repeats"]
        multiplier = dice_options["multiplier"]
        bonus = dice_options["bonus"]
        if repeats is not None and (repeats <= 0
                                    or repeats > self.max_repeats):
            raise RepeatsValueError(repeats, self.max_repeats)
        if throws <= 0 or throws > self.max_throws:
            raise ThrowsValueError(throws, self.max_throws)
        if sides <= 0 or sides > self.max_sides:
            raise SidesValueError(sides, self.max_sides)

        self.throws = throws
        self.sides = sides

        self.repeats = 1 if repeats is None else repeats
        self.multiplier = multiplier
        self.bonus = bonus


if __name__ == "__main__":
    dice = Dice()
    try:
        dice.roll("100#30d100*5+2")
    except RepeatsValueError as e:
        from pprint import pprint
        print(f"{e=}")
        pprint(dir(e))

    print(dice.get_message())
