from dataclasses import dataclass
from typing import Union


@dataclass
class LinkConfig:
    ip: str
    mask: int


@dataclass
class Link:
    source_port: int
    destination_name: str
    config: Union[LinkConfig, None]
