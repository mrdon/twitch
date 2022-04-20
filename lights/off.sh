#!/bin/bash

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$DIR/venv/bin/kasa --host=192.168.0.136 --plug off
$DIR/venv/bin/kasa --host=192.168.0.224 --plug off
$DIR/venv/bin/kasa --host=192.168.0.211 --plug off
#gnome-screensaver-command -l
