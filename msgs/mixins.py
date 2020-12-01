import base64
import os
from io import BytesIO

from django.conf import settings
from django.template import Template as DjangoTemplate, Context
from django.template.loader import get_template
# from xhtml2pdf import pisa


class TemplatingMixin(object):
    def get_context_data(self, message, context=None):
        ctxt = message.context
        if context and isinstance(context, dict):
            ctxt.update(context)
        return ctxt

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
        # attachment_tpls = message.tpl.attachments.all()
        attachments = []
        # if not attachment_tpls:
        #     return attachments
        # if not context:
        #     context = self.get_context_data(message)
        # for attachment_tpl in attachment_tpls:
        #     tpl = get_template(f"{lang}/{attachment_tpl.template_name}.html")
        #     html = tpl.render(context)
        #     result = BytesIO()
        #     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        #     encoded_file = base64.b64encode(result.getvalue()).decode()
        #     # encoded_file = base64.b64encode(HttpResponse(result.getvalue(), content_type='application/pdf')).decode()
        #     attachments.append(
        #         self.build_attachment_object(
        #             file_content=encoded_file,
        #             file_name='attachment.pdf',
        #             file_type='application/pdf',
        #             disposition='attachment',
        #         )
        #     )
        return attachments

    def render(self, message, lang, context=None):
        title_tpl = DjangoTemplate(f"{message.tpl.get_subject(lang)}")
        title_html = title_tpl.render(Context(context))
        body_tpl = DjangoTemplate(f"{message.tpl.get_body(lang)}")
        body_html = body_tpl.render(Context(context))
        # attachments = self.get_attachments(message, context=context, lang=lang)
        return title_html, body_html

    # render from file
    # def render(self, message, lang):
    #     context = self.get_context_data(message)
    #     title_tpl = DjangoTemplate(f"{message.tpl.get_subject(lang)}")
    #     title_html = title_tpl.render(Context(context))
    #     body_tpl = get_template(f"{lang}/{message.tpl.key}.html")
    #     body_html = body_tpl.render(context)
    #     attachments = self.get_attachments(message, context=context, lang=lang)
    #     return title_html, body_html, attachments
