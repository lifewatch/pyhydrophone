from datetime import datetime
import os

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents an AMARG3 acoustic recorder
"""


class AmarG3(Hydrophone):
    def __init__(self, name, model, serial_number, hydroph_sensitivity, preamp_gain, Vpp):
        """
        Init an instance of AMARG3
        """
        super().__init__(name, model, serial_number, hydroph_sensitivity, preamp_gain, Vpp)

    
    def get_name_datetime(self, file_name, utc=False):
        """
        Get the data and time of recording from the name of the file 
        """
        name = os.path.split(file_name)[1]
        date_string = name.split('.')[-2][-16:-1]
        date = datetime.strptime(date_string, "%Y%m%dT%H%M%S")

        return date
    

    def get_new_name(self, filename, new_date):
        """
        Replace the datetime with the appropiate one
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
        """
        self.mems_sensitivity = mems_sensitivity
        super().__init__(name, model, serial_number, hydroph_sensitivity, preamp_gain, Vpp)
