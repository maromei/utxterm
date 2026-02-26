import logging

from utxterm._argparse import setup_argparse, CliArgs
from utxterm._validate import generate_config, Config
from utxterm._render_puml import render_puml, UtxtPath
from utxterm._read_file import read_utxt_content
from utxterm._replace_formatting import replace_loop


LOGGER: logging.Logger = logging.getLogger(__name__)


def main():
    args: CliArgs = setup_argparse()
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="[%(levelname)s] %(message)s "
        )
    config: Config = generate_config(args)

    utxt_path: UtxtPath = config.filepath
    if config.is_puml:
        LOGGER.info("Rendering the puml file.")
        utxt_path = render_puml(config.filepath, config.plantuml_callable)

    utxt_content: str = read_utxt_content(utxt_path)
    terminal_content: str = replace_loop(utxt_content, config.mode)

    print(terminal_content, end="")
