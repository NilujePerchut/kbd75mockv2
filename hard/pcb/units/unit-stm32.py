#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net, POWER
from sch_utils import unit_map_on_he10, run_unit

from src.stm32 import stm32


def unit_stm32():
    """Unit test the stm32 stage"""
    # Input signals & connector
    power = {"v33": Net("V33"), "gnd": Net("GND")}
    power["v33"].drive = POWER
    power["gnd"].drive = POWER
    usb = {"usb_n": Net("USB_N"), "usb_p": Net("USB_P")}
    in_nets = {**power, **usb}
    unit_map_on_he10(in_nets.values())

    res = stm32(power, usb)

    out_signals = [res["per_key_leds_command"],
                   res["backlight_leds_command"]] + \
                  res["rows"] + res["cols"]
    unit_map_on_he10(out_signals)


if __name__ == "__main__":
    run_unit(unit_stm32)
