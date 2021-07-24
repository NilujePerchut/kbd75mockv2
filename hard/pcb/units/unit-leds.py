#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net, POWER
from sch_utils import unit_map_on_he10, run_unit

from src.leds import leds


class FakeKey():
    def __init__(self, label):
        self.label = label


def unit_leds():
    """Unit test the LED chain"""
    # Input signals & connector
    power = {"v5v": Net("V5V"), "gnd": Net("GND")}
    power["v5v"].drive = POWER
    power["gnd"].drive = POWER
    command = Net("COMMAND")
    in_signals = list({**power}.values()) + [command]
    unit_map_on_he10(in_signals)

    iterator = [FakeKey(F"LED_{i}") for i in range(10)]

    leds(power, command, iterator)


if __name__ == "__main__":
    run_unit(unit_leds)
