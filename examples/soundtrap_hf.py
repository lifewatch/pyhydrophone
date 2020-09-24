import pyhydrophone as pyhy

# Sound Files
sound_folder_path = ""

# Output path for the detected clicks
clicks_output_path = "test.pickle"

name = 'SoundTrap'
model = 1
serial_number = 67416073
Vpp = 2
hydrophone = pyhy.SoundTrapHF(name, model, serial_number, Vpp)


if __name__ == "__main__":
    """
    Detect clicks on sound data
    """
    # Convert the sound clips to click and save
    clicks_df = hydrophone.read_HFclicks(sound_folder_path)
    clicks_df.to_pickle(clicks_output_path)