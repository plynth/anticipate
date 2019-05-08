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

=========
Changelog
=========

0.9.0
=====

* Dropped support for Python 2.6, added support for Python 3.7.
* Cleaned up code formatting

Bug Fixes
---------

* Fixed issue that prevented use of an adaptable object (has an
  ``adapt`` method) as an anticipated list of type.

0.8.0
=====

* Change so that anticipating an iterable using ``[type]`` will always
  return a list instead of generator
* Added ``anticipate_input_factory`` to make it easier to implement
  input handlers that need to inject values or handle input errors
  differently
* Made it so you can use any object that implements ``adapt`` as an
  anticipate type so you can use `SpringField`_ fields as input types
* Improved error messages
* Split anticipate input and output handling into separate functions to
  make it easier to intercept input or output handling
* Check that the params being anticipated exist in the function
  signature


.. _SpringField: https://github.com/six8/springfield

