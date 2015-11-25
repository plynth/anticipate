import inspect
import types
from anticipate.adapt import adapt, adapt_all, register_adapter, AdaptError, AdaptErrors
import sys
from functools import partial, update_wrapper, wraps
from itertools import izip
from anticipate.exceptions import AnticipateErrors, AnticipateParamError


__all__ = []


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

        if isinstance(self.returns, list):
            # Return value is a list of items matching the first element
            if len(self.returns) == 1:
                self.returns = self.returns[0]
                self.adapt = adapt_all
            else:
                raise TypeError('An anticipated list can only contain one type')

        args, _, kwargs, _ = inspect.getargspec(func)

        self.arg_names = args

            
        if not kwargs:
            # If kwargs are accepted then any parameter name can be used. 
            # Otherwise, we check to see if there are parameters that do not
            # match the funtion signature. This is a safety precaution to
            # protect againts typo in parameter names.
            invalid_params = set(self.params.keys()) - set(self.arg_names)
            if invalid_params:
                raise KeyError(
                    'Invalid anticipate parameters found that do not match '
                    'function signature: %s' % ', '.join(invalid_params))

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

        # Make this look like the original function
        update_wrapper(self, self.func)

    def __get__(self, instance, owner):
        """
        If `anticipate` is decrating a method, `anticipate_wrapper` will be 
        a descriptor.

        `__get__` will be called in this case which gives us an opportunity to 
        bind to the instance.
        """
        return partial(self.__call__, instance)

    def __unadapted__(self, *args, **kwargs):
        """
        Call the wrapped function without adapting.
        """
        return self.func(*args, **kwargs)

    def _adapt_param(self, key, val):
        """
        Adapt the value if an adapter is defined.
        """
        if key in self.param_adapters:
            try:
                return self.param_adapters[key](val)
            except (AdaptError, AdaptErrors, TypeError, ValueError) as e:
                if hasattr(e, 'errors'):
                    errors = e.errors
                else:
                    errors = [e]

                raise AnticipateParamError(
                    message='Input value %r for parameter `%s` does not match '
                        'anticipated type %r' % (type(val), key, self.params[key]),
                    name=key,
                    value=val,
                    anticipated=self.params[key],
                    errors=errors)
        else:
            return val

    def input(self, *args, **kwargs):
        """
        Adapt the input and check for errors.

        Returns a tuple of adapted (args, kwargs) or raises
        AnticipateErrors
        """
        errors = []

        if args and self.arg_names:
            args = list(args)            
            # Replace args inline that have adapters
            for i, (key, val) in enumerate(izip(self.arg_names, args)):
                try:
                    args[i] = self._adapt_param(key, val)
                except Exception as e:
                    errors.append(e)
            args = tuple(args)

        if kwargs and self.params:
            # Adapt all adaptable arguments
            for key, val in kwargs.items():
                try:
                    kwargs[key] = self._adapt_param(key, val)
                except Exception as e:
                    errors.append(e)

        if errors:
            raise AnticipateErrors(
                message='Invalid input for %s' % self.func,
                errors=errors)

        return args, kwargs

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function, adapting if needed.
        """
        args, kwargs = self.input(*args, **kwargs)
        result = self.func(*args, **kwargs)
        return self.output(result)

    def output(self, result):        
        """
        Adapts the result of a function based on the returns definition.
        """
        if self.returns:
            errors = None
            try:
                return self.adapt(result, self.returns)
            except AdaptErrors as e:
                errors = e.errors
            except AdaptError as e:
                errors = [e]

            raise AnticipateErrors(
                message='Return value %r does not match anticipated type %r' 
                    % (type(result), self.returns), 
                errors=errors)
        elif self.strict:
            if result is not None:
                raise AnticipateErrors(
                    message='Return value %r does not match anticipated value '
                    'of None' % type(result), 
                    errors=None)
            return None
        else:
            return result


class anticipate(object):
    """
    A decorator that defines what a function/method expects.

    Args:
        returns (mixed): Defines the type of object this function is expected 
            to return. Python basetypes as well as any object is supported. 
            `None` means that nothing can be returned. Use a list 
            (ex: `[MyClass]`) to denote that a list of `MyClass` will be 
            returned.
        params (list): A list of key/type pairs. Each key corresponds to a 
            parameter of the wrapped function. The type is the type of object 
            the function expects for that parameter.

    Example::

        @anticipate(dict, id=int)
        def get_obj(id):
            return {
                'id' : id
            }

    An object that implements an `adapt` function can be used as the return
    or input type. The `adapt` function must accept a single parameter called
    `value` that will be the value to adapt.

    Example::

        class Int(object):
            def adapt(self, value):
                return int(value)

        @anticipate(dict, id=Int())
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
    Like `anticipate` but does not allow extra arguments or return values if 
    `returns` is `None`
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


def anticipate_input_factory(injecters=None, input_error_handler=None, doc=None):
    """
    Returns an anticipate decorator that can inject additional data into
    the request and handle input errors.
    """
    def decorator(*args, **kwargs):
        """
        A decorator that will inject additional parameters into the function
        call for each of the `injecters`.
        """
        if injecters:
            for k in injecters.keys():
                if k not in kwargs:
                    raise KeyError(
                        'A parameter named `%s` is required for '
                        'this decorator.' % k)

        anticipation = anticipate(*args, **kwargs)
        def anticipate_decorator(f):
            f_anticipation = anticipation(f)
            @wraps(f)
            def inner_func(*a, **kw):                
                # Call all the injecters
                for k, v in injecters.iteritems():
                    if k in kw:
                        raise ValueError(
                            '%s may not be passed in as a parameter to this '
                            'function as it is automatically injected.' % k)

                    kw[k] = v()

                try:
                    a, kw = f_anticipation.input(*a, **kw)
                except Exception as e:
                    if input_error_handler:
                        input_error_handler(e)
                    # Either there was no input handler or it did not raise a
                    # new exception so do so here
                    raise

                return f_anticipation.output(f_anticipation.func(*a, **kw))
            return inner_func
        return anticipate_decorator

    decorator.__doc__ = doc
    return decorator