"""Review form – stub for ZIP 2. Full implementation in ZIP 6."""
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Review
        fields = ('customer_name', 'customer_email', 'rating', 'title', 'body')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }
