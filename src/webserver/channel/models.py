from django.db import models

class Channel(models.Model):
    username = models.CharField(max_length=25)