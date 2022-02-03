import pyhydrophone as pyhy
import unittest
import pathlib


# Sound Files
test_files = pathlib.Path('./test_data/soundtrap')

# Output path for the detected clicks
clicks_output_path = 'clicks.pkl'

name = 'SoundTrap'
model = 1
serial_number = 67416073
Vpp = 2


class TestSoundTrap(unittest.TestCase):
    def setUp(self) -> None:
        self.hydrophone = pyhy.SoundTrapHF(name, model, serial_number, Vpp)

    def test_hf(self):
        # Convert the sound clips to click and save
        clicks_df = self.hydrophone.read_HFfolder(test_files, zip_mode=True, include_dirs=True)
        clicks_df.to_pickle(clicks_output_path)

        return clicks_df


if __name__ == '__main__':
    unittest.main()
