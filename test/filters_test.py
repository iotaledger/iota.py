import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, TransactionHash, TryteString
from iota.filters import AddressNoChecksum, GeneratedAddress, NodeUri, Trytes


class GeneratedAddressTestCase(BaseFilterTestCase):
  filter_type = GeneratedAddress

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | GeneratedAddress`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_happy_path(self):
    """
    Incoming value has correct type and attributes.
    """
    self.assertFilterPasses(Address(b'', key_index=42, security_level=2))

  def test_fail_key_index_null(self):
    """
    Incoming value does not have ``key_index`` set.
    """
    self.assertFilterErrors(
      Address(b'', security_level=2),
      [GeneratedAddress.CODE_NO_KEY_INDEX],
    )

  def test_fail_security_level_null(self):
    """
    Incoming value does not have ``security_level`` set.
    """
    self.assertFilterErrors(
      Address(b'', key_index=2),
      [GeneratedAddress.CODE_NO_SECURITY_LEVEL],
    )

  def test_fail_wrong_type(self):
    """
    Incoming value is not an :py:class:`Address` instance.
    """
    self.assertFilterErrors(
      # The only way to ensure ``key_index`` is set is to require that
      # the incoming value is an :py:class:`Address` instance.
      b'TESTVALUE9DONTUSEINPRODUCTION99999WJ9PCA'
      b'RBOSBIMNTGDYKUDYYFJFGZOHORYSQPCWJRKHIOVIY',

      [f.Type.CODE_WRONG_TYPE],
    )


class NodeUriTestCase(BaseFilterTestCase):
  filter_type = NodeUri

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | NodeUri`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_udp(self):
    """
    The incoming value is a valid UDP URI.
    """
    self.assertFilterPasses('udp://localhost:14265/node')

  def test_pass_tcp(self):
    """
    The incoming value is a valid TCP URI.

    https://github.com/iotaledger/iota.py/issues/111
    """
    self.assertFilterPasses('tcp://localhost:14265/node')

  def test_fail_not_a_uri(self):
    """
    The incoming value is not a URI.

    Note: Internally, the filter uses ``resolve_adapter``, which has its
    own unit tests.  We won't duplicate them here; a simple smoke
    check should suffice.

    References:
      - :py:class:`test.adapter_test.ResolveAdapterTestCase`
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
    """
    The incoming value is not a string.
    """
    self.assertFilterErrors(
      # Use ``FilterRepeater(NodeUri)`` to validate a sequence of URIs.
      ['udp://localhost:14265/node'],
      [f.Type.CODE_WRONG_TYPE],
    )


class TrytesTestCase(BaseFilterTestCase):
  filter_type = Trytes

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | Trytes`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_ascii(self):
    """
    The incoming value is ASCII.
    """
    trytes = b'RBTC9D9DCDQAEASBYBCCKBFA'

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_bytearray(self):
    """
    The incoming value is a bytearray.
    """
    trytes = bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA')

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_tryte_string(self):
    """
    The incoming value is a TryteString.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    filter_ = self._filter(trytes)

    self.assertFilterPasses(filter_, trytes)
    self.assertIsInstance(filter_.cleaned_data, TryteString)

  def test_pass_alternate_result_type(self):
    """
    Configuring the filter to return a specific type.
    """
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

    Note: Internally, the filter uses :py:class:`TryteString`, which has
    its own unit tests.  We won't duplicate them here; a simple smoke
    check should suffice.

    References:
      - :py:class:`test.types_test.TryteStringTestCase`
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
    """
    The incoming value has an incompatible type.
    """
    self.assertFilterErrors(
      # Use ``FilterRepeater(Trytes)`` to validate a sequence of tryte
      # representations.
      [TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')],
      [f.Type.CODE_WRONG_TYPE],
    )


class AddressNoChecksumTestCase(BaseFilterTestCase):
  filter_type = AddressNoChecksum

  def setUp(self):
    super(AddressNoChecksumTestCase, self).setUp()

    # Define some addresses that we can reuse between tests
    self.tryte1 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999FBFFTG'
      b'QFWEHEL9KCAFXBJBXGE9HID9XCOHFIDABHDG9AHDR'
    )
    self.checksum = b'ENXYJOBP9'
    self.address = Address(self.tryte1)
    self.address_with_checksum = Address(self.tryte1 + self.checksum)
    self.address_with_bad_checksum = Address(self.tryte1 + b'DEADBEEF9')

  def test_pass_no_checksum_addy(self):
    """
    Incoming value is tryte in address form or Address object.
    """
    self.assertFilterPasses(self.tryte1)
    self.assertFilterPasses(self.address)

  def test_pass_with_checksum_addy(self):
    """
    After passing through the filter an address with a checksum should
    return the address without.
    """
    self.assertFilterPasses(self.address_with_checksum, self.address)

  def test_fail_with_bad_checksum_addy(self):
    """
    If they've got a bad checksum in their address we should probably
    tell them, so they don't wonder why something works in one place and
    not another.
    """
    self.assertFilterErrors(
      self.address_with_bad_checksum,
      [AddressNoChecksum.ADDRESS_BAD_CHECKSUM])
