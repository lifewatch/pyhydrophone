import pathlib
import pyhydrophone as pyhy
import unittest
import numpy as np


test_folder = pathlib.Path("./test_data/rtsys/")
test_file = pathlib.Path("./test_data/rtsys/channelA_2021-10-11_13-11-09.wav")

rtsys_name = 'RTSys'
rtsys_model = 'RESEA320'
rtsys_serial_number = 2003001
rtsys_sens = -180
rtsys_preamp = 0
rtsys_vpp = 5
mode = 'lowpower'
calibration_file = pathlib.Path("./test_data/rtsys/SN130.csv")
rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=rtsys_serial_number, sensitivity=rtsys_sens,
                   preamp_gain=rtsys_preamp, Vpp=rtsys_vpp, mode=mode, calibration_file=calibration_file)


class TestRTSys(unittest.TestCase):
    def setUp(self) -> None:
        self.rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=rtsys_serial_number,
                                sensitivity=rtsys_sens, preamp_gain=rtsys_preamp, Vpp=rtsys_vpp, mode=mode,
                                calibration_file=calibration_file)

    def test_init_from_file(self):
        rtsys = self.rtsys.update_metadata(test_file, zip_mode=False)
        print(rtsys)

    def test_header(self):
        for file_path in test_folder.glob('*.wav'):
            header = self.rtsys.read_header(file_path)
            print(header)

    def test_calibration(self):
        self.rtsys.calibrate(test_file)

    def test_freq_cal_inc(self):
        frequencies = np.arange(2.4001e+04)
        df = self.rtsys.freq_cal_inc(frequencies)
        print(df)


if __name__ == '__main__':
    unittest.main()
