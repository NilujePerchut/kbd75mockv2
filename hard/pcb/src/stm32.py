#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from skidl import Net
from skidl.net import NCNet
from sch_utils import dop_part, bypass_cap, get_res, pull_updown
from sch_utils import get_capa


LAYOUT_COLS = ["PB14", "PB15", "PA10", "PA8", "PA9", "PB9", "PA2", "PA3",
               "PA4", "PA6", "PA5", "PA7", "PB0", "PB1", "PB10"]
LAYOUT_ROWS = ["PA0", "PA1", "PB8", "PB7", "PC13", "PB13"]
PER_KEY_LEDS_COMMAND = "PB12"
BACKLIGHT_LEDS_COMMAND = "PB4"

UNCONNECTED = ["PA15", "PB3", "PB6", "PB11", "PC14", "PC15"]

def stm32(power, usb):
    """The STM32 part"""

    stm32 = dop_part("STM32F103C8", "LQFP-48_7x7mm_P0.5mm",
                     fields={"Reference": "STM32F103C8T6",
                             "descr": "ST ARM Cortex M3",
                             "CC": "1447637",
                             "JLCC": "C8734", "JLROT": "0"})
    stm32["VBAT", "VDD", "VDDA"] += power["v33"]
    stm32["VSS", "VSSA"] += power["gnd"]
    bypass_cap(power["v33"], power["gnd"], ["100nF"]*2,
               fields={"descr": "stm32", "JLCC": "C14663"})

    # Just fixes BOOT0 and BOOT1 to GND through 100K resistor.
    # We will just program the chip via SWD
    boot_res = [get_res("100K", package="0603", fields={"JLCC": "C25803"})
                for i in range(2)]
    stm32["BOOT0"] & Net("BOOT0") & boot_res[0] & power["gnd"]
    stm32["PB2"] & Net("BOOT1") & boot_res[1] & power["gnd"]

    # USB
    usb_serial_res = [get_res("22", "0603", fields={"JLCC": "C23345"})
                      for i in range(2)]
    stm32_usb = {F"STM32_USB_{pol}": Net(F"STM32_USB_{pol}")
                 for pol in ["P", "N"]}
    stm32["PA11"] & stm32_usb["STM32_USB_N"] & usb_serial_res[0] & usb["usb_n"]
    stm32["PA12"] & stm32_usb["STM32_USB_P"] & usb_serial_res[1] & usb["usb_p"]
    pull_updown(power["v33"], stm32_usb["STM32_USB_P"], "1.5K",
                fields = {"JLCC": "C22843"})

    # SWD
    sw_conn = dop_part("CONN_01X04", "SIL4")
    sw_conn[1] += power["v33"]
    sw_conn[2] += Net("SWDIO") & stm32["PA13"]
    sw_conn[3] += Net("SWDCLK") & stm32["PA14"]
    sw_conn[4] += power["gnd"]

    # Reset
    reset_res = get_res("10K", "0603", fields={"JLCC": "C25804"})
    reset_cap = get_capa("100nF", "0603", fields={"JLCC": "C14663"})
    reset_sw = dop_part("SW_PUSH", "SW_SPST_TL3342", fields={"JLCC": "C318884"})
    power["v33"] & reset_res[1,2] & Net("RESETN") & stm32["NRST"] & \
    (reset_cap[1,2] | reset_sw[1,2]) & power["gnd"]

    # Oscillator (forget using crystal with JLCPCB xtals specs)
    osc = dop_part("ASV-xxxMHz", "Oscillator_SMD_Abracon_ASV-4Pin_7.0x5.1mm",
                   fields={"Reference": "YS0751SR", "descr": "8MHz 20ppm",
                           "CC": "1842154", "JLCC": "C160440", "JROT": "0"})
    osc["EN"] += NC
    osc["Vdd"] += power["v33"]
    osc["Gnd"] += power["gnd"]
    osc["OUT"] += stm32["PD0"]
    stm32["PD1"] += NC
    bypass_cap(power["v33"], power["gnd"], "100nF",
               fields={"descr": "oscillator", "JLCC": "C14663"})

    # LED 
    led = dop_part("LED", "0805LED")
    res = get_res("1.4K", "0603", fields={"JLCC": "C22843"})
    stm32["PB5"] & res & led["A,K"] & power["gnd"]

    cols = []
    for i, stm32_col_pin in enumerate(LAYOUT_COLS):
        col_net = Net(F"COL_{i}")
        stm32[stm32_col_pin] += col_net
        cols.append(col_net)

    rows = []
    for i, stm32_row_pin in enumerate(LAYOUT_ROWS):
        row_net = Net(F"ROW_{i}")
        stm32[stm32_row_pin] += row_net
        rows.append(row_net)

    # LEDS strips command
    pklc = Net("PER_KEY_LED_COMMAND")    
    stm32[PER_KEY_LEDS_COMMAND] += pklc
    blc = Net("BACKLIGHT_LED_COMMAND")    
    stm32[BACKLIGHT_LEDS_COMMAND] += blc

    for pin in UNCONNECTED:
        stm32[pin] += NC

    return {"rows": rows, "cols": cols,
            "per_key_leds_command": pklc,
            "backlight_leds_command": blc}