from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile
from .forms import ProfileForm, UserForm, CustomPasswordChangeForm
from games.models import GameDeal
from auto.models import AutoDeal
from home.models import HomeDeal
from electronics.models import ElectronicsDeal
from deals.models import Deal
from news.models import News
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


@login_required
def profile_view(request):
    # Создаем профиль, если его нет
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.update_level()

    if request.method == "POST":
        # Если сохраняем профиль
        if 'save_profile' in request.POST:
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профіль успішно оновлено!')
                return redirect("profile")

        # Если меняем пароль
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Важно! Чтобы не разлогинило
                messages.success(request, 'Пароль успішно змінено!')
                return redirect("profile")
            else:
                messages.error(request, 'Будь ласка, виправте помилки у формі.')

    # Создаем формы для GET запроса
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(request.user)

    context = {
        "profile": profile,
        "user_form": user_form,
        "profile_form": profile_form,
        "password_form": password_form,
        "level": profile.level,
        "level_name": profile.level_name(),
    }
    return render(request, "users/profile.html", context)


@login_required
def toggle_favorite(request):
    obj_type = request.POST.get("type")
    obj_id = request.POST.get("id")
    liked = False

    model_map = {
        "game": GameDeal,
        "auto": AutoDeal,
        "home": HomeDeal,
        "electronics": ElectronicsDeal,
        "deal": Deal,
        "news": News,
    }

    if obj_type not in model_map:
        return JsonResponse({"error": "Unknown type"}, status=400)

    model = model_map[obj_type]
    obj = get_object_or_404(model, id=obj_id)

    if hasattr(obj, "liked_by"):
        if request.user in obj.liked_by.all():
            obj.liked_by.remove(request.user)
            liked = False
        else:
            obj.liked_by.add(request.user)
            liked = True
    else:
        return JsonResponse({"error": "Model has no liked_by"}, status=400)

    # Обновляем уровень пользователя
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.update_level()

    return JsonResponse({"liked": liked, "level": profile.level})


@login_required
def favorites_list(request):
    """Отображаем все избранные элементы пользователя по категориям"""
    liked_games = GameDeal.objects.filter(liked_by=request.user)
    liked_auto = AutoDeal.objects.filter(liked_by=request.user)
    liked_home = HomeDeal.objects.filter(liked_by=request.user)
    liked_electronics = ElectronicsDeal.objects.filter(liked_by=request.user)
    liked_deals = Deal.objects.filter(liked_by=request.user)
    liked_news = News.objects.filter(liked_by=request.user)

    context = {
        "liked_games": liked_games,
        "liked_auto": liked_auto,
        "liked_home": liked_home,
        "liked_electronics": liked_electronics,
        "liked_deals": liked_deals,
        "liked_news": liked_news,
    }
    return render(request, "users/liked_items.html", context)
