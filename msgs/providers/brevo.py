# import json
# import requests
#
# from django.conf import settings
#
# from msgs.providers.base import BaseEmailProvider
# from msgs.mixins import TemplatingMixin
# from msgs.abstract.models import AbstractMessage
#
#
# class SendinblueEmailProvider(TemplatingMixin, BaseEmailProvider):
#     settings = settings.MSGS['providers']['sendinblue']['options']
#
#     def __init__(self):
#         self.url = "https://api.sendinblue.com/v3/smtp/email"
#
#     def get_sender(self, message: AbstractMessage, **kwargs) -> dict:
#         return {
#             'email': self.settings['sender_email'],
#             'name': self.settings['sender_name'],
#         }
#
#     def perform(
#             self, message: AbstractMessage, sender: str, lang: str, **kwargs
#     ) -> (dict, bool):
#         context = self.get_context_data(message)
#         title_html, body_html = self.render(message, lang, context)
#         attachments = self.get_attachments(message, lang, context)
#
#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "api-key": self.settings['api_key'],
#         }
#
#         data = {
#             'sender': self.get_sender(message),
#             'htmlContent': body_html,
#             'subject': title_html,
#             'to': [{'name': message.recipient, 'email': message.recipient}, ],
#             'params': {
#                 'LOGO': 'https://example.com/logo.png',
#             },
#         }
#         if attachments:
#             data.update({'attachment': attachments})
#
#         response = requests.request("POST", self.url, headers=headers, data=json.dumps(data))
#         return response.json(), True  # Dummy True
#
#     def build_attachment_object(self, **kwargs):
#         return {
#             'content': kwargs['file_content'],
#             'name': kwargs['file_name'],
#         }


import requests
from django.conf import settings
from .base import BaseEmailProvider
from ..abstract.models import AbstractMessage
from ..mixins import TemplatingMixin


class BrevoProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['brevo']['options']

    def __init__(self):
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    def perform(
            self, message: AbstractMessage, sender: str, lang: str, **kwargs
    ) -> (dict, bool):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        attachments = self.get_attachments(message, lang, context)
        if not self.settings['api_key']:
            return False, "Brevo API key is not configured."

        headers = {
            "accept": "application/json",
            "api-key": self.settings['api_key'],
            "content-type": "application/json"
        }

        payload = {
            "sender": {
                # "name": self.settings['sender_name'],
                "email": self.get_sender(message),
            },
            "to": [
                {
                    "email": message.recipient,
                    # "name": getattr(message_obj, 'recipient_name', '')
                }
            ],
            "subject": title_html,
            "htmlContent": body_html,
            "textContent": body_html
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)

            if response.status_code in [201, 202]:
                return True, response.json().get('messageId')
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)
