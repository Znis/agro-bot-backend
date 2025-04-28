import random

# --- Planting Grid Positions ---
grid_positions = {
    (0, 0): "X3 Y2", (0, 1): "X3 Y9", (0, 2): "X3 Y15 Z-50",
    (1, 0): "X20 Y2", (1, 1): "X20 Y9", (1, 2): "X20 Y15",
    (2, 0): "X38 Y2", (2, 1): "X38 Y9", (2, 2): "X38 Y15"
}

# Initialize soil moisture with random values
soil_moisture = {(row, col): random.randint(20, 80) for row in range(3) for col in range(3)}

def update_soil_moisture_data():
    """Update all soil moisture values with random data (for simulation)"""
    for row in range(3):
        for col in range(3):
            soil_moisture[(row, col)] = random.randint(20, 80)
    return soil_moisture 