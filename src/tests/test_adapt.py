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




