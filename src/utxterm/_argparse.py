import argparse
from typing import Any
from dataclasses import dataclass


@dataclass
class CliArgs:
    filepath: str


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

    args: argparse.Namespace = parser.parse_args()
    args_dict: dict[str, Any] = vars(args)
    cli_args: CliArgs = CliArgs(**args_dict)

    return cli_args
