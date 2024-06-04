from django.forms import *
from django.core.validators import EmailValidator

class ReportForm(Form):
    date_range = CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    cli = CharField(widget=Select(attrs={
        'class': 'form-control select2',
        'autocomplete': 'off',
        'name':'cli'
    }))
   
    email = EmailField(
    validators=[EmailValidator()],
    widget=TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',
        'name':'email'
    }))
