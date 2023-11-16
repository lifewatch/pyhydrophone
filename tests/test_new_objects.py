import pathlib
import pyhydrophone as pyhy
import unittest

TEST_DATA_DIR = pathlib.Path(__file__).parent / "test_data"


class TestHydrophones(unittest.TestCase):
    def test_st(self):
        # Hydrophone Setup
        model = 1
        name = 'SoundTrap'
        serial_number = 67416073
        calibration_file = TEST_DATA_DIR / "soundtrap" / "calibration_data.xlsx"

        st = pyhy.SoundTrap(name, model, serial_number, calibration_file=calibration_file, val='sensitivity',
                            freq_col_id=1, val_col_id=29, start_data_id=6)

    def test_amar(self):
        # Hydrophone Setup
        sensitivity = -199.0
        preamp_gain = 1
        model = 1
        mems_sensitivity = -199.0
        name = 'AmarG3'
        Vpp = 2

        am = pyhy.AmarG3(name, model, sensitivity, preamp_gain, mems_sensitivity, Vpp)

    def test_uaural(self):
        uaural = pyhy.uAural(sensitivity=-180, name='uAural', model='RX', serial_number=1, preamp_gain=12, Vpp=2.0)

    def test_bk(self):
        bk_model = 'Nexus'
        bk_name = 'B&K'
        preamp_gain = -170
        bk_Vpp = 2.0
        bk_test = pyhy.BruelKjaer(name=bk_name, model=bk_model, preamp_gain=preamp_gain, Vpp=bk_Vpp, serial_number=1,
                                  type_signal='test')
        bk_ref = pyhy.BruelKjaer(name=bk_name, model=bk_model, preamp_gain=preamp_gain, Vpp=bk_Vpp, serial_number=1,
                                 type_signal='ref')

    def test_upam(self):
        upam_model = 'uPam'
        upam_name = 'Seiche'
        upam_serial_number = 'SM7213'
        upam_sensitivity = -196.0
        upam_preamp_gain = 0.0
        upam_Vpp = 20.0
        upam = pyhy.uPam(name=upam_name, model=upam_name, serial_number=upam_serial_number,
                         sensitivity=upam_sensitivity,
                         preamp_gain=upam_preamp_gain, Vpp=upam_Vpp)

    def test_aural(self):
        aural_name = 'Aural'
        aural_model = 'M2'
        aural_serial_number = 0
        aural_sensitivity = -164.0
        aural_preamp_gain = 16.0
        aural_Vpp = 2.0
        aural = pyhy.MTE(name=aural_name, model=aural_model, serial_number=aural_serial_number,
                         sensitivity=aural_sensitivity,
                         preamp_gain=aural_preamp_gain, Vpp=aural_Vpp, string_format='%y%m%d_%H%M%S')

    def test_rtsys(self):
        rtsys_name = 'RTSys'
        rtsys_model = 'RESEA320'
        rtsys_sensitivity = -180
        rtsys_preamp_gain = 0
        rtsys_Vpp = 2.0
        serial_number = 3
        calibration_file = TEST_DATA_DIR / "rtsys" / "SN130.csv"
        rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=serial_number,
                           sensitivity=rtsys_sensitivity,
                           preamp_gain=rtsys_preamp_gain, Vpp=rtsys_Vpp, mode='lowpower', channel='A',
                           calibration_file=calibration_file)

    def test_iclisten(self):
        icListen_name = 'icListen'
        icListen_model = 0
        icListen_serial_number = 0
        icListen_sensitivity = -178
        icListen_Vpp = 6
        icListen_preamp_gain = 0
        icListen = pyhy.icListen(name=icListen_name, model=icListen_model, serial_number=icListen_serial_number,
                                 sensitivity=icListen_sensitivity, preamp_gain=icListen_preamp_gain, Vpp=icListen_Vpp)
