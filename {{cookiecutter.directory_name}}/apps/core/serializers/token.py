from uuid import UUID

from pydantic import Field

from apps.core.serializers import Serializer


class TokenSerializer:
    class Base(Serializer):
        id: UUID = Field(serialization_alias='token')
