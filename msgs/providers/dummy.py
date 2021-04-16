import warnings
from django.conf import settings

from msgs.models import Msg
from msgs.providers.base import BaseProvider


class DummyProvider(BaseProvider):
    settings = settings.MSGS['providers']['dummy']['options']

    def perform(self, message: Msg, sender: str, **kwargs) -> bool:
        warnings.warn(
            f'DummyProvider: {message.recipient}({message.pk}): {message.context}'
        )
        return True
