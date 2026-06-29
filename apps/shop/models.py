"""
Shop models for The Aromatic Breeze.
Category, Product, ProductVariation, ProductImage, Banner, TrustFeature, Cart.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count
from mptt.models import MPTTModel, TreeForeignKey
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

User = get_user_model()


# ─── Category ─────────────────────────────────────────────────
class Category(MPTTModel):
    """
    Hierarchical product category using MPTT.
    Supports unlimited nesting (Men > Arabic > Oud etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = ProcessedImageField(
        upload_to='categories/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )
    icon = models.CharField(max_length=100, blank=True,
                            help_text="FontAwesome class e.g. fa-spray-can")
    parent = TreeForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='children'
    )
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    # Settings
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['display_order', 'name']

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})

    def get_product_count(self):
        return Product.objects.filter(
            categories=self, is_active=True
        ).count()


# ─── Fragrance Family ─────────────────────────────────────────
class FragranceFamily(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Fragrance Family')
        verbose_name_plural = _('Fragrance Families')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ─── Product ──────────────────────────────────────────────────
class Product(models.Model):
    GENDER_CHOICES = [
        ('men', _('Men')),
        ('women', _('Women')),
        ('unisex', _('Unisex')),
        ('kids', _('Kids')),
    ]
    CONCENTRATION_CHOICES = [
        ('edp', 'Eau de Parfum (EDP)'),
        ('edt', 'Eau de Toilette (EDT)'),
        ('parfum', 'Parfum / Extrait'),
        ('edc', 'Eau de Cologne (EDC)'),
        ('edm', 'Eau de Mist'),
        ('oil', 'Perfume Oil'),
        ('attar', 'Attar'),
    ]
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
        ('all', 'All Seasons'),
    ]
    OCCASION_CHOICES = [
        ('daily', 'Daily Wear'),
        ('office', 'Office'),
        ('evening', 'Evening'),
        ('party', 'Party'),
        ('wedding', 'Wedding'),
        ('outdoor', 'Outdoor'),
        ('special', 'Special Occasion'),
    ]

    # ─── Identification ───────────────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True)

    # ─── Relations ────────────────────────────────────────────
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    fragrance_family = models.ForeignKey(
        FragranceFamily, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products'
    )
    related_products = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        related_name='related_to'
    )

    # ─── Fragrance Details ────────────────────────────────────
    brand = models.CharField(max_length=100, blank=True)
    inspired_by = models.CharField(
        max_length=200, blank=True,
        help_text="e.g. Dior Sauvage, Bleu de Chanel"
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    concentration = models.CharField(
        max_length=10, choices=CONCENTRATION_CHOICES, default='edp'
    )
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, default='all')
    occasion = models.CharField(
        max_length=10, choices=OCCASION_CHOICES, default='daily'
    )
    top_notes = models.CharField(max_length=500, blank=True,
                                  help_text="Comma separated e.g. Bergamot, Lemon")
    middle_notes = models.CharField(max_length=500, blank=True)
    base_notes = models.CharField(max_length=500, blank=True)
    longevity = models.CharField(max_length=100, blank=True,
                                  help_text="e.g. 8-12 Hours")
    projection = models.CharField(max_length=100, blank=True,
                                   help_text="e.g. Moderate to Strong")

    # ─── Descriptions ─────────────────────────────────────────
    short_description = models.TextField(
        max_length=500, blank=True,
        help_text="Shown in product cards and quick view"
    )
    description = RichTextUploadingField(blank=True)

    # ─── Pricing ──────────────────────────────────────────────
    regular_price = models.DecimalField(max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=True, blank=True,
                                      validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=True, blank=True,
                                      help_text="Internal cost (not shown to customers)")

    # ─── Stock ────────────────────────────────────────────────
    stock = models.PositiveIntegerField(default=0)
    min_stock_alert = models.PositiveIntegerField(
        default=5, help_text="Alert when stock falls below this"
    )
    track_inventory = models.BooleanField(default=True)

    # ─── Badges & Status ──────────────────────────────────────
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_limited_edition = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # ─── Media ────────────────────────────────────────────────
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")

    # ─── SEO ──────────────────────────────────────────────────
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    og_image = ProcessedImageField(
        upload_to='products/og/',
        processors=[ResizeToFill(1200, 630)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )

    # ─── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['is_active', 'is_new_arrival']),
            models.Index(fields=['is_active', 'is_best_seller']),
            models.Index(fields=['gender']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.sku:
            self.sku = f"AB-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def selling_price(self):
        return self.sale_price if self.sale_price else self.regular_price

    @property
    def discount_percentage(self):
        if self.sale_price and self.regular_price > 0:
            discount = ((self.regular_price - self.sale_price) / self.regular_price) * 100
            return round(discount)
        return 0

    @property
    def is_on_sale(self):
        return bool(self.sale_price and self.sale_price < self.regular_price)

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock > 0

    @property
    def is_low_stock(self):
        return self.track_inventory and 0 < self.stock <= self.min_stock_alert

    @property
    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.selling_price) * 100
        return None

    def get_average_rating(self):
        result = self.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

    def get_review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_primary_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()

    def get_badges(self):
        badges = []
        if self.is_on_sale:
            badges.append({'label': 'Sale', 'color': 'danger'})
        if self.is_new_arrival:
            badges.append({'label': 'New', 'color': 'success'})
        if self.is_best_seller:
            badges.append({'label': 'Best Seller', 'color': 'warning'})
        if self.is_limited_edition:
            badges.append({'label': 'Limited', 'color': 'info'})
        if self.is_trending:
            badges.append({'label': 'Trending', 'color': 'primary'})
        return badges


# ─── Product Image ────────────────────────────────────────────
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image = ProcessedImageField(
        upload_to='products/',
        processors=[ResizeToFit(1200, 1200)],
        format='JPEG', options={'quality': 90}
    )
    thumbnail = ProcessedImageField(
        upload_to='products/thumbs/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG', options={'quality': 80},
        blank=True, null=True
    )
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['display_order', '-is_primary']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


# ─── Product Variation ────────────────────────────────────────
class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variations'
    )
    name = models.CharField(max_length=100, help_text="e.g. 30ml, 50ml, 100ml")
    sku = models.CharField(max_length=100, unique=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2,
                                  null=True, blank=True,
                                  help_text="Weight in grams")
    image = ProcessedImageField(
        upload_to='products/variations/',
        processors=[ResizeToFill(400, 400)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Product Variation')
        verbose_name_plural = _('Product Variations')
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.product.name} – {self.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"VAR-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def selling_price(self):
        return self.sale_price if self.sale_price else self.regular_price

    @property
    def is_in_stock(self):
        return self.stock > 0


# ─── Homepage Banner (Hero Slider) ────────────────────────────
class Banner(models.Model):
    BANNER_TYPES = [
        ('hero', 'Hero Slider'),
        ('promo', 'Promotional Banner'),
        ('category', 'Category Banner'),
        ('popup', 'Popup Banner'),
        ('offer', 'Offer Banner'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image_desktop = ProcessedImageField(
        upload_to='banners/',
        processors=[ResizeToFit(1920, 800)],
        format='JPEG', options={'quality': 90}
    )
    image_mobile = ProcessedImageField(
        upload_to='banners/mobile/',
        processors=[ResizeToFit(768, 500)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )
    button_text = models.CharField(max_length=50, blank=True, default='Shop Now')
    button_url = models.CharField(max_length=200, blank=True, default='/shop/')
    button_text_2 = models.CharField(max_length=50, blank=True)
    button_url_2 = models.CharField(max_length=200, blank=True)
    overlay_color = models.CharField(
        max_length=20, blank=True, default='rgba(0,0,0,0.4)'
    )
    text_alignment = models.CharField(
        max_length=10,
        choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')],
        default='left'
    )
    banner_type = models.CharField(max_length=10, choices=BANNER_TYPES, default='hero')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # Countdown timer
    has_countdown = models.BooleanField(default=False)
    countdown_end = models.DateTimeField(null=True, blank=True)
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    # Scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['display_order']

    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"


# ─── Trust Features ───────────────────────────────────────────
class TrustFeature(models.Model):
    icon = models.CharField(max_length=100, help_text="FontAwesome class")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Trust Feature')
        verbose_name_plural = _('Trust Features')
        ordering = ['display_order']

    def __str__(self):
        return self.title


# ─── Cart ─────────────────────────────────────────────────────
class Cart(models.Model):
    """
    Persistent cart – works for both guests (session) and logged-in users.
    """
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True, related_name='cart_items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='cart_items'
    )
    variation = models.ForeignKey(
        ProductVariation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = [['session_key', 'product', 'variation'],
                           ['user', 'product', 'variation']]

    def __str__(self):
        identifier = self.user.email if self.user else self.session_key[:8]
        return f"{identifier} – {self.product.name} x{self.quantity}"

    @property
    def unit_price(self):
        if self.variation:
            return self.variation.selling_price
        return self.product.selling_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


# ─── Inventory Log ────────────────────────────────────────────
class InventoryLog(models.Model):
    ADJUSTMENT_TYPES = [
        ('purchase', 'Stock Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return / Refund'),
        ('damaged', 'Damaged'),
        ('manual_add', 'Manual Increase'),
        ('manual_remove', 'Manual Decrease'),
        ('restock', 'Restock'),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='inventory_logs'
    )
    variation = models.ForeignKey(
        ProductVariation, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity_change = models.IntegerField(help_text="Positive = increase, Negative = decrease")
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    note = models.TextField(blank=True)
    adjusted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Inventory Log')
        verbose_name_plural = _('Inventory Logs')
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.quantity_change >= 0 else ''
        return f"{self.product.name} {sign}{self.quantity_change} ({self.get_adjustment_type_display()})"
