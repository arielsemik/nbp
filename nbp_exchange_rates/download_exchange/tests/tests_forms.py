from django.test import TestCase
from datetime import date, timedelta
from download_exchange.models import Rate
from download_exchange.forms import DateForms, CurrencyForms, DateInputMax, DateInput


class DateFormsTestCase(TestCase):
    def test_date_forms_valid_data(self):
        form_data = {
            'start_date': '2022-01-01',
            'end_date': '2022-01-31',
        }
        form = DateForms(data=form_data)

        self.assertTrue(form.is_valid())

    def test_date_forms_swapped_data(self):
        form_data = {
            'start_date': '2022-01-01',
            'end_date': '2021-12-31',
        }
        form = DateForms(data=form_data)

        self.assertFalse(form.is_valid())


class CurrencyFormsTestCase(TestCase):
    def test_currency_forms_valid_data(self):
        Rate.objects.create(currency='USD', code='USD', mid=1.2345, table='A', no='094/A/NBP/2023', effective_date=date.today())
        Rate.objects.create(currency='EUR', code='EUR', mid=2.3456, table='A', no='094/A/NBP/2023>', effective_date=date.today())

        form_data = {
            'start_date': '2022-01-01',
            'end_date': '2022-01-31',
            'code': 'USD',
        }
        form = CurrencyForms(data=form_data)

        self.assertTrue(form.is_valid())

    def test_currency_forms_swapped_date(self):
        form_data = {
            'start_date': '2022-01-01',
            'end_date': '2021-12-31',
            'code': 'USD',
        }
        form = CurrencyForms(data=form_data)

        self.assertFalse(form.is_valid())


class DateInputTestCase(TestCase):
    def test_date_input_max_attribute_yesterday(self):
        date_input = DateInput()

        self.assertEqual(date_input.attrs.get('max'), (date.today() - timedelta(days=1)))


class DateInputMaxTestCase(TestCase):
    def test_date_input_max_attribute_today(self):
        date_input_max = DateInputMax()

        self.assertEqual(date_input_max.attrs.get('max'), date.today())
