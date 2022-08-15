# VOC-Sensor-Project

Last Updated August 15 2022 by William Zhang

-----------------------------------------------------------------------------------------------------------------------------------

In addition to python, this project requires matplotlib, scipy, numpy, and tkinter. 
Some python scripts will only work on Windows and not MacOS simply because file paths are written differently.

-----------------------------------------------------------------------------------------------------------------------------------

ABOUT

In this project I tried to generate sensor data for the temperature programmed desorption of VOC mixtures. I created a program
(VOC-Sensor-Project/Data Combination/GasSensor.py) that implements a simple signal addition method to generate mixture data.

This repo contains all the files I used/ am using in this project.

-----------------------------------------------------------------------------------------------------------------------------------

INSTALLATION AND USE

To install this project simply download the VOC-Sensor-Project folder and all of its contents. The VOC-Sensor-Project folder
can be placed anywhere, as long as you know its location.

To start the program navigate to  VOC-Sensor-Project/Data Combination  and run GasSensor.py. The other .py files in this directory
are just libraries used for GasSensor.py and don't do anything if you run them.

The program has three tabs, 'View' , 'Generate' , and 'Load' . 

The 'View' tab contains two selection boxes that contain and seperate source (experimentally gathered) data and generated data.
These boxes correlate to the folder  VOC-Sensor-Project/Data Combination/Source Data  and  VOC-Sensor-Project/Data Combination/Generated Data.
Clicking on a file in either box will display the data for that particular file/experiment on the right.

The 'Generate' tab is used to generate mixture data from the source data. Once you enter the mixture information (the ramp rate,
the mixture componenents and respective concentrations) you can press the generate button. This creates a file with the generated
data. A dialogbox should appear that tells you the file name and where it was saved. If you navigate back to the 'View' tab you should
be able to view the mixture that you just generated.

The 'Load' tab is used to add new source/experimentally collected data that can be used to generate more data. The program can only read
sensor log files. For  example, check out VOC-Sensor-Project/Data/1 - Raw Data. The files that are not .json files are the log files.

-----------------------------------------------------------------------------------------------------------------------------------

PROJECT OVERVIEW

In this project I explored two methods to generate the data. 

The first was based on the Polayni Wigner equation, which is used to describe the rate of gas desorption during temperature 
programmed desorption. Ultimately I abandoned this method because it requires gathering data on the activation energy for
desorption of each gas with the silica. However, if this data was known the amount of gas desorbed could be found by integrating
the gas's rate of desorption with respect to time. This does not exactly replicate sensor readings, but it could be useful.
The work done for this method can be found in the folder called Polyani Wigner.

In the second method I used experimentally gathered data for the desorption of individual gasses to generate data for mixtures 
of gasses. If we can assume that gasses behave ideally the experiment, then the signal from a mixture of gasses should be the combined 
signals of each individual component gas. For example, if I want data for a mixture of 25% IPA and 4% Xylene I simply add together 
the experimental data for 25% IPA and 4% Xylene. Most of the work I used to develop this second method can be found in 
VOC-Sensor-Project/Data Combination. 

Over the summer of 2022 I implemented this second method in a script called GasSensor.py (which can be found in the Data Combination 
folder.) A more technical explanation is in the section below.

The biggest limitation for this second method is that it assumes the experiment conditions for the generated mixture data are 
exactly the same for its components. For example,  if I only have data for gasses desorbed on a 0.5 degree celsius per second
ramp rate, I can only generate data for mixtures using that ramp rate. If I wanted to generate data for mixtures on a different 
ramp rate, like 2 degrees celsius per second, we would need to collect data for each individual gas desorbed on that ramp rate first.

-----------------------------------------------------------------------------------------------------------------------------------

TECHNICAL OVERVIEW

The program I created is essentially a UI that can access some tools access/manipulate three kinds of files. I call these three files
(sensor) log files, source data files, and generated data files. 


Sensor log files are files that contain all of the data outputed by the sensor. They contain time stamps, PID Voltage, peltier temperature,
dilution ratio, etc. as well as sensor events, such as starting the heating ramp or maintaining a certain temperature.

Source data files are cleaned up versions of sensor log files. A sensor log file can contain multiple experimental trials and different
VOC concentrations and dozens of different data streams that aren't necessary for the program. A Source data file is derived from a log file.
But the source data file will only contain basic info about a specific trial (the VOC name, concentration, and ramp rate) and data for
the time elapsed in the experiment and the measured PID voltage. One log file can yield multiple source data files.

Generated data files are similar to source data files, but they are modified so they can hold data for multiple gasses at a time. So instead
of one VOC name, a generated data file might hold 3 VOC names and 3 concentrations and 3 different PID voltage readings for each component
VOC. Additionally, the generated data file will hold the sum of all the PID voltage readings. The PID voltage sum represents the expected
reading for a mixture of the components - hence the generated data name.

Log files are written in the format of typical .csv files, though they are saved as regular .txt files.

Source and generated data files are text files, but have specific formats and naming schemes that can be found in the READ MEs of their
respective folders, VOC-Sensor-Project/Data Combination/Source Data and VOC-Sensor-Project/Data Combination/Generated Data.

There are two libraries that are used to create and manipulate all three kinds of files: archive_reader.py and experiment.py. Both are found
in VOC-Sensor-Project/Data Combination.

archive_reader.py interfaces with log files. It contains tools to extract and slightly process data from a log file. Most importantly is 
get_experiments() which seperates a log file into its trials, and returns the data for all trials as two arrays. 

experiment.py contains two classes, SingleVOC and Mixture. SingleVOC objects represent the data for one trial. Data from get_experiments() can 
be organized into multiple SingleVOC objects, making the data easier to handle. SingleVOC objects can be then saved as source data files.

Mixture objects are created SingleVOC objects. Each SingleVOC object essentially represents one component of the Mixture. When a Mixture
object is intialized with SingleVOC objects as its arguments, the combined (mixed) PID voltage data is automatically calculated. Mixture objects
can be save as generated data files.

The UI, which makes it easier to access these tools and files, is split into two .py files, uitools_new.py and GasSensor.py. uitools is more of the 
"backend" of the program and integrates archive_reader.py,experiment.py with tkinter (python gui library.) GasSensor.py is focused more
on the "frontend" or layouts and widgets used in the program.
