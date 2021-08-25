import requests
from django.conf import settings

from msgs.mixins import TemplatingMixin
from msgs.providers.base import BaseMessageProvider
from msgs.abstract.models import AbstractMessage


class TelegramProvider(TemplatingMixin, BaseMessageProvider):
    settings = settings.MSGS['providers']['telegram']['options']
    bot_token = settings['token']

    def get_chat_id(self, user):
        return self.settings['chat']

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        cid = self.get_chat_id(message.recipient)
        sender = self.get_sender()
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        txt = f'from: {sender}\nto:   {message.recipient}\n\ntitle: {title_html}\n\n {body_html}'
        text = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={txt}'
        response = requests.get(text)
        return response.json()
