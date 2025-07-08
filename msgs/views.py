import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from msgs.helpers import get_provider_class_from_string


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(require_http_methods(["POST"]), name='dispatch')
class WebhookView(View):
    def post(self, request, provider: str):
        payload = request.body

        provider_settings = settings.MSGS["providers"].get(provider)
        if not provider_settings:
            raise ValidationError("Unknown provider")
        provider = get_provider_class_from_string(provider_settings["backend"])()

        if not provider.check_webhook_signature(request):
            return HttpResponseBadRequest("Invalid signature")

        try:
            events = json.loads(payload)
            provider.webhook(events)
            return HttpResponse("OK", status=200)

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            return HttpResponse("Internal Server Error", status=500)
