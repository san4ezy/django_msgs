from django.contrib import admin
from django.db.models.fields.json import JSONField

from django_json_widget.widgets import JSONEditorWidget


MESSAGE_FIELDS = ('recipient', 'template', 'status', 'sent_at', 'related_to',)
TEMPLATE_FIELDS = ('name', 'key', 'subject_en',)


class AbstractMessageAdmin(admin.ModelAdmin):
    list_display = MESSAGE_FIELDS
    list_filter = ('status', 'template',)
    actions = ('send', 'duplicate',)
    readonly_fields = ('status', 'created_at', 'modified_at', 'related_to',)
    fieldsets = [
        ('Common Info', {
            'fields': [
                'recipient',
                'sender',
                'template',
                'status',
                'error',
                'related_to',
                'context',
            ],
        }),
        ('Service Info', {
            'fields': [
                'created_at',
                'modified_at',
                'sent_at',
                'service_context',
            ]
        }),
        ('Provider Info', {
            'fields': [
                'provider_id',
                'provider_response',
            ]
        })
    ]

    def send(self, request, queryset):
        for obj in queryset:
            obj.send()
    send.short_description = "Send"

    def duplicate(self, request, queryset):
        for obj in queryset:
            obj.duplicate()
    duplicate.short_description = "Duplicate"

    def has_change_permission(self, request, obj=None):
        return False


class AbstractTemplateAdmin(admin.ModelAdmin):
    list_display = TEMPLATE_FIELDS
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
