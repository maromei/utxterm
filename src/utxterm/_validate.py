import os
import logging
from shutil import which
from pathlib import Path
from dataclasses import dataclass

from utxterm._argparse import CliArgs
from utxterm._pumlcallable import (
    PlantumlCallable,
    JarInWorkDir,
    NotAvailable,
    InPath,
)


LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    filepath: Path
    is_puml: bool
    plantuml_callable: PlantumlCallable


def _validate_filepath(filepath: str) -> Path:
    path: Path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(filepath)
    if os.path.isdir(path):
        raise IsADirectoryError(filepath)
    return path


def _is_puml(filepath: Path) -> bool:
    suffix: str = filepath.suffix
    return suffix == ".puml"


def _is_plantuml_available() -> PlantumlCallable:
    """Check if plantuml can be called.

    The checks - and plantuml calling preference are done in the

    following order:

    1. `plantuml.jar` in the current working directory.
    2. `plantuml` command in the path.
    """

    ### Plantuml.jar in currnt directory ###

    LOGGER.info(
        "Checking if `plantuml.jar` is found in the current working directory."
    )
    LOGGER.info(f"Current Workingdir: '{os.curdir}'.")

    files: list[str] = os.listdir(os.curdir)
    puml_files: list[str] = [f for f in files if f.lower() == "plantuml.jar"]

    if len(puml_files) != 0:
        files_str: str = ",".join(puml_files)
        selected_puml_file: str = puml_files[0]
        puml_path: Path = Path(selected_puml_file).resolve()

        LOGGER.info(f"Found {len(puml_files)} file(s): {files_str}")
        LOGGER.info(f"Using '{selected_puml_file}'.")

        return JarInWorkDir(puml_path)

    ### Check for plantuml command in path

    LOGGER.info("Checking if the `plantuml` command is available in the path.")

    which_check: str | None = which("plantuml")
    if which_check is not None:
        LOGGER.info(f"Found the following command: '{which_check}'.")
        return InPath()

    LOGGER.info("Found no available plantuml executable.")
    return NotAvailable()


def generate_config(args: CliArgs) -> Config:
    LOGGER.info("Validating Filepath.")
    filepath: Path = _validate_filepath(args.filepath)
    is_puml: bool = _is_puml(filepath)
    if is_puml:
        LOGGER.info("The given filepath is of type `puml`.")
    plantuml_callable: PlantumlCallable = _is_plantuml_available()
    config: Config = Config(
        filepath=filepath, is_puml=is_puml, plantuml_callable=plantuml_callable
    )
    return config
