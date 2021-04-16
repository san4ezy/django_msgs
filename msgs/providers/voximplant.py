class VoximplantProvider(Provider):
    settings = settings.VOXIMPLANT

    def __init__(self):
        self.client = VoximplantAPI(self.settings['credentials_path'])

    def get_sender(self):
        return super().get_sender().strip('+')

    def perform(self, message: Msg, sender: str, lang: str, **kwargs):
        try:
            return self.client.send_sms_message(
                sender,
                message.recipient.phone_number.strip('+'),
                f"{message.text}",
            )
        except VoximplantException as e:
            print(f"Error: {e.message}")
