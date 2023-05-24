from dataclasses import dataclass
from typing import Tuple, List

from model.Link import Link


@dataclass
class Device:
    name: str
    links: List[Link]
