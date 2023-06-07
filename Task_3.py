import serial.tools.list_ports
import csv
import datetime
import time
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

COLUMN_WIDTH = 30

# Open a CSV file for writing
csv_file = open("Output.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Log Number", "Local Time", "Elapsed Time", "Value"])

try:
    SerialInstance = serial.Serial()
    SerialInstance.baudrate = 9600
    SerialInstance.port = "COM5"
    SerialInstance.open()
except serial.SerialException:
    st.error("Error: The port was not detected")
    csv_writer.writerow(["Error: The port was not detected"])
    exit()
except KeyboardInterrupt:
    st.info("Data recording stopped manually by user")
    csv_writer.writerow(["Data recording stopped manually by user"])
    stop_recording = True

data = {
    'Log Number': [],
    'Local Time': [],
    'Elapsed Time': [],
    'Value': []
}

stop_recording = False

# Set up the Streamlit application title and initial graph
st.title('Plotting live data')

graph_fig = go.Figure()
graph_fig.update_layout(title='Real-Time Data', xaxis_title='Time', yaxis_title='Value')
graph = st.plotly_chart(graph_fig)

# Start time for calculating elapsed time
StartTime = time.time()

while not stop_recording:
    try:
        if SerialInstance.in_waiting:
            Line = SerialInstance.readline().decode('utf-8').strip()

            Counter = len(data['Log Number']) + 1
            CurrentTime = time.time()
            
            ElapsedTime = CurrentTime - StartTime
            LocalTime = datetime.datetime.now().strftime('%H:%M:%S')
            Microseconds = int((ElapsedTime - int(ElapsedTime)) * 1000000)
            ElapsedTimeString = f"{int(ElapsedTime/3600):02d}:{int(ElapsedTime/60)%60:02d}:{int(ElapsedTime)%60:02d}.{Microseconds:06d}"

            # Append data to the dictionary
            data['Log Number'].append(str(Counter).ljust(COLUMN_WIDTH))
            data['Local Time'].append(str(LocalTime).ljust(COLUMN_WIDTH))
            data['Elapsed Time'].append(str(ElapsedTimeString).ljust(COLUMN_WIDTH))
            data['Value'].append(str(Line).ljust(COLUMN_WIDTH))

            # Write data to the CSV file
            csv_writer.writerow([str(Counter).ljust(COLUMN_WIDTH),
                                 str(LocalTime).ljust(COLUMN_WIDTH),
                                 str(ElapsedTimeString).ljust(COLUMN_WIDTH),
                                 str(Line).ljust(COLUMN_WIDTH)])

            # Create a DataFrame from the data dictionary
            df = pd.DataFrame(data)

            # Create a new plotly Figure
            graph_fig = go.Figure()
            graph_fig.add_trace(go.Scatter(x=df['Elapsed Time'], y=df['Value'], name='Value'))

            # Update the plotly layout
            graph_fig.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')

            time.sleep(0.1)
            
            # Update the Streamlit graph with the new plotly Figure
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

# Close the serial connection and the CSV file
SerialInstance.close()
csv_file.close()
