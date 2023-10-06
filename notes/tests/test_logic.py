from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNotesCreate(TestCase):
    ORIGINAL_SLUG = 'OirginalSlug'
    START_NOTES_COUNT = 1

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url_creat_note = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.data_for_add = {
            'title': 'Заголовок для теста',
            'text': 'Текс для теста',
            'author': cls.author,
            'slug': cls.ORIGINAL_SLUG
        }
        cls.note = Note.objects.create(
            title=cls.data_for_add['title'],
            text=cls.data_for_add['text'],
            author=cls.data_for_add['author'],
            slug=cls.data_for_add['slug']
        )

    def test_create_note_with_repeat_slug(self):
        start_count_notes = Note.objects.count()
        self.author_client.post(
            self.url_creat_note,
            data=self.data_for_add
            )
        end_count_notes = Note.objects.count()
        self.assertEqual(start_count_notes, end_count_notes)

    def test_anonimus_cant_create_note(self):
        self.client.post(
            self.url_creat_note,
            data=self.data_for_add
            )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.START_NOTES_COUNT)

    def test_user_can_create_note(self):
        response = self.client.post(
            self.url_creat_note,
            data=self.data_for_add
            )
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.START_NOTES_COUNT+1)
        note = Note.objects.last()
        self.assertEqual(note.text, self.data_for_add['text'])
        self.assertEqual(note.title, self.data_for_add['title'])
        self.assertEqual(note.author, self.author)


class TestNotetEditDelete(TestCase):

    NOTE_TEXT = 'Текст поста'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug='Slug',
                                       author=cls.author,)
        cls.url_success = reverse('notes:success', None)
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.note.slug)
        self.assertEqual(self.note.author, self.note.author)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.note.slug)
        self.assertEqual(self.note.author, self.note.author)

    def test_add_note_slug_nul(self):
        notes_count_first = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        slug_slugify = slugify(self.NOTE_TITLE)
        self.note.refresh_from_db()
        notes_count_last = Note.objects.count()
        self.assertEqual(notes_count_last, notes_count_first + 1)
        self.assertEqual(Note.objects.last().slug, slug_slugify)
