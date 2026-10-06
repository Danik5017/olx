from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Listing, Category, ListingImage, Favorite, Profile, Chat, Message
from .forms import ListingForm, ProfileForm

def index_view(request):
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
        
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'listings': listings.distinct(),
        'categories': categories,
        'search_query': search_query,
        'location_query': location_query,
        'selected_category': category_id,
    })

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

@login_required
def profile_view(request):
    my_listings = Listing.objects.filter(seller=request.user)
    return render(request, 'profile.html', {'my_listings': my_listings})

@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

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
    
    messages = chat.messages.all()
    chat.messages.exclude(sender=request.user).update(is_read=True)
    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required
def send_message_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    if chat.buyer != request.user and chat.listing.seller != request.user:
        return HttpResponse(status=403)
        
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            message = Message.objects.create(chat=chat, sender=request.user, text=text)
            return render(request, 'partials/message_item.html', {'message': message})
    return HttpResponse(status=400)

@login_required
def get_new_messages_view(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    if chat.buyer != request.user and chat.listing.seller != request.user:
        return HttpResponse(status=403)
    
    messages = chat.messages.all()
    chat.messages.exclude(sender=request.user).update(is_read=True)
    return render(request, 'partials/messages_loop.html', {'messages': messages})
