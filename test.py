#!/usr/bin/env python

import signal
import sys
from my_keyboard import Keyboard

def sigint_handler(sig, frame):
    print("Exiting Capture...")
    sys.exit(0)

# Handle SIGINT gracefully
signal.signal(signal.SIGINT, sigint_handler)

keyboard = Keyboard()

# Start event loop
keyboard.capture()
