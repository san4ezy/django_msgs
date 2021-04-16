import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from django.conf import settings

from msgs.providers.base import BaseProvider
from msgs.mixins import TemplatingMixin


class SendinblueSDKProvider(TemplatingMixin, BaseProvider):
    settings = settings.MSGS['providers']['sendinblue_sdk']['options']

    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.settings['api_key']
        self.configuration = configuration
        self.client = sib_api_v3_sdk.SendSmtpEmail

    @property
    def sender_name(self):
        return self.settings['sender_name']

    @property
    def sender_email(self):
        return self.settings['sender_email']

    def get_sender(self) -> str:
        return self.sender_email

    def perform(self, message: Msg, sender: str, lang: str, **kwargs):
        title_html, body_html, attachments = self.render(message, lang)
        api_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(self.configuration))
        senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(
            name=self.sender_name,
            email=self.sender_email,
        )
        sendTo = sib_api_v3_sdk.SendSmtpEmailTo(
            email=message.recipient,
            name="Recipient Name"  # what's the name?
        )
        arrTo = [sendTo]
        sending_kwargs = {
            "sender": senderSmtp,
            "to": arrTo,
            "html_content": body_html,
            "subject": title_html,
        }
        # attachments.append(self.get_logo_attachment())
        if attachments:
            sending_kwargs['attachment'] = attachments
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**sending_kwargs)
        api_response = api_instance.send_transac_email(send_smtp_email)
        return api_response

    def build_attachment_object(self, **kwargs):
        return sib_api_v3_sdk.SendSmtpEmailAttachment(
            content=kwargs['file_content'],
            name=kwargs['file_name'],
        )
