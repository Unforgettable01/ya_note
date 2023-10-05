from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='User Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок для теста',
            text='Текс для теста',
            author=cls.author,
            slug='testSlug'
        )
        cls.slug_for_urls = cls.note.slug
        cls.urls_with_slug = (
            ('notes:detail', (cls.slug_for_urls,)),
            ('notes:delete', (cls.slug_for_urls,)),
            ('notes:edit', (cls.slug_for_urls,)),
        )
        cls.urls_for_auth_user = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )

    def test_page_availability(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_detail_edit_and_delete(self):
        users_status = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, 404),
        )
        for user, status in users_status:
            for name, args in self.urls_with_slug:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_list_add_done(self):
        for name, args in self.urls_for_auth_user:
            with self.subTest(user=self.reader_client, name=name):
                url = reverse(name, args=args)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_not_auth_user(self):
        urls = self.urls_for_auth_user + self.urls_with_slug
        login_url = reverse('users:login') 
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
