import logging
import subprocess
from shutil import rmtree
from pathlib import Path
from dataclasses import dataclass
from typing import assert_never, cast, Union, Self
from tempfile import mkdtemp

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
    temp_dir: str
    filepath: Path

    def cleanup(self):
        rmtree(self.temp_dir, ignore_errors=True)


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

    temp_dir_str: str = mkdtemp()
    render_cmd: str = (
        f"{base_render_cmd} --format utxt --output-dir {temp_dir_str} "
        f"{filepath.as_posix()}"
    )

    LOGGER.info(
        "Calling the following command to render the plantuml file: "
        f"'{render_cmd}'"
    )

    render_cmd_args: list[str] = render_cmd.split(" ")
    subprocess.check_call(render_cmd_args)

    generated_file: Path = Path(temp_dir_str) / f"{filepath.stem}.utxt"
    temp_dir: TempDirRenderedUtxt = TempDirRenderedUtxt(
        temp_dir_str, generated_file
    )
    if not generated_file.exists():
        temp_dir.cleanup()
        raise FileNotFoundError(
            "Eventhough the plantuml render command successfully completed, "
            "the generate file could not be found "
            f"'{generated_file.as_posix()}'."
        )

    return temp_dir
