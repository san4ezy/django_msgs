import importlib


NULLABLE = {'blank': True, 'null': True}


def get_provider_class_from_string(reference: str):
    module_name, func = reference.rsplit('.', maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, func)
