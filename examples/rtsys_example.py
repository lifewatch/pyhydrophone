"""
RTSys extra functions
=====================

An example of how to use the class RTSys to check the board files after a deployment
"""

import pyhydrophone as pyhy

Vpp = 5.0

# Hydrophone Setup
sensitivity = -180
preamp_gain = 0
model = 1
serial_number = 1000
name = 'RESEA320'
mode = 'lowpower'

folder_path = 'tests/test_data/rtsys/'

rtsys = pyhy.RTSys(name, model, serial_number, sensitivity, preamp_gain, Vpp, mode)
rtsys.plot_consumption_total_mission(mission_folder_path=folder_path)
print('Total consumption', rtsys.compute_consumption_total_mission(mission_folder_path=folder_path))
