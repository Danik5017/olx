from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('listing/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('listing/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('listing/add/', views.create_listing_view, name='create_listing'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # URL системи повідомлень
    path('chats/', views.chats_list_view, name='chats_list'),
    path('chats/start/<int:listing_id>/', views.start_chat_view, name='start_chat'),
    path('chats/<int:pk>/', views.chat_detail_view, name='chat_detail'),
    path('chats/<int:pk>/send/', views.send_message_view, name='send_message'),
    path('chats/<int:pk>/updates/', views.get_new_messages_view, name='chat_updates'),
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
