"""Inject site-wide settings into every template."""
from .models import SiteSettings


def site_settings_context(request):
    settings = SiteSettings.load()
    return {
        'site_settings': settings,
        'site_name': settings.site_name,
        'site_tagline': settings.site_tagline,
        'announcement_text': settings.announcement_text,
        'announcement_is_active': settings.announcement_is_active,
        'announcement_bg_color': settings.announcement_bg_color,
        'announcement_text_color': settings.announcement_text_color,
        'whatsapp_number': settings.whatsapp_number,
        'currency_symbol': settings.currency_symbol,
    }
