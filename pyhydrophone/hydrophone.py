"""
Class that represents an acoustic recorder
"""


class Hydrophone:
    def __init__(self, name, model, serial_number, sensitivity, preamp_gain, Vpp):
        """
        Base class Hydrophone initialization
        """
        self.name = name
        self.model = model
        self.serial_number = serial_number
        self.sensitivity = sensitivity
        self.preamp_gain = preamp_gain
        self.Vpp = Vpp


    def get_name_datetime(self, file_name):
        """
        Read the name of the file and according to the hydrophone protocol get the date 
        """
        pass
