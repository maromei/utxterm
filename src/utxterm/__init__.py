from utxterm._argparse import setup_argparse, CliArgs
from utxterm._validate import generate_config, Config


def main():
    args: CliArgs = setup_argparse()
    config: Config = generate_config(args)
