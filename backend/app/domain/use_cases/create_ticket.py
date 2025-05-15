from datetime import datetime
from backend.app.domain.entities.ticket import Ticket
from backend.app.domain.repositories.ticket_repository import TicketRepository
from backend.app.domain.repositories.service_repository import ServiceRepository


class CreateTicket:
    def __init__(self, ticket_repo: TicketRepository, service_repo: ServiceRepository):
        self.ticket_repo = ticket_repo
        self.service_repo = service_repo

    def execute(self, service_id: int) -> Ticket:
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")

        queue_position = self.ticket_repo.get_queue_position(service_id) + 1
        estimated_wait_time = queue_position * 5  # Simplified: 5 min per position
        ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"

        ticket = Ticket(
            id=0,
            ticket_number=ticket_number,
            service_id=service_id,
            status="waiting",
            created_at=datetime.now(),
            estimated_wait_time=estimated_wait_time,
            queue_position=queue_position
        )
        return self.ticket_repo.create(ticket)