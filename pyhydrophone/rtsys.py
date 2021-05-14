#!/usr/bin/python
"""

=======
Module : seiche.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 9/23/2020
>>>>>>> 4dbb56f24caac07d983b69479e57cb57cfb894fb
"""

from pyhydrophone.hydrophone import Hydrophone

from datetime import datetime


try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ModuleNotFoundError:
    pass


class RTSys(Hydrophone):
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format="%Y%m%d_%H%M%S_%f"):

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
        name = file_name.split('.')[0]
        start_timestamp = name.find('_') + 1
        date_string = name[start_timestamp::]
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

    @staticmethod
    def plot_consumption(board_file_path):
        """
        Plot the consumption evolution from the board_file_path
        Parameters
        ----------
        board_file_path : str or Path
        """
        board_info = pd.read_csv(board_file_path, delimiter=';', names=['id', 'T', 'V', 'I', 'P'],
                                 usecols=[0, 1, 2, 3, 4])
        board_info['T'] = board_info['T'].str.replace('T:', '').astype(float)
        board_info['V'] = board_info['V'].str.replace('V:', '').astype(float)
        board_info['I'] = board_info['I'].str.replace('I:', '').astype(float)
        board_info['P'] = board_info['P'].str.replace('P:', '').astype(float)
        board_info.plot(y=['V', 'P'])
        plt.show()
        
