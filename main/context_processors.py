from .models import Favorite

def favorites_counter_processor(request):
    # Якщо користувач залогінений, рахуємо його записи в таблиці Favorite
    if request.user.is_authenticated:
        favorites_count = Favorite.objects.filter(user=request.user).count()
    else:
        favorites_count = 0
        
    return {
        'global_favorites_count': favorites_count
    }
