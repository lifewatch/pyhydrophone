import numpy as np
import os
import soundfile as sf
import scipy.signal as sig


class HydroFile:
    def __init__(self, wavfile_path, hydrophone, p_ref=1.0):
        """
        Data recorded in a wav file.
        Hydrophone has to be from the class hydrophone 
        p_ref in uPa
        """
        # Save hydrophone model 
        self.hydrophone = hydrophone 

        # Get the date from the name
        file_name = os.path.split(wavfile_path)[-1]
        self.date = hydrophone.get_name_date(file_name)

        # Signal
        self.wavfile_path = wavfile_path
        self.sound_file = sf.SoundFile(self.wavfile_path)
        self.fs = self.sound_file.samplerate

        # Reference pressure in uPa
        self.p_ref = p_ref


    def wav2uPa(self):
        """ 
        Compute the pressure from the wav signal 
        """
        # Read 
        wav = self.sound_file.read()

        # First convert it to Volts and then to dB according to sensitivity
        Mv = 10 ** (self.hydrophone.sensitivity / 20.0)
        return (wav * self.hydrophone.Vpp/2.0) / Mv


    def wav2dB(self):
        """ 
        Compute the dB SPL from the wav signal
        """
        # Read 
        wav = self.sound_file.read()
        
        return 10*np.log10(wav**2) - self.hydrophone.sensitivity

    
    def dB2uPa(self, signal_dB):
        """
        Compute the uPa from the dB signals
        """
        return np.power(10, signal_dB / 20.0)
    

    def uPa2dB(self):
        """ 
        Compute the dB from the uPa signal
        """
        # Read the signal in uPa
        signal_uPa = self.wav2uPa()
        return 10*np.log10(signal_uPa**2 / self.p_ref**2)

    
    def freq_distr(self, nfft=512):
        """
        Read the frequency distribution
        """
        # Read the signal in uPa
        signal_uPa = self.wav2uPa()

        window = sig.get_window('hann', nfft)

        # PS is the freq power spectrum in [uPa**2]
        freq, ps = sig.periodogram(signal_uPa, nfft=nfft, fs=self.fs, scaling='spectrum')

        ps_db = 10*np.log10(ps / (self.p_ref**2)) 

        return freq, ps_db

    
    def rms_db(self):
        """
        Return the mean squared value of the signal in db
        """
        # Read the signal in uPa
        signal_uPa = self.wav2uPa()
                
        return 10*np.log10((signal_uPa**2).mean()/self.p_ref)

    
    def perc_distr(self, percentages):
        """
        Return the sound level where a percentage of the samples is, in db
        """
        # Read the signal in uPa
        signal_uPa = self.wav2uPa()

        signal_db = 10*np.log10(signal_uPa**2 / self.p_ref**2)
        min_lev = signal_db.min()
        max_lev = signal_db.max()

        quantiles = np.quantile(signal_db, percentages)

        lims = np.concatenate(([min_lev, max_lev], quantiles))
        
        return lims