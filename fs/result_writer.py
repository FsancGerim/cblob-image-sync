from pathlib import Path
from datetime import datetime

class SyncResultWriter:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, status: str, itmref: str, path: Path | str, message: str = ""):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} | {status:<7} | {itmref} | {path} | {message}\n"
        self.file_path.open("a", encoding="utf-8").write(line)