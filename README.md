# pyhydrophone

Package to make it easier to read different hydrophones' output files and extract the information.

pyhydrophone helps keeping together all the information of the recorder. 

Each class represents a different hydrophone. The available ones now are (others will be added): 
- SoundTrap (OceanInstruments)
- Seiche (Seiche)
- AMAR (JASCO)

They all inherit from the main class Hydrophone. 
If a hydrophone provides an output different than a regular wav file, functions to read and understand the output are provided. 
Functions to read the metadata are also provided (which is often encoded in the file name).

pyhydrophone also has a class to work with hydrophone files: HydroFile. It consists of several functions to get the *sound information* out of the wav output.


## How to install
```
pip install setup.py
```
```
pip install -r requirements.txt
```

## How to use
pyhydrophone allows to create an object which represents the hydrophone so you can just pass the hydrophone object from one function to another of your analysis without repeating all the parameters. 

The object has some extra functions as reading the datetime when it was recorded (usually it is stored in the file name, but some times there is an extra metadata file). 

There is also the HydroFile which is a class with some functions initialized with a wav file and a hydrophone. It gives some functions like read the sound pressure level out of the wav file by doing the proper conversion according to the device.

The normal use would be to create the hydrophone object and then start reading your files. Every time you want to know the datetime of your file you would do:
```
hydrophone.get_name_date(path_to_your_file) 
```
and you would not have to worry about which format the file name has or where the information of the datetime is stored.

For example, for a Seiche hydrophone: 
```
1)	sei = Seiche(args)
2)	hyfile = HydroFile(path_to_my_wav, sei)
3)	uPa_signal = hyfile.wav2uPa()
```

For more information about the parameters that each hydrophone takes, see examples folder: 

```
sei = pyhy.Seiche(name, model, sensitivity, preamp_gain)
st = pyhy.SoundTrap(name, model, serial_number)
am = pyhy.AmarG3(name, model, sensitivity, preamp_gain, mems_sensitivity)
```



### Hydrophone
It is the base class, which can be used in case the user is only interested in keeping the parameters together. 

### SoundTrap 
Provides two classes, SoundTrap and SoundTrapHF. 

To create a SoundTrap object, sensitiviy and preamp_gain are read from the configuration file. They do not have to be specified by the user.
(Gain type "High" or "Low" has to be specified).
A routine for reading the xml file is provided (still some parameters missing).

In a future it will be implemented to read the calibration from oceaninstruments but now the calibration file has to be saved inside the folder "calibration/" under the name of the serial number with THE SAME structure than the one exemplified. 
(information can be obtained from http://oceaninstruments.azurewebsites.net/App/#/%23)

SoundTrapHF (inherited from SoundTrap) comes with a routine to read the *.dwv files from SoundTrap and store all the high frequency clicks as a pandas df to be able to work with them. 

A folder with several (xml, bcl, dwv) files can be specified and passed to the function.

### Seiche
For now only provides a method to read the date from the filename as it comes out from the device.

https://www.seiche.com/underwater-acoustic-products/acoustic-sensors/

Other devices such as Orca will be added. 

### AMAR 
For now only provides a method to read the date from the filename as it comes out from the device.

https://www.jasco.com/


### HydroFile
Provides a class with routines to convert wav files to sound values according to the hydrophone used to record them. 


