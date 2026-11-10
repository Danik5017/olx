from django import forms
from django.contrib.auth.models import User
from .models import Listing, Profile

# =====================================================================
# 1. ФОРМА СТВОРЕННЯ ОГОЛОШЕННЯ (Твоя оригінальна)
# =====================================================================
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'price', 'condition', 'description', 'city', 'district', 'olx_delivery']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': ''}),
            'category': forms.Select(attrs={'class': 'form-select py-2'}),
            'price': forms.NumberInput(attrs={'class': 'form-control py-2', 'placeholder': '0'}),
            'condition': forms.Select(attrs={'class': 'form-select py-2'}),
            'description': forms.Textarea(attrs={'class': 'form-control py-2', 'rows': 5, 'placeholder': 'Опишіть свій товар...'}),
            'city': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': ''}),
            'olx_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# =====================================================================
# 2. ФОРМА ПРОФІЛЮ (Твоя оригінальна)
# =====================================================================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'city', 'avatar']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': '+380...'}),
            'city': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'Ваше місто'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control py-2'}),
        }


# =====================================================================
# 3. НОВА ФОРМА: РЕДАГУВАННЯ ДАНИХ АКАУНТА USER (Додано)
# =====================================================================
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Електронна пошта", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Нікнейм',
            'first_name': "Ім'я",
            'last_name': 'Прізвище'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control py-2'})


# =====================================================================
# 4. НОВА ФОРМА: РЕДАГУВАННЯ ПРОФІЛЮ (Додано)
# =====================================================================
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'city', 'avatar']
        labels = {
            'phone_number': 'Номер телефону',
            'city': 'Місто',
            'avatar': 'Фото профілю (Аватарка)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control py-2', 'placeholder': '+380...'})
        self.fields['city'].widget.attrs.update({'class': 'form-control py-2', 'placeholder': 'Ваше місто'})
        self.fields['avatar'].widget.attrs.update({'class': 'form-control py-2'})
