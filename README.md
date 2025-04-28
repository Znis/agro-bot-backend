# Agro-Bot: CNC-Based Farming System

This project provides control for a CNC-based farming system designed for automated grid-based farming operations. The backend is built with FastAPI and handles communication with CNC hardware via serial connection.

## System Features

- **Grid-Based Layout**: The farming area is organized in a 3x3 grid system.
- **CNC Control**: Direct G-code commands to control the CNC machine's X, Y, Z axes.
- **Soil Moisture Monitoring**: Check moisture levels at each grid position.
- **Watering Automation**: Water plants based on soil moisture readings.
- **Maintenance Cycles**: Complete cycles for checking and maintaining crops.
- **Data Persistence**: MongoDB integration for storing historical data.
- **Image Storage**: Cloudinary integration for storing plant images.

## Project Structure

```
agro-bot-backend/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   │   ├── __init__.py
│   │   └── basic.py        # Basic CNC control endpoints
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── cnc.py          # CNC machine connection
│   │   ├── database.py     # MongoDB integration
│   │   ├── grid.py         # Grid and soil data
│   │   └── storage.py      # Cloudinary integration
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   └── requests.py     # Request models
│   ├── sequences/          # Farming sequences
│   │   ├── __init__.py
│   │   └── farm_ops.py     # Farming operations
│   └── __init__.py         # App factory
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Farming Sequence APIs

### Check Soil Moisture

```
POST /sequences/check-all-soil-moisture
```

Moves the CNC machine to each slot in the grid, lowers the moisture sensor, takes a reading, and returns the moisture levels for all slots. All readings are stored in MongoDB for historical tracking.

### Water Dry Slots

```
POST /sequences/water-dry-slots
```

Checks all slots for moisture and waters those below the specified threshold (default 30%).

Request Body:
```json
{
  "threshold": 30
}
```

### Full Maintenance Cycle

```
POST /sequences/full-maintenance-cycle
```

Performs a complete maintenance cycle:
1. Checks soil moisture in all slots
2. Waters dry slots based on the threshold
3. Performs visual inspection for issues (pests, diseases, growth problems)
4. Generates mock plant images and simulates storing them in CloudFront
5. Stores all data in MongoDB

Request Body:
```json
{
  "watering_threshold": 30
}
```

### Get Maintenance History

```
GET /sequences/maintenance-history?limit=10&skip=0
```

Retrieves the history of maintenance cycles from MongoDB.

Parameters:
- `limit` (optional): Maximum number of cycles to return (default 10)
- `skip` (optional): Number of records to skip for pagination (default 0)

### Get Moisture History

```
GET /sequences/moisture-history?row=0&col=0&limit=50
```

Retrieves the history of soil moisture readings from MongoDB.

Parameters:
- `row` (optional): Specific row to filter by
- `col` (optional): Specific column to filter by
- `limit` (optional): Maximum number of readings to return (default 50)

## Basic CNC Control APIs

### Check Connection Status

```
GET /status
```

Checks if the CNC machine is connected and ready to receive commands.

Response:
```json
{
  "online": true,
  "message": "CNC machine is connected and ready"
}
```

### Current Position

```
GET /position
```

Returns the current position of the CNC machine.

### Send G-code Command

```
POST /send-command
```

Body:
```json
{
  "command": "G90 G0 X10 Y10 Z0"
}
```

Sends a raw G-code command to the CNC machine.

### Jog Movement

```
POST /jog
```

Body:
```json
{
  "direction": "X10"
}
```

Performs a relative movement in the specified direction.

### Move to Grid Slot

```
POST /move-to-slot
```

Body:
```json
{
  "slot_row": 0,
  "slot_col": 0
}
```

Moves to a specific slot in the grid.

## Setup and Running

1. Install dependencies:
   ```
   pip install -r agro-bot-backend/requirements.txt
   ```

2. Configure MongoDB and Cloudinary:
   Create a `.env` file in the agro-bot-backend directory with your MongoDB and Cloudinary credentials:
   ```
   # MongoDB Connection
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/agro_bot?retryWrites=true&w=majority
   MONGO_DB_NAME=agro_bot
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```
   
   Note: If you don't provide these credentials, the application will log warnings but will still function without external services.

3. Run the FastAPI server:
   ```
   cd agro-bot-backend
   python main.py
   ```

   Or use the start script that creates an ngrok tunnel:
   ```
   cd agro-bot-backend
   chmod +x start.sh
   ./start.sh
   ```
   
   To use a custom ngrok domain, add the following to your .env file:
   ```
   NGROK_DOMAIN=your-subdomain.ngrok-free.app
   ```

4. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Hardware Requirements

- CNC machine with USB serial connection
- Sensors for soil moisture detection
- Watering mechanism
- Planting mechanism 
- Camera/sensor for visual inspection

## API Usage Examples

**Check moisture and water dry slots:**

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# First check moisture levels
moisture_response = requests.post(f"{base_url}/sequences/check-all-soil-moisture")
print("Moisture readings:", moisture_response.json())

# Then water dry slots with threshold of 35%
watering_payload = {"threshold": 35}
watering_response = requests.post(f"{base_url}/sequences/water-dry-slots", json=watering_payload)
print("Watering results:", watering_response.json())
```

**Perform full maintenance cycle:**

```python
import requests

payload = {"watering_threshold": 30}
response = requests.post("http://localhost:8000/sequences/full-maintenance-cycle", json=payload)
print("Maintenance cycle results:", response.json())
```

**Retrieve historical data:**

```python
import requests

# Get maintenance history
history_response = requests.get("http://localhost:8000/sequences/maintenance-history?limit=5")
print("Recent maintenance cycles:", history_response.json())

# Get moisture history for a specific slot
slot_moisture = requests.get("http://localhost:8000/sequences/moisture-history?row=1&col=1")
print("Moisture history for slot (2,2):", slot_moisture.json())
``` 