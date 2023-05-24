from django.http import HttpResponse
from django.template import loader
from .forms import DateForms, CurrencyForms
import requests
from .models import Rate
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponseRedirect
def index(request):
    template = loader.get_template("index.html")
    # currency_codes = Rate.objects.all().values('code').annotate(Count('code'))
    # codes = (x['code'] for x in currency_codes)

    context = {
    }
    return HttpResponse(template.render(context, request))

def get_data(start_date, end_date, table ='A'):
    url = f'http://api.nbp.pl/api/exchangerates/tables/{table}/{start_date}/{end_date}/'
    retes = requests.get(url).json()
    return retes

def save_rates(rates):
    for day in rates:
        table = day['table']
        no = day['no']
        effectiveDate = day['effectiveDate']
        rates_list = day['rates']
        for currency in rates_list:
            currency_name = currency['currency']
            code = currency['code']
            mid =currency['mid']
            if Rate.objects.filter(code=code, effectiveDate=effectiveDate).count() ==0:
                Rate.objects.create(
                    currency=currency_name,
                    code=code,
                    mid=mid,
                    table=table,
                    no=no,
                    effectiveDate=effectiveDate
                )
def download_rates(request):
    if request.method == "POST":
        form = DateForms(request.POST)
        # print(form)
        if form.is_valid():
            form_data = form.cleaned_data
            start_date = form_data["start_date"]
            end_date = form_data["end_date"]

            rates = get_data(start_date=start_date, end_date=end_date)
            save_rates(rates=rates)
    else:
        form= CurrencyForms()
    return render(request, '')
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
            data = Rate.objects.filter(code=code, effectiveDate__gte=start_date, effectiveDate__lte=end_date )
            print(data)
            return render(request, 'generated_data.html', {"data": data})
    else:
        form = CurrencyForms()
    return render(request, 'show_rates.html', {"form": form})
def get_all_rates(request):
    # template = loader.get_template("download_rates.html")
    # context = {
    # }
    # return HttpResponse(template.render(context, request))
    rates = (Rate.objects.all().values_list('code','effectiveDate' ))#.annotate(Count('code'))

    # codes = set([x['code'] for x in rates])
    return HttpResponse(rates)
# def generated_data(request):
#     print(request.method, 'ggggggggggggggggg')
#     return render(request, "generated_data.html", {})