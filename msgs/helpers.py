import importlib


def get_provider_class_from_string(reference: str):
    parts = reference.split('.')
    module_name, class_name = '.'.join(parts[:-1]), parts[-1]
    m = importlib.import_module(module_name)
    c = getattr(m, class_name)
    return c
