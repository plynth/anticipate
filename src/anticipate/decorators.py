import inspect
import types

__all__ = [
    'anticipate',
]

class AdaptError(Exception):
    """
    TODO AdaptError needs to be usable by other modules to be able to catch adapting errors.
    Should consider making adapt its own package.
    """
    pass

def adapt(obj, cls):
    """
    Will adapt `obj` to an instance of `cls`.

    First sees if `obj` has an `__adapt__` method and uses it to adapt. If that fails
    it checks if `cls` has an `__adapt__` classmethod and uses it to adapt. If that
    fails, a `TypeError` is raised.

    TODI
    """
    if obj is None:
        return obj
    elif isinstance(obj, cls):
        return obj

    if hasattr(obj, '__adapt__'):
        try:
            return obj.__adapt__(cls)
        except AdaptError as e:
            pass

    if hasattr(cls, '__adapt__'):
        return cls.__adapt__(obj)

    raise AdaptError('Could not adapt %r to %r' % (obj, cls))

def adapt_all(iter, cls):
    """
    Returns a generator that will adapt all objects in an iterable to `cls`
    """
    return (adapt(obj, cls) for obj in iter)

def strictly_anticipate(returns=None, **params):
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
    returns_iter = False
    if isinstance(returns, list):
        # Return value is a list of items matching the first element                        
        if len(returns) == 1:
            returns = returns[0]
            returns_iter = True
        else:
            raise TypeError('An anticipated list can only contain one type')

    def wrapper(func):
        # TODO Make anticipate verify input/output
        original = func
        if returns:
            def check_return(*args, **kwargs):
                check = v = original(*args, **kwargs)
                if returns_iter:
                    if inspect.isgenerator(check):
                        # Give the benefit of the doubt cause we don't
                        # want to iterate if we don't have to
                        # TODO Consider wrapping the generator and checking
                        # type on first iteration
                        return v
                    check = v[0]

                if not isinstance(check, returns):
                    raise TypeError('Return value %r does not match anticipated type %r' % (type(check), returns))

                return v
            func = check_return
        
        func.__unadapted__ = original

        return func

    return wrapper

class anticipate_wrapper(object):
    """
    Callable that is returned when you decorate something with `anticipate`.

    Handles checking or adapting the return type and input parameters.
    """
    def __init__(self, func, returns, params):
        self.func = func
        self.returns = returns
        self.params = params
        self.adapt = adapt
        self.bound_to = None

        if isinstance(self.returns, list):
            # Return value is a list of items matching the first element                        
            if len(self.returns) == 1:
                self.returns = self.returns[0]
                self.adapt = adapt_all
            else:
                raise TypeError('An anticipated list can only contain one type')

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

        if self.bound_to:
            result = self.func(self.bound_to, *args, **kwargs)
        else:
            result = self.func(*args, **kwargs)

        try:
            return self.adapt(result, self.returns)
        except AdaptError as e:                    
            raise TypeError('Return value %r does not match anticipated type %r' % (type(result), self.returns))


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