from iota.crypto import FRAGMENT_LENGTH
from iota.exceptions import with_context
from iota.types import Hash, TryteString, TrytesCompatible

__all__ = [
    'BundleHash',
    'Fragment',
    'TransactionHash',
    'TransactionTrytes',
    'Nonce'
]


class BundleHash(Hash):
    """
    An :py:class:`TryteString` (:py:class:`Hash`) that acts as a bundle hash.
    """
    pass


class TransactionHash(Hash):
    """
    An :py:class:`TryteString` (:py:class:`Hash`) that acts as a transaction hash.
    """
    pass


class Fragment(TryteString):
    """
    An :py:class:`TryteString` representation of a signature/message fragment
    in a transaction.

    :raises ValueError: if ``trytes`` is longer than 2187 trytes in length.
    """
    LEN = FRAGMENT_LENGTH
    """
    Length of a fragment in trytes.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(Fragment, self).__init__(trytes, pad=self.LEN)

        if len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError('{cls} values must be {len} trytes long.'.format(
                    cls=type(self).__name__,
                    len=self.LEN
                )),

                context={
                    'trytes': trytes,
                },
            )


class TransactionTrytes(TryteString):
    """
    An :py:class:`TryteString` representation of a Transaction.

    :raises ValueError: if ``trytes`` is longer than 2673 trytes in length.
    """
    LEN = 2673
    """
    Length of a transaction in trytes.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(TransactionTrytes, self).__init__(trytes, pad=self.LEN)

        if len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError('{cls} values must be {len} trytes long.'.format(
                    cls=type(self).__name__,
                    len=self.LEN
                )),

                context={
                    'trytes': trytes,
                },
            )


class Nonce(TryteString):
    """
    An :py:class:`TryteString` that acts as a transaction nonce.

    :raises ValueError: if ``trytes`` is longer than 27 trytes in length.
    """
    LEN = 27
    """
    Length of a nonce in trytes.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(Nonce, self).__init__(trytes, pad=self.LEN)

        if len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError('{cls} values must be {len} trytes long.'.format(
                    cls=type(self).__name__,
                    len=self.LEN
                )),

                context={
                    'trytes': trytes,
                },
            )
