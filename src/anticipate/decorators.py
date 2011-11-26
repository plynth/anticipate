def anticipate(returns=None, **params):
    """
    A decorator that defines what a function/method expects.

    :param returns: Defines the type of object this function is expected to return.
                    Python basetypes as well as any object is supported. `None` means
                    that nothing can be returned. Use a list (ex: `[MyClass]`) to denote
                    that a list of `MyClass` will be returned. You can also use `(MyClass,)`
                    to denote a tuple.
    :param params: A list of key/type pairs. Each key corresponds to a parameter of the wrapped
                   function. The type is the type of object the function expects for that parameter.

    Example::

        @anticipate(dict, id=int)
        def get_obj(id):
            return {
                'id' : id
            }


    """
    def wrapper(func):
        # TODO Make anticipate verify input/output
        return func

    return wrapper
