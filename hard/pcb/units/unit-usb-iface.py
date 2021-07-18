#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from sch_utils import unit_map_on_he10, run_unit

from src.usb_iface import usb_iface


def unit_usb_iface():
    """Unit test the power stage"""
    # Input signals & connector

    power, usb = usb_iface()
    out_signals = {**power, **usb}
    unit_map_on_he10(out_signals.values())


if __name__ == "__main__":
    run_unit(unit_usb_iface)
