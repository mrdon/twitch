#!/bin/bash

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$DIR/venv/bin/kasa --host=192.168.0.224 --plug on
$DIR/venv/bin/kasa --host=192.168.0.136 --plug on
$DIR/venv/bin/kasa --host=192.168.0.211 --plug on
pactl set-default-source alsa_input.usb-Focusrite_Scarlett_2i2_USB_Y8PNWHM17C1C78-00.analog-stereo
