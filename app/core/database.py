from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection details from .env
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "agro_bot")

# Initialize MongoDB client
client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB."""
    global client, db
    try:
        if not MONGO_URI:
            logger.warning("MONGO_URI not set in environment variables. MongoDB connection will not be established.")
            return
            
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        logger.info(f"Connected to MongoDB database: {DB_NAME}")
        
        # Create indexes
        await db.maintenance_cycles.create_index("timestamp")
        await db.soil_moisture.create_index("timestamp")
        await db.plant_operations.create_index("timestamp")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")

async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# Database operations for maintenance cycles
async def save_maintenance_cycle(data: Dict[str, Any]) -> str:
    """Save maintenance cycle data to MongoDB."""
    if not db:
        logger.error("Database not initialized")
        return None
    
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(UTC)
    
    try:
        result = await db.maintenance_cycles.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving maintenance cycle: {e}")
        return None

async def get_maintenance_cycles(limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
    """Get recent maintenance cycles."""
    if not db:
        logger.error("Database not initialized")
        return []
    
    try:
        cursor = db.maintenance_cycles.find().sort("timestamp", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as e:
        logger.error(f"Error retrieving maintenance cycles: {e}")
        return []

# Database operations for soil moisture
async def save_soil_moisture_reading(data: Dict[str, Any]) -> str:
    """Save soil moisture reading to MongoDB."""
    if not db:
        logger.error("Database not initialized")
        return None
    
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(UTC)
    
    try:
        result = await db.soil_moisture.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving soil moisture reading: {e}")
        return None

async def get_soil_moisture_history(slot_row: Optional[int] = None, slot_col: Optional[int] = None, 
                                    limit: int = 50) -> List[Dict[str, Any]]:
    """Get history of soil moisture readings, optionally filtered by slot."""
    if not db:
        logger.error("Database not initialized")
        return []
    
    query = {}
    if slot_row is not None and slot_col is not None:
        # Find the specific position
        query["position"] = f"{slot_row},{slot_col}"
    
    try:
        cursor = db.soil_moisture.find(query).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as e:
        logger.error(f"Error retrieving soil moisture history: {e}")
        return []

