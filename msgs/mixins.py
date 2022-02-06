import base64
import os
import re
import mimetypes

from django.conf import settings
from django.template import Template as DjangoTemplate, Context


class TemplatingMixin(object):
    def build_attachment_object(self, **kwargs):
        """Override it according to your provider's SDK"""
        return

    def get_logo_attachment(self):
        with open(os.path.join(settings.BASE_DIR, 'static', 'logo.png'), 'rb') as f:
            logo = f.read()
        encoded_logo = base64.b64encode(logo).decode()
        return self.build_attachment_object(
            file_content=encoded_logo,
            file_name='logo.png',
            file_type='image/png',
            disposition='inline',
            content_id='logo',
        )

    def get_attachments(self, message, lang, context=None) -> list:
        attachments = []
        if not hasattr(message, 'attachments'):
            return attachments
        for attachment in message.attachments.all():
            encoded_file = base64.b64encode(attachment.file.read()).decode()
            filename = attachment.file.name.rsplit('/', 1)[-1]
            mimetype, _ = mimetypes.guess_type(filename)
            attachments.append(
                self.build_attachment_object(
                    file_content=encoded_file,
                    file_name=filename,
                    file_type=mimetype,
                    description='attachment',
                )
            )
        return attachments

    @classmethod
    def html_to_text(cls, html):
        clean_regex = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        return re.sub(clean_regex, '', html)

    def render(self, message, lang, context=None):
        title_tpl = DjangoTemplate(f"{message.template.get_subject(lang)}")
        title_html = title_tpl.render(Context(context))
        body_tpl = DjangoTemplate(f"{message.template.get_body(lang)}")
        body_html = body_tpl.render(Context(context))
        return title_html, body_html
