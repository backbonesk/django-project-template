from typing import Optional
from uuid import UUID
from datetime import datetime

from apps.core.serializers import Serializer


class UserSerializer:
    class Base(Serializer):
        id: UUID
        email: str
        name: str
        surname: str
        last_login: Optional[datetime]
        created_at: datetime

    class Detail(Base):
        is_active: bool

    class Me(Detail):
        pass
