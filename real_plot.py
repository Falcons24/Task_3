import serial
import serial.tools.list_ports
#import serial libraries to read arduino data from the serial port
import time
from datetime import datetime
#import time libraries to store current time in the csv file and display on the realtime plot 
import csv
#import csv library to store the data read from the serial port and save it in a csv file
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div
from bokeh.layouts import column
from bokeh.models import HoverTool
#import bokeh libraries for various functions of the realtime plot
import sys
#improt sys library for program termination


#=======================================================================================================
#portInitial(): used to create a list of all the ports connected to the system
#uses portdetect(): to find arduinos connected to the system
#Initializes the port once detected
def portInitial():
    ports = serial.tools.list_ports.comports()          #read all connected serial ports
    print(ports)                                        #print all the ports
    serialInst = serial.Serial()                        #declare a port variable to be initialized

    #creating portlist
    portsList = []                                      #create a empty list to append all available ports
    for onePort in ports:                               #navigate through serial ports
        portsList.append(str(onePort))                  #append port to portlist
        print(str(onePort))                             #display port
    
    portVar=portDetect(portsList)                       #detect arduino connected to serial port using portDetect()
    serialInst.baudrate = 9600                          #set Baud rate to 9600
    serialInst.port = portVar                           #set COM number to detected COM number
    serialInst.open()                                   #open serial port for data tranmission
    return(serialInst)                                  #return initialized port to main


#=======================================================================================================
#portdetect(): used to read the initialized portlist and automatically pick an arduino 
# by matching any one of the keynames listed in the keylist with the portnames

def portDetect(portsList):
    keylst=["Silicon","Arduino","USB Serial"]           #keylist for arduino 
    find_flag=False                                     #Flag set to False until port is detected
    for x in range(0,len(portsList)):                   #navigate through all ports
        for key in keylst:                              #navigate through keylist names
            if key in portsList[x]:                     #check whether any keylist name is present in the port name
                                                        #IF TRUE (Keyname in portname)
                find_flag=True                                 #set find flag to true
                portVar = portsList[x][0:5].rstrip()           #assign corresponding COM number to portVar            
    
    if find_flag:                                       #check if find flag is True or False
                                                        #IF TRUE(Port is detected)
        print("Selecting Port: ",portVar)                       #Display corresponding COM port    
        return(portVar)                                         #return COM number stored in portVar to Main
    
    else:                                               #IF FALSE(Port not detected)
        print("Port Not Detected")                              #display port is not detected
        detect_choice=input("Try Again  [Y/N]:      ")          #Ask user to try again
        if str(detect_choice.upper)=="Y":                       #IF TRUE (User wishes to search for port again)
            print("trying again")                                       #display trying again
            ser = portInitial()                                         #initialize portlist again
            
        else:                                                   #IF FALSE(User does not wish to continue program)
            quit()                                                      #terminate program



#=======================================================================================================
#createCSVfile(): used to create a new csv file with a unique timestamped name to store 
#the realtime data collected from the arduino
def createCSVfile():                                            
    current_local_time = time.localtime()                       #read system current time
    fileArg = time.strftime("%d_%B_%Y_%Hh_%Mm_%Ss",current_local_time)      #format time to include in file name
    filename = 'falcons_das_'+ fileArg + '_daq_log.csv'         #create file name
    print(f'\nCreated Log File -> {filename}')                  #display file name with success message
    return(filename)                                            #return filename to main

#=======================================================================================================
# update() used to read the serial port data and store it in a csv file along with plotting it in realtime
def update():
    # Read data from the serial port
    try:
        data = ser.readline().decode().strip()                  #Adjust the decoding and stripping based on your data format
        value = float(data)                                         
        current_time = datetime.now()                           #read system current time

        new_data = dict(
            time=[current_time],
            value=[value]
        )                                                       #Create a dictionary with key current time and value 
        source.stream(new_data, rollover=200)                   #stream the new data to the source to plot graph in real time
     
        value_paragraph.text = "<div style='font-size: 20px;text-align: left; margin-left: 50px'> Current Value: {:.2f} </div>".format(value)
        #formatting to display current value on realtime plot
        Time_paragraph.text="<div style='font-size: 20px;text-align: left; margin-left: 50px'>Current Time : {time} </div>".format(time=current_time)
        #formatting to display current time on realtime plot
        
        # Print value to the terminal
        print("Distance: {:.2f}".format(value))

        # Append data to the CSV file
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([current_time, value])
            csvfile.flush()  # Flush the data to the file

    except ValueError:
        pass

    except KeyboardInterrupt:
        pop_up_message.text = "<div style='font-size: 20px ; color: red; text-align: left; margin-left: 50px'>Program Status: Terminated [Manually terminated]</div>"
        pop_up_message.visible = True
        

        print("Program Manually Terminated")  # Print error message for disconnected serial port

        # Append disconnected message to the CSV file
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([datetime.now(), "Program Manually Terminated"])
            csvfile.flush()  # Flush the data to the file

        curdoc().add_timeout_callback(terminate_program, 0)  # Terminate program after the pop-up message is displayed


    except serial.SerialException:
        pop_up_message.text = "<div style='font-size: 20px ; color: red; text-align: left; margin-left: 50px'>Program Status: Terminated [Port disconnected]</div>"
        pop_up_message.visible = True
        curdoc().add_timeout_callback(terminate_program, 0)  # Terminate program after the pop-up message is displayed

        print("Port disconnected")  # Print error message for disconnected serial port

        # Append disconnected message to the CSV file
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([datetime.now(), "Port disconnected"])
            csvfile.flush()  # Flush the data to the file

        # ser.close()  # Close the serial port

def terminate_program():
    sys.exit()





ser= portInitial()                                              
# Create a figure with initial height and width

curdoc().theme = 'dark_minimal'
curdoc().template.theme = '''
<style>
    body {
        background-color: lightgray;  /* Set the background color of the web page */
    }
</style>
'''

p = figure(title="Real-Time Serial Data", x_axis_type="datetime", x_axis_label='Time', y_axis_label='Value')
p.height = 500
p.width = 1400
p.margin = 50

# Create a ColumnDataSource to hold the data
source = ColumnDataSource(data=dict(time=[], value=[]))

# Create a line plot
line = p.line(x='time', y='value', source=source, line_width=2)

# Create a paragraph to display the current value
value_paragraph = Div(text="<div style='font-size: 20px;text-align: left; margin-left: 50px'> Current Value: </div>")
Time_paragraph = Div(text="<div style='font-size: 20px;text-align: left; margin-left: 50px'> Current Time: </div>")


falc = figure()

# Load the image
img_path = "C:/Users/Administrator/falcons.png"  # Replace with the correct file path
falc.image_url(url=[img_path], x=0, y=0, w=10, h=10)
#"C:\Users\Administrator\falcons.png"


# Create a CSV file and write the header


filename = createCSVfile()  # Specify the filename for the CSV file



with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time', 'Value'])  # Write the header row

# Create a pop-up message div
pop_up_message = Div(text="<div style='font-size: 20px ; color: green; text-align: left; margin-left: 50px'>Program Status: Active</div>")

#pop_up_message = Div(text="<div style='font-size: 20px; color: red;'>Port disconnected</div>", visible=False)




# Update the plot and value every second
curdoc().add_periodic_callback(update, 200)

# Create hover tool to display value and time on mouseover
hover = HoverTool(renderers=[line], tooltips=[("Time", "@time{%H:%M:%S}"), ("Value", "@value")], formatters={"@time": "datetime"})
p.add_tools(hover)

# Set up the layout
curdoc().add_root(column(falc, value_paragraph, Time_paragraph, p,pop_up_message))


#bokeh serve --show real_plot.py
