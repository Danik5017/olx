from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import Listing, Category, ListingImage, Favorite, Profile, Chat, Message, Review
from .forms import ListingForm, ProfileForm, UserUpdateForm, ProfileUpdateForm

# =====================================================================
# 1. ГОЛОВНА СТОРІНКА ТА ПОШУК
# =====================================================================
def index_view(request):
    """ Головна сторінка сайту зі стрічкою всіх оголошень """
    listings = Listing.objects.filter(status='ACTIVE')
    search_query = request.GET.get('search', '')
    location_query = request.GET.get('location', '')
    category_id = request.GET.get('category', '')
    
    if search_query:
        listings = listings.filter(title__icontains=search_query) | listings.filter(description__icontains=search_query)
    if location_query:
        listings = listings.filter(city__icontains=location_query)
    if category_id:
        listings = listings.filter(category_id=category_id)
        
    # Беремо лише кореневі категорії для виведення на головній (наприклад, іконками)
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    
    return render(request, 'index.html', {
        'listings': listings.distinct(),
        'categories': categories,
        'search_query': search_query,
        'location_query': location_query,
        'selected_category': category_id,
    })


def search_listings_view(request):
    """ Окрема нова сторінка розширеного пошуку з OLX-фільтрами """
    query = request.GET.get('q', '').strip()
    listings = Listing.objects.filter(status='ACTIVE')
    
    # 1. Пошук за назвою або описом
    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    # 2. Фільтр за категорією або її підкатегоріями
    category_id = request.GET.get('category')
    if category_id:
        listings = listings.filter(Q(category_id=category_id) | Q(category__parent_id=category_id))
        
    # 3. Додаткові фільтри (ціна, стан, місто)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min: 
        listings = listings.filter(price__gte=price_min)
    if price_max: 
        listings = listings.filter(price__lte=price_max)
        
    condition = request.GET.get('condition')
    if condition: 
        listings = listings.filter(condition=condition)
        
    city = request.GET.get('city')
    if city: 
        listings = listings.filter(city__icontains=city)

    # Збираємо всі головні категорії з підкатегоріями для лівого випадаючого списку
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')

    context = {
        'listings': listings.distinct(),
        'query': query,
        'current_category': category_id,
        'categories': categories  # Передаємо категорії для правильного селекту
    }
    return render(request, 'search_results.html', context) # Рендерить нову окрему сторінку!

# =====================================================================
# 2. ДЕТАЛІ ОГОЛОШЕННЯ ТА ОБРАНЕ
# =====================================================================
def product_detail_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    
    viewed_listings = request.session.get('viewed_listings', [])
    if listing.id not in viewed_listings:
        listing.views_count += 1
        listing.save(update_fields=['views_count'])
        viewed_listings.append(listing.id)
        request.session['viewed_listings'] = viewed_listings

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, listing=listing).exists()
    
    return render(request, 'product_detail.html', {
        'listing': listing,
        'is_favorite': is_favorite
    })

@login_required
def toggle_favorite_view(request, pk):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
        
        if not created:
            favorite.delete()
            is_favorite = False
            if request.headers.get('HX-Trigger') == f'fav-card-{listing.id}':
                return HttpResponse("")
        else:
            is_favorite = True
            
        return render(request, 'partials/favorite_heart.html', {'is_favorite': is_favorite})
    return redirect('index')

@login_required
def favorites_view(request):
    favorite_items = Favorite.objects.filter(user=request.user).select_related('listing')
    return render(request, 'favorites.html', {'favorite_items': favorite_items})


# =====================================================================
# 3. СТВОРЕННЯ ОГОЛОШЕНЬ
# =====================================================================
@login_required
def create_listing_view(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            for i, f in enumerate(files):
                ListingImage.objects.create(listing=listing, image=f, is_main=(i == 0))
            return redirect('product_detail', pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})


# =====================================================================
# 4. СИСТЕМА ПРОФІЛІВ ТА ВІДГУКІВ
# =====================================================================
def profile_view(request, user_id=None):
    """ Завантажує профіль за ID або відкриває власний профіль поточного користувача """
    if user_id is None:
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            return redirect('login')

    target_user = get_object_or_404(User, id=user_id)
    my_listings = Listing.objects.filter(seller=target_user)
    reviews = target_user.received_reviews.all()
    avg_rating = target_user.profile.average_rating
    
    return render(request, 'profile.html', {
        'my_listings': my_listings,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'target_user': target_user
    })

@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile', user_id=request.user.id)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    return render(request, 'edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

@login_required
def add_review_view(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if request.user != target_user:
            rating = request.POST.get('rating')
            text = request.POST.get('text')
            if rating:
                Review.objects.create(
                    author=request.user,
                    target_user=target_user,
                    rating=int(rating),
                    text=text
                )
    return redirect('profile', user_id=user_id)


# =====================================================================
# 5. АУТЕНТИФІКАЦІЯ ТА РЕЄСТРАЦІЯ
# =====================================================================
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')


# =====================================================================
# 6. СИСТЕМА ЧАТІВ ТА ПОВІДОМЛЕНЬ
# =====================================================================
@login_required
def chats_list_view(request):
    buying_chats = Chat.objects.filter(buyer=request.user).select_related('listing', 'listing__seller')
    selling_chats = Chat.objects.filter(listing__seller=request.user).select_related('listing', 'buyer')
    return render(request, 'chats_list.html', {
        'buying_chats': buying_chats,
        'selling_chats': selling_chats
    })

@login_required
def start_chat_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if listing.seller == request.user:
        return redirect('product_detail', pk=listing.id)
    chat, created = Chat.objects.get_or_create(listing=listing, buyer=request.user)
    return redirect('chat_detail', pk=chat.id)

@login_required
def chat_detail_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    if chat.buyer != request.user and chat.listing.seller != request.user:
        return redirect('index')
    
    messages_list = chat.messages.all()
    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages_list': messages_list
    })

@login_required
def send_message_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                chat=chat, 
                sender=request.user, 
                text=text
            )
            return redirect('chat_detail', pk=chat.id)
    return redirect('chat_detail', pk=chat.id)

def get_new_messages_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    messages_list = chat.messages.all()
    return render(request, 'partials/messages_list.html', {'messages_list': messages_list})


# =====================================================================
# 7. ДОДАТКОВІ СТОРІНКИ
# =====================================================================
def terms_view(request):
    return render(request, 'terms.html')