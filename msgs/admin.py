from django.contrib import admin
from django.conf import settings

from msgs.models import Tpl, Msg, Email, SMS


@admin.register(Tpl)
class TplAdmin(admin.ModelAdmin):
    list_display = ('subject_en',)


# @admin.register(AttachmentTpl)
# class AttachmentTplAdmin(admin.ModelAdmin):
#     list_display = ('name', 'template_name', 'tpl',)


@admin.register(Msg)
class MsgAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipient', 'tpl', 'status', 'created_at', 'modified_at',)
    list_filter = ('status', 'tpl',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipient', 'tpl', 'status', 'created_at', 'modified_at',)
    list_filter = ('status', 'tpl',)
    actions = ('send',)

    def send(self, request, queryset):
        for obj in queryset:
            obj.send(lang=settings.MSGS['options']['default_language'])
    send.short_description = "Send email"


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipient', 'tpl', 'status', 'created_at', 'modified_at',)
    list_filter = ('status', 'tpl',)
    actions = ('send',)

    def send(self, request, queryset):
        for obj in queryset:
            obj.send(lang=settings.MSGS['options']['default_language'])
    send.short_description = "Send sms"

