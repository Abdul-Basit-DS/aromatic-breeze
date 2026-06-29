"""Blog comment form."""
from django import forms
from .models import BlogComment


class CommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ('name', 'email', 'website', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name *'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address *'}),
            'website': forms.URLInput(attrs={'placeholder': 'Website (optional)'}),
            'body': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write your comment here...'
            }),
        }
