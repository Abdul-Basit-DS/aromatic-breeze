"""Contact form."""
from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('full_name', 'email', 'phone', 'subject', 'message')
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name *'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address *'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject *'}),
            'message': forms.Textarea(attrs={
                'rows': 5, 'placeholder': 'Your message...'
            }),
        }
