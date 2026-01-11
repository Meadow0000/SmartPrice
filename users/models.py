# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    level = models.IntegerField(default=1)

    def update_level(self):
        """Обновляет уровень пользователя по количеству избранного"""
        total_likes = (
            self.user.liked_games.count() +
            self.user.liked_auto.count() +
            self.user.liked_home.count() +
            self.user.liked_electronics.count() +
            self.user.liked_deals.count() +
            self.user.liked_news.count()
        )

        if total_likes >= 12:
            self.level = 5
        elif total_likes >= 9:
            self.level = 4
        elif total_likes >= 6:
            self.level = 3
        elif total_likes >= 3:
            self.level = 2
        else:
            self.level = 1

        self.save()

    def level_name(self):
        """Название уровня"""
        names = {
            1: "Новачок",
            2: "Супер знижник",
            3: "Майстер пропозицій",
            4: "Експерт вигод",
            5: "Легенда шопінгу"
        }
        return names.get(self.level, "Новачок")


# ДОБАВЬТЕ ЭТИ СИГНАЛЫ В КОНЕЦ ФАЙЛА models.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
