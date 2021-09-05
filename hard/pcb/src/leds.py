#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from skidl.net import NCNet
from sch_utils import dop_part, bypass_cap, get_res, pull_updown
from sch_utils import get_capa


def per_key_leds(power, command, keys_by_led_iterator, backlight=False,
                 decoupling=False, alternate_command=None, returns=False):
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

    if alternate_command:
        cmd_sw = dop_part("CONN_01X03", "gs3_r")
        cmd_sw[1] += current_command
        cmd_sw[3] += alternate_command
        current_command = Net()
        cmd_sw[2] += current_command

    for key in keys_by_led_iterator:
        if decoupling:
            bypass_cap(power["v5v"], power["gnd"], ["100nF"],
                       fields={"descr": "leds", "JLCC": "C14663"})
        if backlight:
            package = "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm"
        else:
            package = "SK6812-MINI-E"
        inst_led = dop_part("WS2812B", package, value=key.label,
                            fields = {"descr": F"LED_{key.label}"})

        inst_led["VDD"] += power["v5v"]
        inst_led["VSS"] += power["gnd"]
        inst_led["DIN"] += current_command
        current_command = Net(F"LED_RGB_{key.label}")
        inst_led["DOUT"] += current_command

    if returns:
        return current_command
    else:
        # Cleans up the unconnected last DOUT
        inst_led["DOUT"].disconnect()
        inst_led["DOUT"] += NC
        default_circuit.rmv_nets(current_command)


def backlight_leds(power, command, chain_length, designator="BKL",
                   alternate_command=None):
    """Creates a backlight chain using SK6812-MINI-E leds"""
    class BackLightKey(object):
        def __init__(self, name):
            self.label = name

    bkls = [BackLightKey(F"{designator}{i}")
            for i in range(chain_length)]
    per_key_leds(power, command, bkls, backlight=True,
                 alternate_command=alternate_command)

