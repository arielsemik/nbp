from django.db import models
TABLE_CHOICES = (
    ('A', 'Table A'),
    ('B', 'Table B'),
    ('C', 'Table C'),
)


class Rate(models.Model):
    currency = models.CharField(max_length=50, db_index=True)
    code = models.CharField(max_length=3, db_index=True)
    mid = models.DecimalField(max_digits=6, decimal_places=4)
    table = models.CharField(max_length=1, choices=TABLE_CHOICES)
    no = models.CharField(max_length=20)
    effective_date = models.DateField(db_index=True)

