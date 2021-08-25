from typing import Type

from msgs.abstract.models import AbstractMessage


class TemplateContext(dict):
    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.__key = key

    def get_key(self):
        return self.__key


# example = TemplateContext(
#     key='template_unique_key',
#     context_value_1='',
#     context_value_2='',
# )


def build_message(
        model: Type[AbstractMessage],
        recipient: str,
        context: TemplateContext,
) -> AbstractMessage:
    return model(
        recipient=recipient,
        template=model.get_template(
            context.get_key(),
        ),
        context=context,
    )


def send_message(
        model: Type[AbstractMessage],
        recipient: str,
        context: TemplateContext,
        lang: str = None,
) -> AbstractMessage:
    instance = build_message(model, recipient, context)
    instance.send(lang=lang)
    return instance
