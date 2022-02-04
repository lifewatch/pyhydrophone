import pathlib
import pyhydrophone as pyhy
import unittest


test_folder = pathlib.Path("./test_data/rtsys/")
test_file = pathlib.Path("./test_data/rtsys/channelA_2021-10-11_13-11-09.wav")

rtsys_name = 'RTSys'
rtsys_model = 'RESEA320'
rtsys_serial_number = 2003001
rtsys_sens = -180
rtsys_preamp = 0
rtsys_vpp = 5
rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=rtsys_serial_number, sensitivity=rtsys_sens,
                   preamp_gain=rtsys_preamp, Vpp=rtsys_vpp)


class TestRTSys(unittest.TestCase):
    def setUp(self) -> None:
        self.rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=rtsys_serial_number,
                                sensitivity=rtsys_sens, preamp_gain=rtsys_preamp, Vpp=rtsys_vpp)

    def test_init_from_file(self):
        rtsys = pyhy.RTSys.from_header(test_file)
        print(rtsys)

    def test_header(self):
        for file_path in test_folder.glob('*.wav'):
            header = rtsys.read_header(file_path)
            print(header)

    def test_calibration(self):
        rtsys = pyhy.RTSys.from_header(test_file)
        rtsys.calibrate(test_file)


if __name__ == '__main__':
    unittest.main()
