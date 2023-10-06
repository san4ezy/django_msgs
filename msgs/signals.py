from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver


BUILT_SIGNAL, CREATED_SIGNAL, SENT_SIGNAL, STATUS_CHANGED_SIGNAL = \
    'built', 'created', 'sent', 'status_changed'


message_built = Signal()
email_built = Signal()
sms_built = Signal()

message_created = Signal()
email_created = Signal()
sms_created = Signal()

message_sent = Signal()
email_sent = Signal()
sms_sent = Signal()

message_status_changed = Signal()
email_status_changed = Signal()
sms_status_changed = Signal()


SIGNALS = {
    'Message': {
        BUILT_SIGNAL: message_built,
        CREATED_SIGNAL: message_created,
        SENT_SIGNAL: message_sent,
        STATUS_CHANGED_SIGNAL: message_status_changed,
    },
    'Email': {
        BUILT_SIGNAL: email_built,
        CREATED_SIGNAL: email_created,
        SENT_SIGNAL: email_sent,
        STATUS_CHANGED_SIGNAL: email_status_changed,
    },
    'SMS': {
        BUILT_SIGNAL: sms_built,
        CREATED_SIGNAL: sms_created,
        SENT_SIGNAL: sms_sent,
        STATUS_CHANGED_SIGNAL: sms_status_changed,
    },
}


@receiver(post_save, sender='msgs.Email')
@receiver(post_save, sender='msgs.SMS')
@receiver(post_save, sender='msgs.Message')
def delete_after_sending(sender, instance, **kwargs):
    auto_delete = settings.MSGS['options'].get('auto_delete', False)
    if auto_delete and instance.status == instance.Status.SENT:
        instance.delete()
