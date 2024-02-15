from django.contrib.auth.password_validation import validate_password
from django.forms import fields
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_api_forms import Form

from apps.core.models.user import User


class UserForm:
    class Update(Form):
        name = fields.CharField(required=True, max_length=30)
        surname = fields.CharField(required=True, max_length=150)
        email = fields.EmailField(required=True)

    class Create(Update):
        def clean_email(self):
            email = self.cleaned_data['email']
            if User.all_objects.filter(email=email).exists():
                self.add_error(
                    ('email',),
                    ValidationError(_('User with the same email already exists.'), code='email-already-exists')
                )

            return email

    class ChangePasswordForm(Form):
        old_password = fields.CharField(required=True)
        new_password = fields.CharField(required=True, validators=[validate_password])

        def clean_old_password(self):
            old_password = self.cleaned_data['old_password']
            if not self._request.user.check_password(old_password):
                self.add_error(
                    ('old_password',), ValidationError(_('Current password do not match with old password.'))
                )

            return old_password
