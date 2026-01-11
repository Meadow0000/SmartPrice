# news/models.py
from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    title = models.CharField(max_length=255, unique=True)
    content = models.TextField(blank=True)
    url = models.URLField(unique=True)
    image = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    liked_by = models.ManyToManyField(User, related_name="liked_news", blank=True)
    def __str__(self):
        return self.title

