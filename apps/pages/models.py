"""
Pages models – SiteSettings, About, Contact, Newsletter, Announcement.
Everything editable from Django Admin without code changes.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, ResizeToFill
from ckeditor_uploader.fields import RichTextUploadingField


class SiteSettings(models.Model):
    """
    Global site settings – singleton model.
    All settings editable from one place in admin.
    """
    # ─── Identity ─────────────────────────────────────────────
    site_name = models.CharField(max_length=100, default='The Aromatic Breeze')
    site_tagline = models.CharField(max_length=200, blank=True,
                                    default='Premium Perfumes')
    logo = ProcessedImageField(
        upload_to='settings/',
        processors=[ResizeToFit(300, 100)],
        format='PNG', options={'quality': 95},
        null=True, blank=True
    )
    logo_dark = ProcessedImageField(
        upload_to='settings/',
        processors=[ResizeToFit(300, 100)],
        format='PNG', options={'quality': 95},
        null=True, blank=True,
        help_text="Dark version of logo for light backgrounds"
    )
    favicon = models.ImageField(upload_to='settings/', null=True, blank=True)

    # ─── Contact ──────────────────────────────────────────────
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email_support = models.EmailField(blank=True)
    email_info = models.EmailField(blank=True)
    business_hours = models.CharField(
        max_length=200, blank=True,
        default='Mon-Sat: 10am – 7pm'
    )
    google_maps_url = models.URLField(blank=True)
    google_maps_embed = models.TextField(blank=True,
                                          help_text="Paste full Google Maps embed iframe code")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # ─── Social Media ─────────────────────────────────────────
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    snapchat_url = models.URLField(blank=True)

    # ─── Announcement Bar ─────────────────────────────────────
    announcement_text = models.CharField(
        max_length=300, blank=True,
        default='Free Delivery on Orders Above Rs. 2,500'
    )
    announcement_is_active = models.BooleanField(default=True)
    announcement_bg_color = models.CharField(max_length=20, default='#1a1a2e')
    announcement_text_color = models.CharField(max_length=20, default='#d4af37')

    # ─── SEO Defaults ─────────────────────────────────────────
    default_meta_title = models.CharField(max_length=200, blank=True)
    default_meta_description = models.TextField(blank=True)
    default_meta_keywords = models.CharField(max_length=500, blank=True)
    og_default_image = ProcessedImageField(
        upload_to='settings/og/',
        processors=[ResizeToFill(1200, 630)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)

    # ─── Currency & Tax ───────────────────────────────────────
    currency_code = models.CharField(max_length=5, default='PKR')
    currency_symbol = models.CharField(max_length=5, default='Rs.')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # ─── Policies (rich text) ─────────────────────────────────
    privacy_policy = RichTextUploadingField(blank=True)
    terms_conditions = RichTextUploadingField(blank=True)
    shipping_policy = RichTextUploadingField(blank=True)
    return_policy = RichTextUploadingField(blank=True)

    # ─── Maintenance Mode ─────────────────────────────────────
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(
        blank=True, default='We are currently down for maintenance. We will be back shortly!'
    )

    # ─── Free Shipping Threshold ──────────────────────────────
    free_shipping_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=2500
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutPage(models.Model):
    """About Us page – all sections editable from admin."""
    # ─── Hero ─────────────────────────────────────────────────
    hero_image = ProcessedImageField(
        upload_to='about/', processors=[ResizeToFit(1920, 800)],
        format='JPEG', options={'quality': 90}, null=True, blank=True
    )
    hero_heading = models.CharField(max_length=200, default='About The Aromatic Breeze')
    hero_subheading = models.TextField(blank=True)
    hero_btn1_text = models.CharField(max_length=50, default='Shop Now')
    hero_btn1_url = models.CharField(max_length=200, default='/shop/')
    hero_btn2_text = models.CharField(max_length=50, blank=True, default='Contact Us')
    hero_btn2_url = models.CharField(max_length=200, blank=True, default='/contact/')
    overlay_color = models.CharField(max_length=30, default='rgba(0,0,0,0.5)')

    # ─── Story ────────────────────────────────────────────────
    story_heading = models.CharField(max_length=200, default='Our Story')
    story_content = RichTextUploadingField(blank=True)

    # ─── Founder ──────────────────────────────────────────────
    founder_image = ProcessedImageField(
        upload_to='about/founder/', processors=[ResizeToFit(600, 800)],
        format='JPEG', options={'quality': 90}, null=True, blank=True
    )
    founder_name = models.CharField(max_length=100, blank=True)
    founder_designation = models.CharField(max_length=100, blank=True)
    founder_message = RichTextUploadingField(blank=True)
    founder_quote = models.TextField(blank=True)
    founder_signature = models.ImageField(
        upload_to='about/', null=True, blank=True
    )

    # ─── CTA ──────────────────────────────────────────────────
    cta_heading = models.CharField(
        max_length=200, default='Discover Your Signature Fragrance Today'
    )
    cta_description = models.TextField(blank=True)
    cta_btn1_text = models.CharField(max_length=50, default='Shop Now')
    cta_btn1_url = models.CharField(max_length=200, default='/shop/')
    cta_btn2_text = models.CharField(max_length=50, blank=True, default='Contact Us')
    cta_btn2_url = models.CharField(max_length=200, blank=True, default='/contact/')
    cta_bg_image = ProcessedImageField(
        upload_to='about/', processors=[ResizeToFit(1920, 600)],
        format='JPEG', options={'quality': 85}, null=True, blank=True
    )

    # ─── SEO ──────────────────────────────────────────────────
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('About Page')
        verbose_name_plural = _('About Page')

    def __str__(self):
        return 'About Page Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Statistic(models.Model):
    """Animated counter stats shown on About page."""
    icon = models.CharField(max_length=100, help_text="FontAwesome class")
    label = models.CharField(max_length=100)
    value = models.PositiveIntegerField(help_text="The number to count up to")
    suffix = models.CharField(max_length=10, blank=True,
                               help_text="e.g. + or K or %")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Statistic')
        verbose_name_plural = _('Statistics')
        ordering = ['display_order']

    def __str__(self):
        return f"{self.label}: {self.value}{self.suffix}"


class BrandValue(models.Model):
    """Brand values / Why Choose Us cards on About page."""
    SECTION_CHOICES = [
        ('values', 'Brand Values'),
        ('why_us', 'Why Choose Us'),
        ('process', 'Manufacturing Process'),
        ('certifications', 'Certifications'),
    ]
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='values')
    icon = models.CharField(max_length=100, help_text="FontAwesome class")
    title = models.CharField(max_length=100)
    description = models.TextField()
    step_number = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="For process steps only"
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Brand Value / Feature')
        verbose_name_plural = _('Brand Values / Features')
        ordering = ['section', 'display_order']

    def __str__(self):
        return f"[{self.get_section_display()}] {self.title}"


class BrandTimeline(models.Model):
    """Company milestone timeline on About page."""
    year = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Brand Timeline')
        verbose_name_plural = _('Brand Timeline')
        ordering = ['display_order']

    def __str__(self):
        return f"{self.year} – {self.title}"


class ContactPage(models.Model):
    """Contact page hero and settings – singleton."""
    hero_image = ProcessedImageField(
        upload_to='contact/', processors=[ResizeToFit(1920, 600)],
        format='JPEG', options={'quality': 90}, null=True, blank=True
    )
    hero_heading = models.CharField(max_length=200, default='Contact Us')
    hero_subheading = models.CharField(
        max_length=300, blank=True,
        default="We're here to help. Reach out to us anytime."
    )
    intro_heading = models.CharField(max_length=200, default='Get in Touch')
    intro_text = models.TextField(blank=True)
    subject_choices = models.TextField(
        blank=True,
        help_text="One subject per line e.g.\nProduct Inquiry\nOrder Support\nWholesale"
    )
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Contact Page')
        verbose_name_plural = _('Contact Page')

    def __str__(self):
        return 'Contact Page Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_subject_list(self):
        if self.subject_choices:
            return [s.strip() for s in self.subject_choices.strip().splitlines() if s.strip()]
        return ['Product Inquiry', 'Order Support', 'Wholesale Inquiry',
                'Business Partnership', 'Complaint', 'Feedback', 'Other']


class ContactMessage(models.Model):
    """Customer contact form submissions."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
        ('spam', 'Spam'),
        ('archived', 'Archived'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    internal_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_messages'
    )
    reply_sent = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.full_name} – {self.subject[:60]}"
