from fastapi import APIRouter, HTTPException
from app.models import CommandRequest, JogRequest, SlotMoveRequest
from app.core import cnc, grid_positions, soil_moisture, update_soil_moisture_data

router = APIRouter(tags=["basic_controls"])

@router.get("/status")
def check_status():
    """Check if the CNC machine is connected and ready to receive commands."""
    is_connected = cnc.serial_conn is not None
    return {
        "online": is_connected,
        "message": "CNC machine is connected and ready" if is_connected else "CNC machine is not connected"
    }

@router.get("/position")
def get_position():
    """Get the current position of the CNC machine."""
    return cnc.position

@router.post("/send-command")
def send_command(request: CommandRequest):
    """Send a raw G-code command to the CNC machine."""
    response = cnc.send_command_and_wait_response(request.command)
    return {"status": "sent", "response": response}

@router.post("/jog")
def jog_move(jog: JogRequest):
    """Perform a relative movement in the specified direction."""
    response = cnc.send_command_and_wait_response(f"G91 G0 {jog.direction}")
    return {"message": f"Jogged {jog.direction}", "response": response}

@router.post("/move-to-slot")
def move_to_slot(slot: SlotMoveRequest):
    """Move to a specific slot in the grid."""
    pos = grid_positions.get((slot.slot_row, slot.slot_col))
    if not pos:
        raise HTTPException(status_code=404, detail="Invalid slot")
    response = cnc.send_command_and_wait_response(f"G90 G0 {pos}")
    return {"message": f"Moved to slot ({slot.slot_row+1}, {slot.slot_col+1})", "response": response}

@router.get("/soil-moisture")
def get_soil_moisture():
    """Get the current soil moisture readings for all slots."""
    return {"moisture": soil_moisture}

@router.post("/update-soil-moisture")
def update_soil_moisture():
    """Update soil moisture with random values (simulation)."""
    update_soil_moisture_data()
    cnc.log("Soil moisture updated!")
    return {"message": "Soil moisture updated."}

@router.get("/logs")
def get_logs():
    """Get the latest CNC machine logs."""
    return {"logs": cnc.logs[-50:]}  # last 50 logs 