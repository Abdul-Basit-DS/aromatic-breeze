from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Subscriber


@require_POST
def subscribe(request):
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required.'})
    sub, created = Subscriber.objects.get_or_create(
        email=email,
        defaults={'name': name, 'ip_address': request.META.get('REMOTE_ADDR')}
    )
    if not created and sub.is_active:
        return JsonResponse({'status': 'exists', 'message': 'You are already subscribed!'})
    if not created and not sub.is_active:
        sub.is_active = True
        sub.save(update_fields=['is_active'])
    return JsonResponse({'status': 'ok', 'message': 'Thank you for subscribing!'})
