"""
Shop views – Home, Product List, Product Detail, Cart, Quick View, Search.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count, Min, Max
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .models import (
    Product, Category, ProductVariation, Banner, TrustFeature,
    Cart, FragranceFamily, InventoryLog
)


# ─── Helpers ──────────────────────────────────────────────────
def get_or_create_cart_key(request):
    """Ensure session has a cart key."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart_items(request):
    """Return cart queryset for current user or session."""
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).select_related(
            'product', 'variation'
        )
    session_key = get_or_create_cart_key(request)
    return Cart.objects.filter(session_key=session_key).select_related(
        'product', 'variation'
    )


def get_cart_summary(request):
    items = get_cart_items(request)
    subtotal = sum(item.total_price for item in items)
    count = sum(item.quantity for item in items)
    return {'items': items, 'subtotal': subtotal, 'count': count}


# ─── Home Page ────────────────────────────────────────────────
def home(request):
    """Homepage with all sections loaded dynamically."""
    banners = Banner.objects.filter(
        banner_type='hero', is_active=True
    ).order_by('display_order')

    trust_features = TrustFeature.objects.filter(
        is_active=True
    ).order_by('display_order')

    categories = Category.objects.filter(
        is_active=True, parent=None
    ).order_by('display_order')

    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).prefetch_related('images', 'variations', 'categories')[:8]

    new_arrivals = Product.objects.filter(
        is_active=True
    ).order_by('-created_at').prefetch_related('images', 'variations')[:8]

    best_sellers = Product.objects.filter(
        is_active=True, is_best_seller=True
    ).prefetch_related('images', 'variations')[:8]

    # Gift for her = Women category products
    gift_for_her = Product.objects.filter(
        is_active=True, gender='women'
    ).prefetch_related('images', 'variations')[:8]

    promo_banner = Banner.objects.filter(
        banner_type='promo', is_active=True
    ).first()

    # Approved reviews for homepage carousel
    from apps.reviews.models import Review
    customer_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('user', 'product').order_by('-created_at')[:6]

    # Latest blogs
    try:
        from apps.blog.models import BlogPost
        latest_blogs = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at')[:3]
    except Exception:
        latest_blogs = []

    context = {
        'page_title': 'Home',
        'banners': banners,
        'trust_features': trust_features,
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'gift_for_her': gift_for_her,
        'promo_banner': promo_banner,
        'customer_reviews': customer_reviews,
        'latest_blogs': latest_blogs,
    }
    return render(request, 'shop/home.html', context)


# ─── Shop / Product List ──────────────────────────────────────
def shop(request , slug=None):
    """Shop page with all filters, sorting, pagination."""
    products = Product.objects.filter(is_active=True).prefetch_related(
        'images', 'variations', 'categories'
    ).annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews'))

    # ── Search ────────────────────────────────────────────────
    search_q = request.GET.get('q', '').strip()
    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) |
            Q(inspired_by__icontains=search_q) |
            Q(brand__icontains=search_q) |
            Q(sku__icontains=search_q) |
            Q(top_notes__icontains=search_q) |
            Q(middle_notes__icontains=search_q) |
            Q(base_notes__icontains=search_q)
        )

    # ── Filters ───────────────────────────────────────────────
    if slug:
        category_slug = slug
    else:
        category_slug = request.GET.get('category', '')
    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            products = products.filter(categories=category)

    gender_filter = request.GET.getlist('gender')
    if gender_filter:
        products = products.filter(gender__in=gender_filter)

    fragrance_filter = request.GET.getlist('fragrance_family')
    if fragrance_filter:
        products = products.filter(fragrance_family__slug__in=fragrance_filter)

    size_filter = request.GET.getlist('size')
    if size_filter:
        products = products.filter(variations__name__in=size_filter)

    # Price range
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    if price_min:
        try:
            products = products.filter(regular_price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(regular_price__lte=float(price_max))
        except ValueError:
            pass

    # Availability
    in_stock = request.GET.get('in_stock', '')
    if in_stock == '1':
        products = products.filter(stock__gt=0)

    # Rating filter
    min_rating = request.GET.get('rating', '')
    if min_rating:
        try:
            products = products.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass

    # Tag filters
    # Filters
        if request.GET.get('featured'):
            products = products.filter(is_featured=True)

        if request.GET.get('new_arrival'):
            products = products.filter(is_new_arrival=True)

        if request.GET.get('best_seller'):
            products = products.filter(is_best_seller=True)

        if request.GET.get('on_sale'):
            products = products.filter(is_on_sale=True)

        if request.GET.get('gender'):
            products = products.filter(gender=request.GET.get('gender'))

    # ── Sorting ───────────────────────────────────────────────
    sort_by = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'regular_price',
        'price_high': '-regular_price',
        'top_rated': '-avg_rating',
        'most_reviewed': '-review_count',
        'az': 'name',
        'za': '-name',
    }
    products = products.order_by(sort_map.get(sort_by, '-created_at'))
    products = products.distinct()

    # ── Pagination ────────────────────────────────────────────
    per_page = int(request.GET.get('per_page', 12))
    if per_page not in [12, 24, 36, 48]:
        per_page = 12
    paginator = Paginator(products, per_page)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    # ── Sidebar Data ──────────────────────────────────────────
    all_categories = Category.objects.filter(
        is_active=True
    ).annotate(prod_count=Count('products', filter=Q(products__is_active=True)))
    fragrance_families = FragranceFamily.objects.filter(is_active=True)
    price_range = Product.objects.filter(is_active=True).aggregate(
        min_price=Min('regular_price'), max_price=Max('regular_price')
    )
    available_sizes = ProductVariation.objects.filter(
        is_active=True, product__is_active=True
    ).values_list('name', flat=True).distinct()

    context = {
        'page_title': 'Shop',
        'products': products_page,
        'total_count': paginator.count,
        'all_categories': all_categories,
        'fragrance_families': fragrance_families,
        'available_sizes': sorted(set(available_sizes)),
        'price_range': price_range,
        'sort_by': sort_by,
        'per_page': per_page,
        'search_q': search_q,
        'current_filters': request.GET.dict(),
    }
    return render(request, 'shop/shop.html', context)


# ─── Product Detail ───────────────────────────────────────────
def product_detail(request, slug):
    """Full product details page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all().order_by('display_order')
    variations = product.variations.filter(is_active=True).order_by('display_order')

    from apps.reviews.models import Review
    reviews = product.reviews.filter(
        is_approved=True
    ).select_related('user').order_by('-created_at')

    # Rating breakdown
    rating_breakdown = {}
    total_reviews = reviews.count()
    if total_reviews:
        for star in [5, 4, 3, 2, 1]:
            count = reviews.filter(rating=star).count()
            rating_breakdown[star] = {
                'count': count,
                'percentage': round((count / total_reviews) * 100)
            }

    # Related products (same category or fragrance family)
    related = Product.objects.filter(
        is_active=True
    ).exclude(pk=product.pk)
    if product.fragrance_family:
        related = related.filter(fragrance_family=product.fragrance_family)
    else:
        cats = product.categories.all()
        related = related.filter(categories__in=cats)
    related = related.distinct().prefetch_related('images', 'variations')[:6]

    # Recently viewed (session based)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if str(product.pk) not in recently_viewed_ids:
        recently_viewed_ids.insert(0, str(product.pk))
        request.session['recently_viewed'] = recently_viewed_ids[:10]

    recently_viewed = Product.objects.filter(
        id__in=recently_viewed_ids, is_active=True
    ).exclude(pk=product.pk).prefetch_related('images')[:4]

    # Review form
    from apps.reviews.forms import ReviewForm
    review_form = ReviewForm()

    context = {
        'page_title': product.name,
        'product': product,
        'images': images,
        'variations': variations,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'rating_breakdown': rating_breakdown,
        'related_products': related,
        'recently_viewed': recently_viewed,
        'review_form': review_form,
        'avg_rating': product.get_average_rating(),
    }
    return render(request, 'shop/product_detail.html', context)


# ─── Quick View (AJAX) ────────────────────────────────────────
@require_GET
def quick_view(request, slug):
    """Return product data for quick view modal as JSON."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = list(product.images.values('id', 'image', 'alt_text', 'is_primary'))
    for img in images:
        img['image'] = request.build_absolute_uri('/media/' + img['image'])

    variations = list(product.variations.filter(is_active=True).values(
        'id', 'name', 'regular_price', 'sale_price', 'stock', 'sku'
    ))

    return JsonResponse({
        'id': str(product.id),
        'name': product.name,
        'slug': product.slug,
        'inspired_by': product.inspired_by,
        'short_description': product.short_description,
        'regular_price': float(product.regular_price),
        'sale_price': float(product.sale_price) if product.sale_price else None,
        'selling_price': float(product.selling_price),
        'discount_percentage': product.discount_percentage,
        'is_on_sale': product.is_on_sale,
        'is_in_stock': product.is_in_stock,
        'stock': product.stock,
        'avg_rating': product.get_average_rating(),
        'review_count': product.get_review_count(),
        'url': product.get_absolute_url(),
        'images': images,
        'variations': [
            {**v, 'regular_price': float(v['regular_price']),
             'sale_price': float(v['sale_price']) if v['sale_price'] else None}
            for v in variations
        ],
        'badges': product.get_badges(),
    })


# ─── Variation Price (AJAX) ───────────────────────────────────
@require_GET
def variation_detail(request, variation_id):
    """Return variation pricing on size selection."""
    variation = get_object_or_404(ProductVariation, pk=variation_id, is_active=True)
    return JsonResponse({
        'id': variation.id,
        'name': variation.name,
        'regular_price': float(variation.regular_price),
        'sale_price': float(variation.sale_price) if variation.sale_price else None,
        'selling_price': float(variation.selling_price),
        'stock': variation.stock,
        'is_in_stock': variation.is_in_stock,
        'sku': variation.sku,
    })


# ─── Cart ─────────────────────────────────────────────────────
def cart_detail(request):
    """View cart."""
    summary = get_cart_summary(request)
    return render(request, 'shop/cart.html', {
        'page_title': 'Shopping Cart',
        **summary
    })


@require_POST
def cart_add(request, product_id):
    """Add item to cart (AJAX-friendly)."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    variation_id = request.POST.get('variation_id')
    quantity = int(request.POST.get('quantity', 1))

    variation = None
    if variation_id:
        variation = get_object_or_404(ProductVariation, pk=variation_id,
                                       product=product, is_active=True)

    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, product=product, variation=variation,
            defaults={'quantity': 0}
        )
    else:
        session_key = get_or_create_cart_key(request)
        cart_item, created = Cart.objects.get_or_create(
            session_key=session_key, product=product, variation=variation,
            defaults={'quantity': 0}
        )

    cart_item.quantity += quantity
    cart_item.save()

    # Update inventory log (reserved)
    if not created:
        pass  # already in cart

    summary = get_cart_summary(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({
            'status': 'ok',
            'message': f'{product.name} added to cart.',
            'cart_count': summary['count'],
            'cart_subtotal': float(summary['subtotal']),
        })

    messages.success(request, f'{product.name} added to cart.')
    return redirect('shop:cart')


@require_POST
def cart_update(request, item_id):
    """Update cart item quantity (AJAX)."""
    cart_item = get_object_or_404(Cart, pk=item_id)
    # Security: only owner can update
    if request.user.is_authenticated:
        if cart_item.user != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
    else:
        session_key = get_or_create_cart_key(request)
        if cart_item.session_key != session_key:
            return JsonResponse({'error': 'Forbidden'}, status=403)

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        cart_item.delete()
        action = 'removed'
    else:
        cart_item.quantity = quantity
        cart_item.save()
        action = 'updated'

    summary = get_cart_summary(request)
    return JsonResponse({
        'status': action,
        'cart_count': summary['count'],
        'cart_subtotal': float(summary['subtotal']),
        'item_total': float(cart_item.total_price) if action == 'updated' else 0,
    })


@require_POST
def cart_remove(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(Cart, pk=item_id)
    cart_item.delete()
    summary = get_cart_summary(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({
            'status': 'removed',
            'cart_count': summary['count'],
            'cart_subtotal': float(summary['subtotal']),
        })
    messages.success(request, 'Item removed from cart.')
    return redirect('shop:cart')


# ─── Live Search (AJAX) ───────────────────────────────────────
@require_GET
def live_search(request):
    """Live product search for header search bar."""
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=q) | Q(inspired_by__icontains=q) |
            Q(brand__icontains=q) | Q(sku__icontains=q)
        ).prefetch_related('images')[:8]

        for p in products:
            img = p.get_primary_image()
            results.append({
                'name': p.name,
                'inspired_by': p.inspired_by,
                'price': float(p.selling_price),
                'url': p.get_absolute_url(),
                'image': request.build_absolute_uri(img.image.url) if img else '',
            })
    return JsonResponse({'results': results, 'query': q})
