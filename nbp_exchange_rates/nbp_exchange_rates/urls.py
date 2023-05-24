"""
URL configuration for nbp_exchange_rates project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from .n views import get_rates
from download_exchange import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("download_rates/", views.download_rates, name="download_rates"),
    path("currency_rates/", views.currency_rates, name="currency_rates"),
    path("get_all_rates", views.get_all_rates, name="get_all_rates"),
    # path("generated_data/", views.generated_data, name="generated_data"),
    path("", views.index, name="index"),

]
