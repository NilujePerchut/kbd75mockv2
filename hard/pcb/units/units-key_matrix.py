#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from re import I
from skidl import Net, POWER
from sch_utils import unit_map_on_he10, run_unit

from src.key_matrix import key_matrix
from src.kle_parser import KeebLayout

KLE_JSON_FILE = "../rcs/v2.json"

def unit_matrix():
    """Unit test the key matrix using real data"""
    # Input signals & connector
    rows = [Net(F"ROW_{c}") for c in range(6)]
    cols = [Net(F"COL_{c}") for c in range(15)]

    unit_map_on_he10(rows+cols)
    kl = KeebLayout(KLE_JSON_FILE)
    kl.parse()

    key_matrix(kl.keys, rows, cols)


if __name__ == "__main__":
    run_unit(unit_matrix)
