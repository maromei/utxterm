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
