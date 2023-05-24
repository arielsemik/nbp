from django.contrib import admin
from django.urls import path, include
from views import index, get_rates

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", index, name="index"),
    path("get_rates/", get_rates, name="get_rates"),
]