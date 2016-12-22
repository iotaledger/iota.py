# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase

from iota import TryteString, TransactionHash
from iota.filters import NodeUri, Trytes


class NodeUriTestCase(BaseFilterTestCase):
  filter_type = NodeUri

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | NodeUri`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_uri(self):
    """The incoming value is a valid URI."""
    self.assertFilterPasses('udp://localhost:14265/node')

  def test_fail_not_a_uri(self):
    """
    The incoming value is not a URI.

    Note: Internally, the filter uses `resolve_adapter`, which has its
      own unit tests.  We won't duplicate them here; a simple smoke
      check should suffice.

    :py:class:`test.adapter_test.ResolveAdapterTestCase`
    """
    self.assertFilterErrors(
      'not a valid uri',
      [NodeUri.CODE_NOT_NODE_URI],
    )

  def test_fail_bytes(self):
    """
    To ensure consistent behavior in Python 2 and 3, bytes are not
      accepted.
    """
    self.assertFilterErrors(
      b'udp://localhost:14265/node',
      [f.Type.CODE_WRONG_TYPE],
    )

  def test_fail_wrong_type(self):
    """The incoming value is not a string."""
    self.assertFilterErrors(
      # Use ``FilterRepeater(NodeUri)`` to validate a sequence of URIs.
      ['udp://localhost:14265/node'],
      [f.Type.CODE_WRONG_TYPE],
    )


# noinspection SpellCheckingInspection
class TrytesTestCase(BaseFilterTestCase):
  filter_type = Trytes

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | Trytes`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_ascii(self):
    """The incoming value is ASCII."""
    trytes = b'RBTC9D9DCDQAEASBYBCCKBFA'

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_bytearray(self):
    """The incoming value is a bytearray."""
    trytes = bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA')

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_tryte_string(self):
    """The incoming value is a TryteString."""
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_alternate_result_type(self):
    """Configuring the filter to return a specific type."""
    input_trytes = b'RBTC9D9DCDQAEASBYBCCKBFA'

    result_trytes = (
      b'RBTC9D9DCDQAEASBYBCCKBFA9999999999999999'
      b'99999999999999999999999999999999999999999'
    )

    filter_ = self._filter(input_trytes, result_type=TransactionHash)

    self.assertFilterPasses(filter_, result_trytes)
    self.assertIsInstance(filter_.cleaned_data, TransactionHash)

  def test_fail_not_trytes(self):
    """
    The incoming value contains an invalid character.

    Note: Internally, the filter uses `TryteString`, which has its own
      unit tests.  We won't duplicate them here; a simple smoke check
      should suffice.

    :ref:`test.types_test.TryteStringTestCase`
    """
    self.assertFilterErrors(
      # Everyone knows there's no such thing as "8"!
      b'RBTC9D9DCDQAEASBYBCCKBFA8',
      [Trytes.CODE_NOT_TRYTES],
    )

  def test_fail_alternate_result_type(self):
    """
    The incoming value is a valid tryte sequence, but the filter is
      configured for a specific type with stricter validation.
    """
    trytes = (
      # Ooh, just a little bit too long there.
      b'RBTC9D9DCDQAEASBYBCCKBFA99999999999999999'
      b'99999999999999999999999999999999999999999'
    )

    self.assertFilterErrors(
      self._filter(trytes, result_type=TransactionHash),
      [Trytes.CODE_WRONG_FORMAT],
    )

  def test_fail_wrong_type(self):
    """The incoming value has an incompatible type."""
    self.assertFilterErrors(
      # Use ``FilterRepeater(Trytes)`` to validate a sequence of tryte
      #   representations.
      [TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')],
      [f.Type.CODE_WRONG_TYPE],
    )
