from typing import Iterable

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


class EmailAttachment(AbstractAttachment):
    def __str__(self):
        return self.file.url


class SMS(AbstractMessage):
    template = models.ForeignKey(SMSTemplate, on_delete=models.CASCADE)

    def get_provider_name(self):
        return settings.MSGS['sms']

    class Meta:
        verbose_name_plural = 'SMS'


class Email(AbstractMessage):
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    attachments = models.ManyToManyField(EmailAttachment, blank=True)

    reply_to = models.CharField(max_length=256, **NULLABLE)
    cc_emails = models.JSONField(**NULLABLE)
    bcc_emails = models.JSONField(**NULLABLE)

    def get_provider_name(self):
        return settings.MSGS['email']

    def add_attachments(self, attachments: Iterable[str]):
        for item in attachments:
            attachment = EmailAttachment.objects.create(file=item)
            self.attachments.add(attachment)

    def get_cc_emails(self):
        return self.cc_emails or []

    def get_bcc_emails(self):
        return self.bcc_emails or []


class Message(AbstractMessage):
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)

    def get_provider_name(self):
        return settings.MSGS['message']
