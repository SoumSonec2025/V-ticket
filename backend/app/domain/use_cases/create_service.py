from backend.app.domain.entities.service import Service
from backend.app.domain.repositories.service_repository import ServiceRepository


class CreateService:
    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo

    def execute(self, name: str) -> Service:
        if not name or name.strip() == "":
            raise ValueError("Service name cannot be empty")
        service = Service(id=0, name=name.strip())
        return self.service_repo.create(service)