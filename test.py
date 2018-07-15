#!/usr/bin/python2.7

import my_keyboard

from my_keyboard import Keyboard

keyboard = Keyboard()
keyboard.fetch_keyboard()

if keyboard.devices != None:
    keyboard.capture()
