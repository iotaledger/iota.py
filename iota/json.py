# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals


from json.encoder import JSONEncoder as BaseJsonEncoder


# noinspection PyClassHasNoInit
class JsonEncoder(BaseJsonEncoder):
  """JSON encoder with support for custom types."""
  def default(self, o):
    if hasattr(o, 'as_json_compatible'):
      return o.as_json_compatible()
    return super(JsonEncoder, self).default(o)
