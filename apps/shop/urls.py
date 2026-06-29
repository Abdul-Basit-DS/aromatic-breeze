"""URL patterns for the Shop app."""
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # ─── Home ─────────────────────────────────────────────────
    path('', views.home, name='home'),

    # ─── Shop listing ─────────────────────────────────────────
    path('shop/', views.shop, name='shop'),
    path('shop/category/<slug:slug>/', views.shop, name='category'),

    # ─── Product Detail ───────────────────────────────────────
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # ─── Quick View & Variation (AJAX) ────────────────────────
    path('product/<slug:slug>/quick-view/', views.quick_view, name='quick_view'),
    path('variation/<int:variation_id>/', views.variation_detail, name='variation_detail'),

    # ─── Cart ─────────────────────────────────────────────────
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<uuid:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # ─── Live Search ──────────────────────────────────────────
    path('search/', views.live_search, name='live_search'),
]
