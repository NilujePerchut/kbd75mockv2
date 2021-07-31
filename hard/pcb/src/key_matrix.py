#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from skidl.net import NCNet
from sch_utils import dop_part


def key_matrix(keys, rows, cols):
    """The keyboard key matrix"""

    for key in keys:
        width = key.params.get("w", 1)
        if key.label == "ENTERISO":
            package_name = "SW_Cherry_MX_ISOEnter_PCB"
        else:
            package_name = F"SW_Cherry_MX_{width:.02f}u_PCB"
        key_symb = dop_part("SW_PUSH", package_name, value=key.label)

        diode = dop_part("D", "D_SOD-123F",
                         fields={"Reference": "1N4148W",
                                 "JLCC": "C81598", "JLROT": "0"})
        key_symb[2] += cols[key.electrical_col]
        key_symb[1] & diode[2,1] & rows[key.electrical_row]