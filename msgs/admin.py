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
    pass


@admin.register(SMS)
class SMSAdmin(AbstractMessageAdmin):
    pass


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    pass
