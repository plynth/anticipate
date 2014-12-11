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
    assert b.get_wrapped_self() == b
    assert b.get_wrapped_self() == b.get_self()        

    assert id(b.get_wrapped_self().thing) == id(b.get_self().thing)


    c = SubClass()
    assert c.get_wrapped_self() == c
    assert c.get_wrapped_self() == c.get_self()  

    assert id(c.get_wrapped_self().thing) == id(c.get_self().thing)
