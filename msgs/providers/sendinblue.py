import json
import requests

from django.conf import settings

from msgs.providers.base import BaseEmailProvider
from msgs.mixins import TemplatingMixin
from msgs.abstract.models import AbstractMessage


class SendinblueEmailProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['sendinblue']['options']

    def __init__(self):
        self.url = "https://api.sendinblue.com/v3/smtp/email"

    def get_sender(self) -> dict:
        return {
            'email': self.settings['sender_email'],
            'name': self.settings['sender_name'],
        }

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        attachments = self.get_attachments(message, lang, context)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.settings['api_key'],
        }

        data = {
            'sender': self.get_sender(),
            'htmlContent': body_html,
            'subject': title_html,
            'to': [{'name': message.recipient, 'email': message.recipient}, ],
            'params': {
                'LOGO': 'https://example.com/logo.png',
            },
        }
        if attachments:
            data.update({'attachment': attachments})

        response = requests.request("POST", self.url, headers=headers, data=json.dumps(data))
        return response.text

    def build_attachment_object(self, **kwargs):
        return {
            'content': kwargs['file_content'],
            'name': kwargs['file_name'],
        }
