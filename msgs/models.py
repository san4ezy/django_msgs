from django.conf import settings
from django.db import models

from msgs.abstract.models import AbstractTemplate, AbstractMessage, AbstractAttachment
from msgs.helpers import NULLABLE


class SMSTemplate(AbstractTemplate):
    pass


class EmailTemplate(AbstractTemplate):
    pass


class MessageTemplate(AbstractTemplate):
    pass


# class AttachmentTpl(models.Model):
#     name = models.CharField(max_length=64, unique=True)
#     template_name = models.CharField(max_length=64)
#     output_file_name = models.CharField(max_length=64, default='attachment.pdf')
#     tpl = models.ForeignKey(Tpl, on_delete=models.CASCADE, related_name='attachments')
#
#     def __str__(self):
#         return self.name


class EmailAttachment(AbstractAttachment):
    pass


class SMS(AbstractMessage):
    template = models.ForeignKey(SMSTemplate, on_delete=models.CASCADE)

    def get_provider_name(self):
        return settings.MSGS['sms']

    class Meta:
        verbose_name_plural = 'SMS'


class Email(AbstractMessage):
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    attachments = models.ManyToManyField(EmailAttachment)

    def get_provider_name(self):
        return settings.MSGS['email']


class Message(AbstractMessage):
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)

    def get_provider_name(self):
        return settings.MSGS['message']
