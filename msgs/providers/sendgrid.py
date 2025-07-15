from django.conf import settings

from msgs.abstract.models import AbstractMessage

from sendgrid.helpers.eventwebhook import EventWebhook
from sendgrid import SendGridAPIClient, Mail, Email, Attachment, FileContent, FileName, \
    FileType, Disposition, ContentId, CustomArg

from msgs.providers.base import BaseEmailProvider
from msgs.mixins import TemplatingMixin


class SendgridEmailProvider(TemplatingMixin, BaseEmailProvider):
    settings = settings.MSGS['providers']['sendgrid']['options']
    internal_message_id = "internal_message_id"

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

        sendgrid_message.custom_arg = CustomArg(
            self.internal_message_id,
            str(message.id),
        )

        response = self.client.send(sendgrid_message)
        response_data = dict(
            status_code=response.status_code,
            body=response.body,
            headers=response.headers,
        )

        return response_data, 200 <= response.status_code < 300

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

    def check_webhook_signature(self, request):
        public_key = self.settings.get("webhook_verification_key")

        event_webhook = EventWebhook()
        ec_public_key = event_webhook.convert_public_key_to_ecdsa(public_key)

        return event_webhook.verify_signature(
            request.body.decode(),
            request.META['HTTP_X_TWILIO_EMAIL_EVENT_WEBHOOK_SIGNATURE'],
            request.META['HTTP_X_TWILIO_EMAIL_EVENT_WEBHOOK_TIMESTAMP'],
            ec_public_key,
        )

    def process_webhook_event(self, event: dict):
        message_id = event.get(self.internal_message_id)
        if not message_id:
            return None

        event_status = {
            "opened": AbstractMessage.Status.OPENED,
            "delivered": AbstractMessage.Status.DELIVERED,
            "dropped": AbstractMessage.Status.REJECTED,
            "deferred": AbstractMessage.Status.REJECTED,
            "bounced": AbstractMessage.Status.REJECTED,
            "spamreport": AbstractMessage.Status.SPAM_REPORTED,
        }.get(event.get("event"))
        if event_status:
            # Use direct save to make all signals to work
            msg = self.model.objects.filter(id=message_id).last()
            msg.status = event_status
            msg.save(update_fields=["status"])
        return None
