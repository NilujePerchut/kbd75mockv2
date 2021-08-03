#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from skidl.net import NCNet
from sch_utils import dop_part

from src.kle_parser import ELECTRICAL_LAYOUT_DUPLICATED

def key_matrix(keys, rows, cols):
    """The keyboard key matrix"""

    done = []

    for key in keys:
        width = key.params.get("w", 1)
        if key.label == "ENTERISO":
            package_name = "SW_Cherry_MX_ISOEnter_PCB"
        else:
            package_name = F"SW_Cherry_MX_{width:.02f}u_PCB"
        key_symb = dop_part("SW_PUSH", package_name, value=key.label)

        done.append(key.label)
        dup = ELECTRICAL_LAYOUT_DUPLICATED.get(key.label, None)
        ecol = key.electrical_col
        erow = key.electrical_row
        anode_net_name = F"COL{ecol}_ROW{erow}_ANODE"
        key_symb[2] += cols[ecol]
        if (dup is not None) and (dup in done):
            key_symb[1] += Net.get(anode_net_name)
        else:
            diode = dop_part("D", "D_SOD-123F", value=key.label,
                            fields={"Reference": "1N4148W",
                                        "JLCC": "C81598", "JLROT": "0"})
            key_symb[1] & Net(anode_net_name) & diode[2,1] & rows[erow]