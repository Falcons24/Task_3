import serial.tools.list_ports
import csv
import datetime
import time
import streamlit as st
import plotly.graph_objects as go
import keyboard

COLUMN_WIDTH = 30

csv_file = open("Output1.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Log Number", "Local Time", "Elapsed Time", "Value"])

try:
    SerialInstance = serial.Serial()
    SerialInstance.baudrate = 9600
    SerialInstance.port = "COM5"
    SerialInstance.open()
except serial.SerialException as e:
    st.error("Error: The port was not detected")
    error_message = "Error: The port was not detected"
    csv_writer.writerow(["", "", "", error_message])
    exit()
except KeyboardInterrupt:
    status_message = "Program terminated manually by user"
    print(status_message)
    csv_writer.writerow([status_message])

data = []
instant_data = []

stop_recording = False

st.title('Real-Time Data Visualization')

graph_fig = go.Figure()
graph_fig.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')
graph = st.plotly_chart(graph_fig)

StartTime = time.time()

try:
    while not stop_recording:
        if keyboard.is_pressed('r'):
            instant_data = list(data) 

        if SerialInstance.in_waiting:
            Line = SerialInstance.readline().decode('utf-8').strip()

            Counter = len(data) + 1
            CurrentTime = time.time()

            ElapsedTime = CurrentTime - StartTime
            LocalTime = datetime.datetime.now().strftime('%H:%M:%S')
            Microseconds = int((ElapsedTime - int(ElapsedTime)) * 1000000)
            ElapsedTimeString = f"{int(ElapsedTime/3600):02d}:{int(ElapsedTime/60)%60:02d}:{int(ElapsedTime)%60:02d}.{Microseconds:06d}"

            row = [
                str(Counter).ljust(COLUMN_WIDTH),
                str(LocalTime).ljust(COLUMN_WIDTH),
                str(ElapsedTimeString).ljust(COLUMN_WIDTH),
                str(Line).ljust(COLUMN_WIDTH)
            ]

            data.append(row)

            csv_writer.writerow(row)

            graph_fig = go.Figure()
            graph_fig.add_trace(go.Scatter(x=[row[2] for row in data], y=[row[3] for row in data], name='Value'))

            graph_fig.update_layout(title='Real-Time Data', xaxis_title='Log Number', yaxis_title='Value')

            with graph:
                graph.plotly_chart(graph_fig, use_container_width=True)

    # Add the instant data to CSV file when 'r' is pressed
    if instant_data:
        csv_writer.writerow(["POR-", "", "", ""])
        for row in instant_data:
            csv_writer.writerow(row)

except serial.SerialException as e:
    st.error("Error: Arduino disconnected or not found")
    error_message1 = "Error: Arduino disconnected or not found"
    csv_writer.writerow([error_message1])
    st.stop()

except KeyboardInterrupt:
    error_message = "Data recording stopped manually by user"
    csv_writer.writerow([error_message])

finally:
    csv_file.close()