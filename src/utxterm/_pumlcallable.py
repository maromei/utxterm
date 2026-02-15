from pathlib import Path
from typing import Union


class NotAvailable:
    pass


class JarInWorkDir(Path):
    pass


class InPath:
    pass


class CustomJarPath(Path):
    pass


PlantumlCallable = Union[NotAvailable, JarInWorkDir, InPath, CustomJarPath]


class PlantUmlNotAvailable(Exception):
    pass
