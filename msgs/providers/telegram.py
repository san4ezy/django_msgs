import requests

from collections.abc import Iterable

from django.conf import settings

from msgs.mixins import TemplatingMixin
from msgs.providers.base import BaseMessageProvider
from msgs.abstract.models import AbstractMessage


class TelegramProvider(TemplatingMixin, BaseMessageProvider):
    settings = settings.MSGS['providers']['telegram']['options']
    bot_token = settings['token']

    def get_chat_id(self, user):
        return self.settings['chat']

    def get_request_string(self, token, cid, text):
        domain = 'https://api.telegram.org'
        return f'{domain}/bot{token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={text}'

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        cid = self.get_chat_id(message.recipient)
        sender = self.get_sender()
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        txt = f'from: {sender}\nto:   {message.recipient}\n\ntitle: {title_html}\n\n {body_html}'
        text = self.get_request_string(self.bot_token, cid, txt)
        response = requests.get(text)
        return response.json()


class TelegramLoggerProvider(TelegramProvider):
    def get_chat_id(self, user):
        cid = self.settings['chat']
        if not isinstance(cid, Iterable):
            cid = [cid, ]
        return cid

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        cids = self.get_chat_id(message.recipient)
        sender = self.get_sender()
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        text = f'from: {sender}\nto:   {message.recipient}\n\ntitle: {title_html}\n\n {body_html}'
        for cid in cids:
            url = self.get_request_string(self.bot_token, cid, text)
            response = requests.get(url)
        return {'status': 'ok'}
