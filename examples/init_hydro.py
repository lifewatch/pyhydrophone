"""
An example of how to use the classes
"""

import pyhydrophone as pyhy

Vpp = 2.0

def main():
    # Hydrophone Setup
    sensitivity = -199.0
    preamp_gain = 1
    model = 1
    serial_number = 1000
    name = 'Seiche'

    sei = pyhy.Seiche(name, model, serial_number, sensitivity, preamp_gain, Vpp)

    sei.get_name_datetime(file_name='SEPAM_20200506_072841_170.wav', utc=False)
    # Hydrophone Setup
    model = 1
    name = 'SoundTrap'
    serial_number = 67416073

    st = pyhy.SoundTrap(name, model, serial_number)

    # Hydrophone Setup
    sensitivity = -199.0
    preamp_gain = 1
    model = 1
    mems_sensitivity = -199.0
    name = 'AmarG3'

    am = pyhy.AmarG3(name, model, sensitivity, preamp_gain, mems_sensitivity, Vpp)

    print(sei, st, am)

    

if __name__ == '__main__':
    main()