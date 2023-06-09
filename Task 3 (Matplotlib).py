import matplotlib.pyplot as Plot
import matplotlib.animation as Animation
import serial
import datetime

SerialInstance = serial.Serial(port='COM3', baudrate=9600)

if SerialInstance.isOpen() == False:
    SerialInstance.close()

Figure = Plot.figure()
Axes = Figure.add_subplot(1, 1, 1)
X = []
Y = []

def Animate(Interval, X, Y):

    Axes.clear()

    Plot.title('Distance vs Time')
    Plot.xlabel('Time')
    Plot.ylabel('Distance')

    if SerialInstance.in_waiting:
        Current_Time = str(datetime.datetime.now())
        X.append(Current_Time[11:])
        Distance = SerialInstance.readline().decode('utf')
        Y.append(Distance)
    
    Axes.plot(X[-10:], Y[-10:])

    Plot.xticks(rotation=45, ha='right')
    Plot.subplots_adjust(bottom=0.30)

A = Animation.FuncAnimation(Figure, Animate, fargs=(X, Y), interval=1000)

Plot.show()

if SerialInstance.isOpen() == True:
    SerialInstance.close()
