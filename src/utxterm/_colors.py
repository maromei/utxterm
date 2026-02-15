from enum import Enum
from typing import Final, assert_never


class Colors(Enum):
    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37

    grey = 90
    gray = 90

    brightred = 91
    brightgreen = 92
    brightyellow = 93
    brightblue = 94
    brightmagenta = 95
    brightcyan = 96
    brightwhite = 97


ColorDict: Final[dict[str, int]] = {color.name: color.value for color in Colors}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip("#")
    assert len(value) == 6
    hex_strs: tuple[str, str, str] = (value[0:2], value[2:4], value[4:6])
    rgbs: tuple[int, int, int] = (
        int(hex_strs[0], 16),
        int(hex_strs[1], 16),
        int(hex_strs[2], 16),
    )
    return rgbs


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    """Return color as #rrggbb for the given color values."""
    return "#%02x%02x%02x" % (red, green, blue)


class InvalidColor(Exception):
    pass


class AnsiFormat:

    reset_fg: Final[str] = "\033[39m"

    @staticmethod
    def color(color: int | Colors) -> str:
        color_num: int
        match color:
            case int():
                color_num = color
            case Colors():
                color_num = color.value
            case _:
                assert_never(color)

        return f"\033[{color_num}m"

    @staticmethod
    def truecolor(hexcolor: str) -> str:
        r, g, b = hex_to_rgb(hexcolor)
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bold(content: str) -> str:
        return f"\033[1m{content}\033[22m"

    @staticmethod
    def underline(content: str) -> str:
        return f"\033[4m{content}\033[24m"

    @staticmethod
    def italic(content: str) -> str:
        return f"\033[3m{content}\033[23m"

    @staticmethod
    def strikethrough(content: str) -> str:
        return f"\033[9m{content}\033[29m"
