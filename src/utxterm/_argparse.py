import argparse
from typing import Any
from dataclasses import dataclass

from utxterm._replace_formatting import ReplaceMode


@dataclass
class CliArgs:
    filepath: str
    verbose: bool
    mode: ReplaceMode


def setup_argparse() -> CliArgs:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="utxt",
        description=(
            "View ASCII-based or unicode-based puml diagrams "
            "in your terminal with color."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "filepath",
        type=str,
        help=(
            "The file view. If it has the file extension `.puml`, "
            "it will first be rendered."
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    parser.add_argument(
        "-m",
        "--mode",
        default=ReplaceMode.align_left.value,
        choices=ReplaceMode.as_list(),
        help=(
            "Defines how the Tags definining the style are replaced.\n"
            "\n"
            "# simple\n"
            "\n"
            "Simply replace every formatting sequence with a space.\n"
            "\n"
            "| before <color:blue>Blue Text</color> after |\n"
            "| before             Blue Text         after |\n"
            "\n"
            "# align_left\n"
            "\n"
            "The replacement whitespace with will be added to the right of\n"
            "**all following** text.\n"
            "\n"
            "| before <color:blue>Blue Text</color> after |\n"
            "| before Blue Text after                     |\n"
            "\n"
            "# center_ws\n"
            "\n"
            "Centers the text **within** the replacement whitespace.\n"
            "In case of uneven whitespace, the right side will contain one\n"
            "more space than the left side.\n"
            "\n"
            "| before <color:blue>Blue Text</color> after |\n"
            "| before           Blue Text           after |\n"
            "\n"
            "# center_line\n"
            "\n"
            "Centers the line within the bounds.\n"
            "\n"
            "| before <color:blue>Blue Text</color> after |\n"
            "|           before Blue Text after           |\n"
        )
    )

    args: argparse.Namespace = parser.parse_args()
    args_dict: dict[str, Any] = vars(args)

    # The following error checks should never happen due to the parser
    # alredy checking for the errors.
    # Still done here to not assume errors.
    mode_str: str | None = args_dict.get("mode")
    if mode_str is None:
        raise ValueError("No 'mode' setting passed by the argument parser.")
    mode: ReplaceMode | None = ReplaceMode.get_by_value(mode_str)
    if mode is None: 
        raise ValueError("Invalid mode passed")
    args_dict["mode"] = mode

    cli_args: CliArgs = CliArgs(**args_dict)

    return cli_args
