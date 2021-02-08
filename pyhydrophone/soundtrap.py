#!/usr/bin/python
"""
Module : soundtrap.py
Authors : Clea Parcerisas
Institution : VLIZ (Vlaams Instituut voor de Zee)
Last Accessed : 9/23/2020
"""

from pyhydrophone.hydrophone import Hydrophone

import os
import zipfile
import numpy as np
import configparser
import pandas as pd
import soundfile as sf
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import tqdm


class SoundTrap(Hydrophone):
    def __init__(self, name, model, serial_number, sensitivity=None, gain_type='High', string_format="%y%m%d%H%M%S"):
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
        """
        if sensitivity is None:
            try:
                query = 'http://oceaninstruments.azurewebsites.net/api/Devices/Search/%s' % serial_number
                response = requests.get(query).json()[0]
                device_id = response['deviceId']
                query = 'http://oceaninstruments.azurewebsites.net/api/Calibrations/Device/%s' % device_id
                response = requests.get(query).json()[0]
                if gain_type == 'High':
                    sensitivity = response['highFreq']
                elif gain_type == 'Low':
                    sensitivity = response['lowFreq']
                else:
                    raise Exception('Gain type %s is not implemented!' % gain_type)
            except ConnectionError:
                raise Exception('Serial number %s is not in the OceanInstruments database!' % serial_number)

        super().__init__(name, model, serial_number=serial_number, sensitivity=sensitivity, preamp_gain=0.0,
                         Vpp=2.0, string_format=string_format)

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

    def get_name_datetime(self, file_name, utc=True):
        """
        Get the data and time of recording from the name of the file 
        Will convert the local in UTC. It assumes the localtime is the one from the computer
        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        utc : boolean
            If set to True, the time of the file will be considered Local and will be changed to utc according to
            the computer timezone
        """
        name = file_name.split('.')
        date_string = name[1]
        date = super().get_name_datetime(date_string, utc=utc)
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
        old_date = self.get_name_datetime(filename, utc=False)
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
    def __init__(self, name, model, serial_number, sensitivity=None, gain_type='High', string_format="%y%m%d%H%M%S"):
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
        """
        super().__init__(name, model, serial_number, sensitivity, gain_type, string_format)

    def read_HFfolder(self, main_folder_path, zip_mode=False):
        """
        Read all the clicks in all the folders
        Parameters
        ----------
        main_folder_path: str
            Folder containing all the files and/or subfolders to be extracted
        zip_mode : boolean
            Set to True if the folders are zipped

        Returns
        -------
        A DataFrame with all the clicks of all the folders and a fs metadata parameter with the sampling rate
        """
        clicks = pd.DataFrame()
        for folder_name in tqdm(os.listdir(main_folder_path)):
            folder_path = os.path.join(main_folder_path, folder_name)
            folder_clicks = self.read_HFclicks(folder_path, zip_mode=zip_mode)
            clicks = clicks.append(folder_clicks, ignore_index=True)
        
        # Keep the metadata
        clicks.fs = clicks.fs

        return clicks

    def read_HFclicks(self, folder_path, zip_mode=False):
        """
        Read all the clicks stored in a folder with soundtrap files
        Parameters
        ----------
        folder_path: str
            Folder containing files to be extracted
        zip_mode : boolean
            Set to True if the folders are zipped

        Returns
        -------
        A DataFrame with all the clicks and a fs metadata parameter with the sampling rate
        """
        clicks = pd.DataFrame()
        if zip_mode:
            folder_path = zipfile.ZipFile(folder_path, 'r', allowZip64=True)
            files_list = folder_path.namelist()
        else:
            files_list = os.listdir(folder_path)

        fs = None
        for file_name in tqdm(files_list):
            extension = file_name.split(".")[-1]
            if extension == 'wav':
                bcl_name = file_name.replace('.wav', '.bcl')
                dwv_name = file_name.replace('.wav', '.dwv')
                xml_name = file_name.replace('.wav', '.log.xml')
                if zip_mode: 
                    bcl_path = folder_path.open(bcl_name)
                    dwv_path = folder_path.open(dwv_name)
                    xml_path = folder_path.open(xml_name)
                else:
                    bcl_path = os.path.join(folder_path, bcl_name)
                    dwv_path = os.path.join(folder_path, dwv_name)
                    xml_path = os.path.join(folder_path, xml_name)

                try:
                    file_clicks = self._read_HFclicks(bcl_path, dwv_path, xml_path)
                    clicks = clicks.append(file_clicks, ignore_index=True)
                    fs = file_clicks.fs        
                except FileNotFoundError:
                    print(dwv_path, 'has some problem and can not be read')

        # Keep the metadata
        clicks.fs = fs

        return clicks

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
            waves.append(block.astype(np.float))
        
        print(dwv_path, 'bcl:', len(clicks_info), 'dwv:', len(waves))

        if len(waves) < len(clicks_info):
            # Cut the clicks info if there are not enough snippets
            clicks_info = clicks_info.loc[0:len(waves)]
        
        clicks_info['wave'] = waves[0:len(clicks_info)]

        clicks_info['datetime'] = pd.to_datetime(clicks_info['rtime'] + clicks_info['mticks']/1e6, unit='s')

        # Append the samplerate as metadata to be able to access it later
        clicks_info.fs = sound_file.samplerate

        return clicks_info

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
