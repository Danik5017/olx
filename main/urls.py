from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка та деталі оголошення
    path('', views.index_view, name='index'),
    path('search/', views.search_listings_view, name='search_listings'),  # Окрема сторінка пошуку
    path('listing/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('listing/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('listing/add/', views.create_listing_view, name='create_listing'),
    path('favorites/', views.favorites_view, name='favorites'),

    # Додаємо два шляхи з ОДНАКОВИМ ім'ям 'profile'
    path('profile/', views.profile_view, name='profile'),  # Тепер {% url 'profile' %} без аргументів не буде падати!
    path('profile/<int:user_id>/', views.profile_view, name='profile'),  # Для перегляду чужих профілів з ID
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<int:user_id>/add-review/', views.add_review_view, name='add_review'),
    
    # Додаємо шлях для перегляду відгуків користувача
    path('profile/<int:user_id>/reviews/', views.user_reviews_view, name='user_reviews'),
    
    # URL системи повідомлень
    path('chats/', views.chats_list_view, name='chats_list'),
    path('chats/start/<int:listing_id>/', views.start_chat_view, name='start_chat'),
    path('chats/<int:pk>/', views.chat_detail_view, name='chat_detail'),
    path('chats/<int:pk>/send/', views.send_message_view, name='send_message'),
    path('chats/<int:pk>/updates/', views.get_new_messages_view, name='chat_updates'),

    # Аутентифікація
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('terms/', views.terms_view, name='terms'),
]
