from flask import Blueprint, request, jsonify, send_file
from backend.app.domain.repositories.ticket_repository import TicketRepository
from backend.app.domain.repositories.service_repository import ServiceRepository
from backend.app.domain.use_cases.create_ticket import CreateTicket
from backend.app.domain.use_cases.cancel_ticket import CancelTicket
from backend.app.domain.use_cases.get_queue_status import GetQueueStatus
from backend.app.domain.use_cases.create_service import CreateService
from backend.app.domain.use_cases.delete_service import DeleteService
from backend.app.infrastructure.database.postgres_repository import PostgresTicketRepository, PostgresServiceRepository
import qrcode
import io

api_bp = Blueprint('api', __name__)

ticket_repo = PostgresTicketRepository()
service_repo = PostgresServiceRepository()

def require_api_key(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        print(f"Received API Key: {api_key}")
        if api_key != 'admin-key':
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/qr', methods=['GET'])
def generate_qr():
    qr_url = 'http://localhost:5000/visitor.html'
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

@api_bp.route('/services', methods=['GET'])
def get_services():
    print("Fetching all services")
    services = service_repo.get_all()
    return jsonify([{"id": s.id, "name": s.name} for s in services])

@api_bp.route('/services', methods=['POST'], endpoint='create_service')
@require_api_key
def create_service():
    data = request.get_json()
    print(f"Received service creation request: {data}")
    try:
        use_case = CreateService(service_repo)
        service = use_case.execute(data['name'])
        print(f"Service created: {service.id} - {service.name}")
        return jsonify({"id": service.id, "name": service.name}), 201
    except Exception as e:
        print(f"Error creating service: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/services/<int:service_id>', methods=['DELETE'], endpoint='delete_service')
@require_api_key
def delete_service(service_id):
    use_case = DeleteService(service_repo)
    use_case.execute(service_id)
    return jsonify({"message": "Service deleted"}), 200

@api_bp.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    use_case = CreateTicket(ticket_repo, service_repo)
    ticket = use_case.execute(data['service_id'])
    service = service_repo.get_by_id(ticket.service_id)
    return jsonify({
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "service_name": service.name,
        "status": ticket.status,
        "estimated_wait_time": ticket.estimated_wait_time,
        "queue_position": ticket.queue_position
    }), 201

@api_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = ticket_repo.get_by_id(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    queue_position = ticket_repo.get_queue_position(ticket.service_id)
    ticket.estimated_wait_time = queue_position * 5
    ticket.queue_position = queue_position
    ticket_repo.update_wait_time(ticket.id, ticket.estimated_wait_time, ticket.queue_position)
    service = service_repo.get_by_id(ticket.service_id)
    return jsonify({
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "service_name": service.name,
        "status": ticket.status,
        "estimated_wait_time": ticket.estimated_wait_time,
        "queue_position": ticket.queue_position
    })

@api_bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id):
    use_case = CancelTicket(ticket_repo)
    use_case.execute(ticket_id)
    return jsonify({"message": "Ticket cancelled"}), 200

@api_bp.route('/queue', methods=['GET'])
def get_queue():
    use_case = GetQueueStatus(ticket_repo, service_repo)
    queue_data = use_case.execute()
    return jsonify(queue_data)