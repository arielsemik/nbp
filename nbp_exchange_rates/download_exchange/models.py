from django.db import models


class Rate(models.Model):
    currency = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    mid = models.DecimalField(max_digits=6, decimal_places=4)
    table = models.CharField(max_length=1)
    no = models.CharField(max_length=20)
    effectiveDate = models.DateField()
