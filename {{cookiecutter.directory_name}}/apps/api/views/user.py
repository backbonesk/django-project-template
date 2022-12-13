from http import HTTPStatus
from uuid import UUID

from django.db import transaction
from django.utils.translation import gettext as _


from apps.api.views.base import SecuredView
from apps.api.errors import ValidationException, ProblemDetailException
from apps.api.filters.user import UserFilter
from apps.api.forms.user import UserForm
from apps.api.response import SingleResponse, PaginationResponse

from apps.core.models.user import User
from apps.core.serializers.user import UserSerializer


class UserManagement(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic
    def post(self, request):
        form = UserForm.Create.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(request, form)

        password = form.cleaned_data['password']

        user = User()
        form.populate(user)
        user.set_password(password)
        user.save()

        return SingleResponse(request, user, serializer=UserSerializer.Detail, status=HTTPStatus.CREATED)

    def get(self, request):
        users = UserFilter(request.GET, queryset=User.objects.all(), request=request).qs

        return PaginationResponse(request, users, serializer=UserSerializer.Base)


class UserDetail(SecuredView):
    @staticmethod
    def _get_user(request, user_id: UUID) -> User:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as e:
            raise ProblemDetailException(request, _('User not found.'), status=HTTPStatus.NOT_FOUND, previous=e)

        return user

    def get(self, request, user_id: UUID):
        user = self._get_user(request, user_id)

        return SingleResponse(request, user, serializer=UserSerializer.Detail)

    @transaction.atomic
    def put(self, request, user_id: UUID):
        form = UserForm.Update.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(request, form)

        user = self._get_user(request, user_id)

        if User.objects.filter(email=form.cleaned_data['email']).exclude(pk=user.id).exists():
            raise ProblemDetailException(
                request, _('User with the same email already exists.'), status=HTTPStatus.CONFLICT
            )

        form.populate(user)
        user.save()

        return SingleResponse(request, user, serializer=UserSerializer.Detail)

    @transaction.atomic
    def delete(self, request, user_id: UUID):
        user = self._get_user(request, user_id)
        user.delete()

        return SingleResponse(request)


class UserMe(SecuredView):
    def get(self, request):
        return SingleResponse(request, request.user, serializer=UserSerializer.Me)
