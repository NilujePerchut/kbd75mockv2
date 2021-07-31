from sch_utils import dop_part

def mechs():
    """Insert mechanicals stuff"""
    [dop_part("FIDUCIAL", "FIDUCIAL") for i in range(3)]
    [dop_part("Fix", "JLCPCB_TOOLING_HOLE") for i in range(3)] 
    dop_part("Sakura", "Sakura")