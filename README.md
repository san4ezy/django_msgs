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

Django MSGS contains two common data models: Message and Tpl (template). The first one stores your messages, the second 
one describes the messaging templates. \
If you need new type of email, you should create new Tpl with the HTML inside. After that you can use it for sending 
messages with this template. \
By default Django MSGS provide you with two proxy models: Email and SMS. You can customize them on your taste.

## Quick example

Let's create new template for sending registration emails and send one email with some lines of python code.
```python
from msgs.models import Tpl, Email

registration_tpl = Tpl.objects.create(
    key='registration',
    subject_en='Welcome!',
    body_en='''Hello, {{ name }}!
    Welcome!
    '''
)

email = Email.objects.create(
    tpl=registration_tpl,
    recipient='user@email.com',
    context={
        'name': 'John Doe'
    },
)
email.send(lang='en')
``` 

Also you can do this with the Django administration interface. \

Did you catch the i18n options? You can just inherit the existing model with your custom model, add the 
needed language fields and use the `send` method with a language prefix as you need.

## Providers

The Django MSGS works with multiple providers. All of them are placed at the `providers` folder. 
So you can discover them and choose what you need. \
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