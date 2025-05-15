from flask_sqlalchemy import SQLAlchemy
from backend.app.domain.entities.ticket import Ticket
from backend.app.domain.entities.service import Service
from backend.app.domain.repositories.ticket_repository import TicketRepository
from backend.app.domain.repositories.service_repository import ServiceRepository
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

class PostgresTicketRepository(TicketRepository):
    def create(self, ticket: Ticket) -> Ticket:
        db_ticket = {
            'ticket_number': ticket.ticket_number,
            'service_id': ticket.service_id,
            'status': ticket.status,
            'created_at': ticket.created_at,
            'estimated_wait_time': ticket.estimated_wait_time,
            'queue_position': ticket.queue_position
        }
        try:
            result = db.session.execute(
                db.text("INSERT INTO tickets (ticket_number, service_id, status, created_at, estimated_wait_time, queue_position) VALUES (:ticket_number, :service_id, :status, :created_at, :estimated_wait_time, :queue_position) RETURNING id"),
                db_ticket
            )
            ticket.id = result.fetchone()[0]
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to create ticket: {str(e)}")
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket:
        try:
            result = db.session.execute(
                db.text("SELECT * FROM tickets WHERE id = :id"),
                {'id': ticket_id}
            ).fetchone()
            if not result:
                return None
            return Ticket(
                id=result.id,
                ticket_number=result.ticket_number,
                service_id=result.service_id,
                status=result.status,
                created_at=result.created_at,
                estimated_wait_time=result.estimated_wait_time,
                queue_position=result.queue_position
            )
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to retrieve ticket: {str(e)}")

    def get_queue_position(self, service_id: int) -> int:
        try:
            result = db.session.execute(
                db.text("SELECT COUNT(*) FROM tickets WHERE service_id = :service_id AND status = 'waiting'"),
                {'service_id': service_id}
            ).fetchone()
            return result[0]
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to get queue position: {str(e)}")

    def cancel(self, ticket_id: int):
        try:
            db.session.execute(
                db.text("UPDATE tickets SET status = 'cancelled' WHERE id = :id"),
                {'id': ticket_id}
            )
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to cancel ticket: {str(e)}")

    def update_wait_time(self, ticket_id: int, estimated_wait_time: float, queue_position: int):
        try:
            db.session.execute(
                db.text("UPDATE tickets SET estimated_wait_time = :estimated_wait_time, queue_position = :queue_position WHERE id = :id"),
                {'id': ticket_id, 'estimated_wait_time': estimated_wait_time, 'queue_position': queue_position}
            )
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to update wait time: {str(e)}")

    def get_all_active(self):
        try:
            result = db.session.execute(
                db.text("SELECT t.*, s.name as service_name FROM tickets t JOIN services s ON t.service_id = s.id WHERE t.status = 'waiting'")
            )
            return [Ticket(
                id=row.id,
                ticket_number=row.ticket_number,
                service_id=row.service_id,
                status=row.status,
                created_at=row.created_at,
                estimated_wait_time=row.estimated_wait_time,
                queue_position=row.queue_position
            ) for row in result]
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to retrieve active tickets: {str(e)}")

class PostgresServiceRepository(ServiceRepository):
    def create(self, service: Service) -> Service:
        try:
            result = db.session.execute(
                db.text("INSERT INTO services (name) VALUES (:name) RETURNING id"),
                {'name': service.name}
            )
            service.id = result.fetchone()[0]
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to create service: {str(e)}")
        return service

    def get_by_id(self, service_id: int) -> Service:
        try:
            result = db.session.execute(
                db.text("SELECT * FROM services WHERE id = :id"),
                {'id': service_id}
            ).fetchone()
            if not result:
                return None
            return Service(id=result.id, name=result.name)
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to retrieve service: {str(e)}")

    def get_all(self):
        try:
            result = db.session.execute(db.text("SELECT * FROM services"))
            return [Service(id=row.id, name=row.name) for row in result]
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to retrieve services: {str(e)}")

    def delete(self, service_id: int):
        try:
            db.session.execute(
                db.text("DELETE FROM services WHERE id = :id"),
                {'id': service_id}
            )
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete service: {str(e)}")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        with db.engine.connect() as connection:
            try:
                connection.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS services (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS tickets (
                        id SERIAL PRIMARY KEY,
                        ticket_number VARCHAR(50) NOT NULL,
                        service_id INTEGER REFERENCES services(id),
                        status VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        estimated_wait_time FLOAT NOT NULL,
                        queue_position INTEGER NOT NULL
                    );
                """))
                connection.commit()
            except SQLAlchemyError as e:
                connection.rollback()
                raise ValueError(f"Failed to initialize database: {str(e)}")