# Author: William Zhang
# User interface and other tools to easily create and save gas mixtures
# all filenames are local and assume we are in the MAIN directory


from experiment import *
from tkinter import *
import os
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

def get_info_source(file):
    '''Helper function that retrieves chemical name, ramp rate and concentration from a file in source data'''
    line_numbers = [0,1,2]
    l =  [x.strip() for i, x in enumerate(file) if i in line_numbers]
    name = l[0].split(": ")[1]
    rate = float(l[1].split(": ")[1])
    conc = float(l[2].split(": ")[1])
    return name, rate, conc

def get_info_generated(file):
    '''Helper function that retrieves chemical name, ramp rate and concentration from a file in generated data'''
    line_numbers = [0,1,2]
    l =  [x.strip() for i, x in enumerate(file) if i in line_numbers]
    names = l[0].split()
    concs = [float(n) for n in l[1].split()]
    rate = float(l[2])
    return names, concs, rate

#filename = r"C:\\Users\William\Desktop\\My Python Stuff\\GAS SENSOR\\Main\\Generated Data\\0.5Toluene_0.5IPA_0.5"
#file = open(filename,mode = 'r')
#print(get_info_generated(file))
#file.close()

def find_experiment(chemical_name: str, ramp_rate: float, concentration:float):
    '''returns a SingleVOC object that has the inputed properties. This function
    searches through the file Source Data. It finds the file with the same chemical name, 
    ramp rate, and closest concentration. Then it scales the data to the target concentration.'''
    
    cur_directory = "Source Data\\"

    best_concentration_diff = None
    best_file = None

    for filename in os.listdir(cur_directory):

        if filename == '0 - READ ME':
            continue

        file = open(cur_directory+filename, mode = 'r')

        name_b, rate_b, conc_b = get_info_source(file)

        if chemical_name == name_b and ramp_rate == rate_b:

            concentration_diff = abs(concentration - conc_b)
            #print(filename, concentration_diff)

            if best_concentration_diff == None or concentration_diff < best_concentration_diff:
                best_concentration_diff = concentration_diff
                best_file = cur_directory+filename

        file.close()

    #print(best_file)
    if best_file:
        voc = SingleVOC()
        voc.load_experiment(best_file)
        voc.update_scaled_concentration(concentration)

    else:
        voc = None
        print("No file or data found.")
        
    return voc
########################################################################################################################################
#v = find_experiment('IPA',0.5,0.5)
#v.plot()

def create_mixture(chemicals: list, concentrations: list, ramp_rate: float):
    '''returns a mixture object with the specified parameters'''

    componenet_gasses = []

    for index,chemical in enumerate(chemicals):
        single_voc = find_experiment(chemical, ramp_rate, concentrations[index])
        componenet_gasses.append(single_voc)

    mixture = Mixture(componenet_gasses)

    return mixture

def find_all_chemicals():
    '''returns a set of all the chemical names in source data'''
    
    names = set()

    cur_directory = "Source Data\\"
    for filename in os.listdir(cur_directory):
        if filename == '0 - READ ME':
            continue
        else:
            file = open(cur_directory+filename,mode = 'r')
            name = file.readline().split(': ')[1].strip()
            names.add(name)

    return names

def save_log_file_to_source(chemical_name,filename):

    l = load_from_log(compound_name = chemical_name, log_file = filename)
    for e in l:
        e.save_experiment()

    return l