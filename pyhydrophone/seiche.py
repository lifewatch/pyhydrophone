from datetime import datetime

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents a Seiche acoustic recorder
"""


class Seiche(Hydrophone):
    def __init__(self, name, model, sensitivity, preamp_gain, Vpp):
        """
        Init an instance of Seiche
        """
        super().__init__(name, model, sensitivity, preamp_gain, Vpp)


    def get_name_date(self, wavfile_name):
        """
        Get the data and time of recording from the name of the file 
        """
        name = wavfile_name.split('.')
        date_string = name[0][5:-1]
        date = datetime.strptime(date_string, "%Y%m%d_%H%M%S_%f")

        return date