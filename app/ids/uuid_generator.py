import uuid
from app.ports.services.id_generator_port import IdGeneratorPort


class IdGenerator(IdGeneratorPort):
    def new_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex}"
