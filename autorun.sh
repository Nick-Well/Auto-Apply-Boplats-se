#!/bin/bash
xinit &
sleep 5
export DISPLAY=:0
python3 setup.py
sleep 5
killall xinit
