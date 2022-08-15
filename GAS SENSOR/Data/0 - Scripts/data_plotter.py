#plotting the data in TIME_PID_VOLT and other plot testing

import matplotlib.pyplot as plt
from datetime import timedelta

def get_time(time_str):
    """Takes in a string with format HH:MM:SS and returns it as a timedelta object"""
    #print(time_str, type(time_str), sep = ':')
    time_lst = time_str.split(':')
    #print(time_lst, type(time_lst), sep = ':')
    #print(time_lst)
    hour = int(time_lst[0])
    min = int(time_lst[1])
    sec = int(time_lst[2])

    total_seconds = hour*60*60 + min*60 + sec

    return timedelta(seconds = total_seconds)

def get_data_from_line(line):
    """takes in a string and returns the time, and voltage
    time is returned as a timedelta object and voltage as a float"""

    l = line.split()

    date = l[0]
    time = get_time(l[1].strip(","))
    voltage = float(l[2])

    return time, voltage


def plot_desorp_curve(filename):

    #open the file and its contents
    file = open(filename, mode = 'r')

    content = file.readlines()

    #lists of data to plot
    x = time_elapsed = []
    y = voltage_reading = []

    initial_time = None
    initial_voltage = None
    
    for index, line in enumerate(content):
        
        #get the initial starting point
        if index == 1:
        #if initial_time == None and initial_voltage == None and"WAIT_FOR 69.9 <= peltier <= 70.1" in line: # this is the moment when the desorption begin
            initial_index = index#+1
            initial_time,initial_voltage = get_data_from_line(content[initial_index]) #content[index+1] is the next line
            #print(initial_time.total_seconds(),initial_voltage)
            continue

        #incase no initial starting point can be found
        elif index >= len(content):
            print("No desorption event in sensor detected")
            return None


        #after an initial point is found, start collecting data
        #also check if the line is a sensor log, which should be skipped
        if initial_time is not None and initial_voltage is not None:
        
            if line[0] != '#':

                current_time , current_voltage = get_data_from_line(line)
                t_delta = current_time - initial_time
                time_elapsed.append(t_delta.total_seconds())
                voltage_reading.append(float(current_voltage))

            elif line[0] == '#' and "WAIT_FOR 69.9 <= peltier <= 70.1" in line:

                next_index = index+1
                current_time, _ = get_data_from_line(content[next_index])
                t_delta = current_time - initial_time
                
                print(f"Time of interest: t =  {t_delta.total_seconds()}, {current_time}")


    file.close()
    
    return x,y


#opening file
x,y = plot_desorp_curve(input("Paste file name: "))

fig, ax = plt.subplots()

ax.plot(x,y, linewidth= 1.0)


plt.show()