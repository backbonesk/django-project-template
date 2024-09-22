from django.contrib.auth.password_validation import validate_password
from django.forms import fields
from django_api_forms import Form


class RecoveryCodeForm(Form):
    email = fields.EmailField(label='Email')


class NewPasswordForm(Form):
    password = fields.CharField(validators=[validate_password], label='Password')
    recovery_code = fields.UUIDField(label='Recovery Code')
