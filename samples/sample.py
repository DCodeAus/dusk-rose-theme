"""Preview file: open in VS Code to see Rosé All Night on Python."""
from dataclasses import dataclass
import json

MAX_LAPS = 161  # a constant


@dataclass
class Driver:
    name: str
    number: int

    def describe(self, prefix: str = "#") -> str:
        # f-strings, escapes and self
        return f"{prefix}{self.number} {self.name}\n"


def fastest(laps: list[float]) -> float | None:
    if not laps:
        return None
    return min(laps)


data = json.loads('{"driver": "Example", "laps": [128.4, 127.9]}')
print(Driver("Example", 88).describe(), fastest(data["laps"]), True, MAX_LAPS)
