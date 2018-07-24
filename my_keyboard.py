import time
from select import select
from evdev import InputDevice, list_devices, ecodes, categorize

class Keyboard:
    # QWERTY -> DVORAK scancode conversion
    DVORAK_CONVERSIONS = {
        5: 27, 6: 13, 7: 8, 8: 55, 9: 24, 10: 12, 11: 7, 12: 6, 13: 11,
        14: 23, 15: 17, 17: 5, 18: 21, 19: 15, 20: 52, 21: 19, 22: 18, 23: 28,
        24: 10, 25: 14, 26: 54, 27: 20, 28: 9, 29: 51, 45: 47, 46: 48, 47: 56,
        48: 46, 51: 22, 52: 45, 54: 26, 55: 25, 56: 29
    }

    def __init__(self):
        self.reset_device_state()

    def reset_device_state(self):
        self.devices = {}
        self.state = [
            0xA1, # Input report
            0x01, # Usage report
            # Modifier Bits
            # Right Window, Alt, Shift, Ctrl,
            # Left Window, Alt, Shift, Ctrl Respectively
            [0, 0, 0, 0, 0, 0, 0, 0],
            0x00, # Vendor reserved
            0x00, # Padding x6
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

    # Will block until a keyboard is connected
    def fetch_keyboard(self):
        while True:
            devices = [InputDevice(path) for path in list_devices()]
            devices = [d for d in devices if "keyboard" in d.name.lower()]
            devices = {d.fd: d for d in devices}
            self.devices = devices

            if len(self.devices) > 0:
                print("Keyboard found")
                break

            time.sleep(3)

    def capture(self):
        while True:
            # Will block until a keyboard is connected
            if not self.is_connected():
                self.fetch_keyboard()

            try:
                self.read_event()
            except OSError:
                print("Keyboard disconnected")
                self.reset_device_state()
                time.sleep(1)

    def read_event(self):
        while True:
            read_list, _, _ = select(self.devices, [], [])
            for file_descriptor in read_list:
                for event in self.devices[file_descriptor].read():
                    # Is a keypress and only care for keyup and keydown
                    if event.type == ecodes.EV_KEY and event.value < 2:
                        self.toggle_state(event)

    def toggle_state(self, event):
        code = ecodes.KEY[event.code]
        print(code)

    def is_connected(self):
        return len(self.devices) > 0
