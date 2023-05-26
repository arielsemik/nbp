import datetime
from .models import Rate
from django import forms
from django.db.models import Count


def show_currency() -> list:
    currency_codes = Rate.objects.all().values("code").annotate(Count("code"))
    codes = [(code["code"], code["code"]) for code in currency_codes]
    return codes


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs.setdefault("max", datetime.date.today() - datetime.timedelta(1))


class DateInputMax(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.setdefault("max", datetime.date.today())


class DateForms(forms.Form):
    start_date = forms.DateField(label="start_date", required=True, widget=DateInput)
    end_date = forms.DateField(label="end_date", required=True, widget=DateInputMax)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date nie może być większa niż end date.")

        return cleaned_data

class CurrencyForms(forms.Form):
    start_date = forms.DateField(label="start_date", required=True, widget=DateInput)
    end_date = forms.DateField(label="end_date", required=True, widget=DateInputMax)
    code = forms.ChoiceField(choices=show_currency())

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date nie może być większa niż end date.")

        return cleaned_data

