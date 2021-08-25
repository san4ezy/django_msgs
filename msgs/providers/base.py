from django.conf import settings

from msgs.exceptions import MSGSProviderIsDisabled
from msgs.abstract.models import AbstractMessage
from msgs.models import Email, SMS, Message


class BaseProvider(object):
    client = None
    settings = None
    default_language = 'en'
    model: AbstractMessage = None  # !required!

    def get_lang(self, lang=None):
        if lang:
            return lang
        try:
            return settings.MSGS['options']['default_language']
        except KeyError:
            return self.default_language

    def get_sender(self) -> str:
        return self.settings['sender']

    @staticmethod
    def get_context_data(message, context=None):
        ctxt = message.context
        if context and isinstance(context, dict):
            ctxt.update(context)
        return ctxt

    def success(self, message: AbstractMessage) -> AbstractMessage:
        message.status = self.model.Status.SENT
        return message

    def error(self, message: AbstractMessage, error_text: str) -> AbstractMessage:
        message.status = self.model.Status.ERROR
        message.error = error_text
        return message

    def save_message(self, message: AbstractMessage):
        # Call this method for saving message state
        message.save()

    def perform(
            self, message: AbstractMessage, sender: str, lang: str, **kwargs,
    ) -> bool:
        """Override this method according to the particular provider"""
        return True

    def pre_send(self, message: AbstractMessage, **kwargs):
        pass

    def post_send(self, message: AbstractMessage, **kwargs):
        pass

    def send(self, message: AbstractMessage, **kwargs) -> bool:
        sender = self.get_sender()
        if not kwargs.get('lang'):
            kwargs['lang'] = self.get_lang()
        if self.settings.get('is_active') and sender:
            self.pre_send(message, **kwargs)
            r = None
            try:
                r = self.perform(message, sender, **kwargs)
                self.success(message)
            except Exception as e:
                self.error(message, str(e))
            else:
                self.post_send(message, response=r, **kwargs)
            finally:
                self.save_message(message)
                return r
        raise MSGSProviderIsDisabled(f"{self.__class__.__name__}'s sending is disabled")


class BaseEmailProvider(BaseProvider):
    model = Email


class BaseSMSProvider(BaseProvider):
    model = SMS


class BaseMessageProvider(BaseProvider):
    model = Message
