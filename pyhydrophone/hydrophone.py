#!/usr/bin/python
from datetime import datetime
import numpy as np
import soundfile as sf
import pandas as pd
import scipy.interpolate

try:
    import scipy.signal as sig
except ModuleNotFoundError:
    pass


class Hydrophone:
    """
    Base class Hydrophone initialization

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
    calibration_file : string or Path
        File where the frequency dependent sensitivity values for the calibration are
    """
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp, string_format, calibration_file=None,
                 **kwargs):
        self.name = name
        self.model = model
        self.serial_number = serial_number
        self.sensitivity = sensitivity
        self.preamp_gain = preamp_gain
        self.Vpp = Vpp
        self.string_format = string_format
        self.cal_freq = 250
        self.cal_value = 114
        self.calibration_file = calibration_file
        self.freq_cal = None
        if calibration_file is not None:
            self.freq_cal = self.get_freq_cal(**kwargs)

    def get_name_datetime(self, date_string):
        """
        Read the name of the file and according to the hydrophone protocol get the date
        Parameters
        ----------
        date_string : string
            Datetime in string format
        """
        date = datetime.strptime(date_string, self.string_format)
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
        raise Exception('get_new_name should be declared in the subclass %s' % self.__name__)

    def change_calibration_system(self, cal_freq, cal_val):
        """
        Change the parameters of the calibration system (piston phone)

        Parameters
        ----------
        cal_freq: float
            Calibration frequency in Hz
        cal_val: float
            Expected value in db

        """
        self.cal_value = cal_val
        self.cal_freq = cal_freq

    def update_calibration(self, calibration_signal, p_ref=1.0):
        """
        Updates ONLY the parameter preamp_gain of the hydrophone with a correction factor to match expected calibration.

        Parameters
        ----------
        calibration_signal: np.array
            signal to calibrate from (already cut to ONLY calibration)
        p_ref: float
            Reference pressure to compute db from

        Returns
        -------
        Updates the parameter preamp_gain
        """
        ref_wav = np.sqrt((calibration_signal ** 2).mean())
        mv = 10 ** (self.sensitivity / 20.0) * p_ref
        ma = 10 ** (self.preamp_gain / 20.0) * p_ref
        gain_upa = (self.Vpp / 2.0) / (mv * ma)
        real_db = 20 * np.log10(ref_wav * gain_upa)
        correction_factor = real_db - self.cal_value
        self.preamp_gain += correction_factor

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
        calibration_signal = wav_file.read()
        self.update_calibration(calibration_signal)

        return None

    def end_to_end_calibration(self, p_ref=1.0):
        """
        Returns the end to end calibration of the system, so it can be directly used on a wav file to obtain uPa

        Parameters
        ----------
        p_ref

        Returns
        -------
        End to end calibration in db
        """
        mv = 10 ** (self.sensitivity / 20.0) * p_ref
        ma = 10 ** (self.preamp_gain / 20.0) * p_ref
        gain_upa = (self.Vpp / 2.0) / (mv * ma)
        return 10 * np.log10(gain_upa**2)

    def get_freq_cal(self, sep=',', freq_col_id=0, sens_col_id=1, start_data_id=0):
        """
        Compute a dataframe with all the frequency dependent sensitivity values from the calibration file

        Parameters
        ----------
        sep : str
            Separator between the different columns in csv or txt files
        freq_col_id : int
            Id of the frequency column in the file (starts with 0)
        sens_col_id : int
            Id of the sensitivity column in the file (starts with 0)
        start_data_id : int
            Id of the first line with data (without title) in the file (starts with 0)
        """

        if self.calibration_file.suffix == '.csv' or self.calibration_file.suffix == '.txt':
            df = pd.read_csv(self.calibration_file, sep=sep, header=None)

        elif self.calibration_file.suffix == '.xlsx':
            df = pd.read_excel(self.calibration_file, header=None)

            df = df.iloc[:, (i for i in range(len(df.columns)) if i == freq_col_id or i == sens_col_id)]
            df = df[start_data_id:]
            df = df.dropna(subset=[df.columns[0]])
            df = df.replace('[A-Za-z:]', '', regex=True).astype(float)
            df = df.reset_index(drop=True)
            df.columns = ['frequency', 'sensitivity']

        self.freq_cal = df

    def freq_cal_inc(self, frequencies):
        """
        Returns a dataframe with the frequency dependent values to increment from the selected frequencies you give from
        the data you want to increment

        Parameters
        ----------
        frequencies : 1d array
            Frequencies from the data you want to increment with frequency dependent calibration

        Returns
        -------
        df_freq_inc : pandas Dataframe
            Frequency dependent values to increment in your data
        """
        df = self.freq_cal
        min_freq = df['frequency'][0]
        max_freq = df['frequency'][df.shape[0] - 1]
        interpol = scipy.interpolate.interp1d(df['frequency'], df['sensitivity'], kind='linear')

        frequencies_below = frequencies.compress(frequencies < min_freq)
        frequencies_between = frequencies.compress(np.logical_and(frequencies >= min_freq, frequencies <= max_freq))
        frequencies_above = frequencies.compress(frequencies > max_freq)

        freq_dep_cal = interpol(frequencies_between)
        freq_cal_inc = freq_dep_cal - (-1 * self.end_to_end_calibration())
        freq_cal_inc = np.concatenate((np.zeros(frequencies_below.shape), freq_cal_inc, np.zeros(frequencies_above.shape)))
        df_freq_inc = pd.DataFrame(data=np.vstack((frequencies, freq_cal_inc)).T, columns=['frequency', 'inc_value'])

        return df_freq_inc
