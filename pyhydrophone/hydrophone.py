#!/usr/bin/python
"""
Module : hydrophone.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 9/23/2020
"""
from datetime import datetime

class Hydrophone:
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format):
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
        self.name = name
        self.model = model
        self.serial_number = serial_number
        self.sensitivity = sensitivity
        self.preamp_gain = preamp_gain
        self.Vpp = Vpp
        self.string_format = string_format

    def get_name_datetime(self, date_string, utc=False):
        """
        Read the name of the file and according to the hydrophone protocol get the date
        Parameters
        ----------
        date_string : string
            Datetime in string format
        utc : boolean
            If set to True, the time of the file will be considered Local and will be changed to utc according to
            the computer timezone
        """
        date = datetime.strptime(date_string, self.string_format)
        if utc:
            timeoff = datetime.utcnow() - datetime.now()
            date += timeoff
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

    def update_calibration(self, ref_signal):
        """
        Update the calibration
        Parameters
        ----------
        ref_signal : str or Path
            File path to the reference file to update the Vpp according to the calibration tone
        """
        raise Exception('update_calibration should be declared in the subclass %s' % self.__name__)
