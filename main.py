import time
import random
import matplotlib.pyplot as plt

# Simulating data stream 
def add_extreme_noise(value, anomaly_factor_range=(5, 10)):
    # Create an extreme anomaly by multiplying the value by a large factor (5x to 10x by default)
    anomaly_factor = random.uniform(*anomaly_factor_range)
    return value * anomaly_factor  # Return value with extreme noise applied

def get_seasonal_multiplier():
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
        # ToDo round the value?
        yield value

        # Sleep for half a second 
        time.sleep(0.5)

# Starting data stream simulation
data_stream = start_data_stream()

# Visualization setup
plt.ion()  # Turn on interactive mode for live updates
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2, color='black') # Create an empty line object that we will update with new data
ax.set_xlim(0, 100)
ax.set_ylim(0, 12000)  
ax.set_xlabel('Transactions')  # Label for the x-axis
ax.set_ylabel('Value')         # Label for the y-axis
ax.set_title('Real-Time Data Stream with Anomalies')  # Title of the plot

x_data = []
y_data = []

# Anomalies detection
for index, value in enumerate(data_stream):
    anomaly = False
    print(value)
    #ToDo do something with value (if anomaly -> anomaly = Talse)
    ...
    # Update the data for plotting
    x_data.append(index)
    y_data.append(value)

    # Update the plot
    line.set_data(x_data, y_data) # Update the plot with the new data
    ax.scatter(x_data, y_data, color='red' if anomaly else 'green', s=50 if anomaly else 20, edgecolor='black', zorder=2)  # Add circle markers
    ax.relim() # Adjust axis limits based on new data
    ax.autoscale_view() # Automatically rescale the plot to fit the new data

    plt.draw() # Redraw the updated plot
    plt.pause(0.01)  # Pause to allow for the plot update

    # Limit the x-axis to show the last 100 data points for better visualization
    if len(x_data) > 100:
        ax.set_xlim(index - 100, index)  # Shift x-axis to the right

        # only keep the last 100 points to make the x-axis range more manageable
        x_data = x_data[-100:]
        y_data = y_data[-100:]

    # Visualization 
    # plt.plot(index, value)
    # animation = FuncAnimation(plt.gcf(), interval = 1000, frames = 500, repeat = False)

# ! will never get to this line  
# plt.ioff()  # Turn off interactive mode
# plt.show()
