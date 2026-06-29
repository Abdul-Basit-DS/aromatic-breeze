"""Reviews admin stub – full implementation in ZIP 6."""
from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    list_editable = ('is_approved',)
    search_fields = ('customer_name', 'customer_email', 'product__name')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approve selected reviews'
