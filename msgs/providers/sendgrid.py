from django.conf import settings

from msgs.abstract.models import AbstractMessage
from sendgrid import SendGridAPIClient, Mail, Email, Attachment, FileContent, FileName, FileType, Disposition, ContentId

from msgs.providers.base import BaseEmailProvider
from msgs.mixins import TemplatingMixin


class SendgridEmailProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['sendgrid']['options']

    def __init__(self):
        self.client = SendGridAPIClient(
            self.settings['api_key']
        )

    def perform(
            self, message: AbstractMessage, sender: str, lang: str, **kwargs
    ) -> (dict, bool):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        attachments = self.get_attachments(message, lang, context)
        sendgrid_message = Mail(
            from_email=self.get_sender(message),
            to_emails=message.recipient,
            subject=title_html,
            html_content=body_html,
        )

        if message.reply_to:
            sendgrid_message.reply_to = message.reply_to

        for cc in message.get_cc_emails():
            sendgrid_message.personalizations[0].add_cc(Email(cc))

        for bcc in message.get_bcc_emails():
            sendgrid_message.personalizations[0].add_bcc(Email(bcc))

        for attachment in attachments:
            sendgrid_message.add_attachment(attachment)
        # sendgrid_message.add_attachment(self.get_logo_attachment())  # must be removed to the child class for the library version
        response = self.client.send(sendgrid_message)
        return response.to_dict, 200 <= response.status_code < 300

    def build_attachment_object(self, **kwargs):
        attachment_kwargs = [
            FileContent(kwargs['file_content']),
            FileName(kwargs['file_name']),
            FileType(kwargs['file_type']),
            Disposition(kwargs['disposition']),
        ]
        if 'content_id' in kwargs:
            attachment_kwargs.append(ContentId(kwargs['content_id']))
        return Attachment(*attachment_kwargs)
