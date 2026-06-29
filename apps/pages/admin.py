"""Pages admin – SiteSettings, About, Contact, ContactMessage."""
from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    SiteSettings, AboutPage, Statistic, BrandValue,
    BrandTimeline, ContactPage, ContactMessage
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {
            'fields': ('site_name', 'site_tagline', 'logo', 'logo_dark', 'favicon')
        }),
        ('Announcement Bar', {
            'fields': ('announcement_is_active', 'announcement_text',
                       'announcement_bg_color', 'announcement_text_color')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'phone_primary', 'phone_secondary',
                       'whatsapp_number', 'email_support', 'email_info',
                       'business_hours', 'google_maps_url', 'google_maps_embed',
                       'latitude', 'longitude')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url',
                       'tiktok_url', 'linkedin_url', 'twitter_url',
                       'pinterest_url', 'snapchat_url')
        }),
        ('SEO & Analytics', {
            'fields': ('default_meta_title', 'default_meta_description',
                       'default_meta_keywords', 'og_default_image',
                       'google_analytics_id', 'facebook_pixel_id',
                       'google_tag_manager_id')
        }),
        ('Currency & Tax', {
            'fields': ('currency_code', 'currency_symbol', 'tax_rate',
                       'free_shipping_threshold')
        }),
        ('Policies', {
            'fields': ('privacy_policy', 'terms_conditions',
                       'shipping_policy', 'return_policy'),
            'classes': ('collapse',)
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_image', 'hero_heading', 'hero_subheading',
                       'overlay_color', 'hero_btn1_text', 'hero_btn1_url',
                       'hero_btn2_text', 'hero_btn2_url')
        }),
        ('Our Story', {'fields': ('story_heading', 'story_content')}),
        ('Founder Message', {
            'fields': ('founder_image', 'founder_name', 'founder_designation',
                       'founder_message', 'founder_quote', 'founder_signature')
        }),
        ('Call to Action', {
            'fields': ('cta_heading', 'cta_description', 'cta_bg_image',
                       'cta_btn1_text', 'cta_btn1_url',
                       'cta_btn2_text', 'cta_btn2_url')
        }),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'suffix', 'icon', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order', 'value')


@admin.register(BrandValue)
class BrandValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'icon', 'is_active', 'display_order')
    list_filter = ('section', 'is_active')
    list_editable = ('is_active', 'display_order')


@admin.register(BrandTimeline)
class BrandTimelineAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')


@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero', {'fields': ('hero_image', 'hero_heading', 'hero_subheading')}),
        ('Content', {'fields': ('intro_heading', 'intro_text', 'subject_choices')}),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
    )

    def has_add_permission(self, request):
        return not ContactPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject_preview',
                    'status_badge', 'reply_sent', 'created_at')
    list_filter = ('status', 'reply_sent', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('full_name', 'email', 'phone', 'subject', 'message',
                       'ip_address', 'user_agent', 'created_at')
    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ('Message', {
            'fields': ('full_name', 'email', 'phone', 'subject', 'message',
                       'ip_address', 'user_agent', 'created_at')
        }),
        ('Management', {
            'fields': ('status', 'assigned_to', 'internal_notes')
        }),
        ('Reply', {
            'fields': ('reply_sent', 'reply_message')
        }),
    )

    actions = ['mark_read', 'mark_spam', 'archive_messages', 'send_replies']

    def subject_preview(self, obj):
        return (obj.subject[:60] + '…') if len(obj.subject) > 60 else obj.subject
    subject_preview.short_description = 'Subject'

    def status_badge(self, obj):
        colors = {
            'new': '#dc3545', 'read': '#0d6efd', 'replied': '#198754',
            'pending': '#ffc107', 'closed': '#6c757d',
            'spam': '#343a40', 'archived': '#adb5bd'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:3px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        # Auto-mark as read when opened
        if change and obj.status == 'new':
            obj.status = 'read'
        # Send reply email if reply message added
        if obj.reply_message and not obj.reply_sent:
            try:
                send_mail(
                    subject=f'Re: {obj.subject} – The Aromatic Breeze',
                    message=obj.reply_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    fail_silently=True,
                )
                obj.reply_sent = True
                obj.status = 'replied'
            except Exception:
                pass
        super().save_model(request, obj, form, change)

    def mark_read(self, request, queryset):
        queryset.update(status='read')
        self.message_user(request, f'{queryset.count()} messages marked as Read.')
    mark_read.short_description = 'Mark as Read'

    def mark_spam(self, request, queryset):
        queryset.update(status='spam')
        self.message_user(request, f'{queryset.count()} messages marked as Spam.')
    mark_spam.short_description = 'Mark as Spam'

    def archive_messages(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, f'{queryset.count()} messages archived.')
    archive_messages.short_description = 'Archive selected messages'
