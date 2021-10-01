#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pcbnew
import argparse
from pcbnew import FromMM, FromMils, wxPoint

from route_utils import get_layer_table
from route_utils import get_pad_by_name
from route_utils import route_2_pads
from route_utils import get_net_by_name
from route_utils import create_via
from src.kle_parser import KeebLayout
from src.place import create_assoc_map


KLE_JSON_FILE = "rcs/v2.json"

SHEET_LEN = FromMM(410)
SHEET_HIGHT = FromMM(210)

# Plate dimensions
PLATE_X = FromMM(308)
PLATE_Y = FromMM(118)

# PCB dimensions
PCB_X = FromMM(302)
PCB_Y = FromMM(114.5)

BOUNDING_POLY_COMPENTATION = FromMM(0.2)
ARC_SEGMENT_COUNT = 50

U1 = FromMM(19.05)

# Case related constants
UP_THICKNESS = FromMM(10)
DOWN_THICKNESS = FromMM(3.8)
UPPER_CASE_TO_FIRST_FIX = FromMM(19.66)

# JLCPCB settings
JLCPCB_CAPABILITIES = {
    "TrackMinWidth": FromMils(3.5),
    "ViasMinSize": FromMM(0.4),
    "ViasMinDrill": FromMM(0.2),

    "Clearance": FromMils(5),
    "TrackWidth": FromMils(10),
    "ViaDiameter": FromMils(27),
    "ViaDrill": FromMils(13),
    "uViaDiameter": FromMils(27),
    "uViaDrill": FromMils(13),
    "DiffPairWidth": FromMM(0.229),
    "DiffPairGap": FromMM(0.154),
}


POWER_NET_CLASS = {
    "Clearance": FromMils(10),
    "TrackWidth": FromMils(30),
    "ViaDiameter": FromMils(45),
    "ViaDrill": FromMils(20),
    "uViaDiameter": FromMils(27),
    "uViaDrill": FromMils(13),
    "DiffPairWidth": FromMM(0.229),
    "DiffPairGap": FromMM(0.154),
}


def _get_module_boudingpoly(pcb, switches=False, usb_conn=False):
    """Return the outline of all the selected modules"""
    modules = []
    for module in pcb.GetModules():
        # Only consider Switches and USB connector for now
        lib_name = str(module.GetFPID().GetLibItemName())
        if switches and lib_name.startswith("SW_Cherry_MX"):
            modules.append(module)
        elif usb_conn and lib_name.startswith("USB_C"):
            modules.append(module)

    hull = modules[0].GetBoundingPoly()
    for m in modules[1:]:
        hull.BooleanAdd(m.GetBoundingPoly(), hull.PM_FAST)
    hull.Unfracture(hull.PM_FAST)
    hull.RemoveNullSegments()
    # Compensate GetBoundingPoly
    hull.Inflate(-BOUNDING_POLY_COMPENTATION, ARC_SEGMENT_COUNT)
    return hull


def _is_inside_sheet(point):
    """Return True if given point is located inside the sheet"""
    if point.x < 0:
        return False
    if point.x > SHEET_LEN:
        return False
    if point.y < 0:    
        return False
    if point.y > SHEET_HIGHT:    
        return False
    return True


def _draw_tracks_from_outline(pcb, outline, layer):
    """Draw track along an outline"""
    points = [outline.CPoint(i).getWxPoint()
              for i in range(outline.PointCount())]
    points = [point for point in points if _is_inside_sheet(point)]
    points.append(points[0])

    p1 = points[0]
    for p2 in points[1:]:
        seg = pcbnew.DRAWSEGMENT(pcb)
        pcb.Add(seg)
        seg.SetStart(p1)
        seg.SetEnd(p2)
        seg.SetLayer(layer)
        p1 = p2


def setup_pcb_options(pcb, profile):
    """Apply board options"""
    design_settings = pcb.GetDesignSettings()
    design_settings.SetCopperLayerCount(2)

    design_settings.m_TrackMinWidth = profile["TrackMinWidth"]
    design_settings.m_ViasMinSize = profile["ViasMinSize"]
    design_settings.m_ViasMinDrill = profile["ViasMinDrill"]

    # Default class (signals)
    default_class = design_settings.GetDefault()
    default_class.SetClearance(profile["Clearance"])
    default_class.SetTrackWidth(profile["TrackWidth"])
    default_class.SetViaDiameter(profile["ViaDiameter"])
    default_class.SetViaDrill(profile["ViaDrill"])
    default_class.SetuViaDiameter(profile["uViaDiameter"])
    default_class.SetuViaDrill(profile["ViaDrill"])
    default_class.SetDiffPairWidth(profile["DiffPairWidth"])
    default_class.SetDiffPairGap(profile["DiffPairGap"])

    # Power class (V5V, V33, GND)
    power_class = pcbnew.NETCLASSPTR("Power")
    power_class.SetClearance(POWER_NET_CLASS["Clearance"])
    power_class.SetTrackWidth(POWER_NET_CLASS["TrackWidth"])
    power_class.SetViaDiameter(POWER_NET_CLASS["ViaDiameter"])
    power_class.SetViaDrill(POWER_NET_CLASS["ViaDrill"])
    power_class.SetuViaDiameter(POWER_NET_CLASS["uViaDiameter"])
    power_class.SetuViaDrill(POWER_NET_CLASS["ViaDrill"])
    power_class.SetDiffPairWidth(POWER_NET_CLASS["DiffPairWidth"])
    power_class.SetDiffPairGap(POWER_NET_CLASS["DiffPairGap"])
    net_classes = design_settings.m_NetClasses
    net_names = power_class.NetNames()
    for net_name in ["VBUS", "V5V", "V33", "GND"]:
        net_names.append(net_name)
    net_classes.Add(power_class)

    pcb.SetDesignSettings(design_settings)
    # Call to BuildListOfNets id mandatory to populate new netclass members
    pcb.BuildListOfNets()


def draw_edge_cut(pcb):
    """Draws the edge cut."""
    hull = _get_module_boudingpoly(pcb, switches=True, usb_conn=True)
    outline = hull.Outline(0)
    edgecuts_layer = get_layer_table(pcb)["Edge.Cuts"]
    _draw_tracks_from_outline(pcb, outline, edgecuts_layer)


def route_diode_anode(pcb, am):
    """Route the diode anode to switch pin1"""
    for label, assoc in am.items():
        switch = assoc["switch"]
        diode = assoc["diode"]
        if (switch is None) or (diode is None):
            continue
        switch_pin1 = get_pad_by_name(switch, "1")
        diode_anode = get_pad_by_name(diode, "2")
        layer = get_layer_table(pcb)["B.Cu"]
        route_2_pads(pcb, switch_pin1, diode_anode, layer)


def _build_zone_from_hull(pcb, hull, net, layer):
    """Creates a zone from the given hull"""
    z = pcbnew.ZONE_CONTAINER(pcb)

    # Add zone properties
    z.SetLayer(layer)
    z.SetNetCode(net.GetNet())
    z.SetPadConnection(pcbnew.PAD_ZONE_CONN_THERMAL)
    z.SetMinThickness(25400)  # The minimum
    z.SetIsFilled(True)
    z.SetPriority(50)
    ol = z.Outline()
    ol.NewOutline()

    outline = hull.Outline(0)
    points = [outline.CPoint(i).getWxPoint()
              for i in range(outline.PointCount())]
    points = [point for point in points if _is_inside_sheet(point)]

    for p in points:
        ol.Append(p.x, p.y)
    pcb.Add(z)

    # Redraw zones
    filler = pcbnew.ZONE_FILLER(pcb)
    filler.Fill(pcb.Zones())


def place_planes(pcb):
    """Create GND and 5V planes"""
    hull =  _get_module_boudingpoly(pcb, switches=True)

    for netname, layername in [("GND", "F.Cu"), ("V5V", "B.Cu")]:
        net = get_net_by_name(pcb, netname)
        layer = get_layer_table(pcb)[layername]
        _build_zone_from_hull(pcb, hull, net, layer)


def set_leds_gnd_vias(pcb, am, bl):
    """Set vias on each per-key led's GND pin"""
    VIA_X_DIST = 1.5
    VIA_Y_DIST = 1
    net = get_net_by_name(pcb, "GND")
    layer = get_layer_table(pcb)["B.Cu"]

    pk = [assoc["led"] for l, assoc in am.items() if assoc["led"]]
    bk = [bl[label] for label in bl]
    for led in pk + bk:
        lib_name = str(led.GetFPID().GetLibItemName())
        backlight = "PLCC4" in lib_name
        orientation = led.GetOrientation()
        pad = get_pad_by_name(led, "3")
        pad_pos = pad.GetPosition()

        if orientation == 0.0:
            via1_pos = wxPoint(pad_pos.x + FromMM(VIA_X_DIST), pad_pos.y)
            if backlight:
                via2_pos = wxPoint(pad_pos.x, pad_pos.y - FromMM(VIA_Y_DIST))
            else:
                via2_pos = wxPoint(pad_pos.x, pad_pos.y + FromMM(VIA_Y_DIST))

        else:
            via1_pos = wxPoint(pad_pos.x - FromMM(VIA_X_DIST), pad_pos.y)
            if backlight:
                via2_pos = wxPoint(pad_pos.x, pad_pos.y + FromMM(VIA_Y_DIST))
            else:
                via2_pos = wxPoint(pad_pos.x, pad_pos.y - FromMM(VIA_Y_DIST))

        route_2_pads(pcb, pad, create_via(pcb, net, via1_pos), layer)
        route_2_pads(pcb, pad, create_via(pcb, net, via2_pos), layer)


def __route_led_chain(pcb, pad1, pad2, net_name, reverse=False):
    """Route the led chain"""
    # Route 1/4, 3/4 of length on each side (B.Cu)
    # Place VIA at the end of these track
    # Bridge both vias on F.Cu
    net = get_net_by_name(pcb, net_name)
    if pad1.GetPosition().x < pad2.GetPosition().x:
        pads = [pad1, pad2]
    else:
        pads = [pad2, pad1]

    pad1_pos = pads[0].GetPosition()
    pad2_pos = pads[1].GetPosition()
    bcu_hlength_short = int(abs(pad1_pos.x - pad2_pos.x) / 4)
    bcu_hlength_long = int(3 * abs(pad1_pos.x - pad2_pos.x) / 4)
    if reverse:
        length1 = bcu_hlength_long
        length2 = bcu_hlength_short
    else:
        length1 = bcu_hlength_short
        length2 = bcu_hlength_long
    via1_pos = wxPoint(pad1_pos.x + length1, pad1_pos.y)
    via2_pos = wxPoint(pad2_pos.x - length2, pad2_pos.y)
    via1 = create_via(pcb, net, via1_pos)
    via2 = create_via(pcb, net, via2_pos)
    route_2_pads(pcb, pads[0], via1, get_layer_table(pcb)["B.Cu"])
    route_2_pads(pcb, pads[1], via2, get_layer_table(pcb)["B.Cu"])
    route_2_pads(pcb, via1, via2, get_layer_table(pcb)["F.Cu"])


def link_leds(pcb, am, bl):
    """Links the leds"""
    # Did not find an easy way to get pads connected to a net
    # So, just build up a list of all pads DIN, DOUT of all LEDs,
    # then make pairs
    themap = {}
    pk = [assoc["led"] for l, assoc in am.items() if assoc["led"]]
    bk = [bl[label] for label in bl]
    for led in pk + bk:
        for padnum in ["2", "4"]:
            pad = get_pad_by_name(led, padnum)
            netname = pad.GetNetname()
            if netname not in themap:
                themap[netname] = []
            themap[netname].insert(0, pad)

        themap[netname].append(led.GetOrientation() == 0)

    for name, pads in themap.items():
        if len(pads) != 3:
            continue
        __route_led_chain(pcb, pads[0], pads[1], name, reverse=pads[2])


def route(unrouted, routed):
    """Routes the (hopefuly) most of the pcb"""
    # Open the PCB and create the layout
    pcb = pcbnew.LoadBoard(unrouted)
    kl = KeebLayout(KLE_JSON_FILE)
    kl.parse()

    am, bl = create_assoc_map(kl, pcb)
    setup_pcb_options(pcb, JLCPCB_CAPABILITIES)
    draw_edge_cut(pcb)
    route_diode_anode(pcb, am)
    place_planes(pcb)
    set_leds_gnd_vias(pcb, am, bl)
    link_leds(pcb, am, bl)
    # Rebuild zones
    filler = pcbnew.ZONE_FILLER(pcb)
    filler.Fill(pcb.Zones())
    pcb.Save(routed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("unrouted_pcb", help="The unrouted pcb path")
    parser.add_argument("routed_pcb", help="The routed pcb path")
    args = parser.parse_args()

    route(args.unrouted_pcb, args.routed_pcb)