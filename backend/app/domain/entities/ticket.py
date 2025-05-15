from dataclasses import dataclass
from datetime import datetime

@dataclass
class Ticket:
    id: int
    ticket_number: str
    service_id: int
    status: str
    created_at: datetime
    estimated_wait_time: float
    queue_position: int