from pathlib import Path
import os
from typing import Tuple


def get_jpg_names(folder: str | Path) -> set[str]:
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError(f"La carpeta no existe: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"No es una carpeta: {path}")

    result: set[str] = set()
    with os.scandir(path) as it:
        for entry in it:
            if not entry.is_file():
                continue
            if not entry.name.lower().endswith(".jpg"):
                continue

            stem = os.path.splitext(entry.name)[0]
            if stem.lower().endswith("_ch"):
                stem = stem[:-3]
            result.add(stem)
    return result


def get_base_and_ch(folder: str | Path) -> Tuple[set[str], set[str]]:
    """Devuelve (base_itmrefs, ch_itmrefs) donde ch_itmrefs son los ITMREF que tienen *_ch.jpg."""
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError(f"La carpeta no existe: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"No es una carpeta: {path}")

    base: set[str] = set()
    ch: set[str] = set()

    with os.scandir(path) as it:
        for entry in it:
            if not entry.is_file():
                continue
            if not entry.name.lower().endswith(".jpg"):
                continue

            stem = os.path.splitext(entry.name)[0]
            if stem.lower().endswith("_ch"):
                ch.add(stem[:-3])
            else:
                base.add(stem)

    return base, ch
