from datetime import datetime

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents a Seiche acoustic recorder
"""


class Seiche(Hydrophone):
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp):
        """
        Init an instance of Seiche
        """
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp)


    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file 
        """
        name = file_name.split('.')
        start_timestamp = name[0].find('_') + 1
        date_string = name[0][start_timestamp:-1]
        date = datetime.strptime(date_string, "%Y%m%d_%H%M%S_%f")

        return date