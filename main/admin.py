from django.contrib import admin
from .models import Profile, Category, Listing, ListingImage, Favorite, Review, Chat, Message

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 3

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'seller', 'status', 'condition', 'created_at')
    list_filter = ('status', 'condition', 'category', 'created_at')
    search_fields = ('title', 'description', 'city')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ListingImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'created_at')
    search_fields = ('user__username', 'phone_number', 'city')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'created_at')
    inlines = [MessageInline]

admin.site.register(Favorite)
admin.site.register(Review)
