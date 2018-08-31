#!/usr/bin/env python

import os
import sys
import time
import dbus
import bluetooth
import signal
from gi.repository import GObject
from bluetooth import *
from dbus import service
from dbus.mainloop.glib import DBusGMainLoop

class MyKeyboardBluezProfile(dbus.service.Object):
    fd = -1

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Profile1",
                         in_signature = "",
                         out_signature = "")
    def Release(self):
        print("Release")
        dbus.mainloop.quit()

    @dbus.service.method("org.bluez.Profile1",
                         in_signature = "",
                         out_signature = "")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1",
                         in_signature = "oha{sv}",
                         out_signature = "")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

    @dbus.service.method("org.bluez.Profile1",
                         in_signature = "o",
                         out_signature = "")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if self.fd > 0:
            os.close(self.fd)
            self.fd = -1

class MyKeyboardBluetoothDevice:
    DEVICE_ADDRESS = "00:19:86:00:23:81"
    DEVICE_NAME    = "Karun Keyboard"

    P_CTRL = 17 # Control port - the same as broadcasted in SDP record
    P_INTR = 19 # Interrupt port - the same as broadcasted SDP interrupt port

    # dbus path of the creating bluetooth bluez profile
    DBUS_PROFILE_PATH = "/bluez/karunsiri/my_keyboard_profile"
    SDP_RECORD_PATH = sys.path[0] + "/sdp_record.xml"

    # Broadcast as HID device. See
    # https://www.bluetooth.com/specifications/assigned-numbers/service-discovery
    UUID = "00001124-0000-1000-8000-00805f9b34fb"

    def __init__(self):
        print("Setting up a device")
        self.__init_device()
        self.__init_bluez_profile()

    def listen(self):
        print("Open for connections...")
        self.scontrol   = BluetoothSocket(L2CAP)
        self.sinterrupt = BluetoothSocket(L2CAP)

        # Bind sockets to set ports
        self.scontrol.bind((self.DEVICE_ADDRESS, self.P_CTRL))
        self.sinterrupt.bind((self.DEVICE_ADDRESS, self.P_INTR))

        # Limit to only 1 connection on each socket
        self.scontrol.listen(1)
        self.sinterrupt.listen(1)

        self.ccontrol, cinfo = self.scontrol.accept()
        print("Connection from control", cinfo[0])

        self.cinterrupt, cinfo = self.sinterrupt.accept()
        print("Connection from interrupt", cinfo[0])

    def send_string(self, message):
        self.cinterrupt.send(message)

    def __init_device(self):
        print("Setting up '%s'..." % self.DEVICE_NAME)

        # Keyboard Peripheral class set to 0x000540
        # See http://domoticx.com/bluetooth-class-of-device-lijst-cod/
        os.system("sudo hciconfig hci0 up")
        os.system("sudo btmgmt discov yes")
        os.system("sudo btmgmt pairable on")
        os.system("sudo btmgmt connectable on")
        os.system("sudo btmgmt bondable on")
        os.system("sudo btmgmt name \"Karun Keyboard\"")
        os.system("sudo btmgmt class 5 64")
        os.system("sudo btmgmt power on")

        # Make discoverable
        os.system("hciconfig hci0 piscan")

    def __init_bluez_profile(self):
        print("Setting up BlueZ profile...")
        sdp_record = self.__read_sdp_record()

        options = {
            "ServiceRecord": sdp_record,
            "Role": "server",
            "RequireAuthentication": False,
            "RequireAuthorization": False
        }

        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")

        profile = MyKeyboardBluezProfile(bus, self.DBUS_PROFILE_PATH)
        manager.RegisterProfile(self.DBUS_PROFILE_PATH, self.UUID, options)
        print("Profile Registered...")

    def __read_sdp_record(self):
        print("Reading SDP record...")
        try:
            _file = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Cannot read SDP record")

        return _file.read()

# The actual dbus service that receive signals from clients
class MyKeyboardService(dbus.service.Object):
    def __init__(self):
        print("Setting up a service...")

        bus_name = dbus.service.BusName("org.karunsiri.btkeyboard", bus = dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, "/org/karunsiri/btkeyboard")

        self.device = MyKeyboardBluetoothDevice()
        self.device.listen()

    @dbus.service.method('org.karunsiri.btkeyboard', in_signature='iay')
    def send_keys(self, modifier_byte, keys):
        string = ""
        string += chr(0xA1)
        string += chr(0x01)
        string += chr(modifier_byte)
        string += chr(0x00)

        count = 0
        for code in keys:
            if count < 6:
                string += chr(code)
            count += 1

        self.device.send_string(string)

if __name__ == "__main__":
    # Only allow root to run the script
    if not os.geteuid() == 0:
        sys.exit("Only root can run the script")

    DBusGMainLoop(set_as_default = True)
    service = MyKeyboardService()


    main_loop = GObject.MainLoop()

    sigint_handler = lambda sig, frame: main_loop.quit()

    # Handle SIGINT gracefully
    signal.signal(signal.SIGINT, sigint_handler)
    main_loop.run()
