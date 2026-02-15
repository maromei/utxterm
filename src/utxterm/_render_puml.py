import logging
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import assert_never, cast, Union
from tempfile import TemporaryDirectory

from utxterm._pumlcallable import (
    PlantumlCallable,
    NotAvailable,
    JarInWorkDir,
    InPath,
    CustomJarPath,
    PlantUmlNotAvailable,
)


LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class TempDirRenderedUtxt:
    temp_dir: TemporaryDirectory[str]
    filepath: Path


UtxtPath = Union[Path, TempDirRenderedUtxt]


def render_puml(filepath: Path, puml_callable: PlantumlCallable) -> UtxtPath:
    """Render a `.puml` file to a temporary directory.

    This function does not check whether the `filepath` is actually
    a `.puml` file. It is assumed to be validated already.
    """

    base_render_cmd: str
    match puml_callable:
        case NotAvailable():
            raise PlantUmlNotAvailable(
                "Cannot render the given `*.puml` file. "
                "Did not find a valid plantuml jar or command."
            )
        case JarInWorkDir(path) | CustomJarPath(path):
            # The cast below is only necessary because `ty` still fails to
            # to infer the type of values unpacked in a match statement.
            path: Path = cast(Path, path)
            base_render_cmd = f"java -jar {path.as_posix()}"
        case InPath():
            base_render_cmd = "plantuml"
        case _:
            assert_never(puml_callable)

    temp_dir: TemporaryDirectory[str] = TemporaryDirectory()
    temp_dir_str: str = str(temp_dir)
    render_cmd: str = (
        f"{base_render_cmd} --format utxt --output-dir {temp_dir_str}"
    )

    LOGGER.info(
        "Calling the following command to render the plantuml file: "
        f"'{render_cmd}'"
    )

    render_cmd_args: list[str] = render_cmd.split(" ")
    subprocess.check_call(render_cmd_args)

    generated_file: Path = Path(temp_dir_str) / f"{filepath.stem}.utxt"
    if not generated_file.exists():
        temp_dir.cleanup()
        raise FileNotFoundError(
            "Eventhough the plantuml render command successfully completed, "
            "the generate file could not be found "
            f"'{generated_file.as_posix()}'."
        )

    return TempDirRenderedUtxt(temp_dir, generated_file)
