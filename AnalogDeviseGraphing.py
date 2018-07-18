import Tkinter as tk
import matplotlib
import re
import sys
import tkMessageBox

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import serial



#Font for the GUI
#Plot style
LARGE_FONT = ('Verdana', 12)                    
style.use("ggplot")



#Setting the figure size
#Sets size and posistion in figure, (211) = 2x1 grid and 1st plot
#(212) = 2x1 grid and 2nd plot
#Voltage strings for the two different transmitters
plotFigure = Figure(figsize=(5, 5), dpi=100)                    
plotA = plotFigure.add_subplot(211)                             
plotB = plotFigure.add_subplot(212)                             
voltage1 = []                                                   
voltage2 = []



#Auto detects which usb port is connected
def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result



#converts from list to singal string
comPort = ''.join(serial_ports())



#Try's to connect to the arduino
try:
    arduinoData = serial.Serial(comPort, 9600)  
except:
    tkMessageBox.showerror('ERROR', 'No USB device detected! \nPlease connect the device and try again \n'
                                    'Multiple serial ports connected may also cause an issue!')
    exit()



#Animates plotA graph                                                
def animate(i):
    while (arduinoData.inWaiting() == 0):
        pass

    pullData = arduinoData.readline()

    #Checks if its the voltage from transmitter 1
    if 'v1' in pullData:                        
        v1 = True
        pullData = re.findall("\d+\.\d+", pullData)
        voltage1.append(pullData)
    else:
        #If its not Transmitter 1 it assumes its from transmitter 2
        v1 = False
        pullData = re.findall("\d+\.\d+", pullData)
        voltage2.append(pullData)

    if len(voltage1) >= 30 or len(voltage2) >= 30:
        del voltage1[0]
        del voltage2[0]

    try:
        #Chacks the voltage value to decide which colour to set the plot
        if float(pullData[-1]) >= 0.8 and float(pullData[-1]) < 1.75:
            if v1:
                plotA.clear()
                plotA.plot(voltage1, color='yellow', label='CABLE 1 NEEDS MAINTENANCE!!')
            else:
                plotB.clear()
                plotB.plot(voltage2, color='yellow', label='CABLE 2 NEEDS MAINTENANCE!!')
        elif float(pullData[-1]) < 0.8:
            if v1:
                plotA.clear()
                plotA.plot(voltage1, color='red', label='Cable 1 is plotA Dead Link ')
            else:
                plotB.clear()
                plotB.plot(voltage2, color='red', label='Cable 2 is plotA Dead Link')
        else:
            if v1:
                plotA.clear()
                plotA.plot(voltage1, color='green', label='Cable 1 - Good Connection')
            else:
                plotB.clear()
                plotB.plot(voltage2, color='green', label='Cable 2 - Good Connection')

        plotA.legend(loc=2)
        plotB.legend(loc=2)

    except:
        pass

    #Set plot labels, limits and title
    plotA.set_ylim(0, 4)                        
    plotB.set_ylim(0, 4)
    plotA.set_ylabel('Voltage (V)')             
    plotB.set_ylabel('Voltage (V)')
    plotA.set_title('Connection Health')        



#Initialize GUI window
class seaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default='FC_Logo.ico')
        tk.Tk.wm_title(self, "Signal Stenght Graphic")

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = graphPage(container, self)
        self.frames[graphPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(graphPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



#Creates graph page
class graphPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        canvas = FigureCanvasTkAgg(plotFigure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)



#Setting the interval time too low cna create plotA laggy program
app = seaofBTCapp()
ani = animation.FuncAnimation(plotFigure, animate, interval=250) 
app.mainloop()
