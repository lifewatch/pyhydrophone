# pyhydrophone

Package to make it easier to read different hydrophones' output files and extract the information.

pyhydrophone helps keeping together all the information of the recorder. 

Each class represents a different hydrophone. The available ones now are (others will be added): 
- SoundTrap (OceanInstruments)
- Seiche (Seiche)
- AMAR (JASCO)
- B&K Nexus

They all inherit from the main class Hydrophone. 
If a hydrophone provides an output different than a regular wav file, functions to read and understand the output are provided. 
Functions to read the metadata are also provided (which is often encoded in the file name).


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

The normal use would be to create the hydrophone object and then start reading your files. Every time you want to know the datetime of your file you would do:
```
hydrophone.get_name_date(path_to_your_file) 
```
and you would not have to worry about which format the file name has or where the information of the datetime is stored.



For more information about the parameters that each hydrophone takes, see examples folder: 

```
sei = pyhy.Seiche(name, model, sensitivity, preamp_gain)
st = pyhy.SoundTrap(name, model, serial_number)
am = pyhy.AmarG3(name, model, sensitivity, preamp_gain, mems_sensitivity)
bk = pyhy.BruelKjaer(name, model, amplif)
```



### Hydrophone
It is the base class, which can be used in case the user is only interested in keeping the parameters together. 

### SoundTrap 
Provides two classes, SoundTrap and SoundTrapHF. 

The date format of the file is assumed to be: *model_name.yymmddHHMMSS.ext*

To create a SoundTrap object, sensitiviy and preamp_gain are read from the configuration file. They do not have to be specified by the user.
(Gain type "High" or "Low" has to be specified).
A routine for reading the xml file is provided (still some parameters missing).

In a future it will be implemented to read the calibration from oceaninstruments but now the calibration file has to be saved inside the folder "calibration/" under the name of the serial number with THE SAME structure than the one exemplified. 
(information can be obtained from http://oceaninstruments.azurewebsites.net/App/#/%23)

SoundTrapHF (inherited from SoundTrap) comes with a routine to read the *.dwv files from SoundTrap and store all the high frequency clicks as a pandas df to be able to work with them. 

A folder with several (xml, bcl, dwv) files can be specified and passed to the function.

### Seiche
For now only provides a method to read the date from the filename as it comes out from the device.

The date format of the file is assumed to be: *project_name_yymmdd_HHMMSS_NUM.ext*
Where project_name and NUM depend on your personal choice. 

https://www.seiche.com/underwater-acoustic-products/acoustic-sensors/

Other devices such as Orca will be added. 

### AMAR 
For now only provides a method to read the date from the filename as it comes out from the device.

https://www.jasco.com/


### B&K
Provides a method to read the date from the filename (it has to be changed, as the date is not saved in the file).
It also provides the calculation of the sensitivity according to the selected amplification. Only [100e-6, 316e-6, 1e-3, 3.16e-3, 10e-3, 31.6e-3, 100e-3, 316e-3, 1.0, 3.16, 10.0] V are valid numbers. 
A function to change the sensitivity of the hydrophone is provided (update_calibration), which can be used when the test signal is created at the beggining of the file.

https://www.bksv.com/en/products/transducers/conditioning/microphone/2690-A-0F2


