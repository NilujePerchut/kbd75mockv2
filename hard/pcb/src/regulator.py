from skidl import Net
from sch_utils import dop_part
from sch_utils import bypass_cap


def regulator(power):
    """3.3V from 5V Regulator"""
    v33 = Net("V33")

    reg = dop_part("AP1117-15", "SOT-223",
                   fields = {"Reference": "AP1117-33",
                             "Descr": "5V to 3.3V 1A LDO",
                             "CC": "NA",
                             "JLCC": "C6186", "JLROT": "0"})

    reg["GND"] += power["gnd"]
    reg["VI"] += power["v5v"]
    reg["VO"] += v33

    # Datasheets recommends 22uF
    bypass_cap(v33, power["gnd"], "22uF", package="0805",
               fields={"JLCC": "C45783", "JLROT": "0"})

    power["v33"] = v33
    return power