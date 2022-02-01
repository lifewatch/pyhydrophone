#!/usr/bin/python
from datetime import datetime
import numpy as np


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

    def calibrate(self, file_path):
        """
        Calibrate the instrument with that file

        Parameters
        ----------
        file_path : string or Path
            File containing the calibration tone

        Returns
        -------
        End sample of the calibration (int)
        """
        raise Exception('calibrate is not defined in the subclass %s' % self.__name__)

    def end_to_end_calibration(self, p_ref=1.0):
        mv = 10 ** (self.sensitivity / 20.0) * p_ref
        ma = 10 ** (self.preamp_gain / 20.0) * p_ref
        gain_upa = (self.Vpp / 2.0) / (mv * ma)
        return 10 * np.log10(gain_upa**2)
