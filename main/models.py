from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

# =====================================================================
# 1. ПРОФІЛЬ КОРИСТУВАЧА
# =====================================================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    # Динамічний підрахунок середнього рейтингу продавця
    @property
    def average_rating(self):
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 2)
        return 5.0

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Якщо профілю немає, створюємо його, якщо є то оновлюємо
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# =====================================================================
# 2. КАТЕГОРІЇ ТА ПІДКАТЕГОРІЇ
# =====================================================================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


# =====================================================================
# 3. ОГОЛОШЕННЯ
# =====================================================================
class Listing(models.Model):
    class Condition(models.TextChoices):
        NEW = 'NEW', 'Нове'
        USED = 'USED', 'Вживане'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активне'
        SOLD = 'SOLD', 'Продано'
        ARCHIVED = 'ARCHIVED', 'В архіві'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UAH')
    
    condition = models.CharField(max_length=10, choices=Condition.choices, default=Condition.USED)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='listings')
    
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    olx_delivery = models.BooleanField(default=False)
    
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =====================================================================
# 4. ЗОБРАЖЕННЯ ОГОЛОШЕННЯ
# =====================================================================
class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.listing.title}"


# =====================================================================
# 5. ОБРАНЕ
# =====================================================================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.username} saved {self.listing.title}"


# =====================================================================
# 6. ВІДГУКИ ТА ОЦІНКИ
# =====================================================================
class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='left_reviews')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review from {self.author.username} to {self.target_user.username}"


# =====================================================================
# 7. СИСТЕМА ЧАТІВ ТА ПОВІДОМЛЕНЬ
# =====================================================================
class Chat(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='chats')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'buyer')

    def __str__(self):
        return f"Chat for {self.listing.title} (Buyer: {self.buyer.username})"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username}"
