"""
Accounts models for The Aromatic Breeze.
Custom User model + Profile + Address + ActivityLog.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class UserManager(BaseUserManager):
    """Custom manager using email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required.'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based access control.
    Email is the unique identifier instead of username.
    """
    # ─── Roles ────────────────────────────────────────────────
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    ORDER_MANAGER = 'order_manager'
    CONTENT_MANAGER = 'content_manager'
    CUSTOMER_SUPPORT = 'customer_support'
    MARKETING_MANAGER = 'marketing_manager'
    INVENTORY_MANAGER = 'inventory_manager'
    CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (SUPER_ADMIN, _('Super Admin')),
        (ADMIN, _('Admin')),
        (ORDER_MANAGER, _('Order Manager')),
        (CONTENT_MANAGER, _('Content Manager')),
        (CUSTOMER_SUPPORT, _('Customer Support')),
        (MARKETING_MANAGER, _('Marketing Manager')),
        (INVENTORY_MANAGER, _('Inventory Manager')),
        (CUSTOMER, _('Customer')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    role = models.CharField(
        _('role'), max_length=30, choices=ROLE_CHOICES, default=CUSTOMER
    )

    # ─── Status ───────────────────────────────────────────────
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_blocked = models.BooleanField(_('blocked'), default=False)
    email_verified = models.BooleanField(_('email verified'), default=False)

    # ─── Timestamps ───────────────────────────────────────────
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name

    @property
    def is_admin_user(self):
        return self.role in [self.SUPER_ADMIN, self.ADMIN]

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def total_spending(self):
        from apps.orders.models import Order
        result = self.orders.filter(
            payment_status='paid'
        ).aggregate(total=models.Sum('grand_total'))
        return result['total'] or 0


class UserProfile(models.Model):
    """Extended profile information for customers."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    avatar = ProcessedImageField(
        upload_to='avatars/',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 90},
        null=True, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True
    )
    bio = models.TextField(blank=True)

    # ─── Newsletter & Marketing ───────────────────────────────
    newsletter_subscribed = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=True)

    # ─── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class Address(models.Model):
    """Customer address book – supports multiple addresses per user."""
    HOME = 'home'
    OFFICE = 'office'
    GIFT = 'gift'
    OTHER = 'other'

    ADDRESS_TYPE_CHOICES = [
        (HOME, _('Home')),
        (OFFICE, _('Office')),
        (GIFT, _('Gift Address')),
        (OTHER, _('Other')),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses'
    )
    address_type = models.CharField(
        max_length=10, choices=ADDRESS_TYPE_CHOICES, default=HOME
    )
    label = models.CharField(max_length=50, blank=True,
                             help_text="Custom label e.g. 'Mama's house'")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Pakistan')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} – {self.city}, {self.province}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)

    def get_full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts += [self.city, self.province]
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.country)
        return ', '.join(parts)


class ActivityLog(models.Model):
    """
    Audit log for both admin actions and customer activities.
    Records every important action with context.
    """
    # ─── Action types ─────────────────────────────────────────
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    PASSWORD_RESET = 'password_reset'
    PROFILE_UPDATE = 'profile_update'
    ORDER_PLACED = 'order_placed'
    ORDER_CANCELLED = 'order_cancelled'
    REVIEW_SUBMITTED = 'review_submitted'
    WISHLIST_ADD = 'wishlist_add'
    WISHLIST_REMOVE = 'wishlist_remove'
    PRODUCT_CREATE = 'product_create'
    PRODUCT_UPDATE = 'product_update'
    PRODUCT_DELETE = 'product_delete'
    ORDER_UPDATE = 'order_update'
    REVIEW_APPROVE = 'review_approve'
    REVIEW_REJECT = 'review_reject'
    BLOG_PUBLISH = 'blog_publish'
    BANNER_CHANGE = 'banner_change'
    CUSTOMER_DELETE = 'customer_delete'
    CUSTOMER_BLOCK = 'customer_block'
    COUPON_CREATE = 'coupon_create'
    SETTINGS_UPDATE = 'settings_update'
    OTHER = 'other'

    ACTION_CHOICES = [
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (PASSWORD_CHANGE, 'Password Change'),
        (PASSWORD_RESET, 'Password Reset'),
        (PROFILE_UPDATE, 'Profile Update'),
        (ORDER_PLACED, 'Order Placed'),
        (ORDER_CANCELLED, 'Order Cancelled'),
        (REVIEW_SUBMITTED, 'Review Submitted'),
        (WISHLIST_ADD, 'Wishlist Add'),
        (WISHLIST_REMOVE, 'Wishlist Remove'),
        (PRODUCT_CREATE, 'Product Create'),
        (PRODUCT_UPDATE, 'Product Update'),
        (PRODUCT_DELETE, 'Product Delete'),
        (ORDER_UPDATE, 'Order Update'),
        (REVIEW_APPROVE, 'Review Approve'),
        (REVIEW_REJECT, 'Review Reject'),
        (BLOG_PUBLISH, 'Blog Publish'),
        (BANNER_CHANGE, 'Banner Change'),
        (CUSTOMER_DELETE, 'Customer Delete'),
        (CUSTOMER_BLOCK, 'Customer Block'),
        (COUPON_CREATE, 'Coupon Create'),
        (SETTINGS_UPDATE, 'Settings Update'),
        (OTHER, 'Other'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    module = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    old_value = models.JSONField(null=True, blank=True,
                                 help_text="Value before change (for audit)")
    new_value = models.JSONField(null=True, blank=True,
                                 help_text="Value after change (for audit)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Activity Log')
        verbose_name_plural = _('Activity Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_str} – {self.get_action_display()} – {self.timestamp:%Y-%m-%d %H:%M}"

    @classmethod
    def log(cls, user, action, description, module='', old_value=None,
            new_value=None, ip_address=None, user_agent=''):
        """Convenience class method to create log entries."""
        return cls.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )


class Wishlist(models.Model):
    """Customer wishlist – products saved for future purchase."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='wishlist'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')

    def __str__(self):
        return f"Wishlist of {self.user.get_full_name()}"

    def get_item_count(self):
        return self.items.count()


class WishlistItem(models.Model):
    """Individual product inside a customer's wishlist."""
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        'shop.Product', on_delete=models.CASCADE, related_name='wishlist_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.get_full_name()}'s wishlist"
