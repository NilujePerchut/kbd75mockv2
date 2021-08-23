#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pcbnew
import argparse
from pcbnew import FromMM

from route_utils import get_layer_table


def draw_edge_cut(pcb, fillet_radius=1, max_fillet_error=50):
    """Draws the edge cut."""
    modules = []
    edgecuts_layer = get_layer_table(pcb)["Edge.Cuts"]

    for module in pcb.GetModules():
        # Only consider Switches and USB connector for now
        lib_name = str(module.GetFPID().GetLibItemName())
        if lib_name.startswith("SW_Cherry_MX") or lib_name.startswith("USB_C"):
            modules.append(module)

    hull = modules[0].GetBoundingPoly()
    for m in modules[1:]:
        hull.BooleanAdd(m.GetBoundingPoly(), hull.PM_FAST)
    hull.RemoveNullSegments()
    hull = hull.Fillet(FromMM(fillet_radius), max_fillet_error)

    hull_outline = hull.Outline(0)
    points = [hull_outline.CPoint(i).getWxPoint()
              for i in range(hull_outline.PointCount())]
    points.append(points[0])

    p1 = points[0]
    for p2 in points[1:]:
        seg = pcbnew.DRAWSEGMENT(pcb)
        pcb.Add(seg)
        seg.SetStart(p1)
        seg.SetEnd(p2)
        seg.SetLayer(edgecuts_layer)
        p1 = p2

def route(unrouted, routed):
    """Routes the (hopefuly) most of the pcb"""
    pcb = pcbnew.LoadBoard(unrouted)
    draw_edge_cut(pcb)
    pcb.Save(routed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("unrouted_pcb", help="The unrouted pcb path")
    parser.add_argument("routed_pcb", help="The routed pcb path")
    args = parser.parse_args()

    route(args.unrouted_pcb, args.routed_pcb)