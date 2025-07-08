from django.urls import path
from .views import WebhookView

urlpatterns = [
    path('webhooks/<str:provider>/', WebhookView.as_view(), name='webhook'),
]
