#!/usr/bin/python
from pyhydrophone.hydrophone import Hydrophone

import os
import numpy as np
import soundfile as sf
import datetime

try:
    import scipy.signal as sig
except ModuleNotFoundError:
    pass


class BruelKjaer(Hydrophone):
    """
    Init an instance of B&K Nexus.
    Check well the Vpp in case you don't have a reference signal! Specially of the recorder used.
    Parameters
    ----------
    name: str
        Name of the acoustic recorder
    model: str or int
        Model of the acoustic recorder
    serial_number : str or int
        Serial number of the acoustic recorder
    preamp_gain: float
        Amplification selected in the Nexus in db 10*log10((V/uPa)^2)
    Vpp: float
        Volts peak to peak
    string_format: string
        Format of the datetime string present in the filename
    type_signal : str
        Can be 'ref' or 'test'
    calibration_file : string or Path
        File where the frequency dependent sensitivity values for the calibration are
    """
    def __init__(self, name, model, serial_number, preamp_gain, Vpp=2.0, string_format="%y%m%d%H%M%S", type_signal='ref',
                 max_calibration_time=120.0, calibration_file=None, **kwargs):
        self.amplif = np.sqrt(10**(preamp_gain/10)) * 1e6
        self.preamp_gain = preamp_gain
        self.type_signal = type_signal
        self.max_calibration_time = max_calibration_time
        self.cal_freq = 159.9
        self.min_duration = 10.0
        
        super().__init__(name, model, serial_number, sensitivity=0.0, preamp_gain=preamp_gain,
                         Vpp=Vpp, string_format=string_format, calibration_file=calibration_file, **kwargs)

    def __setattr__(self, name, value):
        """
        If the amplif is changed, update the preamp_gain
        """
        if name == 'amplif':
            self.__dict__['preamp_gain'] = 10 * np.log10((value/1e6)**2)
        if name == 'preamp_gain':
            self.__dict__['amplif'] = np.sqrt(10**(value/10)) * 1e6
        if name == 'type_signal':
            if value not in ['ref', 'test']:
                raise Exception('%s is not an option in Nexus!' % value)
        return super().__setattr__(name, value)

    def get_name_datetime(self, file_name):
        """
        Get the data and time of recording from the name of the file
        Parameters
        ----------
        file_name : string
            File name (not path) of the file
        """
        name = file_name.split('.')
        date_string = name[0].split('_')[0]
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
        old_date_name = datetime.datetime.strftime(old_date, self.string_format)
        new_date_name = datetime.datetime.strftime(new_date, self.string_format)
        new_filename = filename.replace(old_date_name, new_date_name)
        
        return new_filename

    def read_start_time_metadata(self, file_path):
        """
        Return the starting time of the file by getting the last modification minus the duration of the file
        Parameters
        ----------
        file_path : string or Path
            Path to the file to read the information from

        Returns
        -------
        Datetime, starting moment of the file
        """
        modif_timestamp = os.path.getmtime(file_path)
        modif_datetime = datetime.datetime.fromtimestamp(modif_timestamp)
        duration = datetime.timedelta(seconds=sf.info(file_path).duration)
        start_time = modif_datetime - duration
        return start_time
    
    def update_calibration(self, ref_signal):
        """
        Update the calibration
        Parameters
        ----------
        ref_signal : str or Path
            File path to the reference file to update the Vpp according to the calibration tone
        """
        ref_wav = np.sqrt((ref_signal ** 2).mean())
        # Sensitivity is in negative values!
        if self.type_signal == 'ref':
            # The signal is then 1 V
            ref_v = 1
        else:
            # The signal is the amplification value
            ref_v = 100 * self.amplif * np.sqrt(2)
        self.preamp_gain = 10 * np.log10((self.amplif / 1e6) ** 2) + 10*np.log10((ref_wav / ref_v)**2)

    def calibrate(self, file_path):
        """
        Find the beginning and ending sample of the calibration tone
        Returns start and end points, in seconds
        Parameters
        ----------
        file_path : string or Path
            File where to look for the calibration (at the beginning of the file)

        Returns
        -------
        end sample of the calibration (int)
        """
        wav_file = sf.SoundFile(file_path)
        tone_samples = int(self.max_calibration_time * wav_file.samplerate)
        first_part = wav_file.read(frames=tone_samples)
        analytic_signal = sig.hilbert(first_part)
        amplitude_envelope = np.abs(analytic_signal)
        possible_points = np.zeros(amplitude_envelope.shape)
        possible_points[np.where(amplitude_envelope >= 0.05)] = 1
        start_points = np.where(np.diff(possible_points) == 1)[0]
        end_points = np.where(np.diff(possible_points) == -1)[0]
        if start_points.size == 0:
            return None
        if end_points[0] < start_points[0]:
            end_points = end_points[1:]
        if start_points.size != end_points.size:
            start_points = start_points[0:end_points.size]
        select_idx = np.argmax(end_points - start_points)
        # Round to a second
        start = int(start_points[select_idx])
        end = int(end_points[select_idx])

        if (end - start) / wav_file.samplerate < self.min_duration:
            return 0

        self.update_calibration(first_part[start:end])

        return end