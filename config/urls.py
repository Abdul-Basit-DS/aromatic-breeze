"""Main URL configuration for The Aromatic Breeze."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

admin.site.site_header = "The Aromatic Breeze Admin"
admin.site.site_title = "Aromatic Breeze"
admin.site.index_title = "Business Management Panel"

urlpatterns = [
    # ─── Admin ────────────────────────────────────────────────
    path('control-panel/', admin.site.urls),

    # ─── Accounts ─────────────────────────────────────────────
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),

    # ─── Shop ─────────────────────────────────────────────────
    path('', include('apps.shop.urls')),
    path('shop/', include('apps.shop.urls', namespace='shop')),

    # ─── Orders ───────────────────────────────────────────────
    path('orders/', include('apps.orders.urls', namespace='orders')),

    # ─── Blog ─────────────────────────────────────────────────
    path('blog/', include('apps.blog.urls', namespace='blog')),

    # ─── Pages ────────────────────────────────────────────────
    path('', include('apps.pages.urls', namespace='pages')),

    # ─── Newsletter ───────────────────────────────────────────
    path('newsletter/', include('apps.newsletter.urls', namespace='newsletter')),

    # ─── Contact ──────────────────────────────────────────────
    path('contact/', include('apps.contact.urls', namespace='contact')),

    # ─── Reviews ──────────────────────────────────────────────
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),

    # ─── Coupons ──────────────────────────────────────────────
    path('coupons/', include('apps.coupons.urls', namespace='coupons')),

    # ─── CKEditor uploads ─────────────────────────────────────
    path('ckeditor/', include('ckeditor_uploader.urls')),
]



# ─── Media files in development ───────────────────────────────
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
