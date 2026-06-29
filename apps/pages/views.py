"""Pages views – About, Contact, Policy pages, Homepage sections."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import (SiteSettings, AboutPage, Statistic, BrandValue,
                     BrandTimeline, ContactPage, ContactMessage)
from .forms import ContactForm
from apps.blog.models import FAQ


def about(request):
    page = AboutPage.load()
    stats = Statistic.objects.filter(is_active=True).order_by('display_order')
    values = BrandValue.objects.filter(is_active=True, section='values')
    why_us = BrandValue.objects.filter(is_active=True, section='why_us')
    process = BrandValue.objects.filter(is_active=True, section='process').order_by('display_order')
    certifications = BrandValue.objects.filter(is_active=True, section='certifications')
    timeline = BrandTimeline.objects.filter(is_active=True).order_by('display_order')

    from apps.reviews.models import Review
    testimonials = Review.objects.filter(is_approved=True).order_by('-created_at')[:6]

    return render(request, 'pages/about.html', {
        'page_title': 'About Us',
        'page': page,
        'stats': stats,
        'values': values,
        'why_us': why_us,
        'process': process,
        'certifications': certifications,
        'timeline': timeline,
        'testimonials': testimonials,
    })


def contact(request):
    page = ContactPage.load()
    faqs = FAQ.objects.filter(page='contact', is_active=True).order_by('display_order')
    site = SiteSettings.load()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ip_address = request.META.get('REMOTE_ADDR')
            msg.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            msg.save()
            # Confirmation to customer
            send_mail(
                f'We received your message – {site.site_name}',
                f'Dear {msg.full_name},\n\nThank you for contacting us.\n'
                f'Subject: {msg.subject}\n\nWe will get back to you shortly.\n\n'
                f'Best Regards,\n{site.site_name}',
                settings.DEFAULT_FROM_EMAIL,
                [msg.email],
                fail_silently=True,
            )
            # Notify admin
            send_mail(
                f'New Contact Message: {msg.subject}',
                f'From: {msg.full_name} ({msg.email})\nPhone: {msg.phone}\n\n{msg.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
            messages.success(
                request,
                _('Thank you! Your message has been received. We will get back to you soon.')
            )
            return redirect('pages:contact')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {
        'page_title': 'Contact Us',
        'page': page,
        'form': form,
        'faqs': faqs,
        'site': site,
    })


def privacy_policy(request):
    site = SiteSettings.load()
    return render(request, 'pages/policy.html', {
        'page_title': 'Privacy Policy',
        'content': site.privacy_policy,
    })


def terms_conditions(request):
    site = SiteSettings.load()
    return render(request, 'pages/policy.html', {
        'page_title': 'Terms & Conditions',
        'content': site.terms_conditions,
    })


def shipping_policy(request):
    site = SiteSettings.load()
    return render(request, 'pages/policy.html', {
        'page_title': 'Shipping Policy',
        'content': site.shipping_policy,
    })


def return_policy(request):
    site = SiteSettings.load()
    return render(request, 'pages/policy.html', {
        'page_title': 'Return & Refund Policy',
        'content': site.return_policy,
    })


def faq_page(request):
    faqs = FAQ.objects.filter(page='general', is_active=True).order_by('display_order')
    return render(request, 'pages/faq.html', {
        'page_title': 'Frequently Asked Questions',
        'faqs': faqs,
    })
