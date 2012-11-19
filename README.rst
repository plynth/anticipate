==========
Anticipate
==========

.. image:: https://secure.travis-ci.org/six8/anticipate.png
    :target: http://travis-ci.org/six8/anticipate
    :alt: Build Status


Expect the unexpected, but get what you want.

::

    @anticipate(int)
    def get_int():
      return '1'

    assert get_int() == 1

    @anticipate(str)
    def get_str():
      return 22

    assert get_str() == '22'

    @anticipate([str])
    def get_strs(*args):
      return args

    assert list(get_strs(1, 2, 3)) == ['1', '2', '3']

Works much better with your own objects or with `SpringField <https://github.com/six8/springfield>`_

