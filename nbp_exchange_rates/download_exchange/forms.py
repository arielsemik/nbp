from .models import Rate
from django import forms
from django.db.models import Count

# from nbp_exchange_rates.settings import DATE_FORMAT
def show_currency():
    currency_codes = Rate.objects.all().values('code').annotate(Count('code'))
    codes = []
    n=1
    for code in currency_codes:
        codes.append((code['code'],code['code']))
        n+=1
    # codes = ( x['code'] for x in currency_codes)
    return codes
class DateForms(forms.Form):
    start_date = forms.DateField(label="start_date", required=True)
    end_date = forms.DateField(label="end_date",  required=True)
class DateInput(forms.DateInput):
    input_type = 'date'
class CurrencyForms(forms.Form):
    start_date = forms.DateField(label="start_date", required=True, widget=DateInput)
    end_date = forms.DateField(label="end_date",  required=True, widget=DateInput)
    code = forms.ChoiceField(choices=show_currency())