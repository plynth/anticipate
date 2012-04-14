import inspect
import types
from anticipate.adapt import adapt, adapt_all, register_adapter, AdaptError, AdaptErrors
import sys
from functools import partial

__all__ = []

class AnticipateTypeError(Exception):
    def __init__(self, message, errors=None):
        super(AnticipateTypeError, self).__init__(message)
        self.errors = errors

class anticipate_wrapper(object):
    """
    Callable that is returned when you decorate something with `anticipate`.

    Handles checking or adapting the return type and input parameters.
    """
    def __init__(self, func, returns, params, strict=False):
        self.func = func
        self.returns = returns
        self.params = params
        self.adapt = adapt
        self.strict = strict
        self.bound_to = None

        if isinstance(self.returns, list):
            # Return value is a list of items matching the first element
            if len(self.returns) == 1:
                self.returns = self.returns[0]
                self.adapt = adapt_all
            else:
                raise TypeError('An anticipated list can only contain one type')

        self.arg_names = [n for n in inspect.getargspec(func)[0] if n != 'self']
        self.param_adapters = {}
        for key, p in self.params.items():
            if isinstance(p, list):
                # Value is a list of items matching the first element
                if len(p) == 1:
                    self.param_adapters[key] = partial(adapt_all, to_cls=p[0])
                else:
                    raise TypeError('An anticipated list can only contain one type')
            else:
                self.param_adapters[key] = partial(adapt, to_cls=p)

    def __get__(self, instance, owner):
        """
        If `anticipate` is decrating a method, `anticipate_wrapper` will be a descriptor.

        `__get__` will be called in this case which gives us an opportunity to bind to
        the instance.
        """
        if instance is None:
            return self
        elif not self.bound_to:
            # Bind this method to an object instance
            self.bound_to = instance

        return self

    def __unadapted__(self, *args, **kwargs):
        """
        Call the wrapped function without adapting.
        """
        if self.bound_to:
            result = self.func(self.bound_to, *args, **kwargs)
        else:
            result = self.func(*args, **kwargs)
        return result

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function, adapting if needed.
        """

        if args and self.arg_names:
            # Turn any named arguments into keyword arguments
            args = list(args)
            for name in self.arg_names:
                if name not in kwargs:
                    try:
                        kwargs[name] = args.pop(0)
                    except IndexError:
                        break

        if kwargs and self.params:
            # Adapt all adaptable arguments
            # TODO Strict checking
            for key, val in kwargs.items():
                if key in self.param_adapters:
                    try:
                        kwargs[key] = self.param_adapters[key](val)
                    except (AdaptError, AdaptErrors) as e:
                        if hasattr(e, 'errors'):
                            errors = e.errors
                        else:
                            errors = [e]

                        raise AnticipateTypeError('Input value %r for %s does not match anticipated type %r' % (type(val), key, self.params[key]), errors=errors)

        if self.bound_to:
            result = self.func(self.bound_to, *args, **kwargs)
        else:
            result = self.func(*args, **kwargs)

        if self.returns:
            errors = None
            try:
                return self.adapt(result, self.returns)
            except AdaptErrors as e:
                errors = e.errors
            except AdaptError as e:
                errors = [e]

            raise AnticipateTypeError('Return value %r does not match anticipated type %r' % (type(result), self.returns), errors=errors)
        elif self.strict:
            if result is not None:
                raise AnticipateTypeError('Return value %r does not match anticipated value of None' % (type(result),), errors=None)
            return None
        else:
            return result



class anticipate(object):
    """
    A decorator that defines what a function/method expects.

    :param returns: Defines the type of object this function is expected to return.
                    Python basetypes as well as any object is supported. `None` means
                    that nothing can be returned. Use a list (ex: `[MyClass]`) to denote
                    that an iterable of `MyClass` will be returned.
    :param params: A list of key/type pairs. Each key corresponds to a parameter of the wrapped
                   function. The type is the type of object the function expects for that parameter.

    Example::

        @anticipate(dict, id=int)
        def get_obj(id):
            return {
                'id' : id
            }


    """
    def __init__(self, returns=None, **params):
        self.returns = returns
        self.params = params

    def __call__(self, func):
        return anticipate_wrapper(func, self.returns, self.params)

class strictly_anticipate(object):
    """
    Like `anticipate` but does not allow extra arguments or return values if `returns` is `None`
    """
    def __init__(self, returns=None, **params):
        self.returns = returns
        self.params = params

    def __call__(self, func):
        return anticipate_wrapper(func, self.returns, self.params, strict=True)

class adapter(object):
    """
    A decorator that registers an adapter

    :param from_cls: The class to convert from.
    :param to_cls: The class to convert to.

    Example::

        @adapter(int, str)
        def to_str(input, to_cls):
            return str(input)

    """
    def __init__(self, from_cls, to_cls):
        self.from_cls = from_cls
        self.to_cls = to_cls

    def __call__(self, func):
        register_adapter(self.from_cls, self.to_cls, func)
        return func