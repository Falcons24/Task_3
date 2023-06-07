import serial.tools.list_ports
import csv
import datetime
import time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

COLUMN_WIDTH = 30

# Open the CSV file for writing
csv_file = open("Output.csv", "w", newline="")
csv_writer = csv.writer(csv_file)

# Write the header row in the CSV file
csv_writer.writerow(["Log Number", "Local Time", "Elapsed Time", "Value"])

try:
    # Set up the serial connection
    SerialInstance = serial.Serial()
    SerialInstance.baudrate = 9600
    SerialInstance.port = "COM3"
    SerialInstance.open()
except serial.SerialException:
    st.error("Error: The port was not detected")
    csv_writer.writerow(["Error: The port was not detected"])
    exit()
except KeyboardInterrupt:
    st.info("Data recording stopped manually by user")
    csv_writer.writerow(["Data recording stopped manually by user"])
    stop_recording = True

# Dictionary to store the data
data = {
    'Log Number': [],
    'Local Time': [],
    'Elapsed Time': [],
    'Value': []
}

# Variable to control the loop
stop_recording = False

# Set up the Streamlit app and plotly chart
st.title('Real-Time Data Visualization')
graph_fig = go.Figure()
graph_fig.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')
graph = st.plotly_chart(graph_fig)

# Start time for calculating elapsed time
StartTime = time.time()

while not stop_recording:
    try:
        # Check if there is data available from the serial port
        if SerialInstance.in_waiting:
            # Read a line from the serial port and decode it
            Line = SerialInstance.readline().decode('utf-8').strip()

            # Count the number of data points received
            Counter = len(data['Log Number'])

            # Calculate elapsed time and local time
            CurrentTime = time.time()
            ElapsedTime = CurrentTime - StartTime
            LocalTime = datetime.datetime.now().strftime('%H:%M:%S')
            Microseconds = int((ElapsedTime - int(ElapsedTime)) * 1000000)
            ElapsedTimeString = f"{int(ElapsedTime/3600):02d}:{int(ElapsedTime/60)%60:02d}:{int(ElapsedTime)%60:02d}.{Microseconds:06d}"

            # Add the data to the dictionary and write to the CSV file
            data['Log Number'].append(str(Counter).ljust(COLUMN_WIDTH))
            data['Local Time'].append(str(LocalTime).ljust(COLUMN_WIDTH))
            data['Elapsed Time'].append(str(ElapsedTimeString).ljust(COLUMN_WIDTH))
            data['Value'].append(str(Line).ljust(COLUMN_WIDTH))

            csv_writer.writerow([str(Counter).ljust(COLUMN_WIDTH),
                                 str(LocalTime).ljust(COLUMN_WIDTH),
                                 str(ElapsedTimeString).ljust(COLUMN_WIDTH),
                                 str(Line).ljust(COLUMN_WIDTH)])

            # Create a DataFrame from the data dictionary
            df = pd.DataFrame(data)

            # Create a new plotly figure and update the layout
            graph_fig = go.Figure()
            graph_fig.add_trace(go.Scatter(x=df['Elapsed Time'], y=df['Value'], name='Value'))
            graph_fig.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')

            # Update the plotly chart in the Streamlit app
            with graph:
                graph.plotly_chart(graph_fig, use_container_width=True)

    except serial.SerialException:
        st.error("Error: Port disconnected")
        csv_writer.writerow(["Error: The port was not detected"])
        exit()
    except KeyboardInterrupt:
        st.info("Data recording stopped manually by user")
        csv_writer.writerow(["Data recording stopped manually by user"])
        stop_recording = True

# Close the CSV file
csv_file.close()
