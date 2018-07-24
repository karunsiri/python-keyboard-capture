import time
from select import select
from evdev import InputDevice, list_devices, ecodes, categorize

class Keyboard:
    # QWERTY -> DVORAK scancode conversion
    DVORAK_CONVERSIONS = {
        12: 26, 13: 27,
        16: 39, 17: 51, 18: 52, 19: 25, 20: 21, 21: 33, 22: 34, 23: 46, 24: 19, 25: 38, 26: 53, 27: 13,
        31: 24, 32: 18, 33: 22, 34: 23, 35: 32, 36: 35, 37: 20, 38: 49, 39: 31, 40: 12,
        44: 40, 45: 16, 46: 36, 47: 37, 48: 45, 49: 48, 51: 17, 52: 47, 53: 44
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
        converted = self.DVORAK_CONVERSIONS.get(event.code, event.code)
        print("You typed", ecodes.KEY[converted])

    def is_connected(self):
        return len(self.devices) > 0
