"""
Blog models for The Aromatic Breeze.
BlogPost, BlogCategory, BlogTag, BlogComment, BlogFAQ, BlogImage.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, ResizeToFill
import uuid
import math

User = get_user_model()


# ─── Blog Category ────────────────────────────────────────────
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True,
                            help_text="FontAwesome class e.g. fa-book")
    image = ProcessedImageField(
        upload_to='blog/categories/',
        processors=[ResizeToFill(600, 400)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Blog Category')
        verbose_name_plural = _('Blog Categories')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    def get_post_count(self):
        return self.posts.filter(status='published').count()


# ─── Blog Tag ─────────────────────────────────────────────────
class BlogTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Blog Tag')
        verbose_name_plural = _('Blog Tags')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})

    def get_post_count(self):
        return self.posts.filter(status='published').count()


# ─── Blog Post ────────────────────────────────────────────────
class BlogPost(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    SCHEDULED = 'scheduled'
    ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Published')),
        (SCHEDULED, _('Scheduled')),
        (ARCHIVED, _('Archived')),
    ]

    # ─── Identification ───────────────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)

    # ─── Relations ────────────────────────────────────────────
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='blog_posts'
    )
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='posts'
    )
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    related_products = models.ManyToManyField(
        'shop.Product', blank=True, related_name='blog_posts'
    )
    related_posts = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='related_to'
    )

    # ─── Content ──────────────────────────────────────────────
    excerpt = models.TextField(
        max_length=500, blank=True,
        help_text="Short summary shown in blog listing cards"
    )
    content = RichTextUploadingField()
    featured_image = ProcessedImageField(
        upload_to='blog/featured/',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG', options={'quality': 90}
    )
    og_image = ProcessedImageField(
        upload_to='blog/og/',
        processors=[ResizeToFill(1200, 630)],
        format='JPEG', options={'quality': 85},
        null=True, blank=True,
        help_text="Open Graph image for social sharing (1200×630)"
    )

    # ─── Status & Scheduling ──────────────────────────────────
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=DRAFT
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show as the large featured article on blog listing page"
    )
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Auto-publish at this date/time (set status to Scheduled)"
    )

    # ─── Analytics ────────────────────────────────────────────
    view_count = models.PositiveIntegerField(default=0)

    # ─── SEO ──────────────────────────────────────────────────
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    canonical_url = models.URLField(blank=True)

    # ─── Timestamps ───────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Auto-set published_at
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimate reading time in minutes based on word count."""
        words = len(self.content.split()) if self.content else 0
        minutes = math.ceil(words / 200)
        return max(1, minutes)

    @property
    def is_published(self):
        return self.status == self.PUBLISHED

    def get_approved_comments(self):
        return self.comments.filter(
            is_approved=True, parent__isnull=True
        ).select_related('user').prefetch_related('replies')

    def get_comment_count(self):
        return self.comments.filter(is_approved=True).count()

    def increment_views(self):
        BlogPost.objects.filter(pk=self.pk).update(
            view_count=models.F('view_count') + 1
        )


# ─── Blog Image (inline gallery) ─────────────────────────────
class BlogImage(models.Model):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='images'
    )
    image = ProcessedImageField(
        upload_to='blog/images/',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG', options={'quality': 90}
    )
    caption = models.CharField(max_length=300, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Blog Image')
        verbose_name_plural = _('Blog Images')
        ordering = ['display_order']

    def __str__(self):
        return f"Image for: {self.post.title[:50]}"


# ─── Blog FAQ ─────────────────────────────────────────────────
class BlogFAQ(models.Model):
    """FAQs attached to individual blog articles (accordion layout)."""
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='faqs'
    )
    question = models.CharField(max_length=400)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Blog FAQ')
        verbose_name_plural = _('Blog FAQs')
        ordering = ['display_order']

    def __str__(self):
        return f"FAQ: {self.question[:80]}"


# ─── Blog Comment ─────────────────────────────────────────────
class BlogComment(models.Model):
    """Threaded comments on blog posts. Admin-approval required."""
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='blog_comments'
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    website = models.URLField(blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Blog Comment')
        verbose_name_plural = _('Blog Comments')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['is_approved', '-created_at']),
        ]

    def __str__(self):
        return f"{self.name} on '{self.post.title[:40]}'"

    @property
    def is_reply(self):
        return self.parent is not None


# ─── Global FAQ (for other pages) ────────────────────────────
class FAQ(models.Model):
    """Site-wide FAQs assignable to different pages."""
    PAGE_CHOICES = [
        ('homepage', 'Homepage'),
        ('product', 'Product Pages'),
        ('blog', 'Blog Pages'),
        ('contact', 'Contact Page'),
        ('about', 'About Us Page'),
        ('shipping', 'Shipping Policy'),
        ('returns', 'Returns & Refunds'),
        ('checkout', 'Checkout Page'),
        ('general', 'General / FAQ Page'),
    ]

    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default='general')
    question = models.CharField(max_length=400)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['page', 'display_order']

    def __str__(self):
        return f"[{self.get_page_display()}] {self.question[:80]}"
