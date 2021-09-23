# Django MSGS

This small framework provides you with a set of flexible tools for implementing the message sending functionality. \
Any type of informational messaging are available: emails, sms, telegram...

## Installation

```
pip install django-msgs
```

settings.py:
```
INSTALLED_APPS = [
...
'msgs',
]
```

Apply the migrations for creation the tables at your database:
```
./manage.py migrate msgs
```

## Structure

Django MSGS contains two common data models: Message and Template. The first one stores your messages, the second 
one describes the messaging templates. \
If you need new type of email, you should create new Tpl with the HTML inside. After that you can use it for sending 
messages with this template. \
By default Django MSGS provide you with three proxy models: `Email`, `SMS` and `Message`. You can customize them on your taste. \
Also you can find a template model for any type of message: `EmailTemplate`, `SMSTemplate` and `MessageTemplate`.

## Quick example

Look at the admin interface and create some templates for your messages.

Now we can use them for sending messages:

```python
from msgs.models import Email

template_key = 'registration'  # a unique key for search the template
Email.create(
    template=template_key,
    recipient='john.doe@example.com',
    context={
        'name': 'John Doe',
        'link': 'https://example.com/registration',
    },
).send()
```

If you need i18n options, you can just inherit the existing template models with adding the 
needed language fields and use the `send` method with a language prefix as you need.

Let's look at the one more very useful attribute -- `related_to`. This library uses a generic foreign key for linking messages with another objects. You should provide this object when you create a message.

```python
from msgs.models import SMS

instance = new_user  # this is an object you want to link with the email

SMS.create(
    template='registration',
    recipient='1234567890',
    context={
        'name': 'John Doe',
        'link': 'https://example.com/registration',
    },
    related_to=instance,  # it does the trick
).send()
```

## Providers

The Django MSGS works with multiple providers. All of them are placed at the `providers` folder. 
So you can discover them and choose what you need.

You can find the `BaseProvider` class, hence nobody can stop you to build your own provider. 

## Settings

```python
MSGS = {
    'providers': {
        'sendgrid': {
            'backend': 'msgs.providers.sendgrid.SendgridProvider',  # use SendGrid Provider
            'options': {
                'is_active': True,  # turn on/off sending messages
                'api_key': 'api-key',
                'sender': 'sender@email.com',
            },
        },
        'telegram': {
            'backend': 'msgs.providers.telegram.TelegramProvider',
            'options': {
                'is_active': False,
                'token': 'telegram-bot-token',
                'chat': 'chat-id',
            },
        },
    },
    'options': {
        'default_language': 'en',
    },
    'development': 'telegram',  # what use on development (not works properly, be careful)
    'email': 'sendgrid',  # use SendGrid Provider for sending emails
    'sms': 'telegram',  # use Telegram Provider for sending sms
}
```