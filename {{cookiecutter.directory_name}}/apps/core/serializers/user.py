from uuid import UUID
from datetime import datetime

from porcupine.base import Serializer


class UserSerializer:
    class Base(Serializer):
        id: UUID
        email: str
        name: str
        surname: str
        last_login: datetime = None
        created_at: datetime

    class Detail(Base):
        pass

    class Me(Detail):
        pass
