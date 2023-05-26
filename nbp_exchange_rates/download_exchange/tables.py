import django_tables2 as tables
from .models import Rate


class RatesTable(tables.Table):
    class Meta:
        model = Rate
        fields = ('code', 'mid', 'effectiveDate')
