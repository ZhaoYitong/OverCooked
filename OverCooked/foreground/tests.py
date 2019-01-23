from django.test import TestCase
import json


class OrderTest(TestCase):
    def test_post(self):
        # data = {
        #     'type': '堂吃',
        #     'price': '112.5',
        #     'foods': [1, 2, 3, 3],
        #     'marks': ['', '中辣', '', ''],
        #     'guest': '',
        #     'phone': '',
        #     'address': '',
        #     'state': '',
        # }
        data = {
            'type': '外带',
            'price': '24.5',
            'foods': [13, 18],
            'marks': ['', ''],
            'guest': '',
            'phone': '',
            'address': '',
            'state': '',
        }
        response = self.client.post('/foreground/ordering/', json.dumps(data, ensure_ascii=False).encode('utf-8'))
        self.assertEqual(response.status_code, 200)

