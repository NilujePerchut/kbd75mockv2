#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net, POWER
from sch_utils import unit_map_on_he10, run_unit

from src.regulator import regulator


def unit_regulator():
    """Unit test the power stage"""
    # Input signals & connector

    power = {"v5v": Net("V5V"), "gnd": Net("GND")}
    power["v5v"].drive = POWER
    power["gnd"].drive = POWER

    in_signals = {**power}
    unit_map_on_he10(in_signals.values())

    power = regulator(power)

    out_signals = {**power}
    unit_map_on_he10(out_signals.values())


if __name__ == "__main__":
    run_unit(unit_regulator)
