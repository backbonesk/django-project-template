from django.forms import fields
from django_api_forms import Form


class TokenForm:
    class Basic(Form):
        email = fields.EmailField(required=True)
        password = fields.CharField(required=True, max_length=128)
