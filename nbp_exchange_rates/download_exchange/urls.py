from django.contrib import admin
from django.urls import path, include
from views import index, download_rates

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", index, name="index"),
    path("get_rates/", download_rates, name="get_rates"),
]