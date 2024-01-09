from object_checker.base_object_checker import AbacChecker

from apps.core.models import User


class UserChecker(AbacChecker):
    @staticmethod
    def check_user_get(request_user: User, user: User, ):
        if not request_user != user:
            return False

        return True
