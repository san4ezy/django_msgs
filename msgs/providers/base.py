from django.conf import settings

from msgs.exceptions import MSGSProviderIsDisabled, MSGSConfigurationError, \
    MSGSCannotBeSent
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

    def get_sender(self, message: AbstractMessage, **kwargs) -> dict | str:
        message_sender = message.sender
        settings_sender = self.settings.get('sender')

        if settings_sender is None:
            raise MSGSConfigurationError("Sender must be set.")
        elif settings_sender == '*':
            if not message_sender:
                raise MSGSConfigurationError("Message sender must be set if global option is a `*` symbol.")
            return message_sender
        elif isinstance(settings_sender, str):
            if message_sender:
                raise MSGSConfigurationError("Message sender cannot be set if the global sender used.")
            return settings_sender
        elif isinstance(settings_sender, list) or isinstance(settings_sender, tuple):
            if not message_sender:
                # set first sender as a default if the message sender is not set
                message_sender = settings_sender[0]
            if message_sender not in settings_sender:
                raise MSGSConfigurationError("Message sender not in the allowed list.")
            return message_sender

    @staticmethod
    def get_context_data(message, context=None):
        ctxt = message.context
        if context and isinstance(context, dict):
            ctxt.update(context)
        return ctxt

    def success(self, message: AbstractMessage, response: dict) -> AbstractMessage:
        message.status = self.model.Status.SENT
        message.provider_response = response
        message.provider_id = self.get_provider_id(message, response)
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
    ) -> (dict, bool):
        """
        Override this method according to the particular provider.
        Return:
            response (dict)
            is_success (bool)
        """
        return {}, True

    def pre_send(self, message: AbstractMessage, **kwargs):
        pass

    def post_send(self, message: AbstractMessage, is_success: bool, **kwargs):
        pass

    def get_provider_id(self, message: AbstractMessage, response: dict) -> str:
        pass

    def send(self, message: AbstractMessage, **kwargs) -> bool:
        raise_exceptions = kwargs.get('raise_exceptions', None)
        if not raise_exceptions:
            raise_exceptions = settings.MSGS['options'].get('raise_exceptions', False)
        if message.status != AbstractMessage.Status.IN_QUEUE and raise_exceptions:
            raise MSGSCannotBeSent
        if not kwargs.get('lang'):
            kwargs['lang'] = self.get_lang()
        if self.settings.get('is_active'):
            self.pre_send(message, **kwargs)
            response, err = None, None
            try:
                sender = self.get_sender(message, **kwargs)
                response, is_success = self.perform(message, sender, **kwargs)
            except Exception as e:
                self.error(message, str(e))
                err = e
            else:
                self.success(message, response)
                self.post_send(
                    message, response=response, is_success=is_success, **kwargs,
                )
            finally:
                self.save_message(message)
                if err and raise_exceptions:
                    raise err
                return response
        raise MSGSProviderIsDisabled(f"{self.__class__.__name__}'s sending is disabled")


class BaseEmailProvider(BaseProvider):
    model = Email


class BaseSMSProvider(BaseProvider):
    model = SMS


class BaseMessageProvider(BaseProvider):
    model = Message


# class ProxyProvider(BaseProvider):
#     proxy_model: BaseProvider
#
#     def send(self, message: AbstractMessage, **kwargs) -> bool:
