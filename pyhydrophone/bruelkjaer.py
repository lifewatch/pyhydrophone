#!/usr/bin/python
"""
Module : bruelkjaer.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 9/23/2020
"""

from pyhydrophone.hydrophone import Hydrophone

import numpy as np
import soundfile as sf
from datetime import datetime


class BruelKjaer(Hydrophone):
    def __init__(self, name, model, serial_number, amplif, string_format="%y%m%d%H%M%S"):
        """
        Init an instance of B&K
        Parameters
        ----------
        name: str
            Name of the acoustic recorder
        model: str or int
            Model of the acoustic recorder
        serial_number : str or int
            Serial number of the acoustic recorder
        amplif : float
            Amplification selected in the Nexus in V/Pa
        string_format : string
            Format of the datetime string present in the filename
        """
        self.amplif = amplif
        if amplif not in [100e-6, 316e-6, 1e-3, 3.16e-3, 10e-3, 31.6e-3, 100e-3, 316e-3, 1.0, 3.16, 10.0]:
            raise Exception('This amplification is not available!')
        sensitivity = 10*np.log10((amplif/1e6)**2)

        super().__init__(name, model, serial_number, sensitivity, preamp_gain=0.0, Vpp=2.0, string_format=string_format)

    def __setattr__(self, name, value):
        """
        If the amplif is changed, update the sensitivity 
        """
        if name == 'amplif':
            sensitivity = 10*np.log10((value/1e6)**2)
            self.__dict__['sensitivity'] = sensitivity
            self.__dict__['amplif'] = value
        else: 
            return super().__setattr__(name, value)

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
        name = file_name.split('.')
        date_string = name[0].split('_')[0]
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
        old_date_name = datetime.strftime(old_date, "%y%m%d%H%M%S")
        new_date_name = datetime.strftime(new_date, "%y%m%d%H%M%S")
        new_filename = filename.replace(old_date_name, new_date_name)
        
        return new_filename
    
    def update_calibration(self, ref_file_path):
        """
        Update the sensitivity
        Parameters
        ----------
        ref_file_path : str or Path
            File path to the reference file to update the sensitivity according to the calibration tone
        """
        ref_file, _ = sf.read(ref_file_path)
        ref_val = 10*np.log10((ref_file**2).mean())

        self.sensitivity = self.sensitivity + ref_val
