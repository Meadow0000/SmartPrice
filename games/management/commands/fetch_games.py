# games/management/commands/fetch_games.py
from django.core.management.base import BaseCommand
from games.models import GameDeal
import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 Version/16.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/120.0",
]

def safe_get(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    time.sleep(random.uniform(1, 2))
    try:
        return requests.get(url, headers=headers, timeout=10)
    except:
        return None

# ============================
# Humble Bundle
# ============================
def fetch_humblebundle():
    url = "https://www.humblebundle.com/store/publisher/all"
    deals = []
    response = safe_get(url)
    if not response:
        return deals
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("a[href^='/store']")
    for item in items[:20]:
        title = item.get_text(strip=True)
        link = "https://www.humblebundle.com" + item.get("href")
        if not title:
            title = "Game from Humble Bundle"
        deals.append({
            "title": title,
            "url": link,
            "store": "Humble Bundle",
            "price_old": 0,
            "price_new": 0,
            "image": None
        })
    return deals

# ============================
# itch.io
# ============================
def fetch_itchio():
    url = "https://itch.io/games/popular"
    deals = []
    response = safe_get(url)
    if not response:
        return deals
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.game_cell a.game_link")
    for item in items[:20]:
        title = item.get("title") or item.get_text(strip=True)
        link = item.get("href")
        if not link.startswith("https://"):
            link = "https://itch.io" + link
        if not title:
            title = "Game from itch.io"
        deals.append({
            "title": title,
            "url": link,
            "store": "itch.io",
            "price_old": 0,
            "price_new": 0,
            "image": None
        })
    return deals

# ============================
# Steam Top Sellers (с HTML-страницы поиска)
# ============================
def fetch_steam():
    url = "https://store.steampowered.com/search/?filter=globaltopsellers"
    deals = []
    response = safe_get(url)
    if not response:
        return deals
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("a.search_result_row")
    for item in items[:20]:
        title_tag = item.select_one("span.title")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = item.get("href")
        deals.append({
            "title": title,
            "url": link,
            "store": "Steam",
            "price_old": 0,
            "price_new": 0,
            "image": None
        })
    return deals

# ============================
# DJANGO COMMAND
# ============================
class Command(BaseCommand):
    help = "Fetch game deals (real games, always adds items)"

    def handle(self, *args, **kwargs):
        all_deals = []
        store_funcs = [fetch_humblebundle, fetch_itchio, fetch_steam]

        for func in store_funcs:
            self.stdout.write(f"Парсим {func.__name__.replace('fetch_', '').capitalize()}...")
            deals = func()
            if not deals:
                self.stdout.write(f"{func.__name__.replace('fetch_', '').capitalize()}: не найдено")
            all_deals += deals

        # Если всё равно пусто, добавим реальные ссылки вручную
        if not all_deals:
            self.stdout.write("Не удалось получить игры с сайтов, добавляем примеры")
            all_deals = [
                {"title": "Stardew Valley", "url": "https://store.steampowered.com/app/413150/Stardew_Valley/", "store": "Steam", "price_old": 0, "price_new": 14.99, "image": None},
                {"title": "Hollow Knight", "url": "https://store.steampowered.com/app/367520/Hollow_Knight/", "store": "Steam", "price_old": 0, "price_new": 9.99, "image": None},
                {"title": "Celeste", "url": "https://store.steampowered.com/app/504230/Celeste/", "store": "Steam", "price_old": 0, "price_new": 19.99, "image": None},
                {"title": "Among Us", "url": "https://store.steampowered.com/app/945360/Among_Us/", "store": "Steam", "price_old": 0, "price_new": 4.99, "image": None},
                {"title": "Hades", "url": "https://store.steampowered.com/app/1145360/Hades/", "store": "Steam", "price_old": 0, "price_new": 24.99, "image": None},
                {"title": "Factorio", "url": "https://store.steampowered.com/app/427520/Factorio/", "store": "Steam", "price_old": 0, "price_new": 30.00, "image": None},
                {"title": "Slay the Spire", "url": "https://store.steampowered.com/app/646570/Slay_the_Spire/", "store": "Steam", "price_old": 0, "price_new": 24.99, "image": None},
                {"title": "Terraria", "url": "https://store.steampowered.com/app/105600/Terraria/", "store": "Steam", "price_old": 0, "price_new": 9.99, "image": None},
                {"title": "Cuphead", "url": "https://store.steampowered.com/app/268910/Cuphead/", "store": "Steam", "price_old": 0, "price_new": 19.99, "image": None},
                {"title": "The Binding of Isaac: Rebirth", "url": "https://store.steampowered.com/app/250900/The_Binding_of_Isaac_Rebirth/", "store": "Steam", "price_old": 0, "price_new": 14.99, "image": None},
            ]

        added = 0
        for d in all_deals:
            obj, created = GameDeal.objects.update_or_create(
                url=d["url"],
                defaults={
                    "title": d["title"],
                    "store": d["store"],
                    "price_old": d["price_old"] or 0,
                    "price_new": d["price_new"] or 0,
                    "image": d["image"] or ""
                }
            )
            if created:
                added += 1

        self.stdout.write(self.style.SUCCESS(f"Добавлено новых игр: {added}"))
