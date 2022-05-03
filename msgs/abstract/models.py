from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.db.models import JSONField, Model
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.db.models.enums import TextChoices
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from msgs.exceptions import MSGSUnknownProvider, MSGSTemplateDoesNotExist
from msgs.helpers import NULLABLE, get_provider_class_from_string


DEFAULT_TEMPLATE_FIELD = 'template'


class AbstractTemplate(models.Model):
    class Meta:
        abstract = True

    # class Type(TextChoices):
    #     EMAIL = 'email'
    #     SMS = 'sms'
    #     MESSENGER = 'messenger'

    name = models.CharField(max_length=64, default='default name')
    notes = models.CharField(max_length=128, **NULLABLE)

    # type = models.CharField(max_length=16, choices=Type.choices, **NULLABLE)
    key = models.CharField(max_length=64, unique=True)
    external_key = models.CharField(max_length=64, **NULLABLE)

    subject_en = models.CharField(max_length=254, default='Subject')
    body_en = models.TextField()

    def __str__(self):
        return self.name

    def get_body(self, lang):
        return getattr(self, f'body_{lang}')

    def get_subject(self, lang):
        return getattr(self, f'subject_{lang}')


class AbstractMessage(TimeStampedModel):
    class Meta:
        abstract = True

    class Status(TextChoices):
        IN_QUEUE = 'in_queue', _('In queue')
        SENT = 'sent', _('Sent')
        ERROR = 'error', _('Error')
        DELIVERED = 'delivered', _('Delivered')
        REJECTED = 'rejected', _('Rejected')

    template = models.ForeignKey(AbstractTemplate, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=64)
    context = JSONField(**NULLABLE)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.IN_QUEUE,
    )
    error = models.CharField(max_length=256, **NULLABLE)

    provider_id = models.CharField(max_length=64, **NULLABLE)
    provider_response = models.CharField(max_length=256, **NULLABLE)

    created_at = models.DateTimeField(auto_now_add=True, **NULLABLE)
    modified_at = models.DateTimeField(auto_now=True, **NULLABLE)
    sent_at = models.DateTimeField(**NULLABLE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, **NULLABLE)
    object_id = models.PositiveIntegerField(**NULLABLE)
    related_to = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.__class__.__name__} for {self.recipient}"

    @classmethod
    def build(
            cls,
            template: str,
            recipient: str,
            context: dict,
            related_to: Model = None,
    ):
        """Returns not saved instance"""
        template = cls.get_template(key=template)
        instance = cls(
            recipient=recipient,
            template=template,
            context=context,
        )
        if related_to:
            instance.related_to = related_to
        return instance

    @classmethod
    def create(
            cls,
            template: str,
            recipient: str,
            context: dict,
            related_to: Model = None,
            skip_duplicates: bool = None,
    ):
        if skip_duplicates is None:
            skip_duplicates = settings.MSGS['options'].get('skip_duplicates')
        if skip_duplicates and cls.objects.filter(
                template__key=template,
                status=cls.Status.IN_QUEUE,
                recipient=recipient,
        ).exists():
            # skip duplicates in queue
            return
        instance = cls.build(
            template=template,
            recipient=recipient,
            context=context,
            related_to=related_to,
        )
        instance.save()
        return instance

    def get_provider_name(self):
        return 'development'

    def get_provider(self):
        provider = settings.MSGS['providers'].get(self.get_provider_name())
        if not provider:
            raise MSGSUnknownProvider(f"{provider} is unknown")
        provider = provider['backend']
        return get_provider_class_from_string(provider)()

    @classmethod
    def get_template(cls, key: str) -> AbstractTemplate:
        template_model = cls.__get_template_model()
        try:
            template = template_model.objects.get(key=key)
        except template_model.DoesNotExist:
            raise MSGSTemplateDoesNotExist
        else:
            return template

    def get_status(self):
        return [x[1] for x in self.Status.choices if x[0] == self.status][0]

    def send(self, lang=None):
        provider = self.get_provider()
        self.sent_at = timezone.now()
        provider.send(self, lang=lang)

    @classmethod
    def __get_template_model(cls) -> Model:
        return cls._meta.get_field(DEFAULT_TEMPLATE_FIELD).related_model


class AbstractAttachment(models.Model):
    class Meta:
        abstract = True

    file = models.FileField(upload_to='msgs/attachments/')
