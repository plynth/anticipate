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
