"""URL patterns for the Orders app."""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('track/<str:order_number>/', views.order_detail_public, name='order_tracking'),
    path('shipping-cost/', views.shipping_cost, name='shipping_cost'),
    path('invoice/<str:order_number>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('<str:order_number>/return/', views.submit_return_request, name='return_request'),
]
