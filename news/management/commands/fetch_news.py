
import feedparser
from django.utils import timezone
from django.core.management.base import BaseCommand
from news.models import News
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = "Fetch latest fashion news from RSS feeds"

    FEEDS = [
        "https://www.thefashionisto.com/feed/",
        "https://www.thefashionisto.com/mens-fashion/feed/",
        "https://www.vogue.com/rss",
    ]

    def handle(self, *args, **kwargs):
        total_new = 0

        for feed_url in self.FEEDS:
            self.stdout.write(f"\nПарсим RSS: {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                self.stdout.write(self.style.ERROR(f"Ошибка RSS → {feed_url}"))
                continue

            for entry in feed.entries:
                title = entry.get("title", "")
                url = entry.get("link", "")


                raw_html = entry.get("summary", "")

                text = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip()

                image = ""
                if "media_content" in entry and entry.media_content:
                    image = entry.media_content[0].get("url", "")

                obj, created = News.objects.update_or_create(
                    url=url,
                    defaults={
                        "title": title,
                        "content": text,
                        "image": image,
                        "published_at": timezone.now()
                    }
                )

                if created:
                    total_new += 1

        self.stdout.write(self.style.SUCCESS(f"\nДобавлено новых новостей: {total_new}"))
