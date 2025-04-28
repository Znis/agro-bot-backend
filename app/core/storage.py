import os
import logging
import random
import uuid
import cloudinary
import cloudinary.uploader
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cloudinary configuration from .env
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Initialize Cloudinary
cloudinary_configured = False
try:
    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        cloudinary_configured = True
        logger.info(f"Cloudinary client initialized for cloud: {CLOUDINARY_CLOUD_NAME}")
    else:
        logger.warning("Cloudinary credentials not found in environment variables. Using mock storage.")
except Exception as e:
    logger.error(f"Could not initialize Cloudinary client: {e}")

async def upload_image(file_data: BytesIO, filename: str) -> Dict[str, Any]:
    """Upload an image to Cloudinary and return URL."""
    if not cloudinary_configured:
        # If no Cloudinary configured, use mock storage
        return await mock_upload_image(filename)
    
    try:
        # Generate a unique folder for organization
        timestamp = datetime.now(UTC).strftime("%Y%m%d")
        folder = f"agro_bot/{timestamp}"
        
        # Generate a unique public_id
        unique_id = str(uuid.uuid4())[:8]
        file_base = filename.split('.')[0] if '.' in filename else filename
        public_id = f"{folder}/{file_base}_{unique_id}"
        
        # Upload to Cloudinary
        file_data.seek(0)
        upload_result = cloudinary.uploader.upload(
            file_data,
            public_id=public_id,
            folder=folder,
            overwrite=True,
            resource_type="image"
        )
        
        logger.info(f"Uploaded image to Cloudinary: {public_id}")
        
        return {
            "success": True,
            "filename": filename,
            "public_id": upload_result["public_id"],
            "url": upload_result["secure_url"],
            "timestamp": datetime.now(UTC),
            "resource_type": upload_result["resource_type"],
            "format": upload_result["format"]
        }
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def mock_upload_image(filename: str) -> Dict[str, Any]:
    """Mock image upload when Cloudinary is not available."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    mock_url = f"https://mock-cloudinary.example.com/agro_bot/{timestamp}/{filename}_{unique_id}"
    
    logger.info(f"Mock: Uploaded image {filename} to mock storage")
    
    return {
        "success": True,
        "filename": filename,
        "public_id": f"mock_images/{timestamp}/{filename}_{unique_id}",
        "url": mock_url,
        "mock": True,
        "timestamp": datetime.now(UTC),
        "resource_type": "image",
        "format": filename.split('.')[-1] if '.' in filename else "jpg"
    }

async def generate_mock_plant_image(row: int, col: int, has_issue: bool = False, 
                                    issue_type: Optional[str] = None) -> Dict[str, Any]:
    """Generate a mock plant image for demonstration."""
    try:
        # Create a new image with a green or problematic background
        width, height = 400, 300
        img = Image.new('RGB', (width, height), color = 'green' if not has_issue else 'yellowgreen')
        draw = ImageDraw.Draw(img)
        
        # Draw grid coordinates
        draw.text((10, 10), f"Slot ({row+1},{col+1})", fill=(255, 255, 255))
        
        # Draw timestamp
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, 30), f"Time: {timestamp}", fill=(255, 255, 255))
        
        # Draw plant-like shape
        center_x, center_y = width // 2, height // 2
        
        # Draw stem
        draw.rectangle([center_x-5, center_y, center_x+5, center_y+100], fill=(101, 67, 33))
        
        # Draw leaves
        draw.ellipse([center_x-50, center_y-20, center_x+50, center_y+30], fill=(0, 100, 0))
        
        # If there's an issue, draw the issue
        if has_issue:
            if issue_type == "pest":
                # Draw some "pests"
                for _ in range(5):
                    x = random.randint(center_x-60, center_x+60)
                    y = random.randint(center_y-30, center_y+40)
                    draw.ellipse([x-5, y-5, x+5, y+5], fill=(0, 0, 0))
            
            elif issue_type == "disease":
                # Draw "disease" spots
                for _ in range(7):
                    x = random.randint(center_x-60, center_x+60)
                    y = random.randint(center_y-30, center_y+40)
                    draw.ellipse([x-8, y-8, x+8, y+8], fill=(139, 69, 19))
            
            elif issue_type == "growth_problem":
                # Draw wilting leaves
                draw.ellipse([center_x-50, center_y-20, center_x+50, center_y+30], fill=(107, 142, 35))
            
            # Draw issue label
            draw.text((10, 50), f"Issue: {issue_type}", fill=(255, 0, 0))
        
        # Save to BytesIO
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Generate a filename
        filename = f"plant_slot_{row+1}_{col+1}_{timestamp.replace(' ', '_').replace(':', '-')}.jpg"
        
        # Use the upload function
        return await upload_image(img_byte_arr, filename)
        
    except Exception as e:
        logger.error(f"Error generating mock plant image: {e}")
        return {
            "success": False,
            "error": str(e)
        } 