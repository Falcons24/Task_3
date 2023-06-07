import csv  # import csv to get the data in the Excel sheet
import serial  # import serial to read the ports
import datetime  # import datetime to get the date and time of printing data.
from serial import SerialException
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Div
from bokeh.layouts import column
from bokeh.models import HoverTool

#to Use hover tool in the graph.
hover_tool = HoverTool(tooltips=[("time", "@time"), ("distance", "@distance")])

p = figure(x_axis_type='datetime', y_axis_label='distance', sizing_mode='stretch_width')
p.add_tools(hover_tool)  # Add hover tool to the plot

# To Name x-axis and y-axis
source = ColumnDataSource(data=dict(time=[], distance=[]))
p.line(x='time', y='distance', line_width=2, source=source)

# To display the popup message in the graph
message_text = Div(text="", width=200, height=100)

# For reading the port which is connected with baud rate 9600.
try:
    ser = serial.Serial('COM10', 9600)
except SerialException:
    message_text.text = "The port is not detected."  # To Display port is not detected in the graph and terminal.
    print("Port is disconnected.")

# To save the data printed in the terminal to a CSV file with time.
csv_filename = 'port.csv'
csv_file = open(csv_filename, 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'distance'])

def update_data():
    try:
        data = ser.readline().decode().strip()  # To read data from the serial port
        time = datetime.datetime.now()  # Get the current time
        distance = float(data)  # Convert the data to a float

        new_data = dict(time=[time], distance=[distance])
        source.stream(new_data, rollover=100)  # Stream the new data to the plot

        csv_writer.writerow([time, distance])  # Write the data to the CSV file
        csv_file.flush()  # Flush the buffer to ensure data is written immediately

        print(f"Time: {time}, distance: {distance}")  # Print the data in the terminal

        message_text.text = ""  # Clear the message text
    except SerialException:
        message_text.text = "The port is disconnected." # To display port is disconnected in the pop up
        print("Port is disconnected.") # To display in the terminal
    except KeyboardInterrupt:
        message_text.text = "Manually stopped printing data"
        print("Manually stopped printing data")  # Display "manually stopped printing data" when Ctrl+C is pressed.

# To change the title size, align the text to the center, move it to the right,
# change its color to red, and set the font to bold
title_div = "<div style='font-size: 20pt; text-align: center; margin-left: 50px; color: red; font-weight: bold;'>TEAM ASSAILING FALCONS</div>"

# Create the layout with the title, plot, message text, and dimensions
layout = column(Div(text=title_div), p, message_text, width=800, height=400, sizing_mode='scale_width')

# To update the data every second
curdoc().add_periodic_callback(update_data, 1000)

curdoc().title = "Real-time Serial Plot"
curdoc().add_root(layout)