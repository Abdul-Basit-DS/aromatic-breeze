"""
Shop admin – Products, Categories, Banners, Cart, Inventory.
Full enterprise admin with all management capabilities.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Avg
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from import_export.admin import ImportExportMixin
from import_export import resources
import csv

from .models import (
    Category, FragranceFamily, Product, ProductImage,
    ProductVariation, Banner, TrustFeature, Cart, InventoryLog
)


# ─── Resources ────────────────────────────────────────────────
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'brand', 'inspired_by', 'gender',
                  'regular_price', 'sale_price', 'cost_price', 'stock',
                  'is_active', 'is_featured', 'is_new_arrival', 'is_best_seller',
                  'created_at')
        export_order = fields


# ─── Inlines ──────────────────────────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 5
    fields = ('image_preview', 'image', 'alt_text', 'is_primary', 'display_order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:4px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Preview'


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ('name', 'regular_price', 'sale_price', 'cost_price',
              'stock', 'sku', 'is_active', 'display_order')


class InventoryLogInline(admin.TabularInline):
    model = InventoryLog
    extra = 0
    readonly_fields = ('adjustment_type', 'quantity_change', 'quantity_before',
                       'quantity_after', 'note', 'adjusted_by', 'created_at')
    can_delete = False
    max_num = 0
    verbose_name = 'Inventory History'
    verbose_name_plural = 'Inventory History (last 10)'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')


# ─── Category Admin ───────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'parent', 'product_count',
                    'is_featured', 'is_active', 'display_order')
    list_filter = ('is_featured', 'is_active', 'parent')
    search_fields = ('name', 'description')
    list_editable = ('is_featured', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25

    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'parent', 'description', 'image', 'icon')}),
        ('Settings', {'fields': ('display_order', 'is_featured', 'is_active')}),
        ('SEO', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="40" style="object-fit:cover;border-radius:4px;">', obj.image.url)
        return '—'
    image_preview.short_description = ''

    def product_count(self, obj):
        count = obj.get_product_count()
        url = reverse('admin:shop_product_changelist') + f'?categories__id__exact={obj.pk}'
        return format_html('<a href="{}">{} products</a>', url, count)
    product_count.short_description = 'Products'


# ─── Fragrance Family Admin ───────────────────────────────────
@admin.register(FragranceFamily)
class FragranceFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}


# ─── Product Admin ────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ProductResource

    list_display = (
        'primary_image', 'name', 'inspired_by_display', 'gender',
        'price_display', 'stock_display', 'badges_display',
        'avg_rating', 'is_active', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'is_new_arrival', 'is_best_seller',
        'is_trending', 'is_limited_edition', 'gender', 'concentration',
        'season', 'categories', 'fragrance_family'
    )
    search_fields = ('name', 'sku', 'inspired_by', 'brand', 'top_notes',
                     'middle_notes', 'base_notes')
    filter_horizontal = ('categories', 'related_products')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at', 'profit_margin_display',
                       'discount_percentage_display')
    save_on_top = True

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'sku', 'barcode', 'brand', 'inspired_by')
        }),
        ('Classification', {
            'fields': ('categories', 'fragrance_family', 'gender',
                       'concentration', 'season', 'occasion')
        }),
        ('Fragrance Profile', {
            'fields': ('top_notes', 'middle_notes', 'base_notes',
                       'longevity', 'projection'),
            'classes': ('collapse',)
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description', 'video_url')
        }),
        ('Pricing', {
            'fields': ('regular_price', 'sale_price', 'cost_price',
                       'profit_margin_display', 'discount_percentage_display')
        }),
        ('Inventory', {
            'fields': ('stock', 'min_stock_alert', 'track_inventory')
        }),
        ('Badges & Status', {
            'fields': ('is_active', 'is_featured', 'is_new_arrival',
                       'is_best_seller', 'is_trending', 'is_limited_edition')
        }),
        ('Related Products', {
            'fields': ('related_products',), 'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProductImageInline, ProductVariationInline, InventoryLogInline]

    actions = [
        'activate_products', 'deactivate_products',
        'mark_featured', 'unmark_featured',
        'mark_new_arrival', 'mark_best_seller',
        'export_csv', 'duplicate_product',
    ]

    # ─── Display methods ──────────────────────────────────────
    def primary_image(self, obj):
        img = obj.get_primary_image()
        if img:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px;">',
                img.image.url
            )
        return format_html('<span style="color:#ccc;">No image</span>')
    primary_image.short_description = ''

    def inspired_by_display(self, obj):
        if obj.inspired_by:
            return format_html(
                '<small style="color:#888;">Inspired by</small><br><strong>{}</strong>',
                obj.inspired_by
            )
        return '—'
    inspired_by_display.short_description = 'Inspired By'

    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color:#dc3545;font-weight:bold;">Rs. {}</span>'
                '<br><small><s style="color:#999;">Rs. {}</s></small>',
                int(obj.sale_price), int(obj.regular_price)
            )
        return format_html('Rs. {}', int(obj.regular_price))
    price_display.short_description = 'Price'

    def stock_display(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:#dc3545;font-weight:bold;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color:#fd7e14;">Low: {}</span>', obj.stock)
        return format_html('<span style="color:#198754;">{}</span>', obj.stock)
    stock_display.short_description = 'Stock'

    def badges_display(self, obj):
        badges = obj.get_badges()
        if not badges:
            return '—'
        html = ' '.join([
            f'<span style="background:#{"dc3545" if b["color"]=="danger" else "198754" if b["color"]=="success" else "ffc107" if b["color"]=="warning" else "0dcaf0"};'
            f'color:{"white" if b["color"]!="warning" else "#000"};padding:2px 6px;border-radius:3px;font-size:10px;">{b["label"]}</span>'
            for b in badges
        ])
        return format_html(html)
    badges_display.short_description = 'Badges'

    def avg_rating(self, obj):
        rating = obj.get_average_rating()
        count = obj.get_review_count()
        stars = '★' * int(rating) + '☆' * (5 - int(rating))
        return format_html(
            '<span style="color:#ffc107;">{}</span> <small>({} reviews)</small>',
            stars, count
        )
    avg_rating.short_description = 'Rating'

    def profit_margin_display(self, obj):
        margin = obj.profit_margin
        if margin is not None:
            color = '#198754' if margin >= 30 else '#ffc107' if margin >= 15 else '#dc3545'
            return format_html('<span style="color:{};">{}%</span>', color, round(margin, 1))
        return '—'
    profit_margin_display.short_description = 'Profit Margin'

    def discount_percentage_display(self, obj):
        if obj.discount_percentage:
            return format_html(
                '<span style="color:#dc3545;font-weight:bold;">{}% OFF</span>',
                obj.discount_percentage
            )
        return '—'
    discount_percentage_display.short_description = 'Discount'

    # ─── Bulk actions ─────────────────────────────────────────
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} products activated.')
    activate_products.short_description = 'Activate selected products'

    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} products deactivated.')
    deactivate_products.short_description = 'Deactivate selected products'

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} products marked as featured.')
    mark_featured.short_description = 'Mark as Featured'

    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} products removed from featured.')
    unmark_featured.short_description = 'Remove from Featured'

    def mark_new_arrival(self, request, queryset):
        queryset.update(is_new_arrival=True)
        self.message_user(request, f'{queryset.count()} products marked as New Arrival.')
    mark_new_arrival.short_description = 'Mark as New Arrival'

    def mark_best_seller(self, request, queryset):
        queryset.update(is_best_seller=True)
        self.message_user(request, f'{queryset.count()} products marked as Best Seller.')
    mark_best_seller.short_description = 'Mark as Best Seller'

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'SKU', 'Brand', 'Inspired By', 'Gender',
                         'Regular Price', 'Sale Price', 'Stock', 'Active'])
        for p in queryset:
            writer.writerow([
                p.name, p.sku, p.brand, p.inspired_by, p.gender,
                p.regular_price, p.sale_price or '', p.stock, p.is_active
            ])
        return response
    export_csv.short_description = 'Export selected to CSV'

    def duplicate_product(self, request, queryset):
        for product in queryset:
            old_pk = product.pk
            product.pk = None
            product.id = None
            product.name = f"Copy of {product.name}"
            product.slug = ''
            product.sku = ''
            product.is_active = False
            product.save()
            # Copy images
            for img in ProductImage.objects.filter(product_id=old_pk):
                img.pk = None
                img.product = product
                img.save()
            # Copy variations
            for var in ProductVariation.objects.filter(product_id=old_pk):
                var.pk = None
                var.product = product
                var.sku = ''
                var.save()
        self.message_user(request, f'{queryset.count()} product(s) duplicated.')
    duplicate_product.short_description = 'Duplicate selected products'


# ─── Banner Admin ─────────────────────────────────────────────
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'banner_type', 'display_order',
                    'is_active', 'view_count', 'click_count')
    list_filter = ('banner_type', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title', 'subtitle')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description',
                       'image_desktop', 'image_mobile')
        }),
        ('Buttons', {
            'fields': ('button_text', 'button_url', 'button_text_2', 'button_url_2')
        }),
        ('Design', {
            'fields': ('overlay_color', 'text_alignment')
        }),
        ('Settings', {
            'fields': ('banner_type', 'display_order', 'is_active',
                       'start_date', 'end_date')
        }),
        ('Countdown Timer', {
            'fields': ('has_countdown', 'countdown_end'),
            'classes': ('collapse',)
        }),
        ('Analytics (Read Only)', {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('view_count', 'click_count')

    def image_preview(self, obj):
        if obj.image_desktop:
            return format_html(
                '<img src="{}" width="120" height="60" style="object-fit:cover;border-radius:4px;">',
                obj.image_desktop.url
            )
        return '—'
    image_preview.short_description = ''


# ─── Trust Feature Admin ──────────────────────────────────────
@admin.register(TrustFeature)
class TrustFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'description', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')


# ─── Cart Admin ───────────────────────────────────────────────
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'product', 'variation', 'quantity',
                    'unit_price', 'total_price_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name', 'session_key')
    readonly_fields = ('created_at', 'updated_at')

    def user_display(self, obj):
        return obj.user.email if obj.user else f'Guest ({obj.session_key[:8]})'
    user_display.short_description = 'User'

    def total_price_display(self, obj):
        return f'Rs. {obj.total_price:,.0f}'
    total_price_display.short_description = 'Total'


# ─── Inventory Log Admin ──────────────────────────────────────
@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation', 'adjustment_type',
                    'quantity_change_display', 'quantity_before',
                    'quantity_after', 'adjusted_by', 'created_at')
    list_filter = ('adjustment_type', 'created_at')
    search_fields = ('product__name', 'note')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def has_change_permission(self, request, obj=None):
        return False

    def quantity_change_display(self, obj):
        sign = '+' if obj.quantity_change >= 0 else ''
        color = '#198754' if obj.quantity_change >= 0 else '#dc3545'
        return format_html(
            '<span style="color:{};font-weight:bold;">{}{}</span>',
            color, sign, obj.quantity_change
        )
    quantity_change_display.short_description = 'Change'
