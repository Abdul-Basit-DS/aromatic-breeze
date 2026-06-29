"""
Orders models for The Aromatic Breeze.
Order, OrderItem, ShippingCharge, Coupon usage, Invoice.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
import random
import string

User = get_user_model()


def generate_order_number():
    """Generate unique order number like AB-2024-XXXX."""
    year = timezone.now().year
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"AB-{year}-{random_part}"


class ShippingZone(models.Model):
    """City/province based shipping charges."""
    name = models.CharField(max_length=100)
    cities = models.TextField(
        help_text="Comma-separated city names e.g. Lahore, Karachi, Islamabad"
    )
    standard_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    express_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cod_charge = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Extra charge for Cash on Delivery"
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=2500,
        help_text="Order amount above which shipping is free"
    )
    standard_days = models.CharField(max_length=50, default='3-5 Days')
    express_days = models.CharField(max_length=50, default='1-2 Days')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Shipping Zone')
        verbose_name_plural = _('Shipping Zones')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_cities_list(self):
        return [c.strip() for c in self.cities.split(',')]


class Order(models.Model):
    """Main order model with full lifecycle management."""

    # ─── Status choices ───────────────────────────────────────
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PACKED = 'packed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    OUT_FOR_DELIVERY = 'out_for_delivery'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    RETURNED = 'returned'
    REFUNDED = 'refunded'

    ORDER_STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (PACKED, _('Packed')),
        (PROCESSING, _('Processing')),
        (SHIPPED, _('Shipped')),
        (OUT_FOR_DELIVERY, _('Out for Delivery')),
        (DELIVERED, _('Delivered')),
        (CANCELLED, _('Cancelled')),
        (RETURNED, _('Returned')),
        (REFUNDED, _('Refunded')),
    ]

    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_COD = 'cod'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, _('Pending')),
        (PAYMENT_PAID, _('Paid')),
        (PAYMENT_FAILED, _('Failed')),
        (PAYMENT_REFUNDED, _('Refunded')),
        (PAYMENT_COD, _('Cash on Delivery')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', _('Cash on Delivery')),
        ('bank_transfer', _('Bank Transfer')),
        ('jazzcash', _('JazzCash')),
        ('easypaisa', _('EasyPaisa')),
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
    ]

    SHIPPING_CHOICES = [
        ('standard', _('Standard Delivery')),
        ('express', _('Express Delivery')),
    ]

    # ─── Identification ───────────────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=30, unique=True, default=generate_order_number, editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders'
    )

    # ─── Customer Info (snapshot at order time) ───────────────
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # ─── Shipping Address ─────────────────────────────────────
    shipping_full_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_province = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, default='Pakistan')

    # ─── Payment ──────────────────────────────────────────────
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod'
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING
    )
    payment_reference = models.CharField(max_length=200, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # ─── Order Status ─────────────────────────────────────────
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING
    )
    shipping_type = models.CharField(
        max_length=10, choices=SHIPPING_CHOICES, default='standard'
    )

    # ─── Pricing ──────────────────────────────────────────────
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cod_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ─── Coupon ───────────────────────────────────────────────
    coupon_code = models.CharField(max_length=50, blank=True)
    coupon_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # ─── Shipping / Tracking ──────────────────────────────────
    tracking_number = models.CharField(max_length=200, blank=True)
    courier_name = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.CharField(max_length=100, blank=True)

    # ─── Notes ────────────────────────────────────────────────
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # ─── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Order #{self.order_number} – {self.customer_name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('orders:order_detail', kwargs={'order_number': self.order_number})

    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'packed': 'info',
            'processing': 'primary',
            'shipped': 'primary',
            'out_for_delivery': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'returned': 'danger',
            'refunded': 'secondary',
        }
        return colors.get(self.status, 'secondary')

    def can_cancel(self):
        return self.status in [self.PENDING, self.CONFIRMED]

    def can_return(self):
        return self.status == self.DELIVERED

    def calculate_totals(self):
        """Recalculate order totals from line items."""
        subtotal = sum(item.total_price for item in self.items.all())
        self.subtotal = subtotal
        self.grand_total = (
            subtotal
            - self.discount_amount
            - self.coupon_discount
            + self.shipping_charge
            + self.cod_charge
            + self.tax_amount
        )
        self.save(update_fields=['subtotal', 'grand_total'])


class OrderItem(models.Model):
    """Individual line item within an order."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        'shop.Product', on_delete=models.SET_NULL, null=True,
        related_name='order_items'
    )
    variation = models.ForeignKey(
        'shop.ProductVariation', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    # Snapshot at order time (in case product changes later)
    product_name = models.CharField(max_length=200)
    variation_name = models.CharField(max_length=100, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class OrderStatusHistory(models.Model):
    """Track every status change for an order."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='status_history'
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    note = models.TextField(blank=True)
    customer_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status History')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.order_number}: {self.old_status} → {self.new_status}"


class ReturnRequest(models.Model):
    """Customer return/refund request."""
    REASON_CHOICES = [
        ('wrong_item', 'Wrong Item Received'),
        ('damaged', 'Damaged / Defective'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed My Mind'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    RESOLUTION_CHOICES = [
        ('refund', 'Refund'),
        ('replacement', 'Replacement'),
        ('store_credit', 'Store Credit'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='return_requests'
    )
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.SET_NULL, null=True, blank=True
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField()
    resolution_requested = models.CharField(
        max_length=20, choices=RESOLUTION_CHOICES, default='refund'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_returns'
    )
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Return Request')
        verbose_name_plural = _('Return Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"Return #{self.pk} for Order {self.order.order_number}"
