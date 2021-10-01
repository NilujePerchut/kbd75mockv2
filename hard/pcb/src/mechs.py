from sch_utils import dop_part

def mechs():
    """Insert mechanicals stuff"""
    [dop_part("FIDUCIAL", "FIDUCIAL") for i in range(3)]
    [dop_part("Fix", "JLCPCB_TOOLING_HOLE") for i in range(3)] 
    dop_part("Sakura", "Sakura_big")
    [dop_part("Fix", "FIX_KEYBOARD") for i in range(10)]
    [dop_part("YMDK_case", "YMDK_case")]