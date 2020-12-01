import requests
from django.conf import settings

from msgs.providers.base import BaseProvider


class TelegramProvider(BaseProvider):
    settings = settings.MSGS['providers']['telegram']['options']
    bot_token = settings['token']

    def get_chat_id(self, user):
        return settings['chat']

    def perform(self, message, sender, **kwargs):
        cid = self.get_chat_id(message.recipient)
        txt = f'from: {message.sender.phone_number}\nto:   {message.recipient.phone_number}\n\nbody: {message.text}'
        text = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={cid}&parse_mode=Markdown&text={txt}'
        response = requests.get(text)
        return response.json()
