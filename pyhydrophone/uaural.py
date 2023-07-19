#!/usr/bin/python
from pyhydrophone.hydrophone import Hydrophone

from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ModuleNotFoundError:
    pass


class uAural(Hydrophone):
    """
    Init an instance of uAural

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
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format="%H%M%S_%Y%m%d"):
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format)

    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file
        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        """
        name = file_name.split('.')[0]
        date_and_time = name.split('_')[:2]
        date_string = '_'.join(date_and_time)
        date = super().get_name_datetime(date_string)
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
        old_date = self.get_name_datetime(filename)
        old_date_name = datetime.strftime(old_date, self.string_format)
        new_date_name = datetime.strftime(new_date, self.string_format)
        new_filename = filename.replace(old_date_name, new_date_name)

        return new_filename
