from tkinter import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)


master = Tk()

fig, ax = plt.subplots()

#ax.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5],label = "first_subplot")

#ax.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8],label = "second_subplot")

#ax.set_xlabel("Time Elapsed")
#ax.set_ylabel("PID Voltage")
#ax.set_title("Test Title")

plt.legend()

canvas = FigureCanvasTkAgg(fig, master)

canvas.draw()

canvas.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas,master)

toolbar.update()

canvas.get_tk_widget().pack()


def on_click():

    plt.cla()
    canvas.draw()

def on_click2():
    ax.plot([1,2,3,4,5,6,7,8],[5,5,5,5,5,5,5,5],label = "first_subplot")

    ax.plot([1,2,3,4,5,6,7,8],[9,8,7,4,5,3,7,2],label = "second_subplot")

    ax.set_xlabel("Time Elapsed")
    ax.set_ylabel("PID Voltage")
    ax.set_title("Test Title")
    plt.legend()

    canvas.draw()

Button(master, borderwidth=5, text = "clear plot", command = on_click).pack()
Button(master, borderwidth=5, text = "replot plot", command = on_click2).pack()

mainloop()