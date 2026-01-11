# news/views.py
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.core.management import call_command
from django.shortcuts import get_object_or_404, redirect
from .models import News


def news_list(request):
    # Проверяем дату последней новости
    latest_news = News.objects.order_by('-published_at').first()
    update_needed = True

    if latest_news and latest_news.published_at is not None:
        if timezone.now() - latest_news.published_at < timedelta(days=1):
            update_needed = False

    # Если новости устарели или нет новостей — вызываем команду fetch_news
    if update_needed:
        try:
            call_command('fetch_news')
        except Exception as e:
            print(f"Ошибка обновления новостей: {e}")

    news = News.objects.all().order_by('-published_at')
    return render(request, 'news/list.html', {'news': news})


def like_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    user = request.user

    if user in news.liked_by.all():
        news.liked_by.remove(user)
    else:
        news.liked_by.add(user)

    return redirect("news_list")
