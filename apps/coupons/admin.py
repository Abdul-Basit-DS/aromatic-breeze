"""Coupons admin."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value_display',
                    'minimum_purchase', 'times_used', 'usage_limit',
                    'valid_to', 'status_badge', 'is_active')
    list_filter = ('discount_type', 'is_active', 'first_order_only')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('times_used', 'created_at')

    fieldsets = (
        ('Coupon Info', {'fields': ('code', 'description', 'is_active')}),
        ('Discount', {'fields': ('discount_type', 'discount_value', 'max_discount_amount')}),
        ('Restrictions', {
            'fields': ('minimum_purchase', 'usage_limit', 'usage_limit_per_user',
                       'first_order_only', 'valid_from', 'valid_to')
        }),
        ('Stats', {'fields': ('times_used', 'created_at')}),
    )

    def discount_value_display(self, obj):
        if obj.discount_type == 'percentage':
            return f'{obj.discount_value}%'
        elif obj.discount_type == 'fixed':
            return f'Rs. {obj.discount_value}'
        return 'Free Shipping'
    discount_value_display.short_description = 'Discount'

    def status_badge(self, obj):
        if obj.is_expired:
            return format_html('<span style="color:#dc3545;">Expired</span>')
        if not obj.is_active:
            return format_html('<span style="color:#6c757d;">Inactive</span>')
        return format_html('<span style="color:#198754;">Active</span>')
    status_badge.short_description = 'Status'
