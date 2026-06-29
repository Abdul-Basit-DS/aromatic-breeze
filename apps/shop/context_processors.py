"""Context processors for shop – cart count and wishlist count."""
from .models import Cart


def cart_context(request):
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(
                user=request.user
            ).values_list('quantity', flat=True)
            cart_count = sum(cart_count)
        elif request.session.session_key:
            cart_count = Cart.objects.filter(
                session_key=request.session.session_key
            ).values_list('quantity', flat=True)
            cart_count = sum(cart_count)
    except Exception:
        cart_count = 0
    return {'cart_count': cart_count}


def wishlist_context(request):
    wishlist_count = 0
    try:
        if request.user.is_authenticated:
            wishlist_count = request.user.wishlist.items.count()
    except Exception:
        pass
    return {'wishlist_count': wishlist_count}
