#!/usr/bin/env python3
from skidl import generate_netlist, net
import argparse
from kle_parser import KeebLayout


def main_board(json_path, netlist_path):
    """Creates the main board"""

    generate_netlist(file=open(netlist_path, "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json", help="Input KLE JSON file")
    parser.add_argument("netlist", help="Output netlist file")
    args = parser.parse_args()