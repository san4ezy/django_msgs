from django.conf import settings

from msgs.exceptions import MSGSProviderIsDisabled


class BaseProvider(object):
    client = None
    settings = None
    default_language = 'en'

    def get_lang(self):
        try:
            return settings.MSGS['options']['default_language']
        except KeyError:
            return self.default_language

    def get_sender(self) -> str:
        return self.settings['sender']

    def perform(self, message, sender, **kwargs):
        """Override this method according to the particular provider"""
        return True

    def pre_send(self, message, **kwargs):
        pass

    def post_send(self, message, **kwargs):
        pass

    def send(self, message, **kwargs) -> bool:
        sender = self.get_sender()
        if self.settings.get('is_active') and sender:
            self.pre_send(message, **kwargs)
            r = self.perform(message, sender, **kwargs)
            self.post_send(message, **kwargs)
            return r
        raise MSGSProviderIsDisabled(f"{self.__class__.__name__}'s sending is disabled")
