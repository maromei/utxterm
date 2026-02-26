from __future__ import annotations
import re
from typing import Callable, assert_never
from functools import partial
from enum import StrEnum, auto
from dataclasses import dataclass

from utxterm._colors import ColorDict, AnsiFormat, InvalidColor


@dataclass
class Tag:
    before: str
    content: str
    after: str

    tagname: str
    tagvalue: str | None

    @staticmethod
    def get_regex_pattern(tagname: str, boundary_str: str = "\u2502") -> str:
        return (
            f"(?<={boundary_str})(?P<before>[^{boundary_str}]*?)"
            f"<(?P<tagname>{tagname})(:(?P<tagvalue>[^>]*?))?>"
            f"(?P<content>[^{boundary_str}]*?)"
            f"</{tagname}>"
            f"(?P<after>[^{boundary_str}]*?)(?={boundary_str})"
        )

    @staticmethod
    def from_match(match: re.Match):
        return Tag(**match.groupdict())


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
    #: In case of uneven whitespace, the right side will contain one more
    #: space than the left side.
    #:
    #: # Example:
    #:
    #: | before <color:blue>Blue Text</color> after |
    #: | before           Blue Text           after |
    center_ws = auto()

    #: Centers the line within the bounds.
    #:
    #: # Example:
    #:
    #: | before <color:blue>Blue Text</color> after |
    #: |           before Blue Text after           |
    center_line = auto()

    @staticmethod
    def as_list() -> list[str]:
        return [mode.value for mode in ReplaceMode]

    @staticmethod
    def get_by_value(
        value: str, default: ReplaceMode | None = None
    ) -> ReplaceMode | None:
        for mode in ReplaceMode:
            if mode.value == value:
                return mode
        return default


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


def _replace_single_tag(
    match: re.Match,
    text_fmt_func: Callable[[str, str|None],str,],
    mode: ReplaceMode,
) -> str:  # fmt: skip
    tag: Tag = Tag.from_match(match)

    content: str = text_fmt_func(tag.content, tag.tagvalue)

    match mode:
        case ReplaceMode.simple:
            num_left_spaces: int = len("<>") + len(tag.tagname)
            if tag.tagvalue is not None:
                num_left_spaces += len(":") + len(tag.tagvalue)
            left_spaces: str = " " * num_left_spaces
            right_spaces: str = " " * (len("</>") + len(tag.tagname))

            return (
                f"{tag.before}{left_spaces}{content}{right_spaces}{tag.after}"
            )

        case ReplaceMode.align_left:
            num_spaces: int = len("<></>") + len(tag.tagname) * 2
            if tag.tagvalue is not None:
                num_spaces += len(":") + len(tag.tagvalue)
            spaces: str = " " * num_spaces
            return f"{tag.before}{content}{tag.after}{spaces}"

        case ReplaceMode.center_ws:
            num_spaces: int = len("<></>") + len(tag.tagname) * 2
            if tag.tagvalue is not None:
                num_spaces += len(":") + len(tag.tagvalue)
            num_spaces_left: int = num_spaces // 2
            num_spaces_right: int = num_spaces // 2

            if num_spaces % 2 == 1:
                num_spaces_right += 1

            left_spaces: str = " " * num_spaces_left
            right_spaces: str = " " * num_spaces_right

            return (
                f"{tag.before}{left_spaces}{content}{right_spaces}{tag.after}"
            )

        case ReplaceMode.center_line:
            num_spaces: int = len("<></>") + len(tag.tagname) * 2
            if tag.tagvalue is not None:
                num_spaces += len(":") + len(tag.tagvalue)

            trailing_spaces: re.Match | None = re.search(" *$", tag.after)
            leading_spaces: re.Match | None = re.search("^ *", tag.before)

            if trailing_spaces is not None:
                num_spaces += len(trailing_spaces.group(0))
                tag.after = tag.after.rstrip()

            if leading_spaces is not None:
                num_spaces += len(leading_spaces.group(0))
                tag.before = tag.before.lstrip()

            num_spaces_left: int = num_spaces // 2
            num_spaces_right: int = num_spaces // 2

            if num_spaces % 2 == 1:
                num_spaces_right += 1

            left_spaces: str = " " * num_spaces_left
            right_spaces: str = " " * num_spaces_right

            return (
                f"{left_spaces}{tag.before}{content}{tag.after}{right_spaces}"
            )

        case _:
            assert_never(mode)


def _re_sub_single_tag(
    content: str,
    tag: str,
    text_fmt_func: Callable[[str, str|None],str,],
    mode: ReplaceMode,
) -> str:  # fmt: skip
    replace_fnc = partial(
        _replace_single_tag, text_fmt_func=text_fmt_func, mode=mode
    )

    pattern: str = Tag.get_regex_pattern(tagname=tag)
    content = re.sub(pattern, replace_fnc, content)
    return content


def replace_bold(content: str, mode: ReplaceMode) -> str:
    return _re_sub_single_tag(
        content=content,
        tag="b",
        text_fmt_func=AnsiFormat.bold,
        mode=mode,
    )


def replace_italic(content: str, mode: ReplaceMode) -> str:
    return _re_sub_single_tag(
        content=content,
        tag="i",
        text_fmt_func=AnsiFormat.italic,
        mode=mode,
    )


def replace_underline(content: str, mode: ReplaceMode) -> str:
    return _re_sub_single_tag(
        content=content,
        tag="u",
        text_fmt_func=AnsiFormat.underline,
        mode=mode,
    )


def replace_strikethrough(content: str, mode: ReplaceMode) -> str:
    return _re_sub_single_tag(
        content=content,
        tag="s",
        text_fmt_func=AnsiFormat.strikethrough,
        mode=mode,
    )


def _replace_color_fmt(content: str, color_spec: str | None):
    if color_spec is None:
        raise ValueError("Used color tag without a color value")
    ansi_code = get_ansi_color(color_spec)
    return f"{ansi_code}{content}{AnsiFormat.reset_fg}"


def replace_color(content: str, mode: ReplaceMode) -> str:
    return _re_sub_single_tag(
        content=content,
        tag="color",
        text_fmt_func=_replace_color_fmt,
        mode=mode,
    )


def replace_single_sweep(content: str, mode: ReplaceMode) -> str:
    content = replace_bold(content, mode)
    content = replace_italic(content, mode)
    content = replace_underline(content, mode)
    content = replace_strikethrough(content, mode)
    content = replace_color(content, mode)
    return content


def replace_loop(content: str, mode: ReplaceMode) -> str:
    content_changed: bool = True
    while content_changed:
        new_content: str = replace_single_sweep(content, mode)
        content_changed = content == new_content
        content = new_content
    return content
