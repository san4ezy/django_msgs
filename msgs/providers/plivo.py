from msgs.exceptions import MSGSProviderIsDisabled
from msgs.mixins import TemplatingMixin
from msgs.abstract.models import AbstractMessage

import plivo

from msgs.providers.base import BaseSMSProvider

from django.conf import settings


class MSGSPlivoProviderError(Exception):
    pass


class PlivoSMSProvider(TemplatingMixin, BaseSMSProvider):
    settings = settings.MSGS['providers']['plivo']['options']

    def __init__(self):
        if not self.settings.get('is_active'):
            self.client = None
        self.client = plivo.RestClient(
            self.settings['auth_id'],
            self.settings['auth_token'],
        )
        self.callback_url = self.settings['callback_url']
        self.powerpack_uuid = self.settings['powerpack_uuid']
        self.sender = self.settings['sender']
        if not self.powerpack_uuid and not self.sender:
            raise MSGSPlivoProviderError(
                'either one of "powerpack_uuid" or "sender" (source phone number) '
                'must be provided')

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs) -> bool:
        context = self.get_context_data(message)
        _, body = self.render(message, lang, context)
        extra_kwargs = {}
        if self.callback_url:
            extra_kwargs.update({'url': self.callback_url})
        if self.sender:
            extra_kwargs.update({'src': self.sender})
        else:
            extra_kwargs.update({'powerpack_uuid': self.powerpack_uuid})

        response = self.client.messages.create(
            dst=message.recipient,
            text=body,
            **extra_kwargs,
        )
        return response

    def send(self, message: AbstractMessage, **kwargs) -> bool:
        r = None
        try:
            r = super().send(message, **kwargs)
        except MSGSProviderIsDisabled as e:
            pass
        return r
