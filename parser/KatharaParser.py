from typing import List, Dict

from Kathara.model.Lab import Lab
from Kathara.parser.netkit.LabParser import LabParser
from Kathara.model.Machine import Machine
from Kathara.model.Link import Link as KatharaLink
from enum import Enum

from model.Device import Device
from model.Host import Host
from model.Link import Link, LinkConfig
from model.Router import Router, RouterConfig, StaticConfig
from model.Switch import Switch


class DeviceType(Enum):
    HOST = 0
    ROUTER = 1
    SWITCH = 2


class KatharaParser:
    @staticmethod
    def parse(path: str) -> List[Device]:
        lab = LabParser.parse(path)
        switches: List[Device] = KatharaParser.parse_switches(lab)
        hosts: List[Device] = KatharaParser.parse_hosts(lab)
        routers: List[Device] = KatharaParser.parse_routers(lab)
        return switches + hosts + routers

    @staticmethod
    def detect_device_type(machine: Machine) -> DeviceType:
        if machine.get_image() == "kathara/quagga":
            return DeviceType.ROUTER
        else:
            return DeviceType.HOST

    @staticmethod
    def parse_switches(lab: Lab) -> List[Switch]:
        switches = []
        for link in filter(lambda l: len(l.machines) > 2, lab.links.values()):
            switches.append(
                Switch(
                    link.name,
                    [
                        Link(
                            source_port,
                            machine.name,
                            None
                        ) for source_port, machine in enumerate(link.machines.values())
                    ]
                )
            )
        return switches

    @staticmethod
    def parse_hosts(lab: Lab) -> List[Host]:
        hosts = []
        for machine in filter(lambda m: KatharaParser.detect_device_type(m) == DeviceType.HOST, lab.machines.values()):
            link_configs = KatharaParser.parse_ip_config(machine)
            hosts.append(
                Host(
                    machine.name,
                    [
                        Link(
                            source_port,
                            link.name if len(link.machines) > 2 else KatharaParser.get_link_destination(machine.name, link),
                            link_configs[source_port]
                        ) for source_port, link in machine.interfaces.items()
                    ]
                )
            )
        return hosts

    @staticmethod
    def parse_routers(lab: Lab) -> List[Router]:
        routers = []
        for machine in filter(lambda m: KatharaParser.detect_device_type(m) == DeviceType.ROUTER, lab.machines.values()):
            link_configs = KatharaParser.parse_ip_config(machine)
            routers.append(
                Router(
                    machine.name,
                    [
                        Link(
                            source_port,
                            link.name if len(link.machines) > 2 else KatharaParser.get_link_destination(machine.name, link),
                            link_configs[source_port]
                        ) for source_port, link in machine.interfaces.items()
                    ],
                    KatharaParser.parse_router_config(machine)
                )
            )
        return routers

    # use when link has only two machines
    @staticmethod
    def get_link_destination(source: str, link: KatharaLink) -> str:
        for machine in link.machines:
            if machine != source:
                return machine

    @staticmethod
    def parse_router_config(machine: Machine) -> List[RouterConfig]:
        return [
            StaticConfig([])
        ]

    @staticmethod
    def parse_ip_config(machine: Machine) -> Dict[int, LinkConfig]:
        link_configs: Dict[int, LinkConfig] = {}
        if machine.lab.fs.exists(f"{machine.name}.startup"):
            with machine.lab.fs.open(f"{machine.name}.startup", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if not line.startswith("ifconfig"):
                        continue
                    tokens = line.split(" ")
                    port = int(tokens[1][3:]) # remove "eth"
                    ip_with_mask = tokens[2]
                    ip_with_mask = ip_with_mask.split("/")
                    ip = ip_with_mask[0]
                    mask = int(ip_with_mask[1])
                    link_configs.update([(port, LinkConfig(ip, mask))])
        return link_configs
