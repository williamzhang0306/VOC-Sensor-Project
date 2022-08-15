# Author: William Zhang
# File description: UI to view and generate gas mixtures.

from uitools_new import *
from tkinter import ttk
from tkinter import messagebox

# initiate tkinter window
master = Tk()
master.title('Gas Sensor')
tabControl = ttk.Notebook(master)

# set up tabs
view_tab = ttk.Frame(tabControl)
generate_tab = ttk.Frame(tabControl)
load_tab = ttk.Frame(tabControl)

tabControl.add(view_tab, text ='View')
tabControl.add(generate_tab, text ='Generate')
tabControl.add(load_tab, text ='Load')
tabControl.pack(expand = 1, fill ="both")

# creating two data fields that contain the file names
source_filenames = [filename for filename in os.listdir("Source Data\\")]
generated_filenames = [filename for filename in os.listdir("Generated Data\\")]


# creating two list boxes that will display the files
ttk.Label(view_tab , text = "Source Data", justify=CENTER).grid(row = 0, column = 0, padx = 10, pady = 5) 
source_lstbx = Listbox ( view_tab, selectmode= "SINGLE", width = 40 , height = 15 )
for filename in source_filenames:
    source_lstbx.insert('end', filename)   
source_lstbx.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = W)

ttk.Label(view_tab , text = "Generated Data").grid(row = 2, column = 0,padx = 10, pady = 5) 
generated_lstbx = Listbox ( view_tab, selectmode= "SINGLE", width = 40, height = 15 )
for filename in generated_filenames:
    generated_lstbx.insert('end', filename)
generated_lstbx.grid(column = 0, row = 3, padx = 5, pady = 5,sticky = W)
    
# function that will totaly update the listboxes if new files are added
def update_file_display():
    global source_filenames
    global generated_filenames
    source_filenames = [filename for filename in os.listdir("Source Data\\")]
    generated_filenames = [filename for filename in os.listdir("Generated Data\\")]
    source_lstbx.delete(0,END)
    generated_lstbx.delete(0,END)
    for filename in generated_filenames:
        generated_lstbx.insert('end', filename)
    for filename in source_filenames:
        source_lstbx.insert('end', filename) 

# function that will identify what file is selected
def get_file():
    '''returns filetype and filename from the list boxes'''    

    if source_lstbx.curselection():
        src_index = int(source_lstbx.curselection()[0])
        filename = source_lstbx.get(src_index)
        file_type = 'source'
    elif generated_lstbx.curselection():
        gen_index = int(generated_lstbx.curselection()[0])
        filename = generated_lstbx.get(gen_index)
        file_type = 'generated'

    else:
        print("Nothing selected")
        return None

    return file_type, filename


# creating a label that will display the selected file info
ttk.Label(view_tab , text = "File info",justify=CENTER).grid(row = 4, column = 0, padx = 10, pady = 5,sticky = W) 
file_info = ttk.Label(view_tab , text = '',justify=LEFT, anchor="w")
file_info.grid(row = 5, column = 0, sticky = W, padx = 10, pady = 5)  

# two functions that will update the file info label when called
#   get_file_info() will return text that will be displayed
#   update_info_label() takes the text created by get_file_info() and displays it

def get_file_info(file_type, filename):
    '''returns a file info string'''
        
    if filename == '0 - READ ME':
        return 'No info'

    info_string = f"File name: {filename}\n"

    if file_type == 'source':
        directory = "Source Data\\"
        file = open(directory + filename, mode = 'r')
        name, rate, conc = get_info_source(file)
        file.close()

        info_string += f"Gas composition:\n    {conc*100}% {name}\nRamp rate: {rate} °C/s"
 

    elif file_type == 'generated':
        directory = "Generated Data\\"
        file = open(directory + filename, mode = 'r')
        names, concs, rate = get_info_generated(file)
        file.close()
            
        info_string += f"Gas composition:\n"

        for index in range(len(names)):

                info_string += f"    {concs[index]*100}% {names[index]}\n"

        info_string += f"Ramp rate: {rate} °C/s"

    return info_string 

def update_info_label(event=None):
    '''Updates file info label when a new file is selected in the list box.'''
    if get_file():
        filetype, filename = get_file()
        info_string = get_file_info(filetype,filename)
        file_info.config(text = info_string)
            
# Binding selecting a file in the list box to file info display update        
source_lstbx.bind('<ButtonRelease-1>', update_info_label)
generated_lstbx.bind('<ButtonRelease-1>', update_info_label)

    #########################################################################################

# set up matplotlib canvas widget
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, view_tab)
canvas.draw()
canvas.get_tk_widget().grid(column = 1, row = 1, padx = 5, pady = 5, sticky = W, rowspan= 3)
    
toolbar_frame = Frame(view_tab) 
toolbar_frame.grid(row=4,column=1) 
toolbar = NavigationToolbar2Tk( canvas, toolbar_frame )
toolbar.update()

# plot function that will plot the selected file to the canvas
def plot(event=None):

        #clear the canvas
    plt.cla()
    canvas.draw()

        #checking that the file is plotable, ie is selected and is not a read_me file
    if get_file() == None:
        return

    else:
           file_type, filename = get_file()

    if filename == "0 - READ ME":
        return

    else:

        ax.set_xlabel("Time Elapsed")
        ax.set_ylabel("PID Voltage")

        if file_type == 'source':
            file_path = "Source Data\\" + filename
            v = SingleVOC()
            v.load_experiment(file_path)
            x = v.time
            y = v.s_data
            ax.plot(x,y,label = v.name + str(v.conc))
            title = f"{v.s_conc*100}% {v.name} on ramp rate {v.ramp}°C/s"
            ax.set_title(title) 

        elif file_type == 'generated':
            file_path = "Generated Data\\" + filename
            v = Mixture()
            v.load_mixture(file_path)
            for i in range(len(v.y_components)):
                x = v.x_sync
                y = v.y_components[i]
                name = f'{v.concs[i]}_{v.labels[i]}'
                ax.plot(x,y,label = name,linestyle="-",marker="")
            x = v.x_sync
            y = v.y_combined
            ax.plot(x,y,label = 'Mixture', linestyle="-",marker="")
            peaks = v.get_peaks()
            for peak in peaks:
                x,y = peak
                ax.plot(x,y,marker="x")
            title = f''
            for index in range(len(v.labels)):
                if index == 0:
                    title += f"{v.concs[index]*100}% {v.labels[index]}"
                else: 
                    title += f", {v.concs[index]*100}% {v.labels[index]}"

            title += f" mixture on ramp rate: {v.rate} °C/s"
            ax.set_title(title)

        plt.legend()
        canvas.draw()
    
    # button that will plot
    #Button(master, borderwidth=5, text = "plot", command =  plot ).grid(column = 1, row = 0, padx = 5, pady = 5)

#binding plot function to selecting file in the list boxes
source_lstbx.bind('<ButtonRelease-1>', plot, add = '+')
generated_lstbx.bind('<ButtonRelease-1>', plot, add = '+')

# initialize list of all the availble chemicals to choose
available_chemicals = list(find_all_chemicals())

# ramp rate
#Label(generate_tab , text = "Enter number of componenets").pack()
#num_gas_components = Entry(generate_tab, width = 4)
#num_gas_components.pack()

Label(generate_tab , text = "Enter ramp rate: ").grid(row = 0, column = 0,padx=5,pady=5)
ramp_rate = Entry(generate_tab, width = 4)
ramp_rate.grid(row = 0, column = 1,padx=5,pady=5)
Label(generate_tab, text = "°C/s").grid(row = 0, column = 2,padx=5,pady=5)

# create a list that will hold dynamically created widgets
# widgets in list can be called to get value, which is used to generate a mixture
input_chemicals = []
input_concentrations = []

# used for formatting dynamically created widgets
percent_labels = []
num_gasses = 0

# function that is called when user is ready to generate a mixture
def generate():
    rate = float(ramp_rate.get())

    vocs = []

    for index, name in enumerate(input_chemicals):
        name = name.get()
        concentration = float(input_concentrations[index].get())/100
        if name and concentration:
            voc = find_experiment(name,rate,concentration)
            voc.remove_baseline()
            vocs.append(voc)
            
    mixture = Mixture(*vocs)
    filename = mixture.save_mixture()
    
    update_file_display()
    selection_index = generated_filenames.index(filename)
    generated_lstbx.select_set(selection_index)
    generated_lstbx.event_generate("<<ListboxSelect>>")

    plot()

    messagebox.showinfo("File Saved",f"{filename} \nsaved at \n{os.getcwd()}\\Generated Data")


# generate button
generate_button = Button(generate_tab, text = "Generate", command = generate)
generate_button.grid(row = num_gasses+3, column = 0,columnspan=1,pady= 5)


# create dynamic combobox that will take in chemical name and concetrations
Label(generate_tab,text = 'Enter name and concentration: ').grid(row = 1, column = 0,padx=5,pady=5,columnspan=2)

# these functions will create or remove an entry field for one gas compononent  when called
num_gasses = 0
def add_chemical_input():
    global num_gasses

    # these 3 blocks create a new row where the user can input info
    name = ttk.Combobox(generate_tab)
    name['values'] = available_chemicals
    input_chemicals.append(name)
    name.grid(row = num_gasses+2, column = 0, padx=5)
    
    concentration = Entry(generate_tab, width = 5)
    input_concentrations.append(concentration)
    concentration.grid(row = num_gasses+2, column = 1)

    a = Label(generate_tab,text = '%')
    a.grid(row = num_gasses+2, column = 2)
    percent_labels.append(a)

    # update generate button location
    generate_button.grid(row = num_gasses+3, column = 1,columnspan=1,pady= 5)

    num_gasses+=1


def remove_chemical_input():

    # if there is only one entry field, don't remove it
    if len(input_chemicals) == 1:
        return None

    last_chemical = input_chemicals[-1]
    last_concentration = input_concentrations[-1]

    last_chemical.grid_forget()
    input_chemicals.pop()

    last_concentration.grid_forget()
    input_concentrations.pop()

    percent_labels[-1].grid_forget()
    percent_labels.pop()

# calling add_chemical_input() so that one input is shown when program is started
add_chemical_input()

#assigning buttons to call  add/remove_chemical_input
Button(generate_tab, text = "+", command = add_chemical_input).grid(row = 2, column = 4)
Button(generate_tab, text = "-", command = remove_chemical_input).grid(row = 2, column = 5)

# create entry place where sensor log files can be loaded
Label(load_tab,text="Enter VOC name: ").grid(row = 0, column = 0)
Label(load_tab,text="Paste file path: ").grid(row = 1, column =0)
Label(load_tab,text= "For example:\n 'C:\\Users\\William\\Desktop\\My Python Stuff\\GAS SENSOR\\{file name}'",justify= 'left').grid(row = 2, column = 0, columnspan=2, sticky= 'W')
log_file_location = Entry(load_tab, width = 50)
log_file_location.grid(row=1, column = 1,pady = 5)
compound_name = Entry(load_tab, width = 50)
compound_name.grid(row=0, column = 1,pady = 5)

#load file function
def load():
    global available_chemicals
    filename = log_file_location.get()
    name = compound_name.get()
    
    try:
        l = save_log_file_to_source(name,filename)
    except:
        messagebox.showinfo("Error","An exception occurred")
    else:

        messagebox.showinfo("Save successful",f"{len(l)} files saved")
        available_chemicals = list(find_all_chemicals())
        update_file_display()

Button(load_tab,  text = "Load", command = load).grid(row = 1, column = 2)


# quit function
def _quit():
    master.quit()
    master.destroy() 



master.protocol("WM_DELETE_WINDOW", _quit)
master.mainloop()


