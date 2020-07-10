import os
from datetime import datetime
import configparser
import xml.etree.ElementTree as ET
import importlib
import pandas as pd
import soundfile as sf
import zipfile
import numpy as np

from pyhydrophone.hydrophone import Hydrophone


"""
Class that represents a SoundTrap acoustic recorder
"""


class SoundTrap(Hydrophone):
    def __init__(self, name, model, serial_number, gain_type='High'):
        """ 
        Initialize a SoundTrap instance
        """
        calibration = self._read_calibration(serial_number)
        rti_level = calibration['RTI']
        sensitivity = calibration[gain_type]
        super().__init__(name, model, serial_number=serial_number, sensitivity=sensitivity, preamp_gain=0.0, Vpp=2.0)


    def read_file_specs(self, xmlfile_path, last_gain, date_format='%Y-%m-%dT%H:%M:%S'):
        """
        Read the specs of the recording from the XML file and save them to the object
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
            sst_gain = tree.find('EVENT/AUDIO').get('Gain')
        else:
            if last_gain is None:
                print('Unknown gain if it is reopened and the last gain is not passed!')
            st_gain = last_gain
        
        start_time = datetime.strptime(sampling_attr['SamplingStartTimeLocal'], date_format)
        stop_time = datetime.strptime(sampling_attr['SamplingStopTimeLocal'], date_format)

        return {'type_start': type_start, 'temp':temp, 'fs':fs, 'st_gain':st_gain, 'start_time':start_time, 'stop_time':stop_time}


    def get_name_date(self, file_name):
        """
        Get the data and time of recording from the name of the file 
        """
        name = file_name.split('.')
        date_string = name[1]
        date = datetime.strptime(date_string, "%y%m%d%H%M%S")

        return date

    
    def _read_calibration(self, serial_number, configfile_path=None):
        """
        Read the calibration file of the sountrap serial number and store it in a dictionary
        """
        if configfile_path == None: 
            file_path = os.path.join('pyhydrophone', 'calibration' ,'soundtrap', str(serial_number)+'.ini')
            parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            configfile_path = os.path.join(parent, file_path)
        config = configparser.ConfigParser()
        config.read(configfile_path)
        high_gain = float(config["End-to-End Calibration"]["High Gain dB"])
        low_gain = float(config["End-to-End Calibration"]["Low Gain dB"])
        rti_level = float(config["Calibration Tone"]["RTI Level at 1kHz dB re 1 uPa"])
        calibration = {"High": high_gain, "Low": low_gain, "RTI": rti_level}

        return calibration
    
    
    def test_calibration(self, signal):
        """
        Test the calibration of the soundtrap
        """
        # TO BE IMPLEMENTED




class SoundTrapHF(SoundTrap): 
    def __init__(self, name, model, serial_number, gain_type='High'):
        """
        Init a SoundTrap HF reader
        """
        super().__init__(name, model, serial_number, gain_type)
    

    def read_HFfolder(self, main_folder_path, zip_mode=False):
        """
        Read all the clicks in all the folders
        """
        clicks = pd.DataFrame()
        for folder_name in os.listdir(main_folder_path):
            folder_path = os.path.join(main_folder_path, folder_name)
            folder_clicks = self.read_HFclicks(folder_path, zip_mode=zip_mode)
            clicks = clicks.append(folder_clicks, ignore_index=True)
        
        # Keep the metadata
        clicks.fs = folder_clicks.fs 

        return clicks


    def read_HFclicks(self, folder_path, zip_mode=False):
        """
        Read all the clicks stored in a folder with soundtrap files
        """
        clicks = pd.DataFrame()
        if zip_mode:
            folder_zip = zipfile.ZipFile(folder_path, 'r', allowZip64=True)
            files_list = folder_zip.namelist()
        else:
            files_list = os.listdir(folder_path)
        
        for file_name in files_list:
            extension = file_name.split(".")[-1]
            if extension == 'wav':
                bcl_name = file_name.replace('.wav', '.bcl')
                dwv_name = file_name.replace('.wav', '.dwv')
                xml_name = file_name.replace('.wav', '.log.xml')
                if zip_mode: 
                    bcl_path = folder_zip.open(bcl_name)
                    dwv_path = folder_zip.open(dwv_name)
                    xml_path = folder_zip.open(xml_name)
                else:
                    bcl_path = os.path.join(folder_path, bcl_name)
                    dwv_path = os.path.join(folder_path, dwv_name)
                    xml_path = os.path.join(folder_path, xml_name)

                try:
                    file_clicks = self._read_HFclicks(bcl_path, dwv_path, xml_path)
                    clicks = clicks.append(file_clicks, ignore_index=True)
                    fs = file_clicks.fs        
                except:
                    print(dwv_path, 'has some problem and can not be read')

        # Keep the metadata
        clicks.fs = fs

        return clicks


    def _read_HFclicks(self, bcl_path, dwv_path, xml_path):
        """
        Read the clicks of one soundtrap file 
        """

        # Read the wav file with all the clicks 
        sound_file = sf.SoundFile(dwv_path, 'r')

        # click_len has to be checked automatically
        click_len = self.read_HFparams(xml_path)

        # Read the info of clicks
        clicks_info = pd.read_csv(bcl_path)
        clicks_info = clicks_info[clicks_info['report'] == 'D']
        clicks_info = clicks_info[clicks_info['state'] == 1]
        waves = []
        
        for block in sound_file.blocks(blocksize=click_len):
            waves.append(block.astype(np.float))
        
        print(dwv_path, len(clicks_info), len(waves))

        if len(waves) < len(clicks_info):
            # Cut the clicks info if there are not enough snippets
            clicks_info = clicks_info.loc[0:len(waves)]
        
        clicks_info['wave'] = waves[0:len(clicks_info)]

        clicks_info['datetime'] = pd.to_datetime(clicks_info['rtime'] + clicks_info['mticks']/1e6, unit='s')

        # Append the samplerate as metadata to be able to access it later
        clicks_info.fs = sound_file.samplerate

        return clicks_info

    
    def read_HFparams(self, xml_path):
        """
        Return the length of the clips and the time in between
        """
        tree = ET.parse(xml_path)

        # blank_len = int(tree.find('CFG/BLANKING').text)
        clip_len = int(tree.find('CFG/PREDET').text) + int(tree.find('CFG/POSTDET').text)

        return clip_len
