"""
Blog views – Listing, Single Post, Category, Tag, Search, Comment.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import (
    BlogPost, BlogCategory, BlogTag, BlogComment, FAQ
)
from .forms import CommentForm


def get_sidebar_data():
    """Common sidebar data used across blog pages."""
    return {
        'blog_categories': BlogCategory.objects.filter(
            is_active=True
        ).annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('display_order'),

        'active_tags': BlogTag.objects.filter(
            is_active=True
        ).annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('display_order')[:30],

        'recent_posts': BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at')[:5],

        'popular_posts': BlogPost.objects.filter(
            status='published'
        ).order_by('-view_count')[:5],
    }


# ─── Blog Listing ─────────────────────────────────────────────
def blog_list(request):
    """Blog listing page with pagination, featured post, sidebar."""
    posts = BlogPost.objects.filter(status='published').select_related(
        'author', 'category'
    ).prefetch_related('tags').order_by('-published_at')

    # ── Filter by category ────────────────────────────────────
    category_slug = request.GET.get('category', '')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(BlogCategory, slug=category_slug, is_active=True)
        posts = posts.filter(category=active_category)

    # ── Filter by tag ─────────────────────────────────────────
    tag_slug = request.GET.get('tag', '')
    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(BlogTag, slug=tag_slug, is_active=True)
        posts = posts.filter(tags=active_tag)

    # ── Search ────────────────────────────────────────────────
    search_q = request.GET.get('q', '').strip()
    if search_q:
        posts = posts.filter(
            Q(title__icontains=search_q) |
            Q(excerpt__icontains=search_q) |
            Q(content__icontains=search_q) |
            Q(tags__name__icontains=search_q)
        ).distinct()

    # ── Featured post (separate from listing) ─────────────────
    featured_post = None
    

    # ── Pagination ────────────────────────────────────────────
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # ── Archive data ──────────────────────────────────────────
    from django.db.models.functions import TruncMonth
    archive = (
        BlogPost.objects
        .filter(status='published')
        .annotate(month=TruncMonth('published_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')[:12]
    )

    context = {
        'page_title': 'Our Blog',
        'posts': page_obj,
        'featured_post': featured_post,
        'active_category': active_category,
        'active_tag': active_tag,
        'search_q': search_q,
        'archive': archive,
        **get_sidebar_data(),
    }
    return render(request, 'blog/blog_list.html', context)


# ─── Single Blog Post ─────────────────────────────────────────
def post_detail(request, slug):
    """Single blog post with comments, FAQs, related content."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    post.increment_views()

    comments = post.get_approved_comments()
    faqs = post.faqs.filter(is_active=True).order_by('display_order')
    related_products = post.related_products.filter(is_active=True)[:4]

    # Related posts: same category or shared tags
    related_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(pk=post.pk)
    if post.category:
        related_posts = related_posts.filter(category=post.category)
    related_posts = related_posts.order_by('-published_at')[:3]

    # Comment form
    comment_form = CommentForm()
    if request.method == 'POST':
        return _handle_comment(request, post)

    context = {
        'page_title': post.title,
        'post': post,
        'comments': comments,
        'comment_count': post.get_comment_count(),
        'comment_form': comment_form,
        'faqs': faqs,
        'related_products': related_products,
        'related_posts': related_posts,
        **get_sidebar_data(),
    }
    return render(request, 'blog/post_detail.html', context)


def _handle_comment(request, post):
    """Process comment submission."""
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.ip_address = request.META.get('REMOTE_ADDR')
        # Link to user if authenticated
        if request.user.is_authenticated:
            comment.user = request.user
            comment.name = request.user.get_full_name() or comment.name
            comment.email = request.user.email

        # Handle reply
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                comment.parent = BlogComment.objects.get(
                    pk=parent_id, post=post, is_approved=True
                )
            except BlogComment.DoesNotExist:
                pass

        comment.save()
        messages.success(
            request,
            _('Your comment has been submitted and is awaiting approval. Thank you!')
        )
    else:
        messages.error(request, _('Please correct the errors in your comment.'))

    return redirect(post.get_absolute_url() + '#comments')


# ─── Category Archive ─────────────────────────────────────────
def category_detail(request, slug):
    """Blog posts filtered by category."""
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(
        status='published', category=category
    ).order_by('-published_at')
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': f'Category: {category.name}',
        'category': category,
        'posts': page_obj,
        **get_sidebar_data(),
    }
    return render(request, 'blog/blog_list.html', context)


# ─── Tag Archive ──────────────────────────────────────────────
def tag_detail(request, slug):
    """Blog posts filtered by tag."""
    tag = get_object_or_404(BlogTag, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(
        status='published', tags=tag
    ).order_by('-published_at')
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': f'Tag: {tag.name}',
        'active_tag': tag,
        'posts': page_obj,
        **get_sidebar_data(),
    }
    return render(request, 'blog/blog_list.html', context)


# ─── Blog Search (AJAX) ───────────────────────────────────────
def blog_search(request):
    """Live blog search via AJAX."""
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        posts = BlogPost.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=q) | Q(excerpt__icontains=q)
        )[:6]
        for p in posts:
            results.append({
                'title': p.title,
                'excerpt': p.excerpt[:100],
                'url': p.get_absolute_url(),
                'image': request.build_absolute_uri(p.featured_image.url) if p.featured_image else '',
                'date': p.published_at.strftime('%d %b %Y') if p.published_at else '',
            })
    return JsonResponse({'results': results})
