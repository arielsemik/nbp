import django_tables2 as tables
from .models import Rate


class RataTable(tables.Table):
    class Meta:
        model = Rate
        fields = ('code', 'mid', 'effectiveDate')
