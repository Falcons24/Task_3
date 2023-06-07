import serial.tools.list_ports  # Importing the serial.tools.list_ports module
import csv  # Importing the csv module
import datetime  # Importing the datetime module
import time  # Importing the time module
import streamlit as st  # Importing the streamlit module and aliasing it as 'st'
import plotly.graph_objects as go  # Importing the plotly.graph_objects module and aliasing it as 'go'

COLUMN_WIDTH = 30  # Constant representing the width of each column in the CSV file

csv_file_new = open("Output1.csv", "w", newline="")  # Opening the CSV file in write mode
csv_writer_new = csv.writer(csv_file_new)  # Creating a CSV writer object
csv_writer_new.writerow(["Log Number", "Local Time", "Elapsed Time", "Value"])  # Writing the column headers to the CSV file

try:
    SerialInstance_new = serial.Serial()  # Creating a new serial instance object
    SerialInstance_new.baudrate = 15200  # Setting the baudrate of the serial instance
    SerialInstance_new.port = "COM6"  # Setting the port of the serial instance
    SerialInstance_new.open()  # Opening the serial port connection
except serial.SerialException as e:
    st.error("Error: The port not detected")  # Displaying an error message in the Streamlit app
    error_message_new = "Error: The port  not detected"
    csv_writer_new.writerow(["", "", "", error_message_new])  # Writing an error message to the CSV file
    exit()  # Exiting the program
except KeyboardInterrupt:
    status_message_new = "Program terminated manually"
    print(status_message_new)
    csv_writer_new.writerow((status_message_new,))

data_new = []  # Creating an empty list to store data

stop_recording_new = False  # Variable to control the recording loop

st.title('Real-Time Data Visualization')  # Setting the title of the Streamlit app

graph_fig_new = go.Figure()  # Creating a new Plotly figure object
graph_fig_new.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')  # Updating the layout of the graph
graph_new = st.plotly_chart(graph_fig_new)  # Creating a new graph in the Streamlit app using Plotly

StartTime_new = time.time()  # Getting the start time of the program

try:
    while not stop_recording_new:  # Loop to continuously record data
        if SerialInstance_new.in_waiting:  # Checking if there is data available in the serial buffer
            Line_new = SerialInstance_new.readline().decode('utf-8').strip()  # Reading a line from the serial buffer and decoding it

            Counter_new = len(data_new) + 1  # Updating the counter variable
            CurrentTime_new = time.time()  # Getting the current time

            ElapsedTime_new = CurrentTime_new - StartTime_new  # Calculating the elapsed time
            LocalTime_new = datetime.datetime.now().strftime('%H:%M:%S')  # Getting the current local time
            Microseconds_new = int((ElapsedTime_new - int(ElapsedTime_new)) * 1000000)  # Calculating the microseconds part of the elapsed time
            ElapsedTimeString_new = f"{int(ElapsedTime_new/3600):02d}:{int(ElapsedTime_new/60)%60:02d}:{int(ElapsedTime_new)%60:02d}.{Microseconds_new:06d}"  # Formatting the elapsed time string

            row_new = [
                str(Counter_new).ljust(COLUMN_WIDTH),
                str(LocalTime_new).ljust(COLUMN_WIDTH),
                str(ElapsedTimeString_new).ljust(COLUMN_WIDTH),
                str(Line_new).ljust(COLUMN_WIDTH)
            ]  # Creating a row of data

            data_new.append(row_new)  # Appending the row to the data list

            csv_writer_new.writerow(row_new)  # Writing the row to the CSV file

            graph_fig_new = go.Figure()  # Creating a new Plotly figure object
            graph_fig_new.add_trace(go.Scatter(x=[row[2] for row in data_new], y=[row[3] for row in data_new], name='Value'))  # Adding a trace to the graph

            graph_fig_new.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')  # Updating the layout of the graph

            with graph_new:
                graph_new.plotly_chart(graph_fig_new, use_container_width=True)  # Updating the graph in the Streamlit app

except serial.SerialException as e:
    st.error("Error: Port disconnected")  # Displaying an error message in the Streamlit app
    error_message1_new = "Error: Port disconnected"
    csv_writer_new.writerow((error_message1_new))
    st.stop()

except KeyboardInterrupt:
    error_message_new = "Data recording stopped manually by user"
    csv_writer_new.writerow((error_message_new,))

finally:
    csv_file_new.close()  # Closing the CSV file
