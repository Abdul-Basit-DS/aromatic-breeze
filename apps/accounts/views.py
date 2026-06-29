"""
Views for the Accounts app.
Customer dashboard, profile, addresses, orders, wishlist, reviews.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from .models import UserProfile, Address, ActivityLog, Wishlist, WishlistItem
from .forms import UserProfileForm, AddressForm, CustomPasswordChangeForm

User = get_user_model()


def get_client_ip(request):
    """Extract real client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ─── Dashboard ────────────────────────────────────────────────
@login_required
def dashboard(request):
    """Customer dashboard – overview of orders, wishlist, reviews."""
    user = request.user
    recent_orders = user.orders.order_by('-created_at')[:5]
    wishlist_items = []
    try:
        wishlist_items = user.wishlist.items.select_related('product')[:4]
    except Wishlist.DoesNotExist:
        pass
    recent_reviews = user.reviews.order_by('-created_at')[:3]

    context = {
        'page_title': 'My Dashboard',
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'recent_reviews': recent_reviews,
        'total_orders': user.orders.count(),
        'total_spending': user.total_spending,
        'wishlist_count': user.wishlist.items.count() if hasattr(user, 'wishlist') else 0,
    }
    return render(request, 'accounts/dashboard.html', context)


# ─── Profile ──────────────────────────────────────────────────
@login_required
def profile(request):
    """View and update user profile."""
    user = request.user
    profile_obj, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, request.FILES, instance=profile_obj, user=user
        )
        if form.is_valid():
            form.save()
            ActivityLog.log(
                user=user,
                action=ActivityLog.PROFILE_UPDATE,
                description=f'User {user.email} updated their profile.',
                module='accounts',
                ip_address=get_client_ip(request),
            )
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile_obj, user=user)

    return render(request, 'accounts/profile.html', {'form': form, 'page_title': 'My Profile'})


# ─── Addresses ────────────────────────────────────────────────
@login_required
def address_list(request):
    """List all saved addresses."""
    addresses = request.user.addresses.all()
    return render(request, 'accounts/addresses.html', {
        'addresses': addresses,
        'page_title': 'My Addresses',
    })


@login_required
def address_add(request):
    """Add a new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('Address added successfully.'))
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {
        'form': form, 'page_title': 'Add Address'
    })


@login_required
def address_edit(request, pk):
    """Edit an existing address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address updated successfully.'))
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {
        'form': form, 'page_title': 'Edit Address'
    })


@login_required
def address_delete(request, pk):
    """Delete an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, _('Address removed.'))
    return redirect('accounts:addresses')


@login_required
@require_POST
def address_set_default(request, pk):
    """Set an address as default via AJAX."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    return JsonResponse({'status': 'ok', 'message': 'Default address updated.'})


# ─── Orders ───────────────────────────────────────────────────
@login_required
def my_orders(request):
    """List all customer orders with pagination."""
    orders = request.user.orders.order_by('-created_at')
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders_page = paginator.get_page(page)
    return render(request, 'accounts/my_orders.html', {
        'orders': orders_page,
        'page_title': 'My Orders',
    })


@login_required
def order_detail(request, order_number):
    """Single order detail view."""
    order = get_object_or_404(
        request.user.orders, order_number=order_number
    )
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'page_title': f'Order #{order.order_number}',
    })


# ─── Wishlist ─────────────────────────────────────────────────
@login_required
def wishlist(request):
    """View wishlist."""
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist_obj.items.select_related('product').all()
    return render(request, 'accounts/wishlist.html', {
        'items': items,
        'page_title': 'My Wishlist',
    })


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    """Add or remove product from wishlist (AJAX)."""
    from apps.shop.models import Product
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)

    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist_obj, product=product
    )
    if created:
        action = ActivityLog.WISHLIST_ADD
        msg = f'{product.name} added to wishlist.'
        status = 'added'
    else:
        item.delete()
        action = ActivityLog.WISHLIST_REMOVE
        msg = f'{product.name} removed from wishlist.'
        status = 'removed'

    ActivityLog.log(
        user=request.user,
        action=action,
        description=msg,
        module='accounts',
    )

    count = wishlist_obj.items.count()
    return JsonResponse({
        'status': status,
        'message': msg,
        'wishlist_count': count,
    })


# ─── Password Change ──────────────────────────────────────────
@login_required
def change_password(request):
    """Allow logged-in user to change their password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            ActivityLog.log(
                user=request.user,
                action=ActivityLog.PASSWORD_CHANGE,
                description='User changed their password.',
                module='accounts',
                ip_address=get_client_ip(request),
            )
            messages.success(request, _('Password changed successfully. Please log in again.'))
            logout(request)
            return redirect('account_login')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form, 'page_title': 'Change Password'
    })


# ─── My Reviews ───────────────────────────────────────────────
@login_required
def my_reviews(request):
    """List all reviews submitted by the customer."""
    reviews = request.user.reviews.select_related('product').order_by('-created_at')
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    return render(request, 'accounts/my_reviews.html', {
        'reviews': paginator.get_page(page),
        'page_title': 'My Reviews',
    })
