#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pcbnew
import argparse
from math import trunc
from pcbnew import FromMM, wxPoint

from src.kle_parser import KeebLayout
from src.kle_parser import get_led_row


KLE_JSON_FILE = "rcs/v2.json"
TOP_LEFT = (FromMM(75.0), FromMM(100.0))
U1 = FromMM(19.05)


def create_assoc_map(layout, pcb):
    """Create a big struct which gathers switch, capa, diode, led"""
    ret = {}
    bl = {}
    for module in pcb.GetModules():
        lib_name = str(module.GetFPID().GetLibItemName())
        label = module.GetValue()

        if "Cherry_MX" in lib_name:
            prop = "switch"
        elif "D_SOD-123F" in lib_name:
            prop = "diode"
        elif "SK6812-MINI-E" in lib_name:
            prop = "led"
        elif "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm" in lib_name:
            bl[label] = module
            continue
        else:
            continue

        if label not in ret.keys():
            key = layout.get_key_from_label(label)
            ret[label] = {"key": key, "switch": None, "diode": None,
                          "led": None}
        ret[label][prop] = module
    return ret, bl


def place_key(label, assoc):
    """Place the key on the pcb"""
    key = assoc["key"]
    module = assoc["switch"]
    w = key.params.get("w", 1)
    adjx = [0, (w-1.0)/2.0][w>1]
    adjy = [0, FromMM(9.5)][label=="ENTERISO"] # ENTER ISO should be lowered
    posx = TOP_LEFT[0]+key.pcb_pos_x*U1 + adjx*U1
    posy = TOP_LEFT[1]+key.pcb_pos_y*U1 + adjy
    module.SetPosition(wxPoint(posx, posy))
    # Also place a label with the key name
    text = pcbnew.TEXTE_MODULE(module)
    pos = module.GetPosition()
    pos.x -= FromMM(2*1.27)
    pos.y += FromMM(10.5*1.27)
    text.SetPosition(pos)
    text.SetVisible(True)
    text.SetText(label)
    module.Add(text)


def place_led(label, assoc):
    """Place the led"""
    switch = assoc["switch"]
    led = assoc["led"]
    if led is None:
        return
    key = assoc["key"]
    pos = switch.GetPosition()
    pos.x -= FromMM(3*3.4/4) 
    pos.y += FromMM(9)
    led.SetPosition(pos)
    led.Flip(led.GetCenter())
    if (get_led_row(label)%2) == 1:
        # Return the LED to allow chain connection
        led.SetOrientation(180*10)
        # Need to rotate the designator too
        led.Reference().SetTextAngle(180*10)
    else:
        # Need to push designator down to avoid the switch main hole
        pos = led.Reference().GetPosition()
        pos.y += FromMM(4.2)
        led.Reference().SetPosition(pos)


def place_diode(label, assoc):
    """Place the diode"""
    diode = assoc["diode"]
    if diode is None:
        return
    switch = assoc["switch"]
    pos = switch.GetPosition()
    pos.x += FromMM(2.5)
    pos.y += FromMM(1.45)
    diode.SetPosition(pos)
    diode.Flip(diode.GetCenter())
    diode.SetOrientation(90*10)


def place_backlight(backlight_assoc):
    """Place the backlight diodes"""
    pos = wxPoint(*TOP_LEFT)
    pos.x += FromMM(7)
    pos.y += FromMM(14.5)
    labels = sorted(backlight_assoc.keys(), key=lambda x: int(x[3:]))
    for i, label in enumerate(labels):
        module = backlight_assoc[label]
        module.SetPosition(pos)
        module.Flip(module.GetCenter())
        if i < 7:
            pos.x += 2 * U1
            module.SetOrientation(180*10)
        elif i == 7:
            pos.y += 4 * U1
            module.SetOrientation(180*10)
        else:
            pos.x -= 2 * U1


def place(unplaced, placed, layout):
    """Place every stuff"""
    pcb = pcbnew.LoadBoard(unplaced)
    am, bl = create_assoc_map(layout, pcb) 
    for label, assoc in am.items():
        place_key(label, assoc)
        place_led(label, assoc)
        place_diode(label, assoc)
    place_backlight(bl)

    pcbnew.SaveBoard(placed, pcb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("unplaced_pcb", help="The unplaced pcb path")
    parser.add_argument("placed_pcb", help="The placed pcb path")
    args = parser.parse_args()

    kl = KeebLayout(KLE_JSON_FILE)
    kl.parse()

    place(args.unplaced_pcb, args.placed_pcb, kl)