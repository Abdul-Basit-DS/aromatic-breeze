"""
Admin configuration for Accounts app.
Full enterprise-grade admin with all management capabilities.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from import_export.admin import ExportMixin
from import_export import resources

from .models import User, UserProfile, Address, ActivityLog, Wishlist, WishlistItem


# ─── Import/Export Resources ──────────────────────────────────
class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone',
                  'role', 'is_active', 'is_blocked', 'date_joined', 'last_login')
        export_order = fields


# ─── Inline Admins ────────────────────────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('avatar', 'date_of_birth', 'gender',
              'newsletter_subscribed', 'marketing_emails')
    extra = 0


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'full_name', 'city', 'province', 'is_default')
    readonly_fields = ('created_at',)


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ('product', 'added_at')
    can_delete = False


# ─── User Admin ───────────────────────────────────────────────
@admin.register(User)
class UserAdmin(ExportMixin, BaseUserAdmin):
    resource_class = UserResource

    list_display = (
        'email', 'get_full_name', 'phone', 'role_badge',
        'is_active_badge', 'is_blocked_badge', 'total_orders_display',
        'total_spending_display', 'date_joined'
    )
    list_filter = ('role', 'is_active', 'is_blocked', 'email_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    list_per_page = 25

    fieldsets = (
        (_('Account'), {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                       'is_blocked', 'email_verified', 'groups', 'user_permissions'),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone',
                       'role', 'password1', 'password2'),
        }),
    )

    inlines = [UserProfileInline, AddressInline]
    readonly_fields = ('date_joined', 'last_login')

    actions = ['activate_users', 'deactivate_users', 'block_users',
               'unblock_users', 'export_to_csv']

    # ─── Custom Display Methods ───────────────────────────────
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def role_badge(self, obj):
        colors = {
            'super_admin': '#dc3545',
            'admin': '#fd7e14',
            'order_manager': '#0d6efd',
            'content_manager': '#6f42c1',
            'customer_support': '#20c997',
            'marketing_manager': '#d63384',
            'inventory_manager': '#0dcaf0',
            'customer': '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">✓ Active</span>')
        return format_html('<span style="color:red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Active'

    def is_blocked_badge(self, obj):
        if obj.is_blocked:
            return format_html('<span style="color:red;">🔒 Blocked</span>')
        return format_html('<span style="color:green;">✓ OK</span>')
    is_blocked_badge.short_description = 'Status'

    def total_orders_display(self, obj):
        count = obj.orders.count()
        if count:
            url = reverse('admin:orders_order_changelist') + f'?user__id__exact={obj.pk}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return '0 orders'
    total_orders_display.short_description = 'Orders'

    def total_spending_display(self, obj):
        total = obj.total_spending
        return f'Rs. {total:,.0f}'
    total_spending_display.short_description = 'Total Spent'

    # ─── Bulk Actions ─────────────────────────────────────────
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

    def block_users(self, request, queryset):
        updated = queryset.update(is_blocked=True, is_active=False)
        self.message_user(request, f'{updated} user(s) blocked.')
    block_users.short_description = 'Block selected users'

    def unblock_users(self, request, queryset):
        updated = queryset.update(is_blocked=False, is_active=True)
        self.message_user(request, f'{updated} user(s) unblocked.')
    unblock_users.short_description = 'Unblock selected users'


# ─── Address Admin ────────────────────────────────────────────
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'address_type', 'city',
                    'province', 'is_default')
    list_filter = ('address_type', 'is_default', 'province', 'country')
    search_fields = ('full_name', 'user__email', 'city', 'phone')
    raw_id_fields = ('user',)
    list_per_page = 25


# ─── Activity Log Admin ───────────────────────────────────────
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_display', 'action', 'module',
                    'description_short', 'ip_address')
    list_filter = ('action', 'module', 'timestamp')
    search_fields = ('user__email', 'description', 'ip_address')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 50
    readonly_fields = ('user', 'action', 'module', 'description',
                       'old_value', 'new_value', 'ip_address',
                       'user_agent', 'timestamp')

    def has_add_permission(self, request):
        return False  # Logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False

    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.get_full_name(), obj.user.email
            )
        return 'Anonymous'
    user_display.short_description = 'User'

    def description_short(self, obj):
        return (obj.description[:80] + '...') if len(obj.description) > 80 else obj.description
    description_short.short_description = 'Description'


# ─── Wishlist Admin ───────────────────────────────────────────
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WishlistItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def has_add_permission(self, request):
        return False
