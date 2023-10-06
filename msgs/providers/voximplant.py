class VoximplantProvider(Provider):
    settings = settings.VOXIMPLANT

    def __init__(self):
        self.client = VoximplantAPI(self.settings['credentials_path'])

    def get_sender(self, message: AbstractMessage, **kwargs):
        return super().get_sender(message).strip('+')

    def perform(
            self, message: Msg, sender: str, lang: str, **kwargs
    ) -> (dict, bool):
        try:
            return self.client.send_sms_message(
                sender,
                message.recipient.phone_number.strip('+'),
                f"{message.text}",
            ), True  # Dummy True
        except VoximplantException as e:
            print(f"Error: {e.message}")
