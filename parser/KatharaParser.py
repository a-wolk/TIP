from typing import List

from Kathara.model.Lab import Lab
from Kathara.parser.netkit.LabParser import LabParser
from Kathara.model.Machine import Machine
from enum import Enum

from model.Device import Device
from model.Host import Host
from model.Link import Link
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
        for machine in lab.machines.values():
            print(machine.name, machine.get_image())
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
        return [
            Switch(
                link.name,
                [
                    Link(
                        source_port,
                        machine.name,
                        None
                    ) for source_port, machine in enumerate(link.machines.values())
                ]
            ) for link in lab.links.values() if len(link.machines) > 1
        ]

    @staticmethod
    def parse_hosts(lab: Lab) -> List[Host]:
        return [
            Host(
                machine.name,
                [
                    Link(
                        source_port,
                        link.name if len(link.machines) > 1 else link.machines[0].name,
                        # Link z więcej niż jednym połączeniem jest switchem
                        None
                    ) for source_port, link in machine.interfaces.items()
                ]
            ) for machine in lab.machines.values() if KatharaParser.detect_device_type(machine) == DeviceType.HOST
        ]

    @staticmethod
    def parse_routers(lab: Lab) -> List[Router]:
        return [
            Router(
                machine.name,
                [
                    Link(
                        source_port,
                        link.name if len(link.machines) > 1 else link.machines[0].name,
                        None
                    ) for source_port, link in machine.interfaces.items()
                ],
                KatharaParser.parse_router_config(machine)
            ) for machine in lab.machines.values() if KatharaParser.detect_device_type(machine) == DeviceType.ROUTER
        ]

    @staticmethod
    def parse_router_config(machine: Machine) -> List[RouterConfig]:
        return [
            StaticConfig([])
        ]
