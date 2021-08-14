#!/usr/bin/env python3

import json
import argparse


"""Implements different type of KLE JSON parsing:
    - Netlist:
        - Electrical net with row/col (might be similar for more than one key)
        - LED chain (with several path style)
    - PCB layout:
        - x & y location on PCB
"""


def flatten(the_list):
    """Just flatten a list"""
    ret = []
    for element in the_list:
        if isinstance(element, list):
            ret += flatten(element)
        else:
            ret.append(element)
    return ret


KEY_TRANSLATE = {
    "`": "BACKQUOTE",
    "-": "MINUS",
    "=": "EQUAL",
    "[": "LEFT_BRACKET",
    "]": "RIGHT_BRACKET",
    "\\_ISO": "BACKSLASHISO",
    "\\_AINSI": "BACKSLASHAINSI",
    ";": "SEMICOLON",
    "'": "SINGLEQUOTE",
    "#": "HASH",
    ",": "COMMA",
    ".": "PERIOD",
    "/": "SLASH",
    "↑": "UPARROW",
    "←": "LEFTARROW",
    "↓": "DOWNARROW",
    "→": "RIGHTARROW",
    " ": "SPACE"
}


ELECTRICAL_LAYOUT_BY_LABEL = {
    # Row 0
    "ESC": (0,0), "F1": (0,1), "F2": (0,2), "F3": (0,3), "F4": (0,4),
    "F5": (0,5), "F6": (0,6), "F7": (0,7), "F8": (0,8), "F9": (0,9),
    "F10": (0,10), "F11": (0,11), "F12": (0,12), "PRTSC": (0,13), "DEL": (0,14),
    # Row 1
    "BACKQUOTE": (1,0), "1": (1,1), "2": (1,2), "3": (1,3), "4": (1,4),
    "5": (1,5), "6": (1,6), "7": (1,7), "8": (1,8), "9": (1,9), "0": (1,10),
    "MINUS": (1,11), "EQUAL": (1,12), "PAUSE": (1,13), "HOME": (1,14),
    # Row 2
    "TAB": (2,0), "Q": (2,1), "W": (2,2), "E": (2,3), "R": (2,4), "T": (2,5),
    "Y": (2,6), "U": (2,7), "I": (2,8), "O": (2,9), "P": (2,10),
    "LEFTBRACKET": (2,11),  "RIGHTBRACKET": (2,12), "BACKSPACE": (2,13),
    "PGUP": (2,14),
    # Row 3
    "CAPSLOCK": (3,0), "A": (3,1), "S": (3,2), "D": (3,3), "F": (3,4),
    "G": (3,5), "H": (3,6), "J": (3,7), "K": (3,8), "L": (3,9),
    "SEMICOLON": (3,10), "SINGLEQUOTE": (3,11), "HASH": (3,12),
    "ENTERAINSI": (3,12), "BACKSLASHAINSI": (3,13), "ENTERISO": (3,13),
    "PGDN": (3,14),
    # Row 4
    "LSHIFTISO": (4,0), "LSHIFTAINSI": (4,0), "BACKSLASHISO": (4,1),
    "Z": (4,2), "X": (4,3), "C": (4,4), "V": (4,5), "B": (4,6), "N": (4,7),
    "M": (4,8), "COMMA": (4,9), "PERIOD": (4,10), "SLASH": (4,11),
    "RSHIFT":(4,12), "UPARROW": (4,13), "END": (4,14),
    # Row 5
    "LCTRL": (5, 0), "WIN": (5,1), "ALT": (5,2), "SPACE": (5, 6),
    "ALTGRSHORT": (5,9), "ALTGRLONG": (5,9), "MENU": (5,10),
    "RCTRLSHORT": (5,11), "RCTRLLONG": (5,11),
    "LEFTARROW": (5,12), "DOWNARROW": (5,13), "RIGHTARROW": (5,14)
}


ELECTRICAL_LAYOUT_DUPLICATED = {
    "LSHIFTISO": "LSHIFTAINSI",
    "LSHIFTAINSI": "LSHIFTISO",
    "ALTGRSHORT": "ALTGRLONG",
    "ALTGRLONG": "ALTGRSHORT",
    "RCTRLSHORT": "RCTRLLONG",
    "RCTRLLONG": "RCTRLSHORT",
    "HASH": "ENTERAINSI",
    "ENTERAINSI": "HASH",
    "ENTERISO": "BACKSLASHAINSI",
    "BACKSLASHAINSI": "ENTERISO",
}

LEDS_RAW = [ [ # Row 0
               "ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
               "F10", "F11", "F12", "PRTSC", "PAUSE", "DEL"],
             [ # Row 1
               "HOME", "BACKSPACE", "EQUAL", "MINUS", "0", "9", "8", "7", "6",
               "5", "4", "3", "2", "1", "BACKQUOTE"],
             [ # Row 2
               "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
               "LEFTBRACKET", "RIGHTBRACKET", "BACKSLASHAINSI", "ENTERISO",
               "PGUP"],
             [ # Row 3
               "PGDN", "ENTERAINSI", "HASH", "SINGLEQUOTE", "SEMICOLON", "L",
               "K", "J", "H", "G", "F", "D", "S", "A", "CAPSLOCK"],
             [ # Row 4
               "LSHIFTISO", "LSHIFTAINSI", "BACKSLASHISO", "Z", "X", "C", "V",
               "B", "N", "M", "COMMA", "PERIOD", "SLASH", "RSHIFT", "UPARROW",
               "END"],
             [ # Row 5
               "RIGHTARROW", "DOWNARROW", "LEFTARROW", "RCTRLLONG", "MENU",
               "ALTGRLONG", "SPACE", "ALT", "WIN", "LCTRL"],
            ]

LEDS_LAYOUT = flatten(LEDS_RAW)
# The whole list needs to be reversed because we are starting from the 
# bottom left
LEDS_LAYOUT.reverse()


def get_led_row(label):
    """Returns the row of the given key"""
    for row, keys in enumerate(LEDS_RAW):
        if label in keys:
            return row
    return None


def key_name_cleanup(label):
    """Clean the given label"""
    # Only keep the main key label
    label = label.split("\n")[-1]
    label = KEY_TRANSLATE.get(label, label)
    label = label.replace(" ", "")
    label = label.replace("_", "")
    return label.upper()


def get_first_key_from_label(label, row):
    """Return electrical location from label in a given row"""
    for k in row:
        if k.label == label:
            return  k
    return None


class Key(object):
    """A dumb class that describes a key"""

    def __init__(self):
        """Init the brand new instance"""
        self.params = {}
        # Electrical settings
        self.electrical_row = None
        self.electrical_col = None
        # LED settings
        self.led_index = None
        self.led_next = None
        self.led_prev = None
        # PCB layout settings
        self.pcb_pos_x = None
        self.pcb_pos_y = None

    def __str__(self):
        """Just summarize the instance"""
        led_prev = None
        if self.led_prev is not None:
            led_prev = self.led_prev.led_index
        led_next = None
        if self.led_next is not None:
            led_next = self.led_next.led_index
        return F"Key {self.label:>15} \t" +\
               F"E({self.electrical_row}, {self.electrical_col}) \t" + \
               F"P({self.pcb_pos_x},{self.pcb_pos_y}) \t" +\
               F"L({self.led_index},{led_prev}, {led_next})"


class KeebLayout(object):
    """Just a KLE JSON parser"""

    def __init__(self, path):
        """Init the brand new instance"""
        self.path = path
        self.keys =[] # Just all keys. No order

    def get_key_from_label(self, label):
        """Return a key from given label, use width to disambiguous"""
        for k in self.keys:
            if k.label != label:
                continue
            return k
        raise ValueError(F"Key {label} not found")

    def parse(self):
        """Parses the JSON file"""
        pcb_pos_y = 0 # in Us
        # Physical and Electrical parsing
        for i, row in enumerate(json.load(open(self.path))):
            current_key = Key()
            pcb_pos_x = 0 # in Us
            for k in row:
                if isinstance(k, dict):
                    current_key.params = k
                    continue

                # This is the moment !
                current_key.label = key_name_cleanup(k)
                w = current_key.params.get("w", 1)

                # PCB stuff
                pcb_pos_x += current_key.params.get("x", 0)
                current_key.pcb_pos_x = pcb_pos_x
                current_key.pcb_pos_y = pcb_pos_y

                # Electrical pos
                electrical_pos = ELECTRICAL_LAYOUT_BY_LABEL[current_key.label]
                current_key.electrical_row = electrical_pos[0]
                current_key.electrical_col = electrical_pos[1]

                # We've done it
                self.keys.append(current_key)
                current_key = Key()
                pcb_pos_x += w
            pcb_pos_y += 1

        # LED parsing
        # Strategy is pretty simple, all LEDs are linked from the top left
        # corner to the bottom right one. Double implents are handled via
        # software
        self.leds = []
        prev_led_key = None
        for i, led_label in enumerate(LEDS_LAYOUT):
            key = self.get_key_from_label(led_label)
            key.led_index = i
            key.led_prev = prev_led_key
            if prev_led_key is not None:
                prev_led_key.led_next = key
            prev_led_key = key
            self.leds.append(key)


    def electrical_iter(self):
        """Basic electric row into electric col"""
        # Not needed for now
        pass

    def led_iter(self):
        return iter(self.leds)

    def pcb_position_iter(self):
        """Iter for PCB position. Order is not important, each keys got its
        own x and y"""
        return iter(self.keys)


if __name__ == "__main__":
    # This is for test purpose only
    parser = argparse.ArgumentParser()
    parser.add_argument("kle_file", help="KLE JSON file")
    args = parser.parse_args()
    print(F"Processing {args.kle_file}")
    kl = KeebLayout(args.kle_file)
    kl.parse()