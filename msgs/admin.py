from django.contrib import admin


from msgs.abstract.admin import AbstractMessageAdmin, AbstractTemplateAdmin
from msgs.models import (
    SMSTemplate, EmailTemplate, MessageTemplate, SMS, Email, Message, EmailAttachment,
)


@admin.register(SMSTemplate)
class SMSTemplateAdmin(AbstractTemplateAdmin):
    pass


@admin.register(EmailTemplate)
class EmailTemplateAdmin(AbstractTemplateAdmin):
    pass


@admin.register(MessageTemplate)
class MessageTemplateAdmin(AbstractTemplateAdmin):
    pass


@admin.register(Message)
class MessageAdmin(AbstractMessageAdmin):
    pass


@admin.register(Email)
class EmailAdmin(AbstractMessageAdmin):
    fieldsets = [
        ('Common Info', {
            'fields': [
                'recipient',
                'sender',
                'reply_to',
                'cc_emails',
                'bcc_emails',
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


@admin.register(SMS)
class SMSAdmin(AbstractMessageAdmin):
    pass


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    pass
