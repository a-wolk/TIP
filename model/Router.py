from dataclasses import dataclass
from typing import List

from model.Device import Device


class RouterConfig:
    pass


@dataclass
class OSPFConfig(RouterConfig):
    pass


@dataclass
class RIPConfig(RouterConfig):
    pass


@dataclass
class StaticRoute:
    network_ip: str
    mask: str
    gateway_ip: str
    interface: int


@dataclass
class StaticConfig(RouterConfig):
    routes: List[StaticRoute]


@dataclass
class Router(Device):
    configs: list[RouterConfig]
