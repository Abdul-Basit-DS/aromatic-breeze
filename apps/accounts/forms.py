"""Forms for the Accounts app."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from allauth.account.forms import SignupForm

from .models import UserProfile, Address

User = get_user_model()


class CustomSignupForm(SignupForm):
    """Extended signup form with first name, last name, and phone."""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number (optional)'})
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.phone = self.cleaned_data.get('phone', '')
        user.save()
        # Create profile automatically
        UserProfile.objects.get_or_create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    """Form to update basic user info."""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = UserProfile
        fields = ('avatar', 'date_of_birth', 'gender',
                  'newsletter_subscribed', 'marketing_emails')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['phone'].initial = self.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.phone = self.cleaned_data.get('phone', '')
            self.user.save()
        if commit:
            profile.save()
        return profile


class AddressForm(forms.ModelForm):
    """Form for creating or updating a delivery address."""
    class Meta:
        model = Address
        fields = ('address_type', 'label', 'full_name', 'phone',
                  'address_line1', 'address_line2', 'city',
                  'province', 'postal_code', 'country', 'is_default')
        widgets = {
            'address_line1': forms.TextInput(attrs={'placeholder': 'Street, Area'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Flat/House No. (optional)'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Styled password change form."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
