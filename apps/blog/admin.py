"""
Blog admin – full management for posts, categories, tags, comments, FAQs.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from import_export.admin import ImportExportMixin

from .models import BlogCategory, BlogTag, BlogPost, BlogImage, BlogFAQ, BlogComment, FAQ


# ─── Inlines ──────────────────────────────────────────────────
class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    max_num = 10
    fields = ('preview', 'image', 'caption', 'alt_text', 'display_order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Preview'


class BlogFAQInline(admin.TabularInline):
    model = BlogFAQ
    extra = 1
    fields = ('question', 'answer', 'display_order', 'is_active')
    ordering = ('display_order',)


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ('name', 'email', 'body', 'is_approved', 'created_at')
    can_delete = True
    fields = ('name', 'email', 'body', 'is_approved', 'created_at')
    ordering = ('-created_at',)
    max_num = 0


# ─── Blog Category Admin ──────────────────────────────────────
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.get_post_count()
    post_count.short_description = 'Published Posts'


# ─── Blog Tag Admin ───────────────────────────────────────────
@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.get_post_count()
    post_count.short_description = 'Posts'


# ─── Blog Post Admin ──────────────────────────────────────────
@admin.register(BlogPost)
class BlogPostAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'featured_image_preview', 'title', 'author', 'category',
        'status_badge', 'is_featured', 'view_count',
        'reading_time_display', 'comment_count', 'published_at'
    )
    list_filter = (
        'status', 'is_featured', 'category', 'tags', 'created_at'
    )
    search_fields = ('title', 'excerpt', 'content', 'author__email')
    filter_horizontal = ('tags', 'related_products', 'related_posts')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-created_at',)
    list_per_page = 20
    list_editable = ('is_featured',)
    readonly_fields = ('id', 'view_count', 'reading_time_display',
                       'created_at', 'updated_at')
    save_on_top = True

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category',
                       'tags', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'og_image')
        }),
        ('Status & Publishing', {
            'fields': ('status', 'is_featured', 'published_at', 'scheduled_at')
        }),
        ('Related Content', {
            'fields': ('related_products', 'related_posts'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('id', 'view_count', 'reading_time_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [BlogImageInline, BlogFAQInline, BlogCommentInline]

    actions = [
        'publish_posts', 'draft_posts', 'archive_posts',
        'mark_featured', 'unmark_featured', 'duplicate_post',
    ]

    # ─── Display methods ──────────────────────────────────────
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="80" height="55" style="object-fit:cover;border-radius:6px;">',
                obj.featured_image.url
            )
        return '—'
    featured_image_preview.short_description = ''

    def status_badge(self, obj):
        colors = {
            'published': '#198754',
            'draft': '#ffc107',
            'scheduled': '#0d6efd',
            'archived': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;'
            'border-radius:20px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def reading_time_display(self, obj):
        return f"{obj.reading_time} min read"
    reading_time_display.short_description = 'Read Time'

    def comment_count(self, obj):
        count = obj.comments.filter(is_approved=True).count()
        pending = obj.comments.filter(is_approved=False).count()
        if pending:
            return format_html(
                '{} <span style="color:#dc3545;font-size:11px;">+{} pending</span>',
                count, pending
            )
        return count
    comment_count.short_description = 'Comments'

    # ─── Bulk actions ─────────────────────────────────────────
    def publish_posts(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} posts published.')
    publish_posts.short_description = 'Publish selected posts'

    def draft_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts moved to draft.')
    draft_posts.short_description = 'Move to Draft'

    def archive_posts(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} posts archived.')
    archive_posts.short_description = 'Archive selected posts'

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} posts marked as featured.')
    mark_featured.short_description = 'Mark as Featured'

    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} posts removed from featured.')
    unmark_featured.short_description = 'Remove from Featured'

    def duplicate_post(self, request, queryset):
        for post in queryset:
            old_pk = post.pk
            post.pk = None
            post.id = None
            post.title = f"Copy of {post.title}"
            post.slug = ''
            post.status = 'draft'
            post.view_count = 0
            post.published_at = None
            post.save()
            # Copy FAQs
            for faq in BlogFAQ.objects.filter(post_id=old_pk):
                faq.pk = None
                faq.post = post
                faq.save()
        self.message_user(request, f'{queryset.count()} post(s) duplicated as drafts.')
    duplicate_post.short_description = 'Duplicate selected posts'


# ─── Blog Comment Admin ───────────────────────────────────────
@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post_link', 'body_preview',
                    'is_reply_badge', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'body', 'post__title')
    list_editable = ('is_approved',)
    readonly_fields = ('ip_address', 'created_at')
    list_per_page = 30

    actions = ['approve_comments', 'reject_comments']

    def post_link(self, obj):
        from django.urls import reverse as r
        url = r('admin:blog_blogpost_change', args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', url, obj.post.title[:40])
    post_link.short_description = 'Post'

    def body_preview(self, obj):
        return (obj.body[:80] + '…') if len(obj.body) > 80 else obj.body
    body_preview.short_description = 'Comment'

    def is_reply_badge(self, obj):
        if obj.is_reply:
            return format_html('<span style="color:#6f42c1;">↩ Reply</span>')
        return format_html('<span style="color:#198754;">✎ Comment</span>')
    is_reply_badge.short_description = 'Type'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} comments rejected.')
    reject_comments.short_description = 'Reject selected comments'


# ─── Global FAQ Admin ─────────────────────────────────────────
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'page', 'is_active', 'display_order')
    list_filter = ('page', 'is_active')
    list_editable = ('is_active', 'display_order')
    search_fields = ('question', 'answer')
    ordering = ('page', 'display_order')

    fieldsets = (
        (None, {'fields': ('page', 'question', 'answer', 'display_order', 'is_active')}),
    )

    def question_preview(self, obj):
        return (obj.question[:80] + '…') if len(obj.question) > 80 else obj.question
    question_preview.short_description = 'Question'
