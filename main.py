#!/usr/bin/env python

import daemon
from LightingControl import LightingControl
from StargateControl import StargateControl
from DialProgram import DialProgram
from StargateAudio import StargateAudio
from StargateLogic import StargateLogic
import config
from time import sleep
from WebServer import StargateHttpHandler
from http.server import HTTPServer
import threading
import sys

#
# Working Stargate Mk2 by Glitch, code by Dan Clarke, modified by Jeremy Gustafson
# Adafruit motor library changes by hendrikmaus, pootle and shrkey
# These changes have a *substantial* impact on the Adafruit motor drive, allowing for high-speed microstep driving
# Raspberry Pi I2C speed must be 400000 (400Khz):
# http://www.mindsensors.com/blog/how-to/change-i2c-speed-with-raspberry-pi

# Packages needed:
# gpiozero, pygame, Adafruit_MCP3008
#

#
# *** DON'T FORGET TO EDIT CONFIG.PY ***
#

# Stargate components
audio = StargateAudio()
light_control = LightingControl()
stargate_control = StargateControl(light_control)
dial_program = DialProgram(stargate_control, light_control, audio)
logic = StargateLogic(audio, light_control, stargate_control, dial_program)

# Run this FIRST to get the best drive method
#stargate_control.drive_test()

# Run this SECOND to get the chevron lighting order
# light_control.cycle_chevrons()

# THIRD, uncomment the "LDR TEST" section below, and also the quick_calibration (if commented out), to test LDR values during initial build/debugging.
# Update "cal_brightness = 200" in config.py based on your output.

# Run this FOURTH to get core calibration settings
#stargate_control.full_calibration()

# Run this to TEST the dial sequence
# dial_program.dial([26, 6, 14, 31, 11, 29, 0])

# Web control
print('Running web server...')
StargateHttpHandler.logic = logic
httpd = HTTPServer(('', 80), StargateHttpHandler)

httpd_thread = threading.Thread(name="HTTP", target=httpd.serve_forever)
httpd_thread.setDaemon(True)
httpd_thread.start()

# LDR TEST; uncomment the following three lines to output LDR values to your terminal
#while True:
#	print("LDR: {}".format(stargate_control.get_ldr_val()))
#	sleep(1)

# Run this NORMALLY to home the gate at start up
# Do this calibration AFTER the web server is launched, so the web page can be opened while calibration is still running
stargate_control.quick_calibration()

# Infinite loop doing stuff
print('Running logic...')
print("LDR: {}".format(stargate_control.get_ldr_val()))
logic.loop()


# Useful test of symbol accuracy - slowly works through each symbol on each side
# for i in xrange(1, 19):
#     light_control.darken_chevron(config.top_chevron)
#     stargate_control.move_to_symbol(i, StargateControl.FORWARD)
#     light_control.light_chevron(config.top_chevron)
#     sleep(5)
#     light_control.darken_chevron(config.top_chevron)
#     stargate_control.move_to_symbol(config.num_symbols - i, StargateControl.BACKWARD)
#     light_control.light_chevron(config.top_chevron)
#     sleep(5)
