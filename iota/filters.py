# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Text

import filters as f
from six import text_type

from iota.adapter import resolve_adapter, InvalidUri


class NodeUri(f.BaseFilter):
  """Validates a string as a node URI."""
  CODE_INVALID = 'not_node_uri'

  templates = {
    CODE_INVALID: 'This value does not appear to be a valid node URI.',
  }

  def _apply(self, value):
    value = self._filter(value, f.Type(text_type)) # type: Text

    if self._has_errors:
      return None

    try:
      resolve_adapter(value)
    except InvalidUri:
      return self._invalid_value(value, self.CODE_INVALID, exc_info=True)

    return value
