import re
from typing import Callable
from enum import StrEnum, auto

from utxterm._colors import ColorDict, AnsiFormat, InvalidColor


class ReplaceMode(StrEnum):

    #: Simply replace every formatting sequence with a space.
    #:
    #: # Example:
    #:
    #: | before <color:blue>Blue Text</color> after |
    #: | before             Blue Text         after |
    simple = auto()

    #: The replacement whitespace with will be added to the right of the
    #: **all following** text.
    #:
    #: # Example:
    #:
    #: | before <color:blue>Blue Text</color> after |
    #: | before Blue Text after                     |
    align_left = auto()

    #: Centers the text **within** the replacement whitespace.
    #:
    #: # Example:
    #:
    #: | before <color:blue>Blue Text</color> after |
    #: | before           Blue Text           after |
    center = auto()


def get_ansi_color(color_spec: str) -> str:
    color_spec = color_spec.lower()

    ansi_color_code: int | None = ColorDict.get(color_spec)
    if ansi_color_code is not None:
        return AnsiFormat.color(ansi_color_code)

    if color_spec.startswith("#") and len(color_spec) == 7:
        return AnsiFormat.truecolor(color_spec)

    raise InvalidColor(
        f"Could not convert the color spec '{color_spec}' to an "
        "ANSII terminal format."
    )


def _replace_single_arg_match(
    match: re.Match,
    num_replacement_spaces: int,
    text_fmt_func: Callable[[str,],str,],
) -> str:  # fmt: skip
    text: str = match.group(1)

    all_groups: list[str | None] = list(match.groups())
    all_groups = all_groups[1:]
    all_groups: list[str] = [grp for grp in all_groups if grp is not None]

    other_content: str = "".join(all_groups)

    replacement_spaces: str = " " * num_replacement_spaces
    fmt_text: str = text_fmt_func(text)

    return f"{fmt_text}{other_content}{replacement_spaces}"


def replace_bold(match: re.Match) -> str:
    return _replace_single_arg_match(
        match=match,
        num_replacement_spaces=7,
        text_fmt_func=AnsiFormat.bold,
    )


def replace_italic(match: re.Match) -> str:
    return _replace_single_arg_match(
        match=match,
        num_replacement_spaces=7,
        text_fmt_func=AnsiFormat.italic,
    )


def replace_underline(match: re.Match) -> str:
    return _replace_single_arg_match(
        match=match,
        num_replacement_spaces=7,
        text_fmt_func=AnsiFormat.underline,
    )


def replace_strikethrough(match: re.Match) -> str:
    return _replace_single_arg_match(
        match=match,
        num_replacement_spaces=7,
        text_fmt_func=AnsiFormat.strikethrough,
    )


def replace_color(match: re.Match) -> str:
    color_spec = match.group(1)
    content = match.group(2)
    ansi_code = get_ansi_color(color_spec)

    all_groups: list[str | None] = list(match.groups())
    all_groups = all_groups[2:]
    all_groups: list[str] = [grp for grp in all_groups if grp is not None]

    other_content: str = "".join(all_groups)

    replacement_spaces: str = " " * (16 + len(color_spec))

    return (
        f"{ansi_code}{content}{AnsiFormat.reset_fg}"
        f"{other_content}{replacement_spaces}"
    )


def replace_single_sweep(content: str) -> str:
    content = re.sub(r"<b>(.*?)</b>(.*?)(?=\u2502)", replace_bold, content)
    content = re.sub(r"<i>(.*?)</i>(.*?)(?=\u2502)", replace_italic, content)
    content = re.sub(r"<u>(.*?)</u>(.*?)(?=\u2502)", replace_underline, content)
    content = re.sub(
        r"<s>(.*?)</s>(.*?)(?=\u2502)", replace_strikethrough, content
    )
    content = re.sub(
        r"<color:(.*?)>(.*?)</color>(.*?)(?=\u2502)",
        replace_color,
        content,
    )
    return content


def replace_loop(content: str) -> str:
    content_changed: bool = True
    while content_changed:
        new_content: str = replace_single_sweep(content)
        content_changed = content == new_content
        content = new_content
    return content
