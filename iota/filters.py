# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Text, Union

import filters as f
from six import binary_type, text_type

from iota import Address, TryteString, TrytesCompatible
from iota.adapter import resolve_adapter, InvalidUri


class GeneratedAddress(f.BaseFilter):
  """
  Validates an incoming value as a generated :py:class:`Address` (must
  have ``key_index`` set).
  """
  CODE_NO_KEY_INDEX = 'no_key_index'

  templates = {
    CODE_NO_KEY_INDEX: 'Address must have ``key_index`` attribute set.',
  }

  def _apply(self, value):
    value = self._filter(value, f.Type(Address)) # type: Address

    if self._has_errors:
      return None

    if value.key_index is None:
      return self._invalid_value(value, self.CODE_NO_KEY_INDEX)

    return value


class NodeUri(f.BaseFilter):
  """
  Validates a string as a node URI.
  """
  CODE_NOT_NODE_URI = 'not_node_uri'

  templates = {
    CODE_NOT_NODE_URI: 'This value does not appear to be a valid node URI.',
  }

  def _apply(self, value):
    value = self._filter(value, f.Type(text_type)) # type: Text

    if self._has_errors:
      return None

    try:
      resolve_adapter(value)
    except InvalidUri:
      return self._invalid_value(value, self.CODE_NOT_NODE_URI, exc_info=True)

    return value


class Trytes(f.BaseFilter):
  """
  Validates a sequence as a sequence of trytes.
  """
  CODE_NOT_TRYTES   = 'not_trytes'
  CODE_WRONG_FORMAT = 'wrong_format'

  templates = {
    CODE_NOT_TRYTES: 'This value is not a valid tryte sequence.',
    CODE_WRONG_FORMAT: 'This value is not a valid {result_type}.',
  }

  def __init__(self, result_type=TryteString):
    # type: (type) -> None
    super(Trytes, self).__init__()

    if not isinstance(result_type, type):
      raise TypeError(
        'Invalid result_type for {filter_type} '
        '(expected subclass of TryteString, '
        'actual instance of {result_type}).'.format(
          filter_type = type(self).__name__,
          result_type = type(result_type).__name__,
        ),
      )

    if not issubclass(result_type, TryteString):
      raise ValueError(
        'Invalid result_type for {filter_type} '
        '(expected TryteString, actual {result_type}).'.format(
          filter_type = type(self).__name__,
          result_type = result_type.__name__,
        ),
      )

    self.result_type = result_type

  def _apply(self, value):
    # noinspection PyTypeChecker
    value = self._filter(value, f.Type((binary_type, bytearray, TryteString))) # type: TrytesCompatible

    if self._has_errors:
      return None

    # If the incoming value already has the correct type, then we're
    # done.
    if isinstance(value, self.result_type):
      return value

    # First convert to a generic TryteString, to make sure that the
    # sequence doesn't contain any invalid characters.
    try:
      value = TryteString(value)
    except ValueError:
      return self._invalid_value(value, self.CODE_NOT_TRYTES, exc_info=True)

    if self.result_type is TryteString:
      return value

    # Now coerce to the expected type and verify that there are no
    # type-specific errors.
    try:
      return self.result_type(value)
    except ValueError:
      return self._invalid_value(
        value     = value,
        reason    = self.CODE_WRONG_FORMAT,
        exc_info  = True,

        template_vars = {
          'result_type': self.result_type.__name__,
        }
      )
