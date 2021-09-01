#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pcbnew
import argparse
from pcbnew import FromMM, FromMils

from route_utils import get_layer_table
from route_utils import get_pad_by_name
from route_utils import route_2_pads
from route_utils import get_net_by_name
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

    default_class = design_settings.GetDefault()
    default_class.SetClearance(profile["Clearance"])
    default_class.SetTrackWidth(profile["TrackWidth"])
    default_class.SetViaDiameter(profile["ViaDiameter"])
    default_class.SetViaDrill(profile["ViaDrill"])
    default_class.SetuViaDiameter(profile["uViaDiameter"])
    default_class.SetuViaDrill(profile["ViaDrill"])
    default_class.SetDiffPairWidth(profile["DiffPairWidth"])
    default_class.SetDiffPairGap(profile["DiffPairGap"])


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
    pcb.Save(routed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("unrouted_pcb", help="The unrouted pcb path")
    parser.add_argument("routed_pcb", help="The routed pcb path")
    args = parser.parse_args()

    route(args.unrouted_pcb, args.routed_pcb)