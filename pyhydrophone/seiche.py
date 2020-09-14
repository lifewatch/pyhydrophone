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


    def get_name_datetime(self, file_name, utc=True):
        """
        Get the data and time of recording from the name of the file 
        """
        name = file_name.split('.')[0]
        start_timestamp = name.find('_') + 1
        date_string = name[start_timestamp::]
        date = datetime.strptime(date_string, "%Y%m%d_%H%M%S_%f")

        return date
    

    def get_new_name(self, filename, new_date):
        """
        Replace the datetime with the appropiate one
        """
        old_date = self.get_name_datetime(filename)
        old_date_name = datetime.strftime(old_date, "%Y%m%d_%H%M%S_%f")
        new_date_name = datetime.strftime(new_date, "%Y%m%d_%H%M%S_%f")
        new_filename = filename.replace(old_date_name, new_date_name)
        
        return new_filename