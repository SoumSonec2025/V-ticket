from backend.app.domain.repositories.service_repository import ServiceRepository


class DeleteService:
    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo

    def execute(self, service_id: int):
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        self.service_repo.delete(service_id)