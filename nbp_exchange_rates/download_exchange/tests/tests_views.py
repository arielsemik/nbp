import requests
from django.http import HttpResponse
import datetime
from django.test import TestCase
from django.urls import reverse
from download_exchange.forms import DateForms, CurrencyForms
from download_exchange.views import get_exchange_rates, check_existing_rates
from unittest.mock import patch, Mock, MagicMock


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
    def test_currency_rates_view_show_rates(self):

        response = self.client.get(reverse('currency_rates'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_rates.html')


class GetExchangeRatesTestCase(TestCase):
    def setUp(self) -> None:
        self.table = 'A'

    def test_return_200_correct_dates(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 1, 7)
        with patch('download_exchange.views.requests.get') as mock_get:

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{'rate': 1.23}, {'rate': 4.56}]
            mock_get.return_value = mock_response

            response = get_exchange_rates(start_date, end_date, self.table)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'rate': 1.23}, {'rate': 4.56}])
        mock_get.assert_called_once_with(f'http://api.nbp.pl/api/exchangerates/tables/{self.table}/{start_date}/{end_date}/')

    def test_get_exchange_rates_failure(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 1, 5)
        with patch('download_exchange.views.requests.get') as mock_get:

            mock_get.side_effect = requests.exceptions.RequestException('Błąd połączenia')

            with self.assertRaises(requests.exceptions.RequestException):
                get_exchange_rates(start_date, end_date, self.table)

    def test_get_exchange_rates_no_data(self):
        today = datetime.date.today()
        start_date = today + datetime.timedelta(days=-3),
        end_date = today + datetime.timedelta(days=1)

        with patch('download_exchange.views.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            response = get_exchange_rates(start_date, end_date, self.table)

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
            mock_filter.return_value.count.return_value = 1
            check_existing_rates(self.day_data, self.currency)

            mock_filter.assert_called_once_with(code='USD', effective_date='2023-05-25')
            self.assertFalse(mock_filter.return_value.create.called)

    def test_new_rates(self):
        with patch('download_exchange.models.Rate.objects.filter') as mock_filter:
            mock_filter.return_value.count.return_value = 0

            with patch('download_exchange.models.Rate.objects.create') as mock_create:
                check_existing_rates(self.day_data, self.currency)

                mock_filter.assert_called_once_with(code='USD', effective_date='2023-05-25')
                mock_create.assert_called_once_with(
                    currency='USD',
                    code='USD',
                    mid=3.5,
                    table='A',
                    no='1',
                    effective_date='2023-05-25'
                )


class DownloadRatesTestCase(TestCase):

    def test_return_clean_data_form_for_get(self):
        form_data = {}
        form_mock = MagicMock(spec=DateForms)
        form_mock.cleaned_data = form_data

        with patch('download_exchange.views.DateForms', return_value=form_mock):
            response = self.client.get('/download_rates/', data=form_data)

        self.assertEqual(response.status_code, 200)

    def test_download_rates_valid_form(self):
        form_data = {'start_date': '2023-01-01', 'end_date': '2023-01-05'}
        form_mock = MagicMock(spec=DateForms)
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = form_data
        exchange_rates_response_mock = MagicMock(spec=HttpResponse)
        exchange_rates_response_mock.status_code = 200

        with patch('download_exchange.views.DateForms', return_value=form_mock):
            with patch('download_exchange.views.get_exchange_rates', return_value=exchange_rates_response_mock):
                with patch('download_exchange.views.save_exchange_rates') as save_exchange_rates_mock:
                    response = self.client.post('/download_rates/', data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(save_exchange_rates_mock.called)
        self.assertTemplateUsed(response, 'index.html')

    def test_404_response_(self):
        today = datetime.date.today()
        start_date = today + datetime.timedelta(days=-3),
        end_date = today + datetime.timedelta(days=1)
        form_data = {'start_date': start_date, 'end_date': end_date}
        form_mock = MagicMock(spec=DateForms)
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = form_data
        exchange_rates_response_mock = MagicMock(spec=HttpResponse)
        exchange_rates_response_mock.status_code = 404

        with patch('download_exchange.views.DateForms', return_value=form_mock):
            with patch('download_exchange.views.get_exchange_rates', return_value=exchange_rates_response_mock):
                response = self.client.post('/download_rates/', data=form_data)

        self.assertEqual(response.status_code, 404)

    def test_response_swapped_dates(self):
        form_data = {'start_date': '2023-01-10', 'end_date': '2023-01-05'}
        form_mock = MagicMock(spec=DateForms)
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = form_data
        exchange_rates_response_mock = MagicMock(spec=HttpResponse)
        exchange_rates_response_mock.status_code = 400

        with patch('download_exchange.views.DateForms', return_value=form_mock):
            with patch('download_exchange.views.get_exchange_rates', return_value=exchange_rates_response_mock):
                response = self.client.post('/download_rates/', data=form_data)

        self.assertEqual(response.status_code, 400)


class CurrencyRatesTestCase(TestCase):

    def test_currency_rates_valid_form(self):
        form_data = {'start_date': '2023-01-01',
                     'end_date': '2023-01-02',
                     'code': 'USD'}
        form_mock = MagicMock(spec=CurrencyForms)
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = form_data

        with patch('download_exchange.views.CurrencyForms', return_value=form_mock):
            response = self.client.post('/currency_rates/', data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'generated_data.html')

    def test_currency_rates_invalid_data(self):
        response = self.client.post('/currency_rates/', {
            'start_date': '2023-01-01',
            'end_date': '2022-12-31',
            'code': 'XYZ'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_rates.html')
