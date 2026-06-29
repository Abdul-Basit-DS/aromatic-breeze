"""Coupons models – complete coupon system."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Coupon(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    FREE_SHIPPING = 'free_shipping'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Percentage Discount'),
        (FIXED, 'Fixed Amount Discount'),
        (FREE_SHIPPING, 'Free Shipping'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=PERCENTAGE
    )
    discount_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Percentage (0-100) or fixed amount in Rs."
    )
    max_discount_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Max discount cap for percentage coupons"
    )
    minimum_purchase = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Minimum cart value to apply this coupon"
    )
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Max total uses. Leave blank for unlimited."
    )
    usage_limit_per_user = models.PositiveIntegerField(
        default=1, help_text="Max uses per customer"
    )
    times_used = models.PositiveIntegerField(default=0, editable=False)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    # Restrictions
    first_order_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    def is_valid(self, cart_total=0, user=None):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if now < self.valid_from:
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        if cart_total < self.minimum_purchase:
            return False
        return True

    def calculate_discount(self, cart_total):
        if self.discount_type == self.PERCENTAGE:
            discount = (cart_total * self.discount_value) / 100
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        elif self.discount_type == self.FIXED:
            return min(self.discount_value, cart_total)
        elif self.discount_type == self.FREE_SHIPPING:
            return 0  # Shipping handled separately
        return 0

    @property
    def is_expired(self):
        return self.valid_to and timezone.now() > self.valid_to
