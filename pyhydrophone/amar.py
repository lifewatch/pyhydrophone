from datetime import datetime
import os

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents an AMARG3 acoustic recorder
"""


class AmarG3(Hydrophone):
    def __init__(self, name, model, hydroph_sensitivity, preamp_gain, mems_sensitivity, Vpp):
        """
        Init an instance of AMARG3
        """
        self.mems_sensitivity = mems_sensitivity
        super().__init__(name, model, hydroph_sensitivity, preamp_gain, Vpp)

    
    def get_name_date(self):
        """
        Get the data and time of recording from the name of the file 
        """
        wavfile_name = os.path.split(self.sound_path)[1]
        date_string = wavfile_name.split('.')[-2][-16:-1]
        date = datetime.strptime(date_string, "%Y%m%dT%H%M%S")

        return date