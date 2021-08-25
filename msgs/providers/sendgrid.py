from django.conf import settings

from msgs.abstract.models import AbstractMessage
from sendgrid import SendGridAPIClient, Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId

from msgs.providers.base import BaseEmailProvider
from msgs.mixins import TemplatingMixin


class SendgridEmailProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['sendgrid']['options']

    def __init__(self):
        self.client = SendGridAPIClient(
            self.settings['api_key']
        )

    def perform(self, message: AbstractMessage, sender: str, lang: str, **kwargs):
        context = self.get_context_data(message)
        title_html, body_html = self.render(message, lang, context)
        attachments = self.get_attachments(message, lang, context)
        sendgrid_message = Mail(
            from_email=self.get_sender(),
            to_emails=message.recipient,
            subject=title_html,
            html_content=body_html,
        )
        for attachment in attachments:
            sendgrid_message.add_attachment(attachment)
        # sendgrid_message.add_attachment(self.get_logo_attachment())  # must be removed to the child class for the library version
        response = self.client.send(sendgrid_message)
        return response

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
