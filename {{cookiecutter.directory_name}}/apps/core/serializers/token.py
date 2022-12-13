from uuid import UUID

from porcupine.base import Serializer


class TokenSerializer:
    class Base(Serializer):
        token: UUID

        @staticmethod
        def resolve_token(token, **kwargs) -> UUID:
            return token.id
