import os
from datetime import datetime
import configparser
import xml.etree.ElementTree as ET
import importlib
import pandas as pd
import soundfile as sf
import zipfile
import numpy as np

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents a Bruel & Kjaer acoustic recorder
"""


class BruelKjaer(Hydrophone):
    def __init__(self, name, model, serial_number, amplif):
        """
        Init an instance of B&K
        `amplif` is in V/Pa
        """
        self.amplif = amplif
        if amplif not in [100e-6, 316e-6, 1e-3, 3.16e-3, 10e-3, 31.6e-3, 100e-3, 316e-3, 1.0, 3.16, 10.0]:
            raise Exception('This amplification is not available!')
        sensitivity = 10*np.log10((amplif/1e6)**2)

        super().__init__(name, model, serial_number, sensitivity, preamp_gain=0.0, Vpp=2.0)
    

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


    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file 
        """
        name = file_name.split('.')
        date_string = name[0].split('_')[0]
        date = datetime.strptime(date_string, "%y%m%d%H%M%S")

        return date

    
    def update_calibration(self, ref_file_path):
        """
        Update the sensitivity
        """
        ref_file, _ = sf.read(ref_file_path)
        ref_val = 10*np.log10((ref_file**2).mean())

        self.sensitivity = self.sensitivity + ref_val