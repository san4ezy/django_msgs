from django.conf import settings
from msgs.mixins import TemplatingMixin

from pysendpulse.pysendpulse import PySendPulse

from msgs.abstract.models import AbstractMessage
from msgs.providers.base import BaseEmailProvider


class SendpulseEmailProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['sendpulse']['options']

    def __init__(self):
        self.client = PySendPulse(
            self.settings['api_id'],
            self.settings['api_secret'],
            # TOKEN_STORAGE,
            # memcached_host=MEMCACHED_HOST,
        )

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        # attachments = self.get_attachments(message, lang, context)
        message_data = {
            'subject': title_html,
            'html': body_html,
            'text': self.html_to_text(body_html),
            'from': {
                'name': self.settings['sender_name'],
                'email': self.settings['sender'],
            },
            'to': [
                {
                    'name': '',
                    'email': message.recipient,
                },
            ],
        }
        response = self.client.smtp_send_mail(message_data)
        return response


class SendpulseTemplatingEmailProvider(SendpulseEmailProvider):
    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        message_data = {
            'subject': title_html,
            'from': {
                'name': self.settings['sender_name'],
                'email': self.settings['sender'],
            },
            'to': [
                {
                    'name': '',
                    'email': message.recipient,
                },
            ],
            "template": {
                'id': message.template.external_key,
                'variables': context,
            },
        }
        response = self.client.smtp_send_mail_with_template(message_data)
        return response
