from __future__ import annotations

from pathlib import Path


class YEPError(Exception):
    def __init__(self, error: str, yep_file: Path, yep_number: int | None = None):
        super().__init__(error)
        self.filename = yep_file
        self.number = yep_number

    def __str__(self):
        error_msg = super(YEPError, self).__str__()
        error_msg = f"({self.filename}): {error_msg}"
        yep_str = f"YEP {self.number}"
        return f"{yep_str} {error_msg}" if self.number is not None else error_msg
