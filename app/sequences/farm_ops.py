from fastapi import APIRouter, BackgroundTasks
import time
import random
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from app.core import (
    cnc, 
    soil_moisture, 
    grid_positions, 
    save_maintenance_cycle,
    save_soil_moisture_reading,
    get_maintenance_cycles,
    get_soil_moisture_history,
    save_planting_operation,
    generate_mock_plant_image
)
from app.models import WateringRequest, PlantingRequest, MaintenanceRequest

# Create a router for farming sequences
router = APIRouter(prefix="/sequences", tags=["farming_sequences"])

@router.post("/check-all-soil-moisture")
async def check_all_soil_moisture(background_tasks: BackgroundTasks):
    """Check soil moisture in every slot of the grid and return the readings."""
    results = {}
    
    # Move to home position first
    cnc.send_command_and_wait_response("G90 G0 X0 Y0 Z0")
    
    # Visit each slot in the grid
    for row in range(3):
        for col in range(3):
            # Move to the slot
            pos = grid_positions.get((row, col))
            if not pos:
                continue
                
            cnc.log(f"Moving to slot ({row+1}, {col+1})")
            cnc.send_command_and_wait_response(f"G90 G0 {pos}")
            
            # Lower moisture sensor (Z axis)
            cnc.send_command_and_wait_response("G90 G0 Z-10")
            
            # Simulate moisture reading (in a real system, this would read from a sensor)
            # Currently using the mock values from the server
            reading = soil_moisture.get((row, col), 0)
            results[(row, col)] = reading
            
            cnc.log(f"Slot ({row+1}, {col+1}) moisture: {reading}%")
            
            # Save the reading to MongoDB in background
            moisture_data = {
                "position": f"{row},{col}",
                "row": row,
                "col": col,
                "moisture": reading,
                "timestamp": datetime.now(UTC)
            }
            background_tasks.add_task(save_soil_moisture_reading, moisture_data)
            
            # Raise Z axis back up
            cnc.send_command_and_wait_response("G90 G0 Z0")
            
            # Small delay between movements
            time.sleep(1)
    
    # Return to home position
    cnc.send_command_and_wait_response("G90 G0 X0 Y0 Z0")
    
    return {"message": "Soil moisture check completed", "readings": results}

@router.post("/water-dry-slots")
async def water_dry_slots(request: WateringRequest, background_tasks: BackgroundTasks):
    """Water all slots with soil moisture below the specified threshold."""
    watered_slots = []
    
    # Check soil moisture in all slots first
    moisture_data = await check_all_soil_moisture(background_tasks=background_tasks)
    readings = moisture_data["readings"]
    
    # Find slots that need watering
    for position, moisture in readings.items():
        row, col = position
        if moisture < request.threshold:
            # Already at this position from the check
            cnc.log(f"Watering slot ({row+1}, {col+1}) with moisture {moisture}%")
            
            # Move to the slot
            pos = grid_positions.get((row, col))
            if not pos:
                continue
                
            cnc.send_command_and_wait_response(f"G90 G0 {pos}")
            
            # Lower watering mechanism
            cnc.send_command_and_wait_response("G90 G0 Z-5")
            
            # Simulate watering (in a real system, this would activate a pump)
            cnc.log(f"Watering slot ({row+1}, {col+1})...")
            time.sleep(2)  # Simulate watering time
            
            # Update moisture value (simulated)
            new_moisture = min(100, moisture + 40)  # Add 40% moisture, max 100
            soil_moisture[(row, col)] = new_moisture
            
            # Raise watering mechanism
            cnc.send_command_and_wait_response("G90 G0 Z0")
            
            watering_data = {
                "position": f"{row},{col}",
                "row": row,
                "col": col,
                "old_moisture": moisture,
                "new_moisture": new_moisture,
                "timestamp": datetime.now(UTC),
                "operation": "watering"
            }
            
            # Save to MongoDB
            background_tasks.add_task(save_planting_operation, watering_data)
            
            watered_slots.append({"position": (row+1, col+1), "old_moisture": moisture, "new_moisture": new_moisture})
    
    # Return to home position
    cnc.send_command_and_wait_response("G90 G0 X0 Y0 Z0")
    
    return {"message": f"Watering completed for {len(watered_slots)} slots", "watered_slots": watered_slots}


@router.post("/full-maintenance-cycle")
async def full_maintenance_cycle(request: MaintenanceRequest, background_tasks: BackgroundTasks):
    """Perform a full maintenance cycle: check all soil moisture, water dry slots, and check for growth issues."""
    results = {
        "stage": "starting",
        "soil_check": None,
        "watering": None,
        "issues_detected": [],
        "images": []
    }
    
    # Step 1: Check soil moisture
    cnc.log("Starting full maintenance cycle - Checking soil moisture")
    soil_data = await check_all_soil_moisture(background_tasks=background_tasks)
    results["soil_check"] = soil_data["readings"]
    results["stage"] = "soil_check_completed"
    
    # Step 2: Water dry slots
    cnc.log("Maintenance cycle - Watering dry slots")
    watering_request = WateringRequest(threshold=request.watering_threshold)
    watering_data = await water_dry_slots(watering_request, background_tasks=background_tasks)
    results["watering"] = watering_data["watered_slots"]
    results["stage"] = "watering_completed"
    
    # Step 3: Visual inspection of each slot (simulated)
    cnc.log("Maintenance cycle - Performing visual inspection")
    
    for row in range(3):
        for col in range(3):
            # Move to the slot
            pos = grid_positions.get((row, col))
            if not pos:
                continue
                
            cnc.log(f"Inspecting slot ({row+1}, {col+1})")
            cnc.send_command_and_wait_response(f"G90 G0 {pos}")
            
            # Lower camera/sensor
            cnc.send_command_and_wait_response("G90 G0 Z-8")
            
            # Simulate visual inspection (in a real system, this would use a camera)
            time.sleep(1)
            
            # Random chance to detect an issue (simulated)
            has_issue = random.random() < 0.2  # 20% chance to find an issue
            issue_type = None
            
            if has_issue:
                issue_type = random.choice(["pest", "disease", "growth_problem"])
                severity = random.randint(1, 5)
                results["issues_detected"].append({
                    "position": (row+1, col+1),
                    "issue": issue_type,
                    "severity": severity
                })
                cnc.log(f"Issue detected at ({row+1}, {col+1}): {issue_type}")
            
            # Generate a mock plant image
            image_data = await generate_mock_plant_image(row, col, has_issue, issue_type)
            if image_data["success"]:
                results["images"].append({
                    "position": (row+1, col+1),
                    "url": image_data["url"],
                    "has_issue": has_issue,
                    "issue_type": issue_type
                })
            
            # Raise camera/sensor
            cnc.send_command_and_wait_response("G90 G0 Z0")
    
    # Return to home position
    cnc.send_command_and_wait_response("G90 G0 X0 Y0 Z0")
    results["stage"] = "completed"
    
    # Save the entire maintenance cycle data to MongoDB
    maintenance_data = {
        "timestamp": datetime.now(UTC),
        "soil_moisture": results["soil_check"],
        "watering": results["watering"],
        "issues_detected": results["issues_detected"],
        "images": [img["url"] for img in results["images"]]
    }
    
    doc_id = await save_maintenance_cycle(maintenance_data)
    results["maintenance_id"] = doc_id
    
    return results

@router.get("/maintenance-history")
async def get_maintenance_history(limit: int = 10, skip: int = 0):
    """Get the history of maintenance cycles."""
    cycles = await get_maintenance_cycles(limit=limit, skip=skip)
    return {"maintenance_cycles": cycles}

@router.get("/moisture-history")
async def get_moisture_history(row: Optional[int] = None, col: Optional[int] = None, limit: int = 50):
    """Get the history of soil moisture readings for a specific slot or all slots."""
    readings = await get_soil_moisture_history(slot_row=row, slot_col=col, limit=limit)
    return {"moisture_history": readings} 