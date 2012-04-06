from anticipate import adapt, adapter

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

    assert False


