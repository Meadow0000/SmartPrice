from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile_view, name="profile"),
    path("favorites/", views.favorites_list, name="liked_items"),

    # AJAX общий для всех типов лайков
    path("toggle/", views.toggle_favorite, name="toggle_favorite"),
]
