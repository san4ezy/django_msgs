from twilio.rest import Client as TwilioClient

from django.conf import settings

from msgs.abstract.models import AbstractMessage

from msgs.providers.base import BaseEmailProvider
from msgs.providers.base import BaseSMSProvider
from msgs.mixins import TemplatingMixin


class TwilioBaseProvider(TemplatingMixin):
    settings = settings.MSGS['providers']['twilio']['options']

    def __init__(self):
        self.client = TwilioClient(
            self.settings['account_sid'],
            self.settings['auth_token'],
        )

    def process_webhook_event(self, event: dict):
        event_status = event['event']
        timestamp = event['timestamp']
        sg_event_id = event['sg_event_id']
        sg_message_id = event['sg_message_id']



class TwilioEmailProvider(TwilioBaseProvider, BaseEmailProvider):
    def perform(
            self, message: AbstractMessage, sender: str, lang: str, **kwargs
    ) -> (dict, bool):
        context = self.get_context_data(message)
        _, body = self.render(message, lang, context)

        extra_kwargs = {}
        if sender.startswith('MG'):
            extra_kwargs = {'messaging_service_sid': sender}
        else:
            extra_kwargs = {'from_': sender}

        recipient = message.recipient
        result = self.client.messages.create(
            body=body,
            to=recipient,
            **extra_kwargs,
        )
        result = result.__dict__
        message.provider_response = result
        return result, True  # Dummy True

class TwilioSMSProvider(TwilioBaseProvider, BaseSMSProvider):
    def __init__(self):
        super().__init__()
        self.internal_message_id = "MessageSid"

    def perform(
            self, message: AbstractMessage, sender: str, lang: str, **kwargs
    ) -> (dict, bool):
        context = self.get_context_data(message)
        _, body = self.render(message, lang, context)

        extra_kwargs = {}
        if sender.startswith('MG'):
            extra_kwargs = {'messaging_service_sid': sender}
        else:
            extra_kwargs = {'from_': sender}

        if webhook_url := self.settings.get("webhook_url"):
            extra_kwargs.update({'status_callback': webhook_url})

        recipient = message.recipient
        if not recipient.startswith('+'):
            recipient = '+' + recipient
        result = self.client.messages.create(
            body=body,
            to=recipient,
            **extra_kwargs,
        )
        result = result.__dict__
        message.provider_response = result
        return result, True  # Dummy True

    def process_webhook_event(self, event: dict):
        message_id = event.get("MessageSid")
        if not message_id:
            return None

        event_status = {
            # "queued": self.model.Status.SENT,
            # "sending": self.model.Status.SENT,
            # "sent": self.model.Status.SENT,
            # "delivering": self.model.Status.SENT, # In transit, but not confirmed delivered
            "delivered": self.model.Status.DELIVERED,

            # Twilio delivery failure statuses:
            "failed": self.model.Status.ERROR,
            # "undelivered": self.model.Status.UNDELIVERED,
            # "accepted": self.model.Status.SENT,
            # "scheduled": self.model.Status.SENT,
            "canceled": self.model.Status.REJECTED,
        }.get(event.get('MessageStatus'))

        if event_status:
            msg = self.model.objects.filter(provider_id=message_id).last()
            msg.status = event_status
            msg.save(update_fields=["status"])
        return None

    def get_provider_id(self, message: AbstractMessage, response: dict) -> str:
        return response.get('sid')
