import serial
import serial.tools.list_ports
import time
import csv
from datetime import datetime
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import Div
from bokeh.layouts import column
from bokeh.models import HoverTool
import sys

#port detect
def portDetect(portsList):
    keylst=["Silicon","Arduino","USB Serial"]
    find_flag=False
    for x in range(0,len(portsList)):
        for key in keylst:
            if key in portsList[x]:
                find_flag=True
                portVar = portsList[x][0:4]
    if find_flag:
        print("Selecting Port: ",portVar)
        return(portVar)
    else:
        print("Port Not Detected")
        detect_choice=input("Try Again  [Y/N]:      ")
        if str(detect_choice.upper)=="Y":
            print("trying again")
            ser = portInitial()
            
        else:
            quit()
        
        #port_det_count=0
        #while port_det_count <5:
            #print("Attempting to detect port")
            #port_detect()

# Open the serial port connection
def portInitial():
    ports = serial.tools.list_ports.comports()
    print(ports)
    serialInst = serial.Serial()

    #creating portlist
    portsList = []
    for onePort in ports:
        portsList.append(str(onePort))
        print(str(onePort))
    
    portVar=portDetect(portsList)
    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()
    return(serialInst)


def createCSVfile():
    current_local_time = time.localtime()
    fileArg = time.strftime("%d_%B_%Y_%Hh_%Mm_%Ss",current_local_time)
    filename = 'falcons_das_'+ fileArg + '_daq_log.csv'
    print(f'\nCreated Log File -> {filename}')
    return(filename)

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


# Function to update the plot and store data in CSV file
def update():
    # Read data from the serial port
    try:
        data = ser.readline().decode().strip()  # Adjust the decoding and stripping based on your data format
        
        value = float(data)
        current_time = datetime.now()

        new_data = dict(
            time=[current_time],
            value=[value]
        )
        source.stream(new_data, rollover=200)
        #"<div style='font-size: 20px;'> Current Value: </div>")
        value_paragraph.text = "<div style='font-size: 20px;text-align: left; margin-left: 50px'> Current Value: {:.2f} </div>".format(value)
        Time_paragraph.text="<div style='font-size: 20px;text-align: left; margin-left: 50px'>Current Time : {time} </div>".format(time=current_time)

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

# Update the plot and value every second
curdoc().add_periodic_callback(update, 200)

# Create hover tool to display value and time on mouseover
hover = HoverTool(renderers=[line], tooltips=[("Time", "@time{%H:%M:%S}"), ("Value", "@value")], formatters={"@time": "datetime"})
p.add_tools(hover)

# Set up the layout
curdoc().add_root(column(falc, value_paragraph, Time_paragraph, p,pop_up_message))


#bokeh serve --show real_plot.py
