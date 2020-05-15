from datetime import datetime
import os

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents an AMARG3 acoustic recorder
"""


class AmarG3(Hydrophone):
    def __init__(self, name, model, hydroph_sensitivity, preamp_gain, Vpp):
        """
        Init an instance of AMARG3
        """
        super().__init__(name, model, hydroph_sensitivity, preamp_gain, Vpp)

    
    def get_name_date(self, file_name):
        """
        Get the data and time of recording from the name of the file 
        """
        name = os.path.split(file_name)[1]
        date_string = name.split('.')[-2][-16:-1]
        date = datetime.strptime(date_string, "%Y%m%dT%H%M%S")

        return date



class AmarG3MEMS(AmarG3):
    def __init__(self, name, model, hydroph_sensitivity, preamp_gain, mems_sensitivity, Vpp):
        """
        Add the MEMS specs
        """
        self.mems_sensitivity = mems_sensitivity
        super().__init__(name, model, hydroph_sensitivity, preamp_gain, Vpp)
