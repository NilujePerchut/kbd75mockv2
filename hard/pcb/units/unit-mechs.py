#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from sch_utils import run_unit

from src.mechs import mechs

def unit_mechs():
    """Just a dummy test to implements mechs"""
    mechs()

if __name__ == "__main__":
    run_unit(unit_mechs)