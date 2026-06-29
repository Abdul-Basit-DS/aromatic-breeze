"""URL patterns for the Accounts app."""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ─── Dashboard ────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ─── Profile ──────────────────────────────────────────────
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),

    # ─── Addresses ────────────────────────────────────────────
    path('addresses/', views.address_list, name='addresses'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.address_set_default,
         name='address_set_default'),

    # ─── Orders ───────────────────────────────────────────────
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),

    # ─── Wishlist ─────────────────────────────────────────────
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle,
         name='wishlist_toggle'),

    # ─── Reviews ──────────────────────────────────────────────
    path('reviews/', views.my_reviews, name='my_reviews'),
]
