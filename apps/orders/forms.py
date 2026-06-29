"""Checkout and order forms."""
from django import forms
from apps.accounts.models import Address


class CheckoutForm(forms.Form):
    """Main checkout form – shipping info + payment method."""
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'placeholder': 'Phone Number'}))
    address_line1 = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={'placeholder': 'Street Address / Area'}))
    address_line2 = forms.CharField(max_length=255, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'House/Flat No. (optional)'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'City'}))
    province = forms.ChoiceField(choices=[
        ('Punjab', 'Punjab'), ('Sindh', 'Sindh'),
        ('KPK', 'Khyber Pakhtunkhwa'), ('Balochistan', 'Balochistan'),
        ('AJK', 'Azad Jammu & Kashmir'), ('Gilgit-Baltistan', 'Gilgit-Baltistan'),
        ('ICT', 'Islamabad Capital Territory'),
    ])
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(
        max_length=100,
        initial='Pakistan',
        required=False,
        widget=forms.HiddenInput(attrs={'value': 'Pakistan'})
    )
    shipping_type = forms.ChoiceField(choices=[
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
    ], widget=forms.RadioSelect)
    payment_method = forms.ChoiceField(choices=[
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
    ], widget=forms.RadioSelect)
    coupon_code = forms.CharField(max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Coupon Code (optional)'}))
    customer_notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special instructions?'}))
    save_address = forms.BooleanField(required=False, initial=False)
