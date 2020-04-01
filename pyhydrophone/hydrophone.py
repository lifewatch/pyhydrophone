"""
Class that represents an acoustic recorder
"""


class Hydrophone:
    def __init__(self, name, model, sensitivity, preamp_gain, Vpp):
        """
        Base class Hydrophone initialization
        """
        self.name = name
        self.model = model
        self.sensitivity = sensitivity
        self.preamp_gain = preamp_gain
        self.Vpp = Vpp


    def get_name_date(self, name):
        """
        Read the name of the file and according to the hydrophone protocol get the date 
        """
        pass
