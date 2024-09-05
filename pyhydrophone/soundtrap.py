#!/usr/bin/python
from pyhydrophone.hydrophone import Hydrophone

import os
import zipfile
import numpy as np
import pandas as pd
import soundfile as sf
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import pathlib


class SoundTrap(Hydrophone):
    """
    Initialize a SoundTrap instance

    Parameters
    ----------
    name: str
        Name of the acoustic recorder
    model: str or int
        Model of the acoustic recorder
    serial_number : str or int
        Serial number of the acoustic recorder. It has to match the one in the calibration file
    sensitivity : float
        Sensitivity of the acoustic recorder in db. If None the one from the calibration file will be read
    gain_type : str
        'High' or 'Low', depending on the settings of the recorder
    string_format : string
        Format of the datetime string present in the filename
    calibration_file : string or Path
        File where the frequency dependent sensitivity values for the calibration are
    """
    def __init__(self, name, model, serial_number, sensitivity=None, gain_type='High', string_format="%y%m%d%H%M%S",
                 calibration_file=None, **kwargs):
        if sensitivity is None:
            try:
                query = 'http://oceaninstruments.azurewebsites.net/api/Devices/Search/%s' % serial_number
                response = requests.get(query).json()
                if len(response) > 1:
                    models_available = {}
                    for device in response:
                        if device['serialNo'] == str(serial_number):
                            models_available[device['modelName']] = device['deviceId']

                    if model not in models_available.keys():
                        raise AttributeError('There are multiple instruments with serial number %s. Set the model '
                                             'parameter to match the model specified in the SoundTrap calibration '
                                             'webpage to chose the correct one: %s' %
                                             (serial_number, models_available.keys()))
                    else:
                        device_id = models_available[model]
                else:
                    # Ignore the model name if there is only one serial number
                    device_id = response[0]['deviceId']
                query = 'http://oceaninstruments.azurewebsites.net/api/Calibrations/Device/%s' % device_id
                response = requests.get(query).json()[0]
                if gain_type == 'High':
                    sensitivity = -response['highFreq']
                elif gain_type == 'Low':
                    sensitivity = -response['lowFreq']
                else:
                    raise Exception('Gain type %s is not implemented!' % gain_type)
            except ConnectionError:
                raise Exception('Serial number %s is not in the OceanInstruments database!' % serial_number)

        super().__init__(name, model, serial_number=serial_number, sensitivity=sensitivity, preamp_gain=0.0,
                         Vpp=2.0, string_format=string_format, calibration_file=calibration_file, **kwargs)

    @staticmethod
    def read_file_specs(xmlfile_path, last_gain, date_format='%Y-%m-%dT%H:%M:%S'):
        """
        Read the specs of the recording from the XML file and save them to the object

        Parameters
        ----------
        xmlfile_path : string or path
            Path to the xml file
        last_gain : str
            Last gain type. 'High' or 'Low', depending on the settings of the recorder
        date_format : string
            Format of the datetime in the .log.xml file
        """
        tree = ET.parse(xmlfile_path)
        type_start = tree.find('EVENT/START').get('STATE')

        # Metadata colected
        temp = float(tree.find('EVENT/TEMPERATURE').text)/100

        # WavFileHandler information
        sampling_attr = {}
        WavFileHandler = tree.findall('PROC_EVENT/WavFileHandler')
        for wfh in WavFileHandler:
            sampling_attr.update(wfh.attrib)

        # Info about the sampling
        fs = float(tree.find('CFG/FS').text)

        # Setup information. Read SoundTrap gain ('HIGH' or 'LOW')
        if type_start == 'NEW':
            st_gain = tree.find('EVENT/AUDIO').get('Gain')
        else:
            if last_gain is None:
                print('Unknown gain if it is reopened and the last gain is not passed!')
            st_gain = last_gain

        start_time = datetime.strptime(sampling_attr['SamplingStartTimeLocal'], date_format)
        stop_time = datetime.strptime(sampling_attr['SamplingStopTimeLocal'], date_format)

        return {'type_start': type_start, 'temp': temp, 'fs': fs, 'st_gain': st_gain,
                'start_time': start_time, 'stop_time': stop_time}

    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file
        Will convert the local in UTC. It assumes the localtime is the one from the computer

        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        """
        name = file_name.split('.')
        date_string = name[1]
        date = super().get_name_datetime(date_string)
        return date

    @staticmethod
    def get_xml_utc_datetime(file_path):
        """
        Get the UTC datetime from the xml file

        Parameters
        ----------
        file_path : str or Path

        """
        if type(file_path) == str:
            xml_name = file_path.replace('.wav', '.log.xml')
        else:
            xml_name = file_path.parent.joinpath(file_path.name.replace('.wav', '.log.xml'))

        tree = ET.parse(xml_name)
        WavFileHandler_list = tree.findall('PROC_EVENT/WavFileHandler')
        for wfh in WavFileHandler_list:
            if 'SamplingStartTimeUTC' in wfh.attrib.keys():
                utc_datetime = datetime.strptime(wfh.attrib.values(), format='%Y-%m-%dTH:M:S')
                return utc_datetime

        return None

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
        old_date_name = datetime.strftime(old_date, "%y%m%d%H%M%S")
        new_date_name = datetime.strftime(new_date, "%y%m%d%H%M%S")
        new_filename = filename.replace(old_date_name, new_date_name)

        return new_filename

    def test_calibration(self, signal):
        """
        Test the calibration of the soundtrap
        """
        # TO BE IMPLEMENTED


class SoundTrapHF(SoundTrap):
    def __init__(self, name, model, serial_number, sensitivity=None, gain_type='High', string_format="%y%m%d%H%M%S",
                 calibration_file=None, **kwargs):
        """
        Init a SoundTrap HF reader

        Parameters
        ----------
        name: str
            Name of the acoustic recorder
        model: str or int
            Model of the acoustic recorder
        serial_number : str or int
            Serial number of the acoustic recorder. It has to match the one in the calibration file
        sensitivity : float
            Sensitivity of the acoustic recorder in db. If None the one from the calibration file will be read
        gain_type : str
            'High' or 'Low', depending on the settings of the recorder
        string_format : string
            Format of the datetime string present in the filename
        calibration_file : string or Path
            File where the frequency dependent sensitivity values for the calibration are
        """
        super().__init__(name, model, serial_number, sensitivity, gain_type, string_format,
                         calibration_file=calibration_file, **kwargs)

    def read_HFfolder(self, main_folder_path, zip_mode=False, include_dirs=False):
        """
        Read all the clicks in all the folders. If zip_mode is True and include_dirs is True, only the INSIDE folders
        can be zipped inside a non-zipped folder. If only one zip folder is to be analyzed, then set include_dirs
        to False.

        Parameters
        ----------
        main_folder_path: str or Path
            Folder containing all the files and/or subfolders to be extracted
        zip_mode : boole
            Set to True if the folders are zipped
        include_dirs : bool
            Set to True if folder needs to be analyzed recursively

        Returns
        -------
        A DataFrame with all the clicks of all the folders and a fs metadata parameter with the sampling rate
        """
        if type(main_folder_path) == str:
            main_folder_path = pathlib.Path(main_folder_path)
        clicks = pd.DataFrame()
        if not zip_mode:
            if include_dirs:
                glob_str = '**.wav'
            else:
                glob_str = '*.wav'
            for file_name in main_folder_path.glob(glob_str):
                clicks_file = self.read_HFclicks_file(file_name, zip_mode)
                clicks = pd.concat([clicks, clicks_file])
        else:
            if include_dirs:
                for zipped_dir in main_folder_path.glob('*'):
                    clicks_file = self.read_HFfolder(zipped_dir, zip_mode=zip_mode, include_dirs=False)
                    clicks = clicks.append(clicks_file)
            else:
                folder_path = zipfile.ZipFile(main_folder_path, 'r', allowZip64=True)
                files_list = folder_path.namelist()
                for file_name in files_list:
                    if file_name.split('.')[-1] == 'wav':
                        file_name = pathlib.Path(folder_path.filename).joinpath(file_name)
                        clicks_file = self.read_HFclicks_file(file_name, zip_mode)
                        clicks = clicks.append(clicks_file)

        return clicks

    def read_HFclicks_file(self, wavfile_path, zip_mode=False):
        """
        Read all the clicks stored in a folder with soundtrap files

        Parameters
        ----------
        wavfile_path: str
            Wav file path
        zip_mode : boolean
            Set to True if the folders are zipped

        Returns
        -------
        A DataFrame with all the clicks and a fs metadata parameter with the sampling rate
        """
        if not isinstance(wavfile_path, pathlib.Path):
            wavfile_path = pathlib.Path(wavfile_path)
        bcl_name = wavfile_path.name.replace('.wav', '.bcl')
        dwv_name = wavfile_path.name.replace('.wav', '.dwv')
        xml_name = wavfile_path.name.replace('.wav', '.log.xml')
        if zip_mode:
            zip_file = zipfile.ZipFile(wavfile_path.parent, 'r', allowZip64=True)
            bcl_path = zip_file.open(bcl_name)
            dwv_path = zip_file.open(dwv_name)
            xml_path = zip_file.open(xml_name)
        else:
            bcl_path = os.path.join(wavfile_path.parent, bcl_name)
            dwv_path = os.path.join(wavfile_path.parent, dwv_name)
            xml_path = os.path.join(wavfile_path.parent, xml_name)

        try:
            file_clicks = self._read_HFclicks(bcl_path, dwv_path, xml_path)
        except FileNotFoundError:
            print(dwv_path, 'has some problem and can not be read')
        if zip_mode:
            dwv_path = wavfile_path.parent.joinpath(bcl_name)
        file_clicks['filename'] = str(dwv_path)
        return file_clicks

    def _read_HFclicks(self, bcl_path, dwv_path, xml_path):
        """
        Read the clicks of one soundtrap file

        Parameters
        ----------
        bcl_path : str or Path
            Path to the bcl file
        dwv_path : str or Path
            Path to the dwv file
        xml_path : str or Path
            Path to the .log.xml file

        Returns
        -------
        A DataFrame with all the parameters from the bcl file + a column with the wave and a column with the datetime
        """

        # Read the wav file with all the clicks
        sound_file = sf.SoundFile(dwv_path, 'r')

        # click_len has to be checked automatically
        click_len = self.read_HFparams(xml_path=xml_path)

        # Read the info of clicks
        clicks_info = pd.read_csv(bcl_path)
        clicks_info = clicks_info[clicks_info['report'] == 'D']
        clicks_info = clicks_info[clicks_info['state'] == 1]
        waves = []

        for block in sound_file.blocks(blocksize=click_len):
            waves.append(block.astype(float))

        print(dwv_path, 'bcl:', len(clicks_info), 'dwv:', len(waves))

        if len(waves) < len(clicks_info):
            # Cut the clicks info if there are not enough snippets
            clicks_info = clicks_info.loc[0:len(waves)]

        clicks_info['wave'] = waves[0:len(clicks_info)]
        clicks_info['start_sample'] = np.arange(len(clicks_info)) * click_len
        clicks_info['end_sample'] = clicks_info['start_sample'] + click_len
        clicks_info['duration'] = click_len
        clicks_info['fs'] = sound_file.samplerate
        clicks_info['datetime'] = pd.to_datetime(clicks_info['rtime'] + clicks_info['mticks'] / 1e6, unit='s')

        return clicks_info.reset_index(drop=True)

    @staticmethod
    def read_HFparams(xml_path):
        """
        Return the length of the clips and the time in between

        Parameters
        ----------
        xml_path : string or Path
            Path to the .log.xml file

        Returns
        -------
        Clip length in samples (int)
        """
        tree = ET.parse(xml_path)

        # blank_len = int(tree.find('CFG/BLANKING').text)
        clip_len = int(tree.find('CFG/PREDET').text) + int(tree.find('CFG/POSTDET').text)

        return clip_len
