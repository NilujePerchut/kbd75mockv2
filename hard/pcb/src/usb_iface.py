from skidl import Net
from sch_utils import dop_part, pull_updown, get_res, get_inductance
from sch_utils import bypass_cap


def usb_iface():
    """The keyboard USB interface"""
    power = {"v5v": Net("V5V"), "gnd": Net("GND")}
    usb = {"usb_p": Net("USB_P"), "usb_n": Net("USB_N")}
    vbus = Net("VBUS")

    usb_conn = dop_part("USB_C_Receptacle_USB2.0",
                        "USB_C_Receptacle_HRO_TYPE-C-31-M-12",
                        fields={"Reference": "HRO_TYPE-C-31-M-12",
                                "descr": "USB C connector (12 pins)",
                                "CC": "NA",
                                "JLCC": "C165948", "JLROT": "0"})
    pull_updown(power["gnd"], [usb_conn["CC1"], usb_conn["CC2"]] ,"5.1K",
                fields={"JLCC": "C23186"})
    usb_conn["vbus"] += vbus
    usb_conn["gnd"] += power["gnd"]
    usb_conn["shield"] += NC
    usb_conn["SBU1"] += NC
    usb_conn["SBU2"] += NC

    esd_prot = dop_part("USBLC6-2SC6", "TSOT-23-6",
                        fields = {"Reference": "USBLC6-2SC6",
                                  "Descr": "ESD protection for USB2",
                                  "CC": "1269406",
                                  "JLCC": "C558442",
                                  "JLROT": "180"})

    ferrite = get_inductance("MPZ1608B471ATA00", "0603",
                             fields={"Reference": "MPZ1608B601ATD25",
                                     "descr": "Ferrite 600Ω @ 100MHz 1A",
                                     "CC": "",
                                     "JLCC": "C193536", "JLROT": "0"})

    # USB + its ESD protection
    # For external USB connection, a sil 4 connector is provided
    #   In this case ESD filter must be removed
    sil4_conn = dop_part("CONN_01X04", "SIL4")
    sil4_conn[1] += vbus
    sil4_conn[4] += power["gnd"]

    usb_conn_dp = Net("USB_CONN_DP")
    usb_conn_dn = Net("USB_CONN_DN")
    usb_conn["A6"] += usb_conn_dp
    usb_conn["A7"] += usb_conn_dn
    usb_conn["D+"] & usb_conn_dp & esd_prot[3,4] & sil4_conn[3] & usb["usb_p"]
    usb_conn["D-"] & usb_conn_dn & esd_prot[1,6] & sil4_conn[2] & usb["usb_n"]
    esd_prot[5] & vbus & ferrite[1,2] & power["v5v"]
    bypass_cap(vbus, power["gnd"], "100nF")
    esd_prot[2] += power["gnd"]

    bypass_cap(power["v5v"], power["gnd"], "100nF",
               fields={"descr": "usb_conn", "JLCC": "C14663"})
    bypass_cap(power["v5v"], power["gnd"], "4.7uF", package="0805",
               fields={"descr": "usb_conn", "JLCC": "C1779"})
    return power, usb