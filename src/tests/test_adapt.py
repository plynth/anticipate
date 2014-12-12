from anticipate import adapt, adapter, anticipate

def test_mro():
    class Foo(object):
        def __init__(self, data):
            self.data = data

    class Bar(Foo):
        pass

    @adapter(Foo, str)
    def to_string(obj, to_cls):
        return 'Adapted to string'

    bar = Bar('My string')

    s = adapt.adapt(bar, str)

    assert s == 'Adapted to string'
    assert s == 'Adapted to string'

    class Zip(object):
        def __init__(self, data):
            self.data = data

    class Zam(Zip):
        pass

    @adapter(Foo, Zip)
    def from_foo_to_zip(obj, to_cls):
        return 'Adapted to zip'

    s = adapt.adapt(bar, Zam)

    assert s == 'Adapted to zip'

def test_adapt_params():
    @anticipate(foo=str, bar=int)
    def test(foo, bar, zing):
        return foo, bar, zing

    class FizzBuzz(object):
        def __str__(self):
            return 'fizzbuzz'

        def __int__(self):
            return 22

    @adapter((basestring, int, float, FizzBuzz), (basestring, int, float))
    def to_int(obj, to_cls):
        return to_cls(obj)

    assert test(1, 2.3, 'fizz') == ('1', 2, 'fizz')
    assert test(1, 2.3, zing='fizz') == ('1', 2, 'fizz')
    assert test(1, bar=2.3, zing='fizz') == ('1', 2, 'fizz')
    assert test(foo=1, bar=2.3, zing='fizz') == ('1', 2, 'fizz')

    assert test('hi', '1', str) == ('hi', 1, str)

    a = FizzBuzz()
    assert test(a, a, a) == ('fizzbuzz', 22, a)


def test_unadapted():
    """
    Ensure we can call a method without it being Adapted
    """
    @anticipate(foo=str, bar=int)
    def test(foo, bar):
        return foo, bar

    assert test(1, '0') == ('1', 0)
    assert test.__unadapted__(1, '0') == (1, '0')


def test_bound_to():
    """
    Ensure that an anticipated method gets bound to the subclass,
    not it's base class.
    """
    class BaseClass(object):
        @anticipate()
        def get_wrapped_self(self):
            return self

    class SubClass(BaseClass):
        def get_self(self):
            return self
            


    a = BaseClass()
    assert a.get_wrapped_self() == a
    

    b = SubClass()
    assert b.get_wrapped_self() == b
    assert b.get_wrapped_self() == b.get_self()


def test_instance_bound_to():
    """
    Ensure that an anticipated method gets bound to each instance
    instead of its first instance.
    """

    class BaseClass(object):
        pass

    class SubClass(BaseClass):
        def __init__(self, *args, **kwargs):
            super(SubClass, self).__init__(*args, **kwargs)
            self.thing = {}

        @anticipate()
        def get_wrapped_self(self):
            return self

        def get_self(self):
            return self

    b = SubClass()
    assert b.get_wrapped_self() is b
    assert b.get_wrapped_self() is b.get_self()        

    assert id(b.get_wrapped_self().thing) == id(b.get_self().thing)


    c = SubClass()
    assert c.get_wrapped_self() is c
    assert c.get_wrapped_self() is c.get_self()  

    assert id(c.get_wrapped_self().thing) == id(c.get_self().thing)


def test_args():
    """
    Verify that `self` is the correct instance when
    additional positional arguments are passed in.
    """
    class Test(object):
        @anticipate()
        def get_args(self, arg, *args):
            return self, arg, args

        @anticipate()
        def get_arg(self, arg):
            return self, arg

        @anticipate()
        def get_self(self, foo=None):
            return self

        @anticipate(arg=int)
        def get_arg_int(self, arg):
            return self, arg

        @anticipate(arg=int)
        def get_args_int(self, arg, *args):
            return self, arg, args

    @anticipate(arg=int)
    def get_arg_int(arg):
        return arg

    obj1 = object()
    obj2 = object()
    obj3 = object()

    b = Test()

    assert b.get_self() is b

    # Verify that if there are no adapters, *args pass through
    r = b.get_args(obj1, obj2, obj3)
    
    assert r[0] is b
    assert r[1] is obj1
    assert r[2][0] is obj2
    assert r[2][1] is obj3

    # Verify that if there are adapters, positional args get adapted
    r = b.get_args_int('1', obj2, obj3)
    
    assert r[0] is b
    assert r[1] == 1
    assert r[2][0] is obj2
    assert r[2][1] is obj3

    # Verify that if there are no adapters, positional args pass through
    r = b.get_arg(obj1)

    assert r[0] is b
    assert r[1] is obj1

    # Verify that if there are no adapters, keyword args pass through
    r = b.get_arg(arg=obj1)

    assert r[0] is b
    assert r[1] is obj1

    # Verify that keyword args are adapted
    r = b.get_arg_int(arg='1')

    assert r[0] is b
    assert r[1] == 1

    assert get_arg_int(arg='1') == 1

def test_kwargs():
    """
    Verify that kwargs can be adapted
    """
    class Test(object):
        @anticipate(foo=int, bar=str)
        def get_args(self, arg, **kwargs):
            return arg, kwargs

    @anticipate(foo=int, bar=str)
    def get_args(arg, **kwargs):
        return arg, kwargs

    t = Test()

    obj = object()

    r = t.get_args(obj, foo='2', bar=3)
    assert r[0] is obj
    assert r[1]['foo'] == 2
    assert r[1]['bar'] == '3'

    r = get_args(obj, foo='2', bar=3)
    assert r[0] is obj
    assert r[1]['foo'] == 2
    assert r[1]['bar'] == '3'    

    r = t.get_args(arg=obj, foo='2', bar=3)
    assert r[0] is obj
    assert r[1]['foo'] == 2
    assert r[1]['bar'] == '3'

    r = get_args(arg=obj, foo='2', bar=3)
    assert r[0] is obj
    assert r[1]['foo'] == 2
    assert r[1]['bar'] == '3'    




