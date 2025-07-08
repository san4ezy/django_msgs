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
        if not recipient.startswith('+'):###################### + is bad for EMAILs!!!!!!!!!!!!!!!!!!
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
        event_status = event['event']
        timestamp = event['timestamp']
        sg_event_id = event['sg_event_id']
        sg_message_id = event['sg_message_id']



class TwilioEmailProvider(TwilioBaseProvider, BaseEmailProvider):
    pass


class TwilioSMSProvider(TwilioBaseProvider, BaseSMSProvider):
    pass
