# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

__all__ = [
    'with_context',
]


def with_context(exc, context):
    # type: (Exception, dict) -> Exception
    """
    Attaches a ``context`` value to an Exception.

    Before:

    .. code-block:: python

        exc = Exception('Frog blast the vent core!')
        exc.context = { ... }
        raise exc

    After:

    .. code-block:: python

        raise with_context(
            exc=Exception('Frog blast the vent core!'),
            context={ ... },
        )
    """
    if not hasattr(exc, 'context'):
        exc.context = {}

    exc.context.update(context)
    return exc
