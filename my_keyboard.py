#!/usr/bin/env python

from select import select
from evdev import InputDevice, list_devices, ecodes, categorize

class Keyboard:
    devices = None

    # QWERTY -> DVORAK scancode conversion
    DVORAK_CONVERSIONS = {
        5: 27, 6: 13, 7: 8, 8: 55, 9: 24, 10: 12, 11: 7, 12: 6, 13: 11,
        14: 23, 15: 17, 17: 5, 18: 21, 19: 15, 20: 52, 21: 19, 22: 18, 23: 28,
        24: 10, 25: 14, 26: 54, 27: 20, 28: 9, 29: 51, 45: 47, 46: 48, 47: 56,
        48: 46, 51: 22, 52: 45, 54: 26, 55: 25, 56: 29
    }

    def fetch_keyboard(self):
        devices = [InputDevice(path) for path in list_devices()]
        devices = [d for d in devices if "keyboard" in d.name.lower()]
        devices = {d.fd: d for d in devices}
        self.devices = devices

    def capture(self):
        while True:
            read_list, _, _ = select(self.devices, [], [])
            for file_descriptor in read_list:
                for event in self.devices[file_descriptor].read():
                    if event.type == ecodes.EV_KEY:
                        print(categorize(event))
