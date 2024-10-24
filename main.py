import time
import random
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
import logging

# Configure logging to write to a file with appropriate format
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='anomaly_detection.log',  # Logs saved to this file
                    filemode='w')  # Overwrite the log file each time

"""
A Python script capable of detecting anomalies in a continuous data stream. 

This script simulates the real-time sequences of floating-point numbers. 
that data steam is passed to a code section that detects anomaly and, 
visualize the data with the detected anomalies.

Limitations:
the detection works after retraining the data(we occur after 100 transactions). 
Initial training with  historical data doesn't work for some reason
"""

# Simulating data stream 
def add_extreme_noise(value, anomaly_factor_range=(5, 10)):
    """
    Adds extreme noise the passed value and returns the modified vale

    Parameters:
    value (float): the normal value
    anomaly_factor_range (tuple with 2 values defaulted to (5, 10)): the noise range 

    Return:
    the passed value with the added noise
    """
    # Create an extreme anomaly by multiplying the value by a large factor (5x to 10x by default)
    anomaly_factor = random.uniform(*anomaly_factor_range)
    return value * anomaly_factor  # Return value with extreme noise applied

def get_seasonal_multiplier():
    """
    identifies and returns the seasonal multiplier depending on the current month

    Return:
    the seasonal multiplier depending on the current month
    """

    month = time.localtime().tm_mon
    # Seasonal multipliers based on the month
    if month in [12, 1, 2]:  # Winter
        return random.uniform(1.2, 1.5)  # Higher spending in winter (e.g., holidays)
    elif month in [3, 4, 5]:  # Spring
        return random.uniform(0.8, 1.2)  # Normal spending
    elif month in [6, 7, 8]:  # Summer
        return random.uniform(0.9, 1.3)  # Slightly higher spending in summer
    elif month in [9, 10, 11]:  # Fall
        return random.uniform(1.0, 1.4)  # Back-to-school and holidays in fall
    return 1.0  # Default multiplier

def start_data_stream():
    """
    Initialize the data stream were it will generate a value every half a second and yield it to the main process.
    The generated value follows a pattern and incorporate seasonal changes.
    Every now and then noise will be added to the generated value before it is passed simulating anomalies. 

    yield:
    the generated value
    """
    logging.info("Starting data stream simulation.")
    variation = 1000 # Value to vary up or down
    base_value = 0 # Base value for transactions

    while True:
        # Create a random transaction value with a seasonal pattern
        seasonal_multiplier = get_seasonal_multiplier()
        value = (base_value + random.uniform(0, variation)) * seasonal_multiplier

        # Introduce an extreme anomaly randomly with a certain probability
        if random.random() < 0.1:  # 10% chance to add noise
            # print ("noise added")
            value = add_extreme_noise(value)
        
        # Pass it to the data stream
        yield value

        # Sleep for half a second 
        time.sleep(0.5)

# Visualization setup
plt.ion()  # Turn on interactive mode for live updates
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2, color='black') # Create an empty line object that we will update with new data

# Starting data stream simulation
data_stream = start_data_stream()

x_data = []
y_data = []
anomaly_pred=[]

# Anomalies detection

# Create the model
model = IsolationForest(contamination=0.1)

# read csv of past transaction data to train the model
try: 
    csv_data = pd.read_csv('transaction_data.csv')
    data = csv_data['Transaction Value'].values
    model.fit(np.array(data).reshape(-1, 1))
    logging.info("Model training with initial data completed.")
except FileNotFoundError:
    logging.error("'transaction_data.csv' not found.")
except pd.errors.EmptyDataError:
    logging.error("The CSV file is empty.")
except Exception as e:
    logging.error(f"An error occurred while reading the CSV file: {e}")

for index, value in enumerate(data_stream):
    anomaly = False
    # Update the data for plotting
    x_data.append(index)
    y_data.append(value)

    # Predict anomalies
    try:
        anomaly = model.predict(np.array([[value]]))  # Predict for the current value
        anomaly = anomaly == -1  # Convert to boolean (True for anomaly)
        if anomaly:
            logging.info(f"Anomaly detected at index {index} with value: {value}")
        else:
            logging.info(f"Normal value at index {index}: {value}")
    except ValueError as e:
        logging.error(f"Error during anomaly prediction: {e}")
    
    # To adapt to seasonal changes -> train the model every new 100 transactions with just their values to avoid duplicates
    if (index % 100 == 0): 
        # Reshape for model input
        try:
            model.fit(np.array(y_data[-100:]).reshape(-1, 1))
        except ValueError as e:
            logging.error(f"Error during model training: {e}")
    anomaly_pred.append(anomaly)

    #Update the plot
    try:
        ax.relim() # Adjust axis limits based on new data
        ax.autoscale_view() # Automatically rescale the plot to fit the new data
        ax.clear()  # Clear only the axis content to redraw the plot
        ax.plot(x_data, y_data, lw=2, color='black')  # Main line plot

        # Plot all points, highlighting anomalies
        for i in range(len(x_data)):
            if anomaly_pred[i]:  # Use stored anomaly predictions
                ax.scatter(x_data[i], y_data[i], color='red', s=100, edgecolor='black', zorder=3)  # Anomaly
            else:
                ax.scatter(x_data[i], y_data[i], color='green', s=20, edgecolor='black', zorder=2)  # Normal point


        ax.set_xlim(max(0, index - 100), index)  # Adjust x-axis to show the last 100 points
        ax.set_ylim(0, 12000)  # Maintain y-axis limits
        ax.set_xlabel('Transactions')
        ax.set_ylabel('Value')
        ax.set_title('Real-Time Data Stream with Anomalies')

        plt.draw() # Redraw the updated plot
        plt.pause(0.01)  # Pause to allow for the plot update
    except Exception as e:
        logging.error(f"Error during plotting: {e}")

    # Limit the x-axis to show the last 100 data points for better visualization
    try:
        if len(x_data) > 100:
            ax.set_xlim(index - 100, index)  # Shift x-axis to the right

            # only keep the last 100 points to make the x-axis range more manageable
            x_data = x_data[-100:]
            y_data = y_data[-100:]
            anomaly_pred = anomaly_pred[-100:]
    except IndexError as e:
        logging.error(f"Index error while limiting x-axis data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while limiting x-axis: {e}")

