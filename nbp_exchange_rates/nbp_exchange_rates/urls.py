from django.contrib import admin
from django.urls import path
from download_exchange import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("download_rates/", views.download_rates, name="download_rates"),
    path("currency_rates/", views.currency_rates, name="currency_rates"),
    path("", views.index, name="index"),
]
