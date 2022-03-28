from django.contrib import admin
from django.db.models.fields.json import JSONField

from django_json_widget.widgets import JSONEditorWidget


MESSAGE_FIELDS = ('recipient', 'template', 'status', 'sent_at', 'related_to',)
TEMPLATE_FIELDS = ('name', 'key', 'subject_en',)


class AbstractMessageAdmin(admin.ModelAdmin):
    list_display = MESSAGE_FIELDS
    list_filter = ('status', 'template',)
    actions = ('send',)
    readonly_fields = ('status',)

    def send(self, request, queryset):
        for obj in queryset:
            obj.send()
    send.short_description = "Send"


class AbstractTemplateAdmin(admin.ModelAdmin):
    list_display = TEMPLATE_FIELDS
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
