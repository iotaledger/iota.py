import warnings
from typing import Optional

from iota.crypto import FRAGMENT_LENGTH, HASH_LENGTH, SeedWarning
from iota.crypto.kerl import Kerl
from iota.exceptions import with_context
from iota.transaction.base import Bundle
from iota.types import Hash, TryteString, TrytesCompatible

__all__ = [
    'Digest',
    'PrivateKey',
    'Seed',
]


class Digest(TryteString):
    """
    A private key digest.  Basically the same thing as a regular
    :py:class:`iota.TryteString`, except that it (usually) has a key index
    associated with it.

    Note: in a few cases (e.g., generating multisig addresses), a key
    index is not necessary/available.

    :param TrytesCompatible trytes:
        Byte string or bytearray.

    :param Optional[int] key_index:
        Key index used for generating the digest.

    :raises ValueError:
        if length of ``trytes`` is not multiple of :py:attr:`iota.Hash.LEN`.
    """

    def __init__(
            self,
            trytes: TrytesCompatible,
            key_index: Optional[int] = None
    ) -> None:
        super(Digest, self).__init__(trytes)

        # A digest is a series of hashes; its length should reflect
        # that.
        if len(self) % Hash.LEN:
            raise with_context(
                exc=ValueError(
                    'Length of {cls} values '
                    'must be a multiple of {len} trytes.'.format(
                        cls=type(self).__name__,
                        len=Hash.LEN,
                    ),
                ),

                context={
                    'trytes': trytes,
                },
            )

        self.key_index = key_index

    @property
    def security_level(self) -> int:
        """
        Returns the number of iterations that were used to generate this
        digest (also known as "security level").

        :return:
            ``int``
        """
        return len(self) // Hash.LEN

    def as_json_compatible(self) -> dict:
        """
        Returns a JSON-compatible representation of the digest.

        :return:
            ``dict`` with the following structure::

                {
                    trytes': str,
                    'key_index': int,
                }

        """
        return {
            'trytes': self._trytes.decode('ascii'),
            'key_index': self.key_index,
        }


class Seed(TryteString):
    """
    An :py:class:`iota.TryteString` that acts as a seed for crypto functions.

    Note: This class is identical to :py:class:`iota.TryteString`, but it has
    a distinct type so that seeds can be identified in Python code.

    IMPORTANT: For maximum security, a seed must be EXACTLY 81 trytes!

    :param TrytesCompatible trytes:
        Byte string or bytearray.

    :raises Warning:
        if ``trytes`` are longer than 81 trytes in length.

    References:

    - https://iota.stackexchange.com/q/249
    """

    LEN = 81
    """
    Length of a Seed.
    """

    def __init__(self, trytes: Optional[TrytesCompatible] = None) -> None:
        if trytes and len(trytes) > Hash.LEN:
            warnings.warn(
                message=(
                    "Seed has inappropriate length! "
                    "(see https://iota.stackexchange.com/q/249 for more info)."
                ),

                category=SeedWarning,
            )

        super(Seed, self).__init__(trytes)

    @classmethod
    def random(cls, length: int = Hash.LEN) -> 'Seed':
        """
        Generates a random seed using a CSPRNG.

        :param int length:
            Length of seed, in trytes.

            For maximum security, this should always be set to 81, but
            you can change it if you're 110% sure you know what you're
            doing.

            See https://iota.stackexchange.com/q/249 for more info.

        :return:
            :py:class:`iota.Seed` object.

        Example usage::

            from iota import Seed

            my_seed = Seed.random()

            print(my_seed)

        """
        return super(Seed, cls).random(length)


class PrivateKey(TryteString):
    """
    An :py:class:`iota.TryteString` that acts as a private key, e.g., for generating
    message signatures, new addresses, etc.

    :param TrytesCompatible trytes:
        Byte string or bytearray.

    :param Optional[int] key_index:
        Key index used for generating the private key.

    :param Optional[int] security_level:
        Security level used for generating the private key.

    :raises ValueError:
        if length of ``trytes`` is not a multiple of
        :py:attr:`iota.transaction.Fragement.LEN`.
    """

    def __init__(
            self,
            trytes: TrytesCompatible,
            key_index: Optional[int] = None,
            security_level: Optional[int] = None
    ) -> None:
        super(PrivateKey, self).__init__(trytes)

        if len(self._trytes) % FRAGMENT_LENGTH:
            raise with_context(
                exc=ValueError(
                    'Length of {cls} values '
                    'must be a multiple of {len} trytes.'.format(
                        cls=type(self).__name__,
                        len=FRAGMENT_LENGTH,
                    ),
                ),

                context={
                    'trytes': self._trytes,
                },
            )

        self.key_index = key_index
        self.security_level = security_level

    def as_json_compatible(self) -> dict:
        """
        Returns a JSON-compatible representation of the private key.

        :return:
            ``dict`` with the following structure::

                {
                    trytes': str,
                    'key_index': int,
                    'security_level': int,
                }

        """
        return {
            'trytes': self._trytes.decode('ascii'),
            'key_index': self.key_index,
            'security_level': self.security_level,
        }

    def get_digest(self) -> Digest:
        """
        Generates the digest used to do the actual signing.

        Signing keys can have variable length and tend to be quite long,
        which makes them not-well-suited for use in crypto algorithms.

        The digest is essentially the result of running the signing key
        through a PBKDF, yielding a constant-length hash that can be
        used for crypto.

        :return:
            :py:class:`iota.crypto.types.Digest` object.
        """
        hashes_per_fragment = FRAGMENT_LENGTH // Hash.LEN

        key_fragments = self.iter_chunks(FRAGMENT_LENGTH)

        # The digest will contain one hash per key fragment.
        digest = [0] * HASH_LENGTH * len(key_fragments)

        # Iterate over each fragment in the key.
        for i, fragment in enumerate(key_fragments):
            fragment_trits = fragment.as_trits()

            key_fragment = [0] * FRAGMENT_LENGTH
            hash_trits = []

            # Within each fragment, iterate over one hash at a time.
            for j in range(hashes_per_fragment):
                hash_start = j * HASH_LENGTH
                hash_end = hash_start + HASH_LENGTH
                hash_trits = fragment_trits[hash_start:hash_end]

                for k in range(26):
                    sponge = Kerl()
                    sponge.absorb(hash_trits)
                    sponge.squeeze(hash_trits)

                key_fragment[hash_start:hash_end] = hash_trits

            # After processing all of the hashes in the fragment,
            # generate a final hash and append it to the digest.
            #
            # Note that we will do this once per fragment in the key, so
            # the longer the key is, the longer the digest will be.
            sponge = Kerl()
            sponge.absorb(key_fragment)
            sponge.squeeze(hash_trits)

            fragment_hash_start = i * HASH_LENGTH
            fragment_hash_end = fragment_hash_start + HASH_LENGTH

            digest[fragment_hash_start:fragment_hash_end] = hash_trits

        return Digest(TryteString.from_trits(digest), self.key_index)

    def sign_input_transactions(
            self,
            bundle: Bundle,
            start_index: int
    ) -> None:
        """
        Signs the inputs starting at the specified index.

        :param Bundle bundle:
            The bundle that contains the input transactions to sign.

        :param int start_index:
            The index of the first input transaction.

            If necessary, the resulting signature will be split across
            subsequent transactions automatically.

        :raises ValuError:
            - if ``bundle`` is not finalized.
            - if attempting to sign non-input transactions.
            - if attempting to sign transactions with non-empty
              ``signature_message_fragment`` field.
        :raises IndexError: if wrong ``start_index`` is provided.
        """

        if not bundle.hash:
            raise with_context(
                exc=ValueError('Cannot sign inputs without a bundle hash!'),

                context={
                    'bundle': bundle,
                    'key_index': self.key_index,
                    'start_index': start_index,
                },
            )

        from iota.crypto.signing import SignatureFragmentGenerator
        signature_fragment_generator = (
            SignatureFragmentGenerator(self, bundle.hash)
        )

        # We can only fit one signature fragment into each transaction,
        # so we have to split the entire signature.
        for j in range(self.security_level):
            # Do lots of validation before we attempt to sign the
            # transaction, and attach lots of context info to any
            # exception.
            #
            # This method is likely to be invoked at a very low level in
            # the application, so if anything goes wrong, we want to
            # make sure it's as easy to troubleshoot as possible!
            try:
                txn = bundle[start_index + j]
            except IndexError as e:
                raise with_context(
                    exc=e,

                    context={
                        'bundle': bundle,
                        'key_index': self.key_index,
                        'current_index': start_index + j,
                    },
                )

            # Only inputs can be signed.
            if txn.value > 0:
                raise with_context(
                    exc=ValueError(
                        'Attempting to sign non-input transaction #{i} '
                        '(value={value}).'.format(
                            i=txn.current_index,
                            value=txn.value,
                        ),
                    ),

                    context={
                        'bundle': bundle,
                        'key_index': self.key_index,
                        'start_index': start_index,
                    },
                )

            if txn.signature_message_fragment:
                raise with_context(
                    exc=ValueError(
                        'Attempting to sign input transaction #{i}, '
                        'but it has a non-empty fragment '
                        '(is it already signed?).'.format(
                            i=txn.current_index,
                        ),
                    ),

                    context={
                        'bundle': bundle,
                        'key_index': self.key_index,
                        'start_index': start_index,
                    },
                )

            txn.signature_message_fragment = next(signature_fragment_generator)
