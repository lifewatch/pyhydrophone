#!/usr/bin/python
from pyhydrophone.hydrophone import Hydrophone

from datetime import datetime
import struct
import numpy as np
import zipfile
import os
import pathlib

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
    mode: string
        Can be 'lowpower' or 'broadband'
    channel: string
        Channel to process, 'A', 'B', 'C' or 'D'
    string_format : string
        Format of the datetime string present in the filename
    calibration_file : string or Path
        File where the frequency dependent sensitivity values for the calibration are
    """
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, mode, channel='A',
                 string_format="%Y-%m-%d_%H-%M-%S", calibration_file=None):
        super().__init__(name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format, calibration_file,
                         sep=';', freq_col_id=0, sens_col_id=1, start_data_id=0)
        self.cal_freq = 250
        self.cal_value = 114
        self.mode = mode
        self.channel = channel

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
    def _parse_board_file(board_file_path):
        board_info = pd.read_csv(board_file_path, delimiter=';', names=['id', 'T', 'V', 'I', 'P'],
                                 usecols=[0, 1, 2, 3, 4])
        board_info['T'] = board_info['T'].str.replace('T:', '')
        board_info.loc[board_info['T'] == ''] = np.nan
        board_info['T'] = board_info['T'].astype(float)
        board_info['V'] = board_info['V'].str.replace('V:', '')
        board_info.loc[board_info['V'] == ''] = np.nan
        board_info['V'] = board_info['V'].astype(float)
        board_info['I'] = board_info['I'].str.replace('I:', '')
        board_info.loc[board_info['I'] == ''] = np.nan
        board_info['I'] = board_info['I'].astype(float)
        board_info['P'] = board_info['P'].str.replace('P:', '')
        board_info.loc[board_info['P'] == ''] = np.nan
        board_info['P'] = board_info['P'].astype(float)
        board_info['timestamp'] = pd.to_datetime(board_info['id'].str.replace('@:', '').astype(float), unit='s')
        board_info['dP'] = board_info['timestamp'].diff().dt.total_seconds() * board_info['P']

        return board_info

    def plot_consumption(self, board_file_path):
        """
        Plot the consumption evolution from the board_file_path
        Parameters
        ----------
        board_file_path : str or Path
        """
        board_info = self._parse_board_file(board_file_path)
        board_info.plot(y=['V', 'P'])
        plt.show()

    def plot_consumption_total_mission(self, mission_folder_path, ax=None, show=True):
        if not isinstance(mission_folder_path, pathlib.Path):
            mission_folder_path = pathlib.Path(mission_folder_path)

        total_board = pd.DataFrame()
        for board_file_i in mission_folder_path.glob('**/*.txt'):
            if 'board' in board_file_i.name:
                board_i = self._parse_board_file(board_file_i)
                total_board = pd.concat([total_board, board_i])

        if ax is None:
            fig, ax = plt.subplots()
        total_board.plot(x='timestamp', y=['V', 'P'], secondary_y='P', ax=ax)
        if show:
            plt.show()

    def compute_consumption(self, board_file_path):
        """
        Calculate the total energy consumption of the file
        Parameters
        ----------
        board_file_path : str or Path

        Returns
        -------
        Total consumption in the file
        """
        board_info = self._parse_board_file(board_file_path)

        return board_info['dP'].sum() / 3600

    def compute_consumption_total_mission(self, mission_folder_path):
        """
        Calculate the total energy consumption of the file
        Parameters
        ----------
        mission_folder_path : str or Path

        Returns
        -------
        Total consumption in the mission
        """
        if not isinstance(mission_folder_path, pathlib.Path):
            mission_folder_path = pathlib.Path(mission_folder_path)

        total_consumption = 0
        for board_file_i in mission_folder_path.glob('**/*.txt'):
            if 'board' in board_file_i.name:
                total_consumption += self.compute_consumption(board_file_i)

        return total_consumption

    @staticmethod
    def read_header(file_path, zip_mode=False):
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

        if zip_mode==True:
            path_zip = file_path.split('.zip')[0]+'.zip'
            file_zip = os.path.relpath(file_path, start=path_zip).replace('\\','/')
            zipFolder = zipfile.ZipFile(path_zip, 'r')
            f = zipFolder.open(file_zip)
        else:
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

    def update_metadata(self, file_path, zip_mode=False):
        """
        Creates a new RTSys object from an already existing one but updating the metadata from the file header.
        The "mode" parameter stays the same.

        Parameters
        ----------
        file_path: str or Path
            path to the wav file recorded with RTSys with a correc header
        zip_mode: bool
            True if file is zipped, otherwise false
        """
        header = self.read_header(file_path, zip_mode)
        name, model, serial_number, sens, ampl = self.meta_from_header(header)
        return RTSys(name=name, model=model, serial_number=serial_number, sensitivity=sens, preamp_gain=ampl, Vpp=5.0,
                     mode=self.mode, calibration_file=self.calibration_file)

    def meta_from_header(self, header):
        sens = header['hydrophone_sensitivity_%s' % self.channel]
        name = 'RTSys'
        model = None
        serial_number = header['serial_number']

        if self.mode == 'lowpower':
            ampl = 20 * np.log10(5 / np.sqrt(2))
        else:
            ampl = 20 * np.log10((1 / (header['hydrophone_amplification_%s' % self.channel] *
                                       header['correction_factor_%s' % self.channel])))
        return name, model, serial_number, sens, ampl

    def one_rtsys_per_channel_from_header(self, file_path, zip_mode=False):
        extra_header = self.read_header(file_path, zip_mode)
        active_channels = []
        for channel_i in np.arange(4):
            if extra_header['active_channels'][channel_i] != '\x00':
                active_channels.append(extra_header['active_channels'][channel_i])

        rtsys_list = []
        for channel in active_channels:
            name, model, serial_number, sens, ampl = self.meta_from_header(extra_header)
            rtsys_list.append(RTSys(name=name, model=model, serial_number=serial_number, sensitivity=sens,
                                    preamp_gain=ampl, Vpp=5.0, channel=channel))

        if len(rtsys_list) == 1:
            return rtsys_list[0]
        else:
            return rtsys_list

    def calibrate(self, file_path, zip_mode=False):
        header = self.read_header(file_path, zip_mode)
        name, model, serial_number, sens, ampl = self.meta_from_header(header)
        self.sensitivity = sens
        self.preamp_gain = ampl
        self.Vpp = 5.0

    def get_freq_cal(self, sep=';', freq_col_id=0, sens_col_id=1, start_data_id=0):
        super().get_freq_cal(sep=sep, freq_col_id=freq_col_id, sens_col_id=sens_col_id, start_data_id=start_data_id)
