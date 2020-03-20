from typing import Type

import filters as f
from filters.macros import filter_macro
from urllib.parse import urlparse

from iota import Address, TryteString, TrytesCompatible
from iota.crypto.addresses import AddressGenerator

__all__ = [
    'AddressNoChecksum',
    'GeneratedAddress',
    'NodeUri',
    'SecurityLevel',
    'StringifiedTrytesArray',
    'Trytes',
]


class GeneratedAddress(f.BaseFilter):
    """
    Validates an incoming value as a generated :py:class:`Address` (must
    have ``key_index`` and ``security_level`` set).

    When a value doesn't pass the filter, a ``ValueError`` is raised with lots
    of contextual info attached to it.

    :return:
        :py:class:`GeneratedAddress` object.
    """
    CODE_NO_KEY_INDEX = 'no_key_index'
    CODE_NO_SECURITY_LEVEL = 'no_security_level'

    templates = {
        CODE_NO_KEY_INDEX:
            'Address must have ``key_index`` attribute set.',

        CODE_NO_SECURITY_LEVEL:
            'Address must have ``security_level`` attribute set.',
    }

    def _apply(self, value):
        value: Address = self._filter(value, f.Type(Address))

        if self._has_errors:
            return None

        if value.key_index is None:
            return self._invalid_value(value, self.CODE_NO_KEY_INDEX)

        if value.security_level is None:
            return self._invalid_value(value, self.CODE_NO_SECURITY_LEVEL)

        return value


class NodeUri(f.BaseFilter):
    """
    Validates a string as a node URI.

    When a value doesn't pass the filter, a ``ValueError`` is raised with lots
    of contextual info attached to it.

    :return:
        :py:class:`NodeUri` object.
    """
    SCHEMES = {'tcp', 'udp'}
    """
    Allowed schemes for node URIs.
    """

    CODE_NOT_NODE_URI = 'not_node_uri'

    templates = {
        CODE_NOT_NODE_URI:
            'This value does not appear to be a valid node URI.',
    }

    def _apply(self, value):
        value: str = self._filter(value, f.Type(str))

        if self._has_errors:
            return None

        parsed = urlparse(value)

        if parsed.scheme not in self.SCHEMES:
            return self._invalid_value(value, self.CODE_NOT_NODE_URI)

        return value


@filter_macro
def SecurityLevel() -> f.FilterChain:
    """
    Generates a filter chain for validating a security level.

    :return:
        :py:class:`filters.FilterChain` object.
    """
    return (
            f.Type(int) |
            f.Min(1) |
            f.Max(3) |
            f.Optional(default=AddressGenerator.DEFAULT_SECURITY_LEVEL)
    )


class Trytes(f.BaseFilter):
    """
    Validates a sequence as a sequence of trytes.

    When a value doesn't pass the filter, a ``ValueError`` is raised with lots
    of contextual info attached to it.

    :param TryteString result_type:
        Any subclass of :py:class:`~iota.TryteString` that you want the filter
        to validate.

    :raises TypeError: if value is not of ``result_type``.
    :raises ValueError:
        if ``result_type`` is not of :py:class:`~iota.TryteString` type.

    :return:
        :py:class:`Trytes` object.

    """
    CODE_NOT_TRYTES = 'not_trytes'
    CODE_WRONG_FORMAT = 'wrong_format'

    templates = {
        CODE_NOT_TRYTES: 'This value is not a valid tryte sequence.',
        CODE_WRONG_FORMAT: 'This value is not a valid {result_type}.',
    }

    def __init__(self, result_type: type = TryteString) -> None:
        super(Trytes, self).__init__()

        if not isinstance(result_type, type):
            raise TypeError(
                'Invalid result_type for {filter_type} '
                '(expected subclass of TryteString, '
                'actual instance of {result_type}).'.format(
                    filter_type=type(self).__name__,
                    result_type=type(result_type).__name__,
                ),
            )

        if not issubclass(result_type, TryteString):
            raise ValueError(
                'Invalid result_type for {filter_type} '
                '(expected TryteString, actual {result_type}).'.format(
                    filter_type=type(self).__name__,
                    result_type=result_type.__name__,
                ),
            )

        self.result_type = result_type

    def _apply(self, value):
        value: TrytesCompatible = self._filter(
            filter_chain=f.Type(
                (bytes, bytearray, str, TryteString)
            ),

            value=value,
        )

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
            return self._invalid_value(
                value=value,
                reason=self.CODE_NOT_TRYTES,
                exc_info=True,
            )

        if self.result_type is TryteString:
            return value

        # Now coerce to the expected type and verify that there are no
        # type-specific errors.
        try:
            return self.result_type(value)
        except ValueError:
            return self._invalid_value(
                value=value,
                reason=self.CODE_WRONG_FORMAT,
                exc_info=True,

                template_vars={
                    'result_type': self.result_type.__name__,
                },
            )


@filter_macro
def StringifiedTrytesArray(trytes_type: Type = TryteString) -> f.FilterChain:
    """
    Validates that the incoming value is an array containing tryte
    strings corresponding to the specified type (e.g.,
    ``TransactionHash``).

    When a value doesn't pass the filter, a ``ValueError`` is raised with lots
    of contextual info attached to it.

    :param TryteString trytes_type:
        Any subclass of :py:class:`~iota.TryteString` that you want the filter
        to validate.

    :return:
        :py:class:`filters.FilterChain` object.

    .. important::
        This filter will return string values, suitable for inclusion in
        an API request.  If you are expecting objects (e.g.,
        :py:class:`Address`), then this is not the filter to use!

    .. note::
        This filter will allow empty arrays and `None`.  If this is not
        desirable, chain this filter with ``f.NotEmpty`` or
        ``f.Required``, respectively.
    """
    return f.Array | f.FilterRepeater(
        f.Required |
        Trytes(trytes_type) |
        f.Unicode(encoding='ascii', normalize=False),
    )


class AddressNoChecksum(Trytes):
    """
    Validates a sequence as an :py:class:`Address`, then chops off the checksum
    if present.

    When a value doesn't pass the filter, a ``ValueError`` is raised with lots
    of contextual info attached to it.

    :return:
        :py:class:`AddressNoChecksum` object.
    """
    ADDRESS_BAD_CHECKSUM = 'address_bad_checksum'

    templates = {
        ADDRESS_BAD_CHECKSUM:
            'Checksum is {supplied_checksum}, should be {expected_checksum}?',
    }

    def __init__(self) -> None:
        super(AddressNoChecksum, self).__init__(result_type=Address)

    def _apply(self, value):
        super(AddressNoChecksum, self)._apply(value)

        if self._has_errors:
            return None

        # Possible it's still just a TryteString.
        if not isinstance(value, Address):
            value = Address(value)

        # Bail out if we have a bad checksum.
        if value.checksum and not value.is_checksum_valid():
            return self._invalid_value(
                value=value,
                reason=self.ADDRESS_BAD_CHECKSUM,
                exc_info=True,

                context={
                    'supplied_checksum': value.checksum,
                    'expected_checksum': value.with_valid_checksum().checksum,
                },
            )

        return Address(value.address)
