import random
import time
from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.api.errors import ValidationException, ProblemDetailException
from apps.api.forms.password import RecoveryCodeForm, NewPasswordForm
from apps.api.response import SingleResponse
from apps.api.views.base import SecuredView
from apps.core.models import User, RecoveryCode
from apps.core.services.email_notification import NotificationEmailService


class PasswordRecoveryManagement(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic
    def post(self, request):
        form = RecoveryCodeForm.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(request, form)

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
                'login_url': f'{settings.BASE_URL}{reverse("password-change")}',
            },
            template=settings.EMAIL_RECOVERY_PATH,
        ).send_email()

        return SingleResponse(request)


class PasswordChangeManagement(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic()
    def post(self, request):
        form = NewPasswordForm.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(request, form)

        RecoveryCode.objects.filter(
            created_at__lte=timezone.now() - timedelta(days=settings.RECOVERY_TIME_EXPIRATION)
        ).delete()

        try:
            recovery_code = RecoveryCode.objects.get(pk=form.cleaned_data['recovery_code'])
        except RecoveryCode.DoesNotExist:
            raise ProblemDetailException(
                request, _('Recovery code expired or does not exists.'), status=HTTPStatus.NOT_FOUND
            )

        recovery_code.user.set_password(form.cleaned_data['password'])
        recovery_code.user.is_active = True
        recovery_code.user.save()
        recovery_code.delete()

        return SingleResponse(request)
