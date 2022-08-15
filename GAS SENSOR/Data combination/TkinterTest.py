#some tkinter notes
from tkinter import *
main_window = Tk()

# Labels : types of widgets that display an output
# you can assign entry fields to variables
Label(main_window , text = "Enter your name").grid(row = 0, column = 0) 

Label(main_window , text = "What is your age").grid(row = 1, column = 0) 

# Text Input
my_name = Entry(main_window, width = 50, borderwidth = 5)
my_name.grid(row = 0, column = 1)

my_age = Entry(main_window, width = 50, borderwidth = 5)
my_age.grid(row = 1, column = 1)

# Buttons
# callback function: function that is activated by the button
def on_click():
    print(f"my name is {my_name.get()} and my age is {my_age.get()}")

Button(main_window, borderwidth=5, text = "click me", command = on_click).grid(row = 2, column = 1)



OPTIONS = [
"Jan",
"Feb",
"Mar"
] #etc

master = Tk()

variable = StringVar(master)
variable.set(OPTIONS[0]) # default value

w = OptionMenu(master, variable, *OPTIONS)
w.pack()




lstbx = Listbox ( master, selectmode= "SINGLE" )
lstbx.insert(1, "Test1")
lstbx.insert(2, "Test2")
lstbx.insert(3, "Test3")
lstbx.pack()



def ok():
    print ("value is:" + variable.get())
    print(lstbx.curselection())
    lstbx.insert(0, variable.get())

button = Button(master, text="OK", command=ok)
button.pack()

mainloop()
#main_window.mainloop()





#
# ideas
# how to add new data
# provide filename as input for load_from _log() --> returns list of SingleVOC objects
# for each SingleVOC object save the data to SourceData
