#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from skidl.net import NCNet
from sch_utils import dop_part, bypass_cap, get_res, pull_updown
from sch_utils import get_capa


def per_key_leds(power, command, keys_by_led_iterator):
    """The LED chain"""

    # Command is in 3.3V, use a level shifter
    level_shifter = dop_part("SN74LV1T34", "SOT23-5",
                             fields={"descr": "3.3V -> 5V level shifter",
                                     "Reference": "SN74LV1T34DBVR",
                                     "JLCC": "C100024", "JLROT": "0"})
    current_command = Net()
    level_shifter["VCC"] += power["v5v"]
    level_shifter["GND"] += power["gnd"]
    level_shifter["A"] += command
    level_shifter["Y"] += current_command
    bypass_cap(power["v5v"], power["gnd"], ["100nF"],
                fields={"descr": "level_shifter", "JLCC": "C14663"})

    for key in keys_by_led_iterator:
        #bypass_cap(power["v5v"], power["gnd"], ["100nF"],
        #           fields={"descr": "leds", "JLCC": "C14663"})
        inst_led = dop_part("WS2812B", "SK6812-MINI-E", value=key.label,
                            fields = {"descr": F"LED_{key.label}"})

        inst_led["VDD"] += power["v5v"]
        inst_led["VSS"] += power["gnd"]
        inst_led["DIN"] += current_command
        current_command = Net()
        inst_led["DOUT"] += current_command

    # Cleans up the unconnected last DOUT
    inst_led["DOUT"].disconnect()
    inst_led["DOUT"] += NC
    default_circuit.rmv_nets(current_command)


def backlight_leds(power, command, chain_length, designator="BKL"):
    """Creates a backlight chain using SK6812-MINI-E leds"""
    class BackLightKey(object):
        def __init__(self, name):
            self.label = name

    bkls = [BackLightKey(F"{designator}{i}")
            for i in range(chain_length)]
    per_key_leds(power, command, bkls)

