.. currentmodule:: pyhydrophone

Introduction to pyhydrophone
============================

Passive acoustics monitoring is becoming more and more popular in marine environments.
Therefore, more and more underwater acoustic recorders can be found in the market. However, the output they give is not
standardized and each of them usually needs an if statement.
pyhydrophone is thus thought as a package which can be used in data analysis pipelines or scripts without having to
change the way the metadata is read for a different recorder.

First, an object is created to represent a hydrophone with all its metadata::

    import pyhydrophone as pyhy

    # SoundTrap
    model = 'SoundTrap 300 STD'
    name = 'SoundTrap'
    serial_number = 67416073
    soundtrap = pyhy.soundtrap.SoundTrap(name=name, model=model, serial_number=serial_number)


Then this object can be used in a pipeline in a way such as::

    wav_path = 'tests/test_data/soundtrap/67416073.210610033655.wav'
    start_datetime_of_wav = soundtrap.get_name_datetime(wav_path)


It can also be used to for calibration::

    import soundfile as sf
    import numpy as np

    wav = sf.read(wav_path)
    rms_db = 10 * np.log10(np.mean(wav**2))
    rms_db_upa = rms_db + soundtrap.end_to_end_calibration()


If you have a frequency dependent calibration file, it can also be used::

    import scipy.signal as sig

    rtsys_name = 'RTSys'
    rtsys_model = 'RESEA320'
    rtsys_serial_number = 2003001
    rtsys_sens = -180
    rtsys_preamp = 0
    rtsys_vpp = 5
    mode = 'lowpower'
    calibration_file = pathlib.Path("tests/test_data/rtsys/SN130.csv")
    rtsys = pyhy.RTSys(name=rtsys_name, model=rtsys_model, serial_number=rtsys_serial_number, sensitivity=rtsys_sens,preamp_gain=rtsys_preamp, Vpp=rtsys_vpp, mode=mode, calibration_file=calibration_file)

    wav_path = 'tests/test_data/rtsys/channelA_2021-10-11_13-11-09.wav'
    wav, fs = sf.read(wav_path)
    frequencies, spectrum = sig.welch(wav)
    frequency_increment = rtsys.freq_cal_inc(frequencies)
    print(df)

