from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import os
from Rememeber import settings


class Profile(models.Model):
    owner = models.OneToOneField(User, related_name='profile')
    history_memes = models.ManyToManyField("MemeObject", related_name='old_m')
    liked_memes = models.ManyToManyField("MemeObject", related_name='liked_m')
    stored_backgrounds = models.ManyToManyField("MemeBackground")
    image = models.ImageField(default=os.path.join(settings.MEDIA_ROOT, 'sample-1.jpg'), upload_to='info/')


# background is equivalent to template
class MemeBackground(models.Model):
    title = models.CharField(max_length=40)
    # All tags are stored in one CharField and seperated by "&"
    tags = models.CharField(max_length=40)
    image = models.ImageField(upload_to="backgrounds", blank=True)  # this is the background image
    created_by = models.ForeignKey(User, related_name='creator')


class MemeObject(models.Model):
    title = models.CharField(max_length=40)
    image = models.ImageField(upload_to="memes", blank=True)  # this is the actual image item of the meme
    # All captions are stored in a list and encoded as json
    captions = models.TextField()
    # Each caption position will be determined by the top left and bottom right pixel position
    # Each pair of the coordinates will be stored in the same order as the captions. The values are encoded as JSON
    caption_positions = models.TextField()
    # All tags are stored in one CharField and seperated by "&"
    tags = models.CharField(max_length=40)
    background = models.ForeignKey(MemeBackground, related_name='background')
    created_at = models.DateTimeField(auto_now_add=True)
    liked_list = models.ManyToManyField(User, related_name='liked_user')
    popularity_score = models.IntegerField(default=0)
    owner = models.ForeignKey(User, related_name='owner')


class MemeWar(models.Model):
    meme_list = models.ManyToManyField(MemeObject, symmetrical=False, related_name='meme_list', default=None)
    # The starting meme of the meme war
    thread_meme = models.ForeignKey(MemeObject, on_delete=models.CASCADE, related_name='thread_meme')
    users = models.ManyToManyField(User, related_name='user_war_list', default=None)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    receiver = models.ForeignKey(User, related_name='receiver')
    has_read = models.BooleanField(default=False)
    thread_meme = models.ForeignKey(MemeWar, related_name='meme_war')
