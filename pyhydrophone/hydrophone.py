#!/usr/bin/python
from datetime import datetime
import numpy as np
import soundfile as sf

try:
    import scipy.signal as sig
except ModuleNotFoundError:
    pass


class Hydrophone:
    """
    Base class Hydrophone initialization

    Parameters
    ----------
    name: str
        Name of the acoustic recorder
    model: str or int
        Model of the acoustic recorder
    serial_number : str or int
        Serial number of the acoustic recorder
    sensitivity : float
        Sensitivity of the acoustic recorder in db
    preamp_gain : float
        Gain of the preamplifier in dB
    Vpp : float
        Voltage peak to peak in volts
    string_format : string
        Format of the datetime string present in the filename
    """
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format):
        self.name = name
        self.model = model
        self.serial_number = serial_number
        self.sensitivity = sensitivity
        self.preamp_gain = preamp_gain
        self.Vpp = Vpp
        self.string_format = string_format
        self.cal_freq = 250
        self.cal_value = 114

    def get_name_datetime(self, date_string):
        """
        Read the name of the file and according to the hydrophone protocol get the date
        Parameters
        ----------
        date_string : string
            Datetime in string format
        """
        date = datetime.strptime(date_string, self.string_format)
        return date

    def get_new_name(self, filename, new_date):
        """
        Replace the datetime with the appropriate one
        Parameters
        ----------
        filename : string
            File name (not path) of the file
        new_date : datetime object
            New datetime to be replaced in the filename
        """
        raise Exception('get_new_name should be declared in the subclass %s' % self.__name__)

    def change_calibration_system(self, cal_freq, cal_val):
        """
        Change the parameters of the calibration system (piston phone)

        Parameters
        ----------
        cal_freq: float
            Calibration frequency in Hz
        cal_val: float
            Expected value in db

        """
        self.cal_value = cal_val
        self.cal_freq = cal_freq

    def update_calibration(self, calibration_signal, p_ref=1.0):
        """
        Updates ONLY the parameter preamp_gain of the hydrophone with a correction factor to match expected calibration.

        Parameters
        ----------
        calibration_signal: np.array
            signal to calibrate from (already cut to ONLY calibration)
        p_ref: float
            Reference pressure to compute db from

        Returns
        -------
        Updates the parameter preamp_gain
        """
        ref_wav = np.sqrt((calibration_signal ** 2).mean())
        mv = 10 ** (self.sensitivity / 20.0) * p_ref
        ma = 10 ** (self.preamp_gain / 20.0) * p_ref
        gain_upa = (self.Vpp / 2.0) / (mv * ma)
        real_db = 20 * np.log10(ref_wav * gain_upa)
        correction_factor = real_db - self.cal_value
        self.preamp_gain += correction_factor

    def calibrate(self, file_path):
        """
        Find the beginning and ending sample of the calibration tone
        Returns start and end points, in seconds
        Parameters
        ----------
        file_path : string or Path
            File where to look for the calibration (at the beginning of the file)

        Returns
        -------
        end sample of the calibration (int)
        """
        wav_file = sf.SoundFile(file_path)
        calibration_signal = wav_file.read()
        self.update_calibration(calibration_signal)

        return None

    def end_to_end_calibration(self, p_ref=1.0):
        """
        Returns the end to end calibration of the system, so it can be directly used on a wav file to obtain uPa

        Parameters
        ----------
        p_ref

        Returns
        -------
        End to end calibration in db
        """
        mv = 10 ** (self.sensitivity / 20.0) * p_ref
        ma = 10 ** (self.preamp_gain / 20.0) * p_ref
        gain_upa = (self.Vpp / 2.0) / (mv * ma)
        return 10 * np.log10(gain_upa**2)
