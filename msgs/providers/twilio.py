class TwilioProvider(Provider):
    settings = settings.TWILIO

    def __init__(self):
        self.client = TwilioClient(
            self.settings['account_sid'],
            self.settings['auth_token'],
        )

    def perform(self, message: Msg, sender: str, lang: str, **kwargs):
        message = self.client.messages.create(
            body=f"{message.text}",
            from_=sender,
            to=message.recipient.phone_number,
        )
        return message.sid
