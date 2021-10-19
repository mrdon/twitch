#!/bin/bash

venv/bin/kasa --host=192.168.1.32 --plug on
venv/bin/kasa --host=192.168.1.141 --plug on
venv/bin/kasa --host=192.168.1.169 --plug on
pactl set-default-source alsa_input.usb-Focusrite_Scarlett_2i2_USB_Y8PNWHM17C1C78-00.analog-stereo
