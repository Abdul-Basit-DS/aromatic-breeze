"""
Orders views – Checkout, Order Success, Order Detail, Invoice PDF, Return Request.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderItem, OrderStatusHistory, ShippingZone, ReturnRequest
from .forms import CheckoutForm
from apps.shop.models import Cart, Product, ProductVariation
from apps.shop.views import get_cart_items, get_cart_summary
from apps.accounts.models import ActivityLog, Address


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


# ─── Checkout ─────────────────────────────────────────────────
def checkout(request):
    """Full checkout page with address, shipping, payment selection."""
    cart_summary = get_cart_summary(request)
    if not cart_summary['items']:
        messages.warning(request, _('Your cart is empty.'))
        return redirect('shop:cart')

    saved_addresses = []
    if request.user.is_authenticated:
        saved_addresses = request.user.addresses.all()

    # Get applicable shipping zones
    shipping_zones = ShippingZone.objects.filter(is_active=True)
    subtotal = cart_summary['subtotal']

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            return _process_checkout(request, form, cart_summary)
    else:
        # Pre-fill from default address if logged in
        initial = {}
        if request.user.is_authenticated:
            default_addr = request.user.addresses.filter(is_default=True).first()
            if default_addr:
                initial = {
                    'full_name': default_addr.full_name,
                    'phone': default_addr.phone,
                    'address_line1': default_addr.address_line1,
                    'address_line2': default_addr.address_line2,
                    'city': default_addr.city,
                    'province': default_addr.province,
                    'postal_code': default_addr.postal_code,
                }
            initial['email'] = request.user.email
        form = CheckoutForm(initial=initial)

    context = {
        'page_title': 'Checkout',
        'form': form,
        'cart_items': cart_summary['items'],
        'subtotal': subtotal,
        'saved_addresses': saved_addresses,
        'shipping_zones': shipping_zones,
    }
    return render(request, 'orders/checkout.html', context)


@transaction.atomic
def _process_checkout(request, form, cart_summary):
    """Create order from cart and form data."""
    data = form.cleaned_data
    cart_items = cart_summary['items']
    subtotal = cart_summary['subtotal']

    # Apply coupon if provided
    coupon_code = data.get('coupon_code', '').strip().upper()
    coupon_discount = 0
    if coupon_code:
        from apps.coupons.models import Coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_valid(subtotal):
                coupon_discount = coupon.calculate_discount(subtotal)
                coupon.times_used += 1
                coupon.save(update_fields=['times_used'])
        except Exception:
            pass

    # Calculate shipping
    shipping_charge = _calculate_shipping(
        data['city'], data['shipping_type'], subtotal
    )
    cod_charge = 0
    if data['payment_method'] == 'cod':
        zone = ShippingZone.objects.filter(
            cities__icontains=data['city']
        ).first()
        if zone:
            cod_charge = zone.cod_charge

    grand_total = subtotal - coupon_discount + shipping_charge + cod_charge

    # Create Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=data['full_name'],
        customer_email=data['email'],
        customer_phone=data['phone'],
        shipping_full_name=data['full_name'],
        shipping_phone=data['phone'],
        shipping_address_line1=data['address_line1'],
        shipping_address_line2=data.get('address_line2', ''),
        shipping_city=data['city'],
        shipping_province=data['province'],
        shipping_postal_code=data.get('postal_code', ''),
        shipping_country=data.get('country', 'Pakistan'),
        payment_method=data['payment_method'],
        payment_status=Order.PAYMENT_COD if data['payment_method'] == 'cod' else Order.PAYMENT_PENDING,
        shipping_type=data['shipping_type'],
        subtotal=subtotal,
        coupon_code=coupon_code,
        coupon_discount=coupon_discount,
        shipping_charge=shipping_charge,
        cod_charge=cod_charge,
        grand_total=grand_total,
        customer_notes=data.get('customer_notes', ''),
    )

    # Create OrderItems & reduce stock
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variation=cart_item.variation,
            product_name=cart_item.product.name,
            variation_name=cart_item.variation.name if cart_item.variation else '',
            sku=cart_item.variation.sku if cart_item.variation else cart_item.product.sku,
            unit_price=cart_item.unit_price,
            quantity=cart_item.quantity,
        )
        # Reduce stock
        if cart_item.variation:
            ProductVariation.objects.filter(pk=cart_item.variation.pk).update(
                stock=max(0, cart_item.variation.stock - cart_item.quantity)
            )
        else:
            Product.objects.filter(pk=cart_item.product.pk).update(
                stock=max(0, cart_item.product.stock - cart_item.quantity)
            )

    # Save address if requested
    if data.get('save_address') and request.user.is_authenticated:
        Address.objects.get_or_create(
            user=request.user,
            address_line1=data['address_line1'],
            city=data['city'],
            defaults={
                'full_name': data['full_name'],
                'phone': data['phone'],
                'address_line2': data.get('address_line2', ''),
                'province': data['province'],
                'postal_code': data.get('postal_code', ''),
            }
        )

    # Clear cart
    cart_items.delete()

    # Initial status history
    OrderStatusHistory.objects.create(
        order=order,
        new_status=Order.PENDING,
        note='Order placed by customer.'
    )

    # Log activity
    ActivityLog.log(
        user=request.user if request.user.is_authenticated else None,
        action=ActivityLog.ORDER_PLACED,
        module='orders',
        description=f'Order {order.order_number} placed. Total: Rs. {grand_total}',
        ip_address=get_client_ip(request),
    )

    # Send confirmation email
    _send_order_confirmation(order)

    return redirect('orders:order_success', order_number=order.order_number)


def _calculate_shipping(city, shipping_type, subtotal):
    """Calculate shipping charge based on city and order amount."""
    zone = ShippingZone.objects.filter(
        cities__icontains=city, is_active=True
    ).first()
    if not zone:
        # Default national shipping
        return 0 if subtotal >= 2500 else 200

    if subtotal >= zone.free_shipping_threshold:
        return 0
    return zone.express_charge if shipping_type == 'express' else zone.standard_charge


def _send_order_confirmation(order):
    try:
        from django.core.mail import EmailMessage
        
        # Customer email
        customer_msg = EmailMessage(
            subject=f'Order Confirmed #{order.order_number} – The Aromatic Breeze',
            body=f"""Assalam-o-Alaikum {order.customer_name},

Aapka order successfully place ho gaya hai!

Order Number: #{order.order_number}
Total Amount: Rs. {order.grand_total}
Payment Method: {order.get_payment_method_display()}
Delivery Address: {order.shipping_address_line1}, {order.shipping_city}

Hum aapke order ko jald dispatch karein ge.

Shukriya!
The Aromatic Breeze Team
support@thearomaticbreeze.com
+92-300-0000000""",
            from_email='The Aromatic Breeze <support@thearomaticbreeze.com>',
            to=[order.customer_email],
        )
        customer_msg.send(fail_silently=False)
        print(f'Customer email sent to {order.customer_email}')

        # Admin email
        admin_msg = EmailMessage(
            subject=f'New Order #{order.order_number} – Rs. {order.grand_total}',
            body=f"""New Order Received!

Order: #{order.order_number}
Customer: {order.customer_name}
Email: {order.customer_email}
Phone: {order.customer_phone}
City: {order.shipping_city}
Total: Rs. {order.grand_total}
Payment: {order.get_payment_method_display()}
Items: {order.items.count()}""",
            from_email='The Aromatic Breeze <support@thearomaticbreeze.com>',
            to=['support@thearomaticbreeze.com'],
        )
        admin_msg.send(fail_silently=False)
        print('Admin email sent')

    except Exception as e:
        print(f'EMAIL ERROR: {e}')

# ─── Order Success ────────────────────────────────────────────
def order_success(request, order_number):
    """Thank you page after successful order placement."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {
        'page_title': 'Order Placed!',
        'order': order,
    })


# ─── Order Detail (customer view) ────────────────────────────
def order_detail_public(request, order_number):
    """Order tracking page – accessible without login via order number + email."""
    order = None
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            order = Order.objects.get(
                order_number=order_number, customer_email__iexact=email
            )
        except Order.DoesNotExist:
            error = 'Order not found. Please check your order number and email.'

    return render(request, 'orders/order_tracking.html', {
        'page_title': f'Track Order #{order_number}',
        'order': order,
        'order_number': order_number,
        'error': error,
    })


# ─── Shipping Cost AJAX ───────────────────────────────────────
def shipping_cost(request):
    """Return shipping cost for a city via AJAX."""
    city = request.GET.get('city', '')
    shipping_type = request.GET.get('type', 'standard')
    subtotal = float(request.GET.get('subtotal', 0))

    charge = _calculate_shipping(city, shipping_type, subtotal)
    zone = ShippingZone.objects.filter(cities__icontains=city, is_active=True).first()
    cod_charge = float(zone.cod_charge) if zone else 0
    days = zone.express_days if shipping_type == 'express' else zone.standard_days if zone else '3-5 Days'

    return JsonResponse({
        'charge': float(charge),
        'cod_charge': cod_charge,
        'estimated_days': days,
        'free_shipping': charge == 0,
    })


# ─── Invoice PDF ──────────────────────────────────────────────
def invoice_pdf(request, order_number):
    """Generate and return PDF invoice for an order."""
    # Security: only order owner, admin, or staff can view
    order = get_object_or_404(Order, order_number=order_number)
    if not request.user.is_staff:
        if not request.user.is_authenticated:
            return redirect('account_login')
        if order.user != request.user:
            messages.error(request, 'You do not have permission to view this invoice.')
            return redirect('accounts:my_orders')

    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        html = render_to_string('orders/invoice_pdf.html', {
            'order': order,
            'items': order.items.all(),
        })
        result = BytesIO()
        pisa.CreatePDF(html, dest=result)
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="Invoice-{order.order_number}.pdf"'
        )
        return response
    except ImportError:
        # Fallback: HTML invoice
        return render(request, 'orders/invoice_pdf.html', {'order': order})


# ─── Return Request ───────────────────────────────────────────
@login_required
@require_POST
def submit_return_request(request, order_number):
    """Customer submits a return/refund request."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if not order.can_return():
        messages.error(request, 'This order is not eligible for return.')
        return redirect('accounts:order_detail', order_number=order_number)

    reason = request.POST.get('reason', 'other')
    description = request.POST.get('description', '')
    resolution = request.POST.get('resolution', 'refund')

    ReturnRequest.objects.create(
        order=order,
        reason=reason,
        description=description,
        resolution_requested=resolution,
    )

    # Notify admin
    send_mail(
        f'Return Request for Order #{order.order_number}',
        f'Customer {order.customer_name} submitted a return request.\nReason: {reason}\n{description}',
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=True,
    )

    messages.success(request, 'Return request submitted. Our team will review it shortly.')
    return redirect('accounts:order_detail', order_number=order_number)
