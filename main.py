import time
import random

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

data_stream = start_data_stream()
for value in data_stream:
    print(value)
    #ToDo do something with value
    ...