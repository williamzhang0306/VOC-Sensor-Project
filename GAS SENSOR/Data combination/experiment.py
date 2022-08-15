# File: experiment.py
# Author: William Zhang
# Date: June 2022
#
# Description of Program: 
#   Revamped Version of 0-scripts that heavily uses OOP instead. This file contains two classes,
#   SingleVOC and Mixture. The SingleVOC class represents the data for the desorption curve of one gas. The Mixture class 
#   takes in multiple SingleVOC objects as parameters and is used to represent a mixture of the gas.
#
# WIP/Things to fix in the future:
#   s_data and related things in SingleVOC class are confusing - potential to directly updata .data instead?
#   baseline not accounted for in SingleVOC - add a method to update .data with baseline removed.
#   sensor polling rate is harded coded to 0.5 hz in mixutre.sync_data().


from msilib.schema import Directory
from scipy.signal import find_peaks
from archive_reader import get_experiments
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import pchip_interpolate
import os
from os import listdir
from os.path import isfile, join

class SingleVOC:
    '''VOC class, which represents the data for one desorption curve and has basic concentration scaling functionality'''

    def __init__(self, voc_name: str = '', heating_ramp: float = 0, concentration: float = 0, time_series: list = None, original_data_series: list = None, scaling_factor: float = 1):
        
        self.name = voc_name
        self.ramp = heating_ramp #measured in celsius degrees per second
        self.conc = concentration
        self.label = f'{round(self.conc*100)}% {self.name}'
       
        if time_series == None:
            self.time = []
        else:
            self.time = time_series
        if original_data_series == None:
            self.data = []
        else:
            self.data = original_data_series
        
        # s indicates that the field is affected by the scaling factor.
        # for instance, self.conc will never change, but self.s_conc changes if self.s changes
        self.s = scaling_factor
        self.s_conc = scaling_factor * concentration
        self.s_data = [y * self.s for y in self.data] #s_data is a scaled version of o_data. Default ratio is 1


    #These update functions are ugly
    #TODO: Make them look nicer.
    def update_scaling_factor(self, new_s):
        '''change the scaling factor directly'''
        self.s = new_s
        #update the scaled concentration and data as well
        self.s_conc = self.s * self.conc
        self.s_data = [y * self.s for y in self.data]
        self.label = f'{round(self.s_conc*100)}% {self.name}'
    
    def update_scaled_concentration(self, new_conc):
        '''change the scaling factor based on a target concentration'''
        self.s = new_conc / self.conc
        self.s_conc = new_conc
        self.s_data = [y * self.s for y in self.data]
        self.label = f'{round(self.s_conc*100)}% {self.name}'

    def remove_baseline(self):
        '''Updates s_data so it begins at 0, removing the baseline'''
        
        baseline = self.s_data[0]
        a = np.array(self.s_data)
        b = a - baseline
        c = np.ndarray.tolist(b)
        
        self.s_data = c
  
    def plot(self):
        '''plots just this experiment'''
        fig, ax = plt.subplots()
        ax.plot(np.array(self.time), np.array(self.s_data), label = self.name + str(self.conc) )
        ax.set_xlabel("Time Elapsed")
        ax.set_ylabel("PID Voltage")
        ax.set_title("Test Title")
        plt.legend()
        plt.show()

    def save_experiment(self):
        '''Saves the experiment to a txt file.\n
        filename - <VOC_name>_<heat_ramp>_
        first line (index 0) contains the chemical name\n
        second line contains heating ramp\n
        third line contains concentration\n
        following lines each contain 1 tuple (x,y) which is a data point in the experiment'''
        new_file_name = f'{self.name}_{self.ramp}_{self.s_conc}'
        
        ###create a check for duplicate file names
        mypath = os.path.dirname(os.path.realpath(__file__))
        dir_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        num = 1
        old = new_file_name
        while new_file_name in dir_files:
            new_file_name = old + '_'+ str(num)
            num += 1

        new_file = open(mypath + '\\Source Data\\' + new_file_name, mode = 'a')
        new_file.write('name: ' + self.name + '\n')
        new_file.write('heating ramp rate: ' + str(self.ramp) + '\n')
        new_file.write('VOC concentration: ' + str(self.conc) + '\n')

        for i in range(len(self.time)):

            x = self.time[i]
            y = self.s_data[i]
            new_file.write(f'{x} {y}\n')

        new_file.close()

    def load_experiment(self,filename: str = None):
        '''Reads a text file in the same format as save_experiment
        and loads data in the experiment object with that data'''

        if filename == None:
            print("Error, no file selected")

        else:
            file = open(filename, mode = 'r')

            for index, line in enumerate(file.readlines()):
                
                if index == 0:
                    self.name = line.split(': ')[1].strip()

                elif index == 1:
                    self.ramp = float(line.split(': ')[1].strip())

                elif index == 2:
                    self.conc = float(line.split(': ')[1].strip())

                else:
                    l = line.split()
                    x, y = float(l[0].strip()), float(l[1].strip())
                    self.time.append(x)
                    self.data.append(y)

            #update the rest of the data
            self.label = f'{round(self.conc*100)}% {self.name}'
            self.s = scaling_factor = 1
            self.s_conc = scaling_factor * self.conc
            self.s_data = [y * self.s for y in self.data]

class Mixture:

    def __init__(self, *vocs: SingleVOC):
        
        #check to make sure that vocs is not empty
        if vocs:
            
            #A list of vocs (list version of the input)
            self.vocs = vocs
            self.num_vocs = len(vocs)

            #Basic Mixture info: labels, concentrations, and heating ramp rate.
            self.concs = [voc.s_conc for voc in vocs]
            self.labels = [voc.name for voc in vocs]
            self.rate = vocs[0].ramp #we assume that the ramp rate is the same for all component gasses of the mixture.

            #Two jagged arrays that each hold the original x and y series data of the component gasses
            #This data is not synced or proccesed.
            self.x_array = np.array([voc.time for voc in vocs],dtype=object)
            self.y_array = np.array([voc.s_data for voc in vocs],dtype=object)
            
            #Synced, combined and processed data. There are 3 stores of data
            #self.x_sync is the time values all of the processed data is synced with.
            #self.y_components is the synced PID readings of the component gasses.
            #self.y_combined is the mixture data, where all the component gas readings are combined together.
            self.x_sync, self.y_components = self.sync_curves(vocs)
            self.y_combined =  self.combine_curves(self.y_components)

        else: #if the input is empty, all data fields are empty
            self.vocs = None
            self.concs = None
            self.labels = None
            self.rate = None
            self.x_array = None
            self.y_array = None
            self.x_sync = None
            self.y_components = None
            self.y_combined = None

            #print('mixture contains nothing')

    # These functions are necessary for combining desorption curves together.
    # First, the data needs to be resampled so data is recorded every other second (0.5 Hz.)
    # This is because most of the data is recorded at this rate, but ocasionally there will be an extra second of delay between
    # data points, causing some data to be out of sync. Resampling the data ensures that the data is synced and can be combined easily

    def sync_curves(self, vocs: list):
        '''interpolates, syncronizes, seperate desorption curves.\n
        Input P is a 1D list of VOCs\n
        e.g [voc1 , voc2, voc3]\n
        There are two outputs: \n
        The first output is a 1D list that represents the time values all the curves are synced to\n
        The second output is a 2D list. Each row in the list is the data series for each curve corresponding to the time series.'''


        # Part 1: create a set of time values to sync all of the curves to.
        # first find the maximum recorded time value of all of the curves.
        # second create a list starting from 0 and counts up by 2 until it exceedes the maximum time value (from step 1)
        # we count up by 2 to simulate the sensor's polling rate. ###THIS IS HARDCODED

        # finding the last time value
        l = [voc.time[-1] for voc in vocs] # p is a voc, P is a list of vocs
        x_final = max(l)

        # creating the time series    
        x_sync = []
        n = 0
        while n < x_final:
            x_sync.append(n)
            n += 2

        # Part 2: interpolate and find the sync data values for each curve, then append that data to a 2d array
        y_sync_array = [] # M is the 2d array that all the synced y_axis data will be appended to

        for voc in vocs:
            #y_sync = barycentric_interpolate(p.time, p.s_data, t_synced)
            y_sync = pchip_interpolate(voc.time, voc.s_data, x_sync)
            y_sync_array.append(y_sync)

        return x_sync, y_sync_array

    def combine_curves(self, y_sync_array):
        '''Input y_sync_array is a 2D array/matrix where each row is the synced data for one component gas.
        This function combines all the rows in the matrix into a 1D vector that represents the synced data for a mixture of 
        the component gasses.'''

        y_combined = np.array(y_sync_array[0]) #start with the first row

        for i, row in enumerate(y_sync_array):

            if i == 0:
                continue
                
            else:
                y_combined += np.array(row)

        return np.ndarray.tolist(y_combined)

    def save_mixture(self):
        '''saves the mixture data to a text file in GeneratedData'''
        
        #create the file name/location, saved Mixture data is saved in the Generated Data folder
        filename = ''

        for i in range(len(self.labels)):

            if i != 0:
                filename += '_'

            filename += f'{self.concs[i]}{self.labels[i]}'

        filename += f'_{self.rate}'

        old_filename = filename

        filename = 'Generated Data\\' + old_filename
        
        file = open(filename, mode='w')
        
        # write the componenet VOC names on the first line
        for i, label  in enumerate(self.labels):
            if i != 0:
                file.write(' ')
            file.write(label)
        file.write('\n')  

        # write the componenet VOC concentrations on the second line  
        for i, conc in enumerate(self.concs):
            if i != 0:
                file.write(' ')
            file.write(f'{conc}')
        file.write('\n')    

        # write the ramp rate on the third line
        file.write(f'{self.rate}\n') 

        #write the data. First column is the time elapsed, last column is mixture data. In between is respective componenet data
        for i, x in enumerate(self.x_sync):

            datapoint = f'{x} '

            for row in self.y_components:
                datapoint += f'{row[i]} '

            datapoint += f'{self.y_combined[i]}'

            file.write(datapoint)
            file.write('\n')
        
        file.close()
        print(filename+" saved")
        return old_filename

    def load_mixture(self, filename):
        '''load an empty mixture object from a txt file. If object is loaded, it will not have .vocs, .x_array or .y_array'''

        if filename == None:
            print("Error, no file selected")

        else:
            file = open(filename, mode = 'r')

            self.x_sync = []
            self.y_components = []
            self.y_combined = []

            for index, line in enumerate(file.readlines()):
                
                if index == 0:
 
                    self.labels = line.split()
                    self.num_vocs = len(self.labels)
                    self.y_components = [ [] for i in range(self.num_vocs) ]

                elif index == 1:
                    self.concs = [float(conc) for conc in line.split()]

                elif index == 2:
                    self.rate = float(line.strip())

                else:
                    l = line.split()
                    #print(f"la: {l}")
                    self.x_sync.append(float(l.pop(0)))
                    self.y_combined.append(float(l.pop(-1)))
                    #print(f"lb: {l}")
                    for i, y in enumerate(l):
                        self.y_components[i].append(float(y))

            file.close()   

    def get_peaks(self):
        '''Returns a list of tuples. Each tuple is the x,y coordinate of peak'''
        # signal.find_peaks takes a 1D array of a signal and returns the index of the peaks
        # peak indexes (peaks) is then used to find all the peaks
        
        peak_prominence = max(self.y_combined)*0.1
        
        peaks,properties = find_peaks(self.y_combined, prominence = peak_prominence)
        
        l_of_peaks = []

        for i in peaks:
             l_of_peaks.append( (self.x_sync[i],self.y_combined[i]) )     
       
        return l_of_peaks

    def get_peaks_sd(self):
        '''Returns a list of tuples. Each tuple is the x,y coordinate of a peak. Peaks are detected using
        the 2 order deriviative of the data.'''
        pass


    def sync_test_plot(self):
        '''Method used to see if curves are synced by plotting curves before and after synchronization.'''
        #very quick and dorty

        #first plot the original data
        self.plot()

        #then plot the synced_data
        t , M = self.sync_curves(self.vocs)

        fig, ax = plt.subplots()
        
        #plot the component curves
        for row in M:
            x = t
            y = row
            ax.plot(x,y,label = "mixture",linestyle="-",marker="")
            

        ax.set_xlabel("Time Elapsed")
        ax.set_ylabel("PID Voltage")
        ax.set_title("Test Title")
        plt.legend()
        plt.show() 

    def plot(self):

        fig, ax = plt.subplots()
        
        #plot component curves
        for i in range(len(self.y_components)):
            x = self.x_sync
            y = self.y_components[i]
            name = f'{self.concs[i]}_{self.labels[i]}'
            ax.plot(x,y,label = name,linestyle="-",marker="")

        # plot combined curves
        x = self.x_sync
        y = self.y_combined
        ax.plot(x,y,label = 'Mixture', linestyle="-",marker="")

        #plot peaks
        peaks = self.get_peaks()
        for peak in peaks:
            x,y = peak
            ax.plot(x,y,marker="x")

        ax.set_xlabel("Time Elapsed")
        ax.set_ylabel("PID Voltage")
        ax.set_title("Test Title")
        plt.legend()
        plt.show() 


# MISC functions, helped with testing/debugging

def load_from_log(compound_name: str = 'no_name', log_file: str = None) -> list:
    '''Returns a list of SingleVOC objects from a log file.'''

    l_of_exp = []

    if log_file == None:
        print("Error: No sensor log file selected")
        return

    x_array, y_array, h_array = get_experiments(log_file, compound_name)

    for i in range(len(x_array)): #x_array and y_array should be the same length

        #unpacking the data for one experiement    
        exp_label, exp_x_series = x_array[i]
        _ , exp_y_series = y_array[i]
        _ , exp_h_series = h_array[i]

        #calculating ramp rate
        temp_delta = exp_h_series[-1] - exp_h_series[0]
        t_elapsed =  exp_x_series[len(exp_h_series)-1]
        #ramp_rate = round(temp_delta/t_elapsed, 1)
        ramp_rate = round(temp_delta/t_elapsed, 1)

        l = exp_label.split()
            #print(l)
        name, _, conc = l[0], float(l[1]), float(l[2])

        cur_exp = SingleVOC(name,ramp_rate,conc,exp_x_series,exp_y_series)
        l_of_exp.append(cur_exp)

    return l_of_exp

def save_all_experiments():
    '''Loads and saves all the data in the data file'''
    d = {
            "IPA":[r"Data\1 - Raw_Data\20190722_Sponge_IPA\20190722_Sponge_Ipa_A.monitor.txt", r"Data\1 - Raw_Data\20190722_Sponge_IPA\20190722_Sponge_Ipa_B.monitor.txt"],
            "Benzene":[r"Data\1 - Raw_Data\20190723_Sponge_Benzene\20190723_Sponge_Benzene_CombinedA.monitor.txt",r"Data\1 - Raw_Data\20190723_Sponge_Benzene\20190723_Sponge_Benzene_CombinedB.monitor.txt"],
            "Benzaldehyde":[r"Data\1 - Raw_Data\20190723_Sponge_Benzene\20190723_Sponge_Benzene_CombinedC.monitor.txt",r"Data\1 - Raw_Data\20190724_Sponge_Benzaldehyde\20190724_Sponge_Benzaldehyde_combined_A.monitor.txt",r"Data\1 - Raw_Data\20190724_Sponge_Benzaldehyde\20190724_Sponge_Benzaldehyde_combined_B.monitor.txt",r"Data\1 - Raw_Data\20190724_Sponge_Benzaldehyde\20190724_Sponge_Benzaldehyde_combined_C.monitor.txt"],
            "Limonene":[r"Data\1 - Raw_Data\20190725_Sponge_Limonene\20190725_Sponge_Limonene_Combined_A.monitor.txt",r"Data\1 - Raw_Data\20190725_Sponge_Limonene\20190725_Sponge_Limonene_Combined_B.monitor.txt",r"Data\1 - Raw_Data\20190725_Sponge_Limonene\20190725_Sponge_Limonene_Combined_C.monitor.txt"],
            "MEK":[r"Data\1 - Raw_Data\20190731_Sponge_MEK\20190731_Sponge_MEK_Combined_A.monitor.txt",r"Data\1 - Raw_Data\20190731_Sponge_MEK\20190731_Sponge_MEK_Combined_B.monitor.txt"],
            "Toluene":[r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_A.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_B.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_C.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_D.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_E.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_F.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_G.monitor.txt",r"Data\1 - Raw_Data\20190820_Sponge_Toluene\20190820_Sponge_Toluene_H.monitor.txt"],
            "oXylene":[r"Data\1 - Raw_Data\20190821_Sponge_oXylene\20190820_overnight_Sponge_oXylene.monitor.txt",r"Data\1 - Raw_Data\20190821_Sponge_oXylene\20190821_Sponge_oXylene.monitor.txt"],
            "Benzene":[r"Data\1 - Raw_Data\20190822_Sponge_Benzene\20190822_Sponge_Benzene.monitor.txt"]
            }

    for name in d:

        l_of_logs = d[name]

        for log in l_of_logs:

            l_of_experiments = load_from_log(compound_name=name,log_file=log)
            for e in l_of_experiments:
                e.save_experiment()

def filter_all_experiments():
      directory = 'Main\Source Data'
      
      for i, filename in enumerate(os.listdir(directory)):

        if i == 0:
            continue

        else:
            e = SingleVOC()
            e.load_experiment(directory+'\\'+filename)
            e.plot()

            option = input("Select 0 to quit. Select 1 to continue.")

            if option == '0':
                break

            elif option == '1':
                pass

def SingleVOC_test():
    #e = SingleVOC()
    #print(e.lable)
    #e.load_experiment(r'C:\Users\William\Desktop\My Python Stuff\0 - Gas Sensor June\Gas Sensor\Main\IPA_0.5_0.5')
    #print(e.lable)
    #e.plot()

    e = SingleVOC('Test_Name',0.5,0.07)
    f = SingleVOC('Test_Name',0.5,0.07)
    e.save_experiment()
    f.save_experiment()
#SingleVOC_test()

def Mixture_test():
    file1 = r'Main\Source Data\IPA_0.5_0.5'
    file2 = r'C:\Users\William\Desktop\My Python Stuff\0 - Gas Sensor June\Gas Sensor\Main\Data\IPA_0.5_0.1'
    file3 = r'C:\Users\William\Desktop\My Python Stuff\0 - Gas Sensor June\Gas Sensor\Main\Data\oXylene_0.5_1.0_1'
    file4 = r'Main\Source Data\Toluene_0.5_1.0'
    file5 = r'Main\Source Data\Benzene_0.5_0.25'
    
    toluene = SingleVOC()
    toluene.load_experiment(file4)
    toluene.update_scaling_factor(.5)
    toluene.remove_baseline()

    ipa = SingleVOC()
    ipa.load_experiment(file1)
    ipa.update_scaling_factor(.5)
    ipa.remove_baseline()

    benezene = SingleVOC()
    benezene.load_experiment(file5)
    benezene.update_scaling_factor(1)
    benezene.remove_baseline()
    

    m = Mixture(toluene,ipa,benezene)
    #print(m.x_sync)
    m.plot()
    #m.save_mixture()
    #print(m.get_peaks())

    e = Mixture()
    e.load_mixture(r"Main\Genereated Data\0.5Toluene_0.25IPA_0.25Benzene_0.5")
    e.plot()


#file = r'C:\Users\William\Desktop\My Python Stuff\GAS SENSOR\Data\1 - Raw_Data\20190722_Sponge_IPA\20190722_Sponge_Ipa_A.monitor.txt'
#file = r'C:\Users\William\Desktop\My Python Stuff\GAS SENSOR\Data\1 - Raw_Data\20190822_Sponge_Benzene'
#file = r'C:\\Users\\William\\Desktop\\My Python Stuff\\GAS SENSOR\Data\\1 - Raw_Data\\20190722_Sponge_IPA\\20190722_Sponge_Ipa_B.monitor.txt'
#file = r'C:\Users\William\Desktop\My Python Stuff\GAS SENSOR\Data\1 - Raw_Data\20190723_Sponge_Benzene\20190723_Sponge_Benzene_CombinedC.monitor.txt'

