import pytest
from anticipate import adapt, adapter, anticipate
from anticipate.adapt import clear_adapters
from anticipate.decorators import anticipate_input_factory
from anticipate.exceptions import AnticipateParamError, AnticipateErrors, \
    AnticipateError


def setup_function(function):
    """
    Make sure there are no adapters defined before start of test
    """
    clear_adapters()

    # Setup a basic int adapter for all tests
    @adapter((basestring, float, int), (int, basestring))
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

    @adapter(FizzBuzz, (basestring, int, float))
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


def test_adapt_custom_fields():
    """
    Verify that adapt and can use any object that implements `adapt`
    as adaptable type. This is good for things like SpringField fields.
    """    
    class IntField(object):
        def adapt(self, value):
            return int(value)

    assert adapt.adapt('1', IntField()) == 1
    assert adapt.adapt(2.33, IntField()) == 2   


def test_adapt_all_custom_fields():
    """
    Verify that adapt_all and can use any object that implements `adapt`
    as adaptable type. This is good for things like SpringField fields.
    """    
    class IntField(object):
        def adapt(self, value):
            return int(value)

    assert adapt.adapt_all(['1', '2'], IntField()) == [1, 2]
    assert adapt.adapt_all((n for n in range(3)), IntField()) == [0, 1, 2]


def test_anticipate_input_factory():
    """
    Verify we can make new anticipate decorators that modify input
    """
    class BadRequest(Exception):
        code = 400

    def get_json_from_request():
        """
        Simulate getting some value from a request object
        such as Flask.
        """
        return {'answer': 42}
        
    def input_error_handler(exc_value):
        """
        Turn anticipate errors into BadRequests so we can do 400 errrors
        """
        if isinstance(exc_value, AnticipateError):
            raise BadRequest(str(exc_value))

    anticipate_json = anticipate_input_factory(
        injecters={
            'json_body': get_json_from_request
        },
        input_error_handler=input_error_handler
    )

    @anticipate_json(json_body=dict, other=str)
    def get_answer(json_body, other=None):
        return json_body, other

    assert get_answer() == ({'answer': 42}, None)
    assert get_answer(other='a') == ({'answer': 42}, 'a')

    # Verify custom exception is raised from middleware on adapt errors
    with pytest.raises(BadRequest):
        get_answer(other=object())        


def test_anticipate_input_factory_missing_injecter():
    """
    Verify a KeyError is raised if an injecter parameter is not defined
    when using the decorator.
    """
    anticipate_foobar = anticipate_input_factory(
        injecters={
            'foobar': lambda: 'foo'
        }
    )

    with pytest.raises(KeyError):
        @anticipate_foobar()
        def noop():
            pass


def test_anticipate_input_factory_overwrite_injecter():
    """
    Verify a ValueError is raised if an injected parameter is attempted
    to be overwritten.
    """
    anticipate_foobar = anticipate_input_factory(
        injecters={
            'foobar': lambda: 'foo'
        }
    )
    
    @anticipate_foobar(foobar=str)
    def noop(foobar):
        pass

    with pytest.raises(ValueError):
        noop(foobar='bar')


def test_anticipate_input_factory_docstring():
    """
    Verify the docstring of an input decorator can be set.
    """
    anticipate_with_doc = anticipate_input_factory(
        doc='foo doc'
    )
    
    assert anticipate_with_doc.__doc__ == 'foo doc'

