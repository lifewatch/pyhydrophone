#!/usr/bin/python
"""
Module : mte.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 25/01/2021
"""

from pyhydrophone.hydrophone import Hydrophone

from datetime import datetime
import os


class MTE(Hydrophone):
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format="%y%m%d_%H%M%S"):
        """
        Init an instance of Seiche
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
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format)

    def get_name_datetime(self, file_name, utc=True):
        """
        Get the data and time of recording from the name of the file
        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        utc : boolean
            If set to True, the time of the file will be considered Local and will be changed to utc according to
            the computer timezone
        """
        # Get the the creation time of the file
        # date = datetime.utcfromtimestamp(os.stat(file_name).st_ctime)
        # return date
        name = file_name.split('.')
        name = name[0].split('_')
        date_string = name[1] + '_' + name[2]
        date = super().get_name_datetime(date_string, utc=utc)
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
        old_date_name = datetime.strftime(old_date, "%Y%m%d_%H%M%S_%f")
        new_date_name = datetime.strftime(new_date, "%Y%m%d_%H%M%S_%f")
        new_filename = filename.replace(old_date_name, new_date_name)

        return new_filename