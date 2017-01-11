from django.test import TestCase
from core.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from Rememeber.settings import *
import os
from django.contrib.auth.models import User


# Create your tests here.

class TestProfileModel(TestCase):
    def test_simple_add(self):
        user_test = User(username='test', password='test')
        user_test.save()
        self.assertTrue(Profile.objects.all().count() == 0)
        new_profile = Profile(owner=user_test)
        new_profile.save()
        self.assertTrue(Profile.objects.all().count() == 1)
        self.assertTrue(Profile.objects.first())

    def test_simple_delete(self):
        user_test = User(username='test', password='test')
        user_test.save()
        self.assertTrue(Profile.objects.all().count() == 0)
        new_profile = Profile(owner=user_test)
        new_profile.save()
        self.assertTrue(Profile.objects.all().count() == 1)
        self.assertTrue(Profile.objects.first())
        new_delete = Profile.objects.first()
        new_delete.delete()
        self.assertTrue(Profile.objects.all().count() == 0)


class TestMemebackgroundModel(TestCase):
    def test_add(self):
        self.assertTrue(MemeBackground.objects.all().count() == 0)
        user_test = User(username='test', password='test')
        user_test.save()
        new_background = MemeBackground()
        new_background.title = 'test_bg'
        new_background.image = SimpleUploadedFile(name='test_image.png',
                                                  content=open(os.path.join(BASE_DIR, 'test_image.png'), 'rb').read(), content_type='image/jpeg')
        new_background.created_by = user_test
        new_background.save()
        # self.assertTrue(MemeBackground.objects.all().count() == 1)
        self.assertTrue(MemeBackground.objects.filter(title='test_bg'))

    def test_delete(self):
        self.assertTrue(MemeBackground.objects.all().count() == 0)
        user_test = User(username='test', password='test')
        user_test.save()
        new_background = MemeBackground(created_by=user_test, created_by_id=user_test.id)
        new_background.title = 'test_bg'
        new_background.image = SimpleUploadedFile(name='test_image.png',
                                                  content=open(os.path.join(BASE_DIR, 'test_image.png'), 'rb').read(), content_type='image/jpeg')
        new_background.created_by = user_test
        new_background.created_by_id = user_test.id
        new_background.tags = 'test'
        new_background.save()
        self.assertTrue(MemeBackground.objects.all().count() == 1)
        MemeObject.objects.all().delete()
        self.assertTrue(MemeBackground.objects.all().count() == 0)


    def test_update(self):
        user_test = User(username='test', password='test')
        user_test.save()
        self.assertTrue(MemeBackground.objects.all().count() == 0)
        new_background = MemeBackground(created_by=user_test, created_by_id=user_test.id)
        new_background.title = 'test_bg'
        new_background.title = 'test_bg'
        new_background.image = SimpleUploadedFile(name='test_image.png',
                                                  content=open(os.path.join(BASE_DIR, 'test_image.png'), 'rb').read(), content_type='image/jpeg')
        new_background.save()
        self.assertTrue(MemeBackground.objects.filter(title='test_bg'))
        bg = MemeBackground.objects.get(title='test_bg')
        bg.title = 'change'
        bg.save()
        self.assertTrue(MemeBackground.objects.filter(title='change'))


class TestMessageModel(TestCase):
    user_test = User.objects.get(username='test')

    def test_add(self):
        return
        # self.assertTrue(MemeObject.objects.all().count() == 0)
