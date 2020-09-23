#!/usr/bin/python
"""
Module : amar.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 9/23/2020
"""

from pyhydrophone.hydrophone import Hydrophone

import os
from datetime import datetime


class AmarG3(Hydrophone):
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp):
        """
        Init an instance of AMARG3
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
        """
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp)
    
    def get_name_datetime(self, file_name, utc=False):
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
        name = os.path.split(file_name)[1]
        date_string = name.split('.')[-2][-16:-1]
        date = datetime.strptime(date_string, "%Y%m%dT%H%M%S")

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
        old_date_name = datetime.strftime(old_date, "%Y%m%dT%H%M%S")
        new_date_name = datetime.strftime(new_date, "%Y%m%dT%H%M%S")
        new_filename = filename.replace(old_date_name, new_date_name)
        
        return new_filename


class AmarG3MEMS(AmarG3):
    def __init__(self, name, model, serial_number, hydroph_sensitivity, preamp_gain, mems_sensitivity, Vpp):
        """
        Add the MEMS specs
        Parameters
        ----------
        name: str
            Name of the acoustic recorder
        model: str or int
            Model of the acoustic recorder
        serial_number : str or int
            Serial number of the acoustic recorder
        hydroph_sensitivity : float
            Sensitivity of the acoustic recorder in db
        preamp_gain : float
            Gain of the preamplifier in dB
        mems_sensitivity : float
            Sensitivity of the accelerometer
        Vpp : float
            Voltage peak to peak in volts
        """
        self.mems_sensitivity = mems_sensitivity
        super().__init__(name, model, serial_number, hydroph_sensitivity, preamp_gain, Vpp)
