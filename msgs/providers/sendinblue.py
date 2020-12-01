import json
import requests

from django.conf import settings

from msgs.providers.base import BaseProvider
from msgs.mixins import TemplatingMixin


class SendinblueProvider(TemplatingMixin, BaseProvider):
    settings = settings.MSGS['providers']['sendinblue']['options']

    def __init__(self):
        self.url = "https://api.sendinblue.com/v3/smtp/email"

    def get_sender(self) -> dict:
        return {
            'email': self.settings['sender_email'],
            'name': self.settings['sender_name'],
        }

    def perform(self, message, sender, **kwargs):
        lang = kwargs.get('lang', self.get_lang())
        title_html, body_html, attachments = self.render(message, lang)

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
                'LOGO': 'https://vetsapp.ch/img/logo.png',
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
