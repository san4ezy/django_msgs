import warnings
from django.conf import settings
from django.apps import apps

from msgs.abstract.models import AbstractMessage
from msgs.providers.base import BaseProvider


class DummyProvider(BaseProvider):
    settings = settings.MSGS['providers']['dummy']['options']

    def __init__(self):
        super().__init__()
        self.model = apps.get_model(self.settings['model'])

    def perform(self, message: AbstractMessage, sender: str, **kwargs) -> bool:
        warnings.warn(
            f'DummyProvider: {message.recipient}({message.pk}): {message.context}'
        )
        return True
