from pathlib import Path

from snowx.api.logger import get_logger


LOGGER = get_logger("EventCounter")


class Counter:
    def __init__(self):
        self.count = 0

    def load(self, filepath: Path) -> None:
        if not filepath.is_file():
            return
        try:
            with open(filepath, "r") as f:
                self.count = max(0, int(f.read()))
        except Exception as e:
            LOGGER.error(f"Cannot load file <{str(filepath)}>", exc_info=e)

    def save(self, filepath: Path) -> None:
        try:
            with open(filepath, "w") as f:
                f.write(str(self.count))
        except Exception as e:
            LOGGER.error(f"Cannot save file <{str(filepath)}>", exc_info=e)

    def set(self, count: int) -> None:
        self.count = count

    def add(self) -> None:
        self.count += 1
