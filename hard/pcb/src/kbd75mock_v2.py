#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from skidl import KICAD, POWER
from skidl import lib_search_paths, ERC, generate_netlist, generate_xml

from src.usb_iface import usb_iface
from src.regulator import regulator
from src.stm32 import stm32
from src.key_matrix import key_matrix
from src.leds import per_key_leds, backlight_leds
from src.kle_parser import KeebLayout


KLE_JSON_FILE = "../rcs/v2.json"
BACKLIGHT_LEDS_LENGTH = 16


def main():
    """The main keyboard construction"""

    kl = KeebLayout(KLE_JSON_FILE)
    kl.parse()

    power, usb = usb_iface()
    power = regulator(power)
    power["v5v"].drive = POWER
    power["v33"].drive = POWER
    power["gnd"].drive = POWER
    ret = stm32(power, usb)
    key_matrix(kl.keys, ret["rows"], ret["cols"])
    per_key_leds(power, ret["per_key_leds_command"], kl.leds)
    backlight_leds(power, ret["backlight_leds_command"], BACKLIGHT_LEDS_LENGTH)


if __name__ == "__main__":
    lib_search_paths[KICAD].append(os.environ["KIPRJLIB"])
    main()
    ERC()
    generate_netlist()
    generate_xml()


