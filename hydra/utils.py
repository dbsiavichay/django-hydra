#Python
import inspect
from importlib import import_module

# Django
from django.core.exceptions import FieldDoesNotExist
from django.forms.utils import pretty_name


def get_label_of_field(model, field):
    names = field.split(".")
    name = names.pop(0)

    try:
        name, verbose_name = name.split(":")
        return pretty_name(verbose_name)
    except ValueError:
        pass

    if not hasattr(model, name):
        try:
            str_model = f"<{model._meta.model_name}>"
        except:
            str_model = str(model)
        raise AttributeError(f"No existe le atributo <{name}> para {str_model}.")

    if len(names):
        if hasattr(model, "_meta"):
            return get_label_of_field(
                model._meta.get_field(name).related_model, ".".join(names)
            )
        else:
            attr = getattr(model, name)
            return get_label_of_field(
                attr() if callable(attr) else attr, ".".join(names)
            )
    try:
        field = model._meta.get_field(name)
        label = field.verbose_name if hasattr(field, "verbose_name") else name
    except FieldDoesNotExist:
        label = str(model._meta.verbose_name) if name == "__str__" else name

    return pretty_name(label)


def get_attr_of_object(instance, field):
    names = field.split(".")
    name = names.pop(0)
    name = name.split(":")[0]

    if not hasattr(instance, name):
        raise AttributeError(f"No existe le atributo <{name}> para {str(instance)}.")

    if len(names):
        return get_attr_of_object(getattr(instance, name), ".".join(names))

    try:
        field = instance._meta.get_field(name)
        if hasattr(field, "choices") and field.choices:
            name = f"get_{name}_display"
    except FieldDoesNotExist:
        pass

    attr = getattr(instance, name)
    return attr() if callable(attr) else attr


def import_class(module_name, class_name):
    cls = None
    try:
        module = import_module(module_name)
        members = inspect.getmembers(module, inspect.isclass)
        for name, klass in members:
            if name == class_name:
                cls = klass
                break
    except ModuleNotFoundError as error:
        print("Not found %s" % module_name)
    return cls
