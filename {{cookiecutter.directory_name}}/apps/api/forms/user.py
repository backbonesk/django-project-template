from django.forms import fields
from django.contrib.auth.password_validation import validate_password
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
        password = fields.CharField(required=True, validators=[validate_password])

        def clean_email(self):
            if User.all_objects.filter(email=self.cleaned_data['email']).exists():
                self.add_error(
                    ('email', ),
                    ValidationError(_('User with the same email already exists.'), code='email-already-exists')
                )

            return self.cleaned_data['email']
