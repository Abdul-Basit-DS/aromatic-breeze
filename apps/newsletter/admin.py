from django.contrib import admin
from django.http import HttpResponse
from .models import Subscriber
import csv


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at', 'ip_address')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    list_editable = ('is_active',)
    actions = ['export_csv', 'activate', 'deactivate']

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Active', 'Subscribed At'])
        for s in queryset:
            writer.writerow([s.email, s.name, s.is_active, s.subscribed_at])
        return response
    export_csv.short_description = 'Export to CSV'

    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = 'Activate selected'

    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = 'Deactivate selected'
