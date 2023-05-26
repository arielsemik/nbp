import datetime

from django.test import TestCase
import requests
import responses
from ..views import get_exchange_rates
# from unittest import TestCase, mock
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.db import DatabaseError
import datetime
from django.test import TestCase, RequestFactory
from django.urls import reverse
from ..models import Rate
from ..forms import DateForms
from ..views import get_exchange_rates, check_existing_rates, save_exchange_rates, download_rates
from unittest.mock import patch, Mock, MagicMock
from requests import Response
from requests.exceptions import RequestException
# class GetExchangeratesTestCase(TestCase):
#     def setUp(self) -> None:
#         self.data_for_400 ={
#         'table': 'A',
#         'start_date': datetime.date(2023,2,1),
#         'end_date': datetime.date(2023,1,1)
#         }
#         self.data_for_404 = {
#             'table': 'A',
#             'start_date': datetime.date.today()+datetime.timedelta(days=-3),
#             'end_date': datetime.date.today()+datetime.timedelta(days=1)
#         }
#     @responses.activate
#     def test_return_404_for_incorrect_date(self):
#         responses.add(**{
#             'method': responses.GET,
#             'url': f'http://api.nbp.pl/api/exchangerates/tables/{self.data_for_404.get("table")}/{self.data_for_404.get("start_date")}/{self.data_for_404.get("end_date")}/',
#             'status': 404,
#             'content_type': 'application/json',
#         })
#
#         response_404 = get_exchange_rates(start_date=self.data_for_404.get("start_date"),
#                                           end_date =self.data_for_404.get("end_date"),
#                                           table=self.data_for_404.get("table")
#                                           )
#         print(response_404,'dadsadadsa')
#         self.assertEqual(404, response_404.status_code)
#
#     def test_return_400_for_incorrect_date(self):
#         responses.add(**{
#             'method': responses.GET,
#             'url': f'http://api.nbp.pl/api/exchangerates/tables/{self.data_for_400.get("table")}/{self.data_for_400.get("start_date")}/{self.data_for_404.get("end_date")}/',
#             'status': 400,
#             'content_type': 'application/json',
#         })
#         print(self.data_for_400.get("start_date"))
#         response_400 = get_exchange_rates(start_date=self.data_for_400.get("start_date"),
#                                           end_date=self.data_for_400.get("end_date"),
#                                           table=self.data_for_400.get("table")
#                                           )
#
#         self.assertEqual(400, response_400.status_code)

class IndexViewTestCase(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class DownloadRatesViewTestCase(TestCase):
    def test_download_rates_view_get(self):
        response = self.client.get(reverse('download_rates'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'download_rates.html')



class CurrencyRatesViewTestCase(TestCase):
    def test_currency_rates_view_get(self):
        response = self.client.get(reverse('currency_rates'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_rates.html')



class GetAllRatesViewTestCase(TestCase):
    def test_get_all_rates_view(self):
        response = self.client.get(reverse('get_all_rates'))
        self.assertEqual(response.status_code, 200)




class GetExchangeRatesTestCase(TestCase):
    def setUp(self) -> None:
        self.table = 'A'

    def test_return_200_correct_dates(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 1, 7)
        response = get_exchange_rates(start_date, end_date, table=self.table)
        self.assertEqual(response.status_code, 200)
        # Add assertions to validate the response data, such as the expected JSON structure or specific values

    def test_return_400_swapped_dates(self):
        start_date = datetime.date(2023, 1, 7)
        end_date = datetime.date(2023, 1, 1)
        response = get_exchange_rates(start_date, end_date, table=self.table)
        self.assertIsInstance(response, Response)

        self.assertEqual(response.status_code, 400)
        # Add assertions to validate the error response, such as the expected error message or status code

    def test_get_exchangerates_no_data(self):
        today = datetime.date.today()
        start_date = today + datetime.timedelta(days=-3),
        end_date = today + datetime.timedelta(days=1)

        # with patch('requests.get') as mock_get:
        #     mock_get.return_value.status_code = 404
        response = get_exchange_rates(start_date, end_date, table=self.table)
        self.assertIsInstance(response, Response)

        self.assertEqual(response.status_code, 404)




class CheckExistingRatesTestCase(TestCase):
    def setUp(self):
        self.day_data = {
            'table': 'A',
            'no': '1',
            'effectiveDate': '2023-05-25'
        }
        self.currency = {
            'currency': 'USD',
            'code': 'USD',
            'mid': 3.5
        }

    def test_existing_rates(self):
        with patch('download_exchange.models.Rate.objects.filter') as mock_filter:
            # mock_filter.return_value.count.return_value = 1
            mock_filter.return_value.count.return_value =1
            check_existing_rates(self.day_data, self.currency)

            mock_filter.assert_called_once_with(code='USD', effectiveDate='2023-05-25')
            self.assertFalse(mock_filter.return_value.create.called)

    def test_new_rates(self):
        with patch('download_exchange.models.Rate.objects.filter') as mock_filter:
            mock_filter.return_value.count.return_value = 0

            with patch('download_exchange.models.Rate.objects.create') as mock_create:
                check_existing_rates(self.day_data, self.currency)

                mock_filter.assert_called_once_with(code='USD', effectiveDate='2023-05-25')
                mock_create.assert_called_once_with(
                    currency='USD',
                    code='USD',
                    mid=3.5,
                    table='A',
                    no='1',
                    effectiveDate='2023-05-25'
                )


class DownloadRatesTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
    def test_return_clean_data_form_for_get(self):
        form_data = {}

        request = self.factory.get('/download_rates/', data = form_data)
        form_mock = MagicMock(spec=DateForms)
        form_mock.cleaned_data = form_data
        with patch('download_exchange.views.DateForms', return_value=form_mock):
            response = download_rates(request)
        self.assertEqual(response.status_code, 200)


    def test_download_rates_valid_data(self):
        form_data = {'start_date': '2023-01-01', 'end_date': '2023-01-05'}
        request = self.factory.post('/download-rates/', data=form_data)
        form_mock = MagicMock(spec=DateForms)
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = form_data
        exchange_rates_response_mock = MagicMock(spec=HttpResponse)
        exchange_rates_response_mock.status_code = 200

        with patch('download_exchange.views.DateForms', return_value=form_mock):
            with patch('download_exchange.views.get_exchange_rates', return_value=exchange_rates_response_mock):
                with patch('download_exchange.views.save_exchange_rates') as save_exchange_rates_mock:
                    response = download_rates(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(save_exchange_rates_mock.called)