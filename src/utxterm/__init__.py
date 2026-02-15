import logging

from utxterm._argparse import setup_argparse, CliArgs
from utxterm._validate import generate_config, Config


def main():
    args: CliArgs = setup_argparse()
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="[%(levelname)s] %(message)s "
        )
    config: Config = generate_config(args)
