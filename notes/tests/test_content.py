from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    NOTE_LIST = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок для теста',
            text='Текс для теста',
            author=cls.author,
            slug='testSlug',
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,)),
        )

    def test_user_has_form(self):
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)

    def test_detail_in_list(self):
        response = self.author_client.get(self.NOTE_LIST)
        self.assertIn(self.note, response.context['object_list'])

    def test_reader_has_his_list(self):
        response = self.reader_client.get(self.NOTE_LIST)
        self.assertNotIn(self.note, response.context['object_list'])
