from backend.app.domain.repositories.ticket_repository import TicketRepository


class CancelTicket:
    def __init__(self, ticket_repo: TicketRepository):
        self.ticket_repo = ticket_repo

    def execute(self, ticket_id: int):
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        if ticket.status == "cancelled":
            raise ValueError("Ticket already cancelled")
        self.ticket_repo.cancel(ticket_id)