from evdev import InputDevice, list_devices, ecodes, categorize
from select import select

class Keyboard(object):
    devices = None

    def fetch_keyboard(self):
        devices = [InputDevice(path) for path in list_devices()]
        devices = [d for d in devices if "keyboard" in d.name.lower()]
        devices = { d.fd: d for d in devices }
        self.devices = devices

    def capture(self):
        while True:
            read_list, w, x = select(self.devices, [], [])
            for file_descriptor in read_list:
                for event in self.devices[file_descriptor].read():
                    if event.type == ecodes.EV_KEY:
                        print(categorize(event))
