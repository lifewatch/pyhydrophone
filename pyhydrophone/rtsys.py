#!/usr/bin/python
from pyhydrophone.hydrophone import Hydrophone

import soundfile as sf
from datetime import datetime
import struct
import numpy as np

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ModuleNotFoundError:
    pass


class RTSys(Hydrophone):
    """
    Init an instance of RTSys
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
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format="%Y-%m-%d_%H-%M-%S"):
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format)
        self.cal_freq = 250
        self.cal_value = 131.4

    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file
        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        """
        name = file_name.split('.')[0]
        start_timestamp = name.find('_') + 1
        date_string = name[start_timestamp::]
        date = super().get_name_datetime(date_string)
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
        old_date_name = datetime.strftime(old_date, self.string_format)
        new_date_name = datetime.strftime(new_date, self.string_format)
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

    @staticmethod
    def compute_consumption(mission_file_path):
        """
        Calculate the total energy consumption of the mission
        Parameters
        ----------
        mission_file_path

        Returns
        -------

        """

    @staticmethod
    def read_header(file_path):
        """
        Return the parameters of the *.wav file's header as a dictionary
        Parameters
        ----------
        file_path: Path or string
            Path to the *.wav file to read the header from

        Returns
        -------
        extra_header: dictionary with all the parameters of the configuration provided by RTSys
        """
        HEADER_CONF = {
            'conf': {'format': 'c', 'start': 0, 'end': 4, 'n': 4},
            'conf_size': {'format': 'I', 'start': 4, 'end': 8, 'n': 1},
            'conf_version': {'format': 'I', 'start': 8, 'end': 12, 'n': 1},
            'epoch_time_recording': {'format': 'd', 'start': 16, 'end': 24, 'n': 1},
            'channel': {'format': 'c', 'start': 23, 'end': 24, 'n': 1},
            'sr': {'format': 'f', 'start': 28, 'end': 32, 'n': 1},
            'hydrophone_sensitivity_A': {'format': 'f', 'start': 32, 'end': 36, 'n': 1},
            'hydrophone_sensitivity_B': {'format': 'f', 'start': 36, 'end': 40, 'n': 1},
            'hydrophone_sensitivity_C': {'format': 'f', 'start': 40, 'end': 44, 'n': 1},
            'hydrophone_sensitivity_D': {'format': 'f', 'start': 44, 'end': 48, 'n': 1},
            'hydrophone_amplification_A': {'format': 'f', 'start': 48, 'end': 52, 'n': 1},
            'hydrophone_amplification_B': {'format': 'f', 'start': 52, 'end': 56, 'n': 1},
            'hydrophone_amplification_C': {'format': 'f', 'start': 56, 'end': 60, 'n': 1},
            'hydrophone_amplification_D': {'format': 'f', 'start': 60, 'end': 64, 'n': 1},
            'correction_factor_A': {'format': 'f', 'start': 64, 'end': 68, 'n': 1},
            'correction_factor_B': {'format': 'f', 'start': 68, 'end': 72, 'n': 1},
            'correction_factor_C': {'format': 'f', 'start': 72, 'end': 76, 'n': 1},
            'correction_factor_D': {'format': 'f', 'start': 76, 'end': 80, 'n': 1},
            'serial_number': {'format': 'f', 'start': 80, 'end': 96, 'n': 4},
            'active_channels': {'format': 'c', 'start': 100, 'end': 104, 'n': 4}
        }

        f = open(file_path, 'rb')
        f.seek(40)
        config_size = struct.unpack('I', f.read(4))[0]
        f.seek(36)
        header_buffer = f.read(config_size)
        f.close()
        extra_header = {}
        for chunk_name, chunk_format in HEADER_CONF.items():
            if (chunk_format['n'] == 1) & (chunk_format['format'] != 'c'):
                extra_header[chunk_name] = struct.unpack(chunk_format['format'],
                                                         header_buffer[chunk_format['start']:chunk_format['end']])[0]
            else:
                extra_header[chunk_name] = bytes.decode(header_buffer[chunk_format['start']:chunk_format['end']])

        return extra_header

    @staticmethod
    def from_header(file_path, mode='broadband'):
        extra_header = RTSys.read_header(file_path)
        channel = str(extra_header['channel'])
        sens = extra_header['hydrophone_sensitivity_%s' % channel]
        name = 'RTSys'
        model = None
        serial_number = extra_header['serial_number']

        if mode == 'lowpower':
            ampl = 20 * np.log10(5/np.sqrt(2))
        else:
            ampl = 20 * np.log10((1 / (extra_header['hydrophone_amplification_%s' % channel] *
                                  extra_header['correction_factor_%s' % channel])))

        return RTSys(name=name, model=model, serial_number=serial_number, sensitivity=sens, preamp_gain=ampl, Vpp=5.0)