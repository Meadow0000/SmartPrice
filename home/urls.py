from django.urls import path
from .views import home_list
from . import views

urlpatterns = [
    path("", home_list, name="home_list"),
    path('toggle-favorite/', views.toggle_favorite_home, name='toggle_favorite_home'),

]
