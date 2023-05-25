import datetime

from django.test import TestCase
import requests
import responses
from ..views import get_exchangerates
class GetExchangeratesTestCase(TestCase):
    def setUp(self) -> None:
        self.table = 'A'
        self.start_date = datetime.date(2023,2,1)
        self.end_date = datetime.date(2023,1,1)
    @responses.activate
    def test_return_error_for_incorrect_date(self):
        print('dasdsa')
        responses.add(**{
            'method': responses.GET,
            'url': f'http://api.nbp.pl/api/exchangerates/tables/{self.table}/{self.start_date}/{self.end_date}/',
            'body': '{"error": "reason"}',
            'status': 404,
            'content_type': 'application/json',
        })

        response = get_exchangerates(start_date=self.start_date,
                                     end_date =  self.end_date,
                                     table= self.table
        )

        self.assertEqual({'error': 'reason'}, response.json())
        self.assertEqual(404, response.status_code)