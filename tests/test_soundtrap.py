import pyhydrophone as pyhy
import unittest
import pathlib


# Sound Files
test_files = pathlib.Path('./test_data/soundtrap')

# Output path for the detected clicks
clicks_output_path = 'clicks.pkl'

name = 'SoundTrap'
model = 'SoundTrap 300 STD'
model2 = 'SoundTrap 500 HF'
model3 = 'ST500 Hydrophone (HF)'
serial_number = 67416073


class TestSoundTrap(unittest.TestCase):
    def test_hf(self):
        # Convert the sound clips to click and save
        hydrophone = pyhy.SoundTrapHF(name, model, serial_number, gain_type='High')

        clicks_df = hydrophone.read_HFfolder(test_files, zip_mode=False, include_dirs=False)
        clicks_df.to_pickle(clicks_output_path)

        return clicks_df

    def test_init_multiple_serial_numbers(self):
        try:
            pyhy.SoundTrapHF(name, model2, 6042, gain_type='High')
        except AttributeError:
            pass
        pyhy.SoundTrapHF(name, model, 6042, gain_type='High')
        pyhy.SoundTrapHF(name, model3, 6042, gain_type='High')


if __name__ == '__main__':
    unittest.main()
