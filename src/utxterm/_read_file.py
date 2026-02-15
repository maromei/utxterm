import logging
from pathlib import Path
from typing import assert_never

from utxterm._render_puml import UtxtPath, TempDirRenderedUtxt


LOGGER: logging.Logger = logging.getLogger(__name__)


def read_utxt_content(utxt_path: UtxtPath) -> str:
    """Read the content of the given path.

    Will delete the temporary directory if `utxt_path` is of type
    `TempDirRenderedUtxt`.

    No validation on the existance of the files are done.
    It is assumed to exist and be validated.
    """

    content: str
    match utxt_path:
        case Path() as filepath:
            with open(filepath, "r") as f:
                content = f.read()
        case TempDirRenderedUtxt():
            with open(utxt_path.filepath, "r") as f:
                content = f.read()
            utxt_path.cleanup()
            LOGGER.info(
                "Deleted the temporary directory after "
                "reading the file content."
            )
        case _:
            assert_never(utxt_path)

    return content
