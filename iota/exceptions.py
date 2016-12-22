# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals


def with_context(exc, context):
  # type: (Exception, dict) -> Exception
  """
  Attaches a ``context`` value to an Exception.

  Before::

     exc = Exception('Frog blast the vent core!')
     exc.context = { ... }
     raise exc

  After::

     raise with_context(Exception('Frog blast the vent core!'), { ... })
  """
  if not hasattr(exc, 'context'):
    exc.context = {}

  exc.context.update(context)
  return exc
