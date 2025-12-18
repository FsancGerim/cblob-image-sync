from pathlib import Path
import time
import os

def get_jpg_names(folder: str | Path) -> set[str]:
    path = Path(folder)

    if not path.exists():
        raise FileNotFoundError(f"La carpeta no existe: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"No es una carpeta: {path}")

    result = set()

    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file() and entry.name.lower().endswith(".jpg"):
                result.add(os.path.splitext(entry.name)[0])

    return result

if __name__ == "__main__":
    folder = r"\\192.168.1.82\srvfotos\Fotos\ImportadasPorNTV"

    start = time.perf_counter()

    jpgs = get_jpg_names(folder)

    end = time.perf_counter()

    print("JPGs encontrados:", len(jpgs))
    print("Tiempo total:", round(end - start, 2), "segundos")