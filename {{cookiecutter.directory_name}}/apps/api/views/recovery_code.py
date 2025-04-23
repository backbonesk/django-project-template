import random
import time
from datetime import timedelta
from http import HTTPStatus
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.api.errors import ValidationException, ProblemDetailException
from apps.api.forms.recovery_code import RecoveryCodeForm
from apps.api.response import SingleResponse
from apps.api.views.base import SecuredView
from apps.core.models import User, RecoveryCode
from apps.core.services.email_notification import NotificationEmailService


class RecoveryCodeManagement(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic
    def post(self, request):
        form = RecoveryCodeForm.Email.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(form)

        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except User.DoesNotExist:
            time.sleep(random.randint(0, 1000) / 1000)
            return SingleResponse(request)

        recovery_code = RecoveryCode.objects.create(
            user=user
        )

        NotificationEmailService.create(
            recipients=[f'{user.get_full_name()} <{user.email}>'],
            subject=_('Change password'),
            content={
                'recovery_code': recovery_code,
                'login_url': request.build_absolute_uri(
                    reverse('recovery-code-id', kwargs={'recovery_code_id': recovery_code.pk})
                ),
            },
            template=settings.EMAIL_RECOVERY_PATH,
        ).send_email()

        return SingleResponse(request)


class RecoveryCodeDetail(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic()
    def post(self, request, recovery_code_id: UUID):
        form = RecoveryCodeForm.Password.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(form)

        RecoveryCode.objects.filter(
            created_at__lte=timezone.now() - timedelta(days=settings.RECOVERY_TIME_EXPIRATION)
        ).delete()

        try:
            recovery_code = RecoveryCode.objects.get(pk=recovery_code_id)
        except RecoveryCode.DoesNotExist:
            raise ProblemDetailException(
                _('Recovery code expired or does not exists.'),
                status=HTTPStatus.NOT_FOUND
            )

        recovery_code.user.set_password(form.cleaned_data['password'])
        recovery_code.user.is_active = True
        recovery_code.user.save()
        recovery_code.delete()

        return SingleResponse(request)
