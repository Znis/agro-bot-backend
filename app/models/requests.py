from pydantic import BaseModel
from typing import List, Optional

class CommandRequest(BaseModel):
    command: str

class JogRequest(BaseModel):
    direction: str

class SlotMoveRequest(BaseModel):
    slot_row: int
    slot_col: int
    
class WateringRequest(BaseModel):
    threshold: Optional[int] = 30
    
class MaintenanceRequest(BaseModel):
    watering_threshold: Optional[int] = 30 