"""URL patterns for the Blog app."""
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
