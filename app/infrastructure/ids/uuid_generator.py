import uuid

from app.ports.services.id_generator_port import IdGeneratorPort


class UuidGenerator(IdGeneratorPort):
    def new_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"