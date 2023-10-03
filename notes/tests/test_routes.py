from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class TestRoutes(TestCase):

    def test_page_availability(self):
        urls = (
            ('notes:home', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
