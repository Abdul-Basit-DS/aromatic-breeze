from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from apps.shop.models import Product

def submit_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
                review.customer_name = review.customer_name or request.user.get_full_name()
                review.customer_email = review.customer_email or request.user.email
            review.save()
            messages.success(request, 'Thank you! Your review has been submitted and is awaiting approval.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return redirect(product.get_absolute_url() + '#reviews')
