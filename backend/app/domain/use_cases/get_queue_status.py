from backend.app.domain.repositories.service_repository import ServiceRepository
from backend.app.domain.repositories.ticket_repository import TicketRepository


class GetQueueStatus:
    def __init__(self, ticket_repo: TicketRepository, service_repo: ServiceRepository):
        self.ticket_repo = ticket_repo
        self.service_repo = service_repo

    def execute(self):
        tickets = self.ticket_repo.get_all_active()
        # Recalculate wait times for all active tickets
        for ticket in tickets:
            queue_position = self.ticket_repo.get_queue_position(ticket.service_id)
            ticket.estimated_wait_time = queue_position * 5  # 5 min per position
            ticket.queue_position = queue_position
            self.ticket_repo.update_wait_time(ticket.id, ticket.estimated_wait_time, ticket.queue_position)

        total_tickets = len(tickets)
        avg_wait_time = sum(t.estimated_wait_time for t in tickets) / total_tickets if total_tickets > 0 else 0

        queue_data = {
            "tickets": [
                {
                    "ticket_number": t.ticket_number,
                    "service_name": self.service_repo.get_by_id(t.service_id).name,
                    "status": t.status,
                    "estimated_wait_time": t.estimated_wait_time
                } for t in tickets
            ],
            "stats": {
                "total_tickets": total_tickets,
                "avg_wait_time": round(avg_wait_time, 2)
            }
        }
        return queue_data