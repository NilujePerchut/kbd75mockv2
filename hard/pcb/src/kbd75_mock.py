#!/usr/bin/env python3
import os
from skidl import generate_netlist, lib_search_paths
import argparse

from skidl.defines import KICAD
from kle_parser import KeebLayout
from usb_iface import usb_iface


def main_board(json_path):
    """Creates the main board"""

    power, usb = usb_iface()

    generate_netlist()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json", help="Input KLE JSON file")
    args = parser.parse_args()
    lib_search_paths[KICAD].append(os.environ["KIPRJLIB"])
    main_board(args.json)