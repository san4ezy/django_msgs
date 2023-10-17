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
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        fields = fieldsets[0][1]['fields']
        fields.extend([
            'reply_to',
            'cc_emails',
            'bcc_emails',
        ])
        fields = list(set(fields))
        fieldsets[0][1]['fields'] = fields
        return fieldsets


@admin.register(SMS)
class SMSAdmin(AbstractMessageAdmin):
    pass


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    pass
