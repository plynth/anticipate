from __future__ import absolute_import

import inspect
import itertools
import sys
import traceback

__adapters__ = {}
__mro__ = {}
__all__ = [
    'AdaptError',
    'AdaptErrors',
    'AdapterExists',
    'adapt',
    'adapt_all',
    'register_adapter',
    'clear_adapters',
]


class AdaptError(Exception):
    pass


class AdaptErrors(AdaptError):

    def __init__(self, message, errors=None):
        super(AdaptErrors, self).__init__(message)
        self.errors = []
        if errors:
            self.add_errors(errors)

    def add_error(self, func, ex_type, ex, tb):
        self.errors.append((func, ex_type, ex, tb))

    def add_errors(self, errors):
        for e in errors:
            self.add_error(*e)

    def errors_string(self):
        """
        Returns all errors as a string
        """
        output = []
        for e in self.errors:
            output.append('%s: %s in %s:' % (e[1], e[2], e[0]))
            output.append(''.join(traceback.format_tb(e[3])))
        return '\n'.join(output)


class AdapterExists(Exception):
    pass


def get_adapter_path(obj, to_cls):
    """
    Returns the adapter path that would be used to adapt `obj` to `to_cls`.
    """
    from_cls = type(obj)
    key = (from_cls, to_cls)
    if key not in __mro__:
        __mro__[key] = list(itertools.product(inspect.getmro(from_cls), inspect.getmro(to_cls)))

    return __mro__[key]


def adapt(obj, to_cls):
    """
    Will adapt `obj` to an instance of `to_cls`.

    First sees if `obj` has an `__adapt__` method and uses it to adapt. If that fails
    it checks if `to_cls` has an `__adapt__` classmethod and uses it to adapt. IF that
    fails, MRO is used. If that
    fails, a `TypeError` is raised.
    """
    if obj is None:
        return obj
    elif isinstance(obj, to_cls):
        return obj

    errors = []

    if hasattr(obj, '__adapt__') and obj.__adapt__:
        try:
            return obj.__adapt__(to_cls)
        except (AdaptError, TypeError) as e:
            ex_type, ex, tb = sys.exc_info()
            errors.append((obj.__adapt__, ex_type, ex, tb))

    if hasattr(to_cls, '__adapt__') and to_cls.__adapt__:
        try:
            return to_cls.__adapt__(obj)
        except (AdaptError, TypeError) as e:
            ex_type, ex, tb = sys.exc_info()
            errors.append((to_cls.__adapt__, ex_type, ex, tb))

    for k in get_adapter_path(obj, to_cls):
        if k in __adapters__:
            try:
                return __adapters__[k](obj, to_cls)
            except (AdaptError, TypeError) as e:
                ex_type, ex, tb = sys.exc_info()
                errors.append((__adapters__[k], ex_type, ex, tb))
                break

    raise AdaptErrors('Could not adapt %r to %r' % (obj, to_cls), errors=errors)


def adapt_all(iterable, to_cls):
    """
    Returns a list of items from adapting each item in iterable to `cls`

    If `iterable` is `None`, an empty list will be returned.
    """
    if iterable is None:
        return []

    return [adapt(obj, to_cls) for obj in iterable]


def register_adapter(from_classes, to_classes, func):
    """
    Register a function that can handle adapting from `from_classes` to `to_classes`.
    """
    assert from_classes, 'Must supply classes to adapt from'
    assert to_classes, 'Must supply classes to adapt to'
    assert func, 'Must supply adapter function'

    if not isinstance(from_classes, (tuple, list)):
        from_classes = [from_classes]
    if not isinstance(to_classes, (tuple, list)):
        to_classes = [to_classes]

    for key in itertools.product(from_classes, to_classes):
        if key in __adapters__:
            raise AdapterExists('%r to %r already exists.' % key)
        __adapters__[key] = func


def clear_adapters():
    """
    Unregister any previously defined adapters.
    """
    __adapters__.clear()
