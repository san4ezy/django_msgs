from django.conf import settings
from django.db.models import JSONField
from django.db import models
from django_extensions.db.models import TimeStampedModel

from msgs.exceptions import MSGSUnknownProvider
from msgs.helpers import get_provider_class_from_string


NULLABLE = {'blank': True, 'null': True}


class Tpl(models.Model):
    key = models.CharField(max_length=32, unique=True)
    subject_en = models.CharField(max_length=254, default='Subject')
    body_en = models.TextField()
    # extends = models.ForeignKey('self')

    def __str__(self):
        return self.subject_en

    def get_subject(self, lang):
        return getattr(self, f'subject_{lang}')

    def get_body(self, lang):
        return getattr(self, f'body_{lang}')


# class AttachmentTpl(models.Model):
#     name = models.CharField(max_length=64, unique=True)
#     template_name = models.CharField(max_length=64)
#     output_file_name = models.CharField(max_length=64, default='attachment.pdf')
#     tpl = models.ForeignKey(Tpl, on_delete=models.CASCADE, related_name='attachments')
#
#     def __str__(self):
#         return self.name


class Msg(TimeStampedModel):
    IN_QUEUE, SENT, ERROR, DELIVERED, REJECTED = range(5)
    STATUS_CHOICES = (
        (IN_QUEUE, 'In queue'),
        (SENT, 'Sent'),
        (ERROR, 'Error'),
        (DELIVERED, 'Delivered'),
        (REJECTED, 'Rejected'),
    )

    recipient = models.CharField(max_length=64)
    tpl = models.ForeignKey(Tpl, on_delete=models.CASCADE)
    context = JSONField(**NULLABLE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=IN_QUEUE)
    error = models.CharField(max_length=256, **NULLABLE)

    provider_id = models.CharField(max_length=64, **NULLABLE)
    provider_response = models.CharField(max_length=256, **NULLABLE)

    created_at = models.DateTimeField(auto_now_add=True,  **NULLABLE)
    modified_at = models.DateTimeField(auto_now=True, **NULLABLE)

    def __str__(self):
        return f"{self.tpl} msg for {self.recipient}"

    def get_provider_name(self):
        return 'development'

    def get_provider(self):
        provider = settings.MSGS['providers'].get(self.get_provider_name())
        if not provider:
            raise MSGSUnknownProvider(f"{provider} is unknown")
        provider = provider['backend']
        return get_provider_class_from_string(provider)()

    def get_status(self):
        return [x[1] for x in self.STATUS_CHOICES if x[0] == self.status][0]

    def send(self, lang=None):
        provider = self.get_provider()
        provider.send(self, lang=lang)


class SMS(Msg):
    class Meta:
        proxy = True

    def get_provider_name(self):
        return settings.MSGS['sms']


class Email(Msg):
    class Meta:
        proxy = True

    def get_provider_name(self):
        return settings.MSGS['email']
