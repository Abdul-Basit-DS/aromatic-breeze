"""
Signals for the Accounts app.
Auto-create profile and wishlist when a new user registers.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile, Wishlist

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_and_wishlist(sender, instance, created, **kwargs):
    """Automatically create Profile and Wishlist for every new user."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        Wishlist.objects.get_or_create(user=instance)
