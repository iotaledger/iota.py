# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from json.encoder import JSONEncoder as BaseJsonEncoder

from six import with_metaclass


class JsonSerializable(with_metaclass(ABCMeta)):
  """
  Interface for classes that can be safely converted to JSON.
  """
  @abstract_method
  def as_json_compatible(self):
    """
    Returns a JSON-compatible representation of the object.

    References:
      - :py:class:`iota.json.JsonEncoder`.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


# noinspection PyClassHasNoInit
class JsonEncoder(BaseJsonEncoder):
  """
  JSON encoder with support for :py:class:`JsonSerializable`.
  """
  def default(self, o):
    if isinstance(o, JsonSerializable):
      return o.as_json_compatible()

    return super(JsonEncoder, self).default(o)
