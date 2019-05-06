from past.builtins import basestring
from builtins import object
import pytest
from anticipate import adapt, adapter, anticipate
from anticipate.adapt import clear_adapters
from anticipate.exceptions import AnticipateParamError, AnticipateErrors


def setup_function(function):
    """
    Make sure there are no adapters defined before start of test
    """
    clear_adapters()

    # Setup a basic int adapter for all tests
    @adapter((str, float, int), (int, str))
    def to_int(obj, to_cls):
        return to_cls(obj)


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

    @adapter(FizzBuzz, (str, int, float))
    def from_fizz(obj, to_cls):
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


def test_adapt_all_list():
    """
    Verify adapt_all returns a list
    """
    int_like = ['1', 2.0]

    r = adapt.adapt_all(int_like, int)
    assert r[0] == 1
    assert r[1] == 2

    assert adapt.adapt_all(int_like, int) == [1, 2]


def test_adapt_all_with_none():
    """
    Verify passing None to adapt_all returns an empty list
    """
    r = adapt.adapt_all(None, int)
    assert r == []
    assert type(r) == list


def test_anticipate_list():
    """
    Verify using a list for a parameter adapts expects an iterable
    and adapts each value in the input.
    """
    @anticipate(items=[int])
    def get_list(items):
        return items

    int_like = ['1', 2.0]

    r = get_list(int_like)
    assert r[0] == 1
    assert r[1] == 2.0

    # Works on list input
    assert get_list(int_like) == [1, 2]

    # Works on tuple input
    assert get_list((4.0, 5.0, 6.0)) == [4, 5, 6]

    # Works on generator input
    assert get_list(iter((4.0, 5.0, 6.0))) == [4, 5, 6]


def test_anticipate_list_with_none():
    """
    Verify passing None for a parameter that expects a list returns an
    empty list.
    """
    @anticipate(items=[int])
    def get_list(items):
        return items

    r = get_list(None)
    assert r == []
    assert type(r) == list


def test_anticipate_input():
    """
    Verify that input can be checked without calling inner function
    """
    @anticipate(items=[int], foo=basestring)
    def get_list(items, foo=None):
        return items, foo

    with pytest.raises(AnticipateErrors) as exc_info:
        get_list.input(items='a')

    assert len(exc_info.value.errors) == 1
    e = exc_info.value.errors[0]
    assert isinstance(e, AnticipateParamError)
    assert e.name == 'items'

    with pytest.raises(AnticipateErrors) as exc_info:
        get_list.input(items=[1], foo=1)

    assert len(exc_info.value.errors) == 1
    e = exc_info.value.errors[0]
    assert isinstance(e, AnticipateParamError)
    assert e.name == 'foo'

    args, kwargs = get_list.input(['1', 2], foo='abc')
    assert args == ([1, 2],)
    assert kwargs == {'foo': 'abc'}


def test_anticipate_wrong_params():
    """
    Verify that anticipate complains if you anticipate invalid parameters
    """
    with pytest.raises(KeyError):
        @anticipate(foobar=int)
        def noop(items):
            pass

    # Sanity check
    @anticipate(items=int)
    def noop(items):
        pass


def test_anticipate_custom_fields():
    """
    Verify that anticipate can use any object that implements `adapt`
    as an anticipated type. This is good for things like SpringField fields.
    """
    class IntField(object):
        def adapt(self, value):
            return int(value)

    @anticipate(num=IntField())
    def get_num(num):
        return num

    assert get_num('1') == 1
    assert get_num(2.33) == 2


def test_anticipate_custom_fields_list():
    """
    Verify that anticipate can use any object that implements ``adapt``
    as an anticipated list of type. This is good for things like
    SpringField fields.
    """
    class IntField(object):
        def adapt(self, value):
            return int(value)

    @anticipate(IntField(), nums=[IntField()])
    def get_sum(nums):
        return sum(nums)

    @anticipate([IntField()], strings=[str])
    def get_as_int(strings):
        return strings

    assert get_sum(['1', '2']) == 3
    assert get_sum([2.33, 1.33]) == 3

    assert get_as_int(['2', '1']) == [2, 1]
