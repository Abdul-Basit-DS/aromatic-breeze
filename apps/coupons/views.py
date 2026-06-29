"""Coupon validation view."""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Coupon


@require_POST
def validate_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    subtotal = float(request.POST.get('subtotal', 0))
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        if coupon.is_valid(subtotal):
            discount = coupon.calculate_discount(subtotal)
            return JsonResponse({
                'valid': True,
                'discount': float(discount),
                'type': coupon.discount_type,
                'message': f'Coupon applied! You save Rs. {discount:,.0f}',
            })
        return JsonResponse({'valid': False, 'message': 'Coupon is not valid for this order.'})
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid coupon code.'})
