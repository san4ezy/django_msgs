from django.conf import settings

from msgs.exceptions import MSGSProviderIsDisabled
from msgs.models import Msg


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

    def success(self, message: Msg) -> Msg:
        message.status = Msg.SENT
        return message

    def error(self, message: Msg, error_text: str) -> Msg:
        message.status = Msg.ERROR
        message.error = error_text
        return message

    def save_message(self, message: Msg):
        # Call this method for saving message state
        message.save()

    def perform(self, message: Msg, sender: str, **kwargs) -> bool:
        """Override this method according to the particular provider"""
        return True

    def pre_send(self, message: Msg, **kwargs):
        pass

    def post_send(self, message: Msg, **kwargs):
        pass

    def send(self, message: Msg, **kwargs) -> bool:
        sender = self.get_sender()
        kwargs['lang'] = kwargs.get('lang', self.get_lang())
        if self.settings.get('is_active') and sender:
            self.pre_send(message, **kwargs)
            r = self.perform(message, sender, **kwargs)
            self.post_send(message, response=r, **kwargs)
            self.save_message(message)
            return r
        raise MSGSProviderIsDisabled(f"{self.__class__.__name__}'s sending is disabled")
