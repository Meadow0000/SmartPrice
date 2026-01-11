from django.db import models
from django.contrib.auth.models import User

class HomeDeal(models.Model):  # аналог Deal
    title = models.CharField(max_length=255)
    store = models.CharField(max_length=255, blank=True, null=True)
    price_old = models.FloatField(blank=True, null=True)
    price_new = models.FloatField()
    url = models.URLField(unique=True)
    image = models.URLField(blank=True, null=True)
    liked_by = models.ManyToManyField(User, related_name="liked_home", blank=True)

    def __str__(self):
        return self.title


