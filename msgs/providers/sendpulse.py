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
        attachments = self.get_attachments(message, lang, context)
        sendpulse_message = {
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
            # 'bcc': [{'name': '', 'email': ''}],
        }
        # try:
        response = self.client.smtp_send_mail(sendpulse_message)
        # except Exception as e:
        #     self.error(message, str(e))
        # else:
        #     if response.get('result', False):
        #         self.success(message)
        #     else:
        #         self.error(response.get('message'), response)
        return response