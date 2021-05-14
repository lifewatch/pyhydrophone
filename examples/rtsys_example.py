"""
An example of how to use the class RTSys
"""

import pyhydrophone as pyhy

Vpp = 2.0

board_file_path = '//archive/other_platforms/rtsys/2021/CPower_Acoustic_Telemetry/card/records/210125/board_2021-01-25_12-20-17.txt'


def main(filepath):
    # Hydrophone Setup
    sensitivity = -180
    preamp_gain = 0
    model = 1
    serial_number = 1000
    name = 'RESEA320'

    rtsys = pyhy.RTSys(name, model, serial_number, sensitivity, preamp_gain, Vpp)
    rtsys.plot_consumption(board_file_path=filepath)


if __name__ == '__main__':
    main(board_file_path)
