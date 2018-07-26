import dbus
import time
from select import select
from evdev import InputDevice, list_devices, ecodes, categorize

class Keyboard:
    # DVORAK -> QWERTY scancode conversion
    DVORAK_CONVERSIONS = {
        # Top row
        12: 26, 13: 27,

        # Q row
        16: 39, 17: 51, 18: 52, 19: 25, 20: 21, 21: 33, 22: 34, 23: 46, 24: 19,
        25: 38, 26: 53, 27: 13,

        # A row
        31: 24, 32: 18, 33: 22, 34: 23, 35: 32, 36: 35, 37: 20, 38: 49, 39: 31,
        40: 12,

        # Z row
        44: 40, 45: 16, 46: 36, 47: 37, 48: 45, 49: 48, 51: 17, 52: 47, 53: 44
    }

    # Modifier scancode to modifier array conversion
    MODIFIER_KEYS = {
        29: 7, # Left Ctrl
        42: 6, # Left Shift
        56: 5, # Left Alt
        125: 4, # Left Meta
        97: 3, # Right Ctrl
        54: 2, # Right Shift
        100: 1, # Right Alt
        231: 0, # Right Meta
    }

    def __init__(self):
        self.__reset_device_state()
        self.__init_service_bus()

    def capture(self):
        while True:
            # Will block until a keyboard is connected
            if not self.__is_connected():
                self.__fetch_keyboard()

            try:
                self.__read_event()
            except OSError:
                print("Keyboard disconnected")
                self.__reset_device_state()
                time.sleep(1)

    def __reset_device_state(self):
        self.devices = {}
        self.state = [
            0xA1, # Input report
            0x01, # Usage report
            # Modifier Bits Array
            # Right Meta, Alt, Shift, Ctrl
            # Left Meta, Alt, Shift, Ctrl Respectively
            [0, 0, 0, 0, 0, 0, 0, 0],
            0x00, # Vendor reserved
            0x00, # Payload x6
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

    def __init_service_bus(self):
        self.bus = dbus.SystemBus()
        self.service = self.bus.get_object("org.karunsiri.btkeyboard", "/org/karunsiri/btkeyboard")
        self.interface = dbus.Interface(self.service, "org.karunsiri.btkeyboard")

    # Will block until a keyboard is connected
    def __fetch_keyboard(self):
        print("Waiting for keyboard...")
        while True:
            devices = [InputDevice(path) for path in list_devices()]
            devices = [d for d in devices if "keyboard" in d.name.lower()]
            devices = {d.fd: d for d in devices}
            self.devices = devices

            if len(self.devices) > 0:
                print("Keyboard found")
                break

            time.sleep(3)

    def __read_event(self):
        while True:
            read_list, _, _ = select(self.devices, [], [])
            for file_descriptor in read_list:
                for event in self.devices[file_descriptor].read():
                    # Is a keypress and only care for keyup and keydown
                    if event.type == ecodes.EV_KEY and event.value < 2:
                        self.__toggle_state(event)
                        self.__send_input()

    def __toggle_state(self, event):
        index = self.MODIFIER_KEYS.get(event.code)

        if not index == None:
            # Set proper modifier bits
            self.__toggle_modifier_bit(event, index)
        else:
            # Normal keys
            self.__toggle_normal_key(event)

    def __toggle_modifier_bit(self, event, index):
        if event.value >= 1:
            # On press & hold
            state = 1
        else:
            # On release
            state = 0

        self.state[2][index] = state

    def __toggle_normal_key(self, event):
        code = self.DVORAK_CONVERSIONS.get(event.code, event.code)

        for i in range(4, 10):
            # Keyup and is the same key
            if self.state[i] == code and event.value == 0:
                self.state[i] = 0x00
            ## Keydown and not registered
            elif self.state[i] == 0x00 and event.value == 1:
                self.state[i] = code
                break

    def __send_input(self):
        _str = ""
        modifier_bits = self.state[2]
        for bit in modifier_bits:
            _str += str(bit)

        self.interface.send_keys(int(_str, 2), self.state[4:10])

    def __is_connected(self):
        return len(self.devices) > 0
