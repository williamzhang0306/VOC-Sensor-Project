import matplotlib.pyplot as plt
import datetime

#Dictionary that associates a data label with its column number in the sensor log file
#Used in get_data() which reads a line of data
label_to_index = {'date_time': 0, 
    'dilution_concentration': 1, 
    'dilution_dilutant': 2, 
    'dilution_pressure': 3, 
    'dilution_ratio': 4, 
    'dilution_sample_flow': 5, 
    'ovg_concentration': 6, 
    'ovg_exhaust': 7, 
    'ovg_sample_flow': 8, 
    'ovg_source': 9, 
    'ovg_temperature': 10, 
    'peltier_current': 11, 
    'peltier_power': 12, 
    'peltier_sink_temperature': 13, 
    'peltier_temperature': 14, 
    'peltier_voltage': 15, 
    'pid_concentration': 16, 
    'pid_voltage': 17, 
    'purge_flow': 18, 
    'sht21_concentration': 19, 
    'sht21_humidity': 20, 
    'sht21_temperature': 21, 
    'valve_position': 22, 
    'valve_purpose': 23
    }

def get_datetime(date_time_str):
    '''Takes in a string in the form YYYY/MM/DD HH:MM:DD and returns a datetime object'''
    date_str = date_time_str.split()[0]
    time_str = date_time_str.split()[1]

    year = date_str.split('/')[0]
    month = date_str.split('/')[1]
    day = date_str.split('/')[2]

    hour = time_str.split(':')[0]
    minute = time_str.split(':')[1]
    second = time_str.split(':')[2]

    date = datetime.date(year, month, day)
    time = datetime.time(hour, minute, second)
    return date, time

def get_time_delta(time_str):
    """Takes in a string with format HH:MM:SS and returns it as a timedelta object"""
    #print(time_str, type(time_str), sep = ':')
    time_lst = time_str.split(':')
    #print(time_lst, type(time_lst), sep = ':')
    #print(time_lst)
    hour = int(time_lst[0])
    min = int(time_lst[1])
    sec = int(time_lst[2])

    total_seconds = hour*60*60 + min*60 + sec

    return datetime.timedelta(seconds = total_seconds)

def datetime_to_timedelta(datetime_str):
    '''converts YYYY/MM/DD HH:MM:SS to a time delta object'''
    time_str = datetime_str.split()[1]
    return get_time_delta(time_str)

def is_command(line):
    '''Checks if a line in the data is a command or not'''
    return line[0] == '#'

def get_data(line, label):
    '''reads a line and returns the data corresponding to the label.
    Line is a string (a line from the log file. Label is a string,
    which is converted to an int using the label_to_index dictionary'''

    lst = line.split(', ')
    
    if label not in label_to_index:
        print('ERROR: Label not found')
        return None

    else:
        index = label_to_index[label]
        #print(f"Get_data: index = {index}, data  = {lst[index]}")
    
    return lst[index]

def plot_file(filename, labels = ['pid_voltage']):
    '''Given a filename, it plots the entire file and any associated labels
    lst_of_labels is a list of strings. Each string is label that should be plotted.
    All labels will be plotted against elapsed time in the experiment
    \n
    Availble labels are:
    date_time, dilution_concentration, dilution_dilutant, 
    dilution_pressure, dilution_ratio, dilution_sample_flow, 
    ovg_concentration, ovg_exhaust, ovg_sample_flow, ovg_source, 
    ovg_temperature, peltier_current, peltier_power, 
    peltier_sink_temperature, peltier_temperature, peltier_voltage, 
    pid_concentration, pid_voltage, purge_flow, 
    sht21_concentration, sht21_humidity, sht21_temperature, valve_position, valve_purpose'''

    #createing a diciontary that will contain all the series for each label
    #Time_elapsed is in the dictionary by default
    series_dict = {'date_time' : []}
    for label in labels:
        series_dict[label] = []

    #open the file
    file = open(filename, mode = 'r')

    #read the file and append data to the label's series

    #reading every line
    for index, line in enumerate(file):

        #skip the first line since it contains the labels but no data
        if index == 0:
            continue
        
        #get initial time from initial data line (index = 1)
        elif index == 1:
            t0_str = get_data(line, 'date_time')
            t0_dt = datetime_to_timedelta(t0_str)
            t0 = t0_dt.total_seconds()
        
        #skip if the line is a sensor log (line begins with a '#)
        if line[0] == '#':
            continue
        
        #read and append the data for each line
        for label in series_dict:
            data_point = get_data(line,label)
            
            if data_point == 'None':
                data_point = 0

            #print(index, label, data_point, type(data_point), sep = ' ')

            if label == 'date_time':
                t_cur = datetime_to_timedelta(data_point)
                time_elapsed = t_cur.total_seconds() - t0
                data_point = time_elapsed
            data_point = float(data_point)
            series_dict[label].append(data_point)
    
    #plotting the data

    #naming time_elapsed - x_axis
    time_elapsed = series_dict['date_time']

    fig, ax = plt.subplots()

    for index,label in enumerate(labels):
        #first series can be plotted normall
        if index == 0:
            ax.plot(time_elapsed,series_dict[label], linewidth= 1.0, label = label)
            ax.set_ylabel(label)
            
        else:
            twin = ax.twinx()
            twin.plot(time_elapsed,series_dict[label],linewidth= 1.0, label = label, color = 'red')
            twin.set_ylabel(label)

    ax.set_xlabel("Time Elapsed (s)")
    lines = ax.get_lines() + twin.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], loc='upper left')
    ax.set_title(filename)
    plt.show()


    file.close()


#Future improvements to get_experiments
#Automate retrieving heating ramp data
#Allow for custom experiment label generation with any experiment parameter

#Heating ramp is hard coded to 0.5 (C`/s)
#

def get_experiments(filename, compound_str = 'no_name', label = 'pid_voltage',heating_ramp = '0.5'):
    '''Returns the time vs label data for every experiment in a file
    The experiment begins when the peltier temperature is set to 70 and rises.
    Function returns a list of tuples for the time series and label series.
    The first element of each tuple is the experiment number or identifier
    (such as the chemical and its concentration)
    
    E.G x_series = [( 'IPA_300pbb' , [0.1,0.2,0.2....] ).
                    ( 'IPA_420ppb' , [0.2,0.2,0.3....] )]

        y_series = [( 'Time_elapsed', [0,2,4,5,6,....])
                    ( 'Time_elapsed', [1,2,3,4,5,....])]       '''
    
    #initialize data series stuff
    time_series = x_series = []
    data_series = y_series = []

    #new in august 2nd 2022
    heat_series = h_series = []

    #Getting the compund name, don't have a better solution rn
    compound_name = compound_str

    #sensor logged commands that indicated the start and stop of one experiment
    start_command = 'WAIT_FOR 69.9 <= peltier <= 70.1'
    stop_command = 'SET vapour_generator:temperature'
    wait_command = "WAIT 600.0s"

    #initial conditions for experiment tracking
    experiment_on = False
    ramp_on = False

    #open and read the file
    file = open(filename, mode = 'r')
    content = file.readlines()
    past_experiment_labels = []
    for index,line in enumerate(content):

        #check if the experiment has begun
        if not experiment_on:
            
            if is_command(line) and start_command in line:
                #if the experiment is on initialize data collection
                experiment_on = True
                ramp_on = True

                #get the initial time from the next line after the experiment starts
                t0_str = get_data(content[index+1], 'date_time')
                t0 = datetime_to_timedelta(t0_str).total_seconds()
                
                #get the concentration used for the experiment
                concentration = float(get_data(content[index+1], 'dilution_concentration'))
                conc_percent = str(round(concentration*100))

                #create an experiment label for the series
                    #experiment_label = f'{conc_percent}% {compound_name}'
                experiment_label = f'{compound_name} {heating_ramp} {round(concentration, 2)}'
                
                #check if the experiment_label already exists and update it
                old = experiment_label
                new = old
                count = 2
                while new in past_experiment_labels:
                    new = old + str(count)
                    count+=1
                experiment_label = new
                past_experiment_labels.append(experiment_label)
                
                #create the tuple
                x_series.append( (experiment_label, [])  )
                y_series.append( (experiment_label, [])  )
                h_series.append( (experiment_label, [])  )

                #print(f'{experiment_label}: ON. Time = {t0_str}')

            else:
                continue
        
        #if the experiment is on start recording data
        elif experiment_on:

            #check if the experimented ended
            if (is_command(line) and stop_command in line) or index + 1 == len(content):
                experiment_on = False
                #print(f'{experiment_label}: OFF. Time = {t0_str}')

            elif wait_command in line:
                #print(line)
                ramp_on = False

            #this checks if there is a command that is not the wait command
            elif is_command(line) and stop_command not in line:
                continue
            
            #if the line is not a command, data is collected
            else:
                time_str = get_data(line, 'date_time')
                data = float(get_data(line,label))
                #print(' ')
                #print(index, time_str, type(time_str) )
                #print(' ')
                t_elapsed = datetime_to_timedelta(time_str).total_seconds() - t0

                #new in august 2nd 2022
                temperature = float(get_data(line, 'peltier_temperature'))

                #append data
                for tup in x_series:
                    if tup[0] == experiment_label:
                        tup[1].append(t_elapsed)
                        break

                for tup in y_series:
                    if tup[0] == experiment_label:
                        tup[1].append(data)
                        break

                for tup in h_series:
                    if tup[0] == experiment_label:
                        if ramp_on:
                            tup[1].append(temperature)
                        break

    file.close()

    return x_series, y_series, h_series
                
def plot_experiments(filename, name = 'no_name', label = 'pid_voltage'):
    x_array, y_array, h_array = get_experiments(filename, name, label)
    #print(len(x_array),len(y_array))

    fig, ax = plt.subplots()

    for i in range(len(x_array)):
        x_label, x_data = x_array[i]
        y_label, y_data = y_array[i]
        ax.plot(x_data, y_data, label = y_label )

    ax.set_xlabel("Time Elapsed")
    ax.set_ylabel(label)
    ax.set_title("Title")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    #misc testing


    ##file = '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190821_Sponge_oXylene/20190820_overnight_Sponge_oXylene.monitor.txt.TESTING'
    ##file = '/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190724_Sponge_Benzaldehyde/20190724_Sponge_Benzaldehyde_combined_A.monitor.txt'
    ##file = "/Users/williamzhang/Documents/MyPyStuff/Gas Sensor/Data/Archive/20190822_Sponge_Benzene/20190822_Sponge_Benzene.monitor.txt"
    #file = r"C:\Users\William\Desktop\My Python Stuff\0 - Gas Sensor June\Gas Sensor\Data\1 - Raw_Data\20190722_Sponge_IPA\20190722_Sponge_Ipa_A.monitor.txt"
    
    
    #plot_file(file,labels = ['pid_voltage', 'dilution_concentration'])
    #plot_experiments(file,'IPA', 'peltier_temperature')
    #plot_experiment(file, 'dilution_concentration')
    #plot_experiments(file,'IPA', 'pid_voltage')
    #plot_file(file)
    #x,y = get_experiments(file,'IPA','pid_voltage')

    #print(y[0])
    
    #print(y)


    file = r'C:\Users\William\Desktop\My Python Stuff\GAS SENSOR\Data\1 - Raw_Data\20190723_Sponge_Benzene\20190723_Sponge_Benzene_CombinedC.monitor.txt'
    plot_file(file,labels = ['pid_voltage','peltier_temperature'])
    pass