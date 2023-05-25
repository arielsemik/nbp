import datetime
from datetime import date
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.template import loader
from .forms import DateForms, CurrencyForms
import requests
from .models import Rate
from django.shortcuts import render
from .tables import RataTable
from django.core.handlers.wsgi import WSGIRequest
from requests.models import Response

def index(request: WSGIRequest) -> HttpResponse:
    template = loader.get_template("index.html")

    context = {
    }
    return HttpResponse(template.render(context, request))


def get_data(start_date: date, end_date: date, table:  str = 'A') -> Response:
    url = f'http://api.nbp.pl/api/exchangerates/tables/{table}/{start_date}/{end_date}/'
    data = requests.get(url)
    return data


def save_exchange_rates(exchange_rates_response: Response) -> None:
    for day in exchange_rates_response.json():
        table = day.get('table')
        no = day.get('no')
        effective_date = day.get('effectiveDate')
        rates_list = day.get('rates')

        for currency in rates_list:
            currency_name = currency.get('currency')
            code = currency.get('code')
            mid =currency.get('mid')
            if Rate.objects.filter(code=code, effectiveDate=effective_date).count() ==0:
                Rate.objects.create(
                    currency=currency_name,
                    code=code,
                    mid=mid,
                    table=table,
                    no=no,
                    effectiveDate=effective_date
                )


def download_rates(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        form = DateForms(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            start_date = form_data["start_date"]
            end_date = form_data["end_date"]

            exchange_rates_response = get_data(start_date=start_date, end_date=end_date)
            if exchange_rates_response.status_code == 404:
                return HttpResponseNotFound('Brak danych lub wybrałeś tą samą datę w start_date i end_date. Cofnij i spróbuj wybrać poprawny zakres dat')
            elif exchange_rates_response.status_code == 400:
                return HttpResponseBadRequest('Start_date nie może być większa niż End_date. Cofnij i wybierz poprawną datę.')
            save_exchange_rates(exchange_rates_response=exchange_rates_response)
            return render(request, 'index.html', {"downloaded": True, 'start_date': start_date, 'end_date': end_date})
    else:
        form = DateForms()
    return render(request, 'download_rates.html', {"form": form})
def currency_rates(request):
    if request.method == "POST":
        form = CurrencyForms(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            start_date = form_data["start_date"]
            print(type(start_date),'sdasada')
            end_date = form_data["end_date"]
            code = form_data['code']
            print(code)
            print(type(code))

            import datetime
            data = Rate.objects.filter(
                code=code,
                effectiveDate__gte=start_date,
                effectiveDate__lte=end_date
            )
            table = RataTable(data)
            return render(request, 'generated_data.html', {"table": table})
    else:
        form = CurrencyForms()
    return render(request, 'show_rates.html', {"form": form})
def get_all_rates(request):

    rates = (Rate.objects.all().values_list('code','effectiveDate' ))#.annotate(Count('code'))
    return HttpResponse(rates)
# def generated_data(request):
#     print(request.method, 'ggggggggggggggggg')
#     return render(request, "generated_data.html", {})