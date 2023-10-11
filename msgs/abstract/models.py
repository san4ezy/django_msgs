from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.db.models import JSONField, Model
from django.db import models
from django.forms import model_to_dict
from django_extensions.db.models import TimeStampedModel
from django.db.models.enums import TextChoices

from django.utils import timezone

from msgs.exceptions import (
    MSGSUnknownProvider, MSGSTemplateDoesNotExist, MSGSSignalNotFound, MSGSCannotBeSent
)
from msgs.helpers import NULLABLE, get_provider_class_from_string
from msgs.signals import (
    SIGNALS, BUILT_SIGNAL, CREATED_SIGNAL, SENT_SIGNAL, STATUS_CHANGED_SIGNAL
)

try:
    from django.utils.translation import gettext_lazy as _
except ImportError:
    from django.utils.translation import ugettext_lazy as _


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
    sender = models.CharField(max_length=256, **NULLABLE)
    context = JSONField(**NULLABLE)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.IN_QUEUE,
    )
    error = models.CharField(max_length=256, **NULLABLE)

    provider_id = models.CharField(max_length=64, **NULLABLE)
    provider_response = models.TextField(**NULLABLE)

    created_at = models.DateTimeField(auto_now_add=True, **NULLABLE)
    modified_at = models.DateTimeField(auto_now=True, **NULLABLE)
    sent_at = models.DateTimeField(**NULLABLE)

    # additional service information could be saved here
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, **NULLABLE)
    object_id = models.CharField(max_length=64, **NULLABLE)
    related_to = GenericForeignKey('content_type', 'object_id')
    service_context = JSONField(**NULLABLE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__origin_status = self.status

    def __str__(self):
        return f"{self.__class__.__name__} for {self.recipient}"

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.__origin_status != self.status:
            self.send_signal(
                STATUS_CHANGED_SIGNAL,
                instance=self,
                origin_status=self.__origin_status,
            )

    @classmethod
    def build(
            cls,
            template: str,
            recipient: str,
            context: dict,
            related_to: Model = None,
            service_context: dict = None,
            **kwargs,
    ):
        """Returns not saved instance"""
        template = cls.get_template(key=template)
        instance = cls(
            recipient=recipient,
            template=template,
            context=context,
            service_context=service_context,
            **kwargs,
        )
        if related_to:
            instance.related_to = related_to
        cls.send_signal(BUILT_SIGNAL, instance=instance)
        return instance

    @classmethod
    def create(
            cls,
            template: str,
            recipient: str,
            context: dict,
            related_to: Model = None,
            service_context: dict = None,
            skip_duplicates: bool = None,
            **kwargs,
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
            service_context=service_context,
            related_to=related_to,
            **kwargs,
        )
        instance.save()
        cls.send_signal(CREATED_SIGNAL, instance=instance)
        return instance

    def duplicate(self):
        data = model_to_dict(self, exclude=[
            'id', 'status', 'sent_at', 'service_context', 'provider_response',
            'error', 'provider_id', 'template', 'content_type',
        ])
        data['template'] = self.template
        data['content_type'] = self.content_type
        attachments = []
        if hasattr(self, 'attachments') and 'attachments' in data:
            data.pop('attachments')
            attachments = self.attachments.all()
        duplicated_obj = self._meta.model.objects.create(**data)
        for a in attachments:
            duplicated_obj.attachments.add(a)
        return duplicated_obj

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

    def send(
            self,
            lang=None,
            raise_exceptions: bool = None,
            duplicate: bool = None,
    ):
        if duplicate is None:
            duplicate = settings.MSGS['options'].get('auto_duplicate', False)
        provider = self.get_provider()
        self.sent_at = timezone.now()
        try:
            provider.send(self, lang=lang, raise_exceptions=raise_exceptions)
        except MSGSCannotBeSent as e:
            if duplicate:  # make a copy of this message and send it
                msg = self.duplicate()
                msg.send(lang=lang)
            else:
                raise e
        else:
            self.send_signal(SENT_SIGNAL, instance=self)

    @classmethod
    def __get_template_model(cls) -> Model:
        return cls._meta.get_field(DEFAULT_TEMPLATE_FIELD).related_model

    @classmethod
    def send_signal(cls, name: str, *args, **kwargs):
        try:
            signal = SIGNALS[cls.__name__][name]
        except KeyError as e:
            raise MSGSSignalNotFound(f'[{cls.__name__}][{name}]')
        else:
            signal.send(cls, *args, **kwargs)


class AbstractAttachment(models.Model):
    class Meta:
        abstract = True

    file = models.FileField(upload_to='msgs/attachments/')
