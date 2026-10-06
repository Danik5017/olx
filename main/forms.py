from django import forms
from .models import Listing, Profile

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
            'district': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': ''}),
            'olx_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'city', 'avatar']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': '+380...'}),
            'city': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'Ваше місто'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control py-2'}),
        }
