from typing import Iterator, List, Sequence

from iota import Hash, TRITS_PER_TRYTE, TryteString, TrytesCompatible, Address
from iota.crypto import FRAGMENT_LENGTH, HASH_LENGTH
from iota.crypto.kerl import Kerl
from iota.crypto.types import PrivateKey, Seed
from iota.exceptions import with_context
from iota.trits import add_trits, trits_from_int

__all__ = [
    'KeyGenerator',
    'KeyIterator',
    'normalize',
    'SignatureFragmentGenerator',
    'validate_signature_fragments',
]


def normalize(hash_: Hash) -> List[List[int]]:
    """
    "Normalizes" a hash, converting it into a sequence of integers
    (not trits!) suitable for use in signature generation/validation.

    The hash is divided up into 3 parts, each of which is "balanced"
    (sum of all the values is equal to zero).
    """
    normalized = []
    source = hash_.as_integers()

    chunk_size = 27

    for i in range(Hash.LEN // chunk_size):
        start = i * chunk_size
        stop = start + chunk_size

        chunk = source[start:stop]
        chunk_sum = sum(chunk)

        while chunk_sum > 0:
            chunk_sum -= 1
            for j in range(chunk_size):
                if chunk[j] > -13:
                    chunk[j] -= 1
                    break

        while chunk_sum < 0:
            chunk_sum += 1
            for j in range(chunk_size):
                if chunk[j] < 13:
                    chunk[j] += 1
                    break

        normalized.append(chunk)

    return normalized


class KeyGenerator(object):
    """
    Generates signing keys for messages.
    """

    def __init__(self, seed: TrytesCompatible) -> None:
        super(KeyGenerator, self).__init__()

        self.seed = Seed(seed)

    def get_key(self, index: int, iterations: int) -> PrivateKey:
        """
        Generates a single key.

        :param index:
            The key index.

        :param iterations:
            Number of transform iterations to apply to the key, also
            known as security level.
            Must be >= 1.

            Increasing this value makes key generation slower, but more
            resistant to brute-forcing.
        """
        return (
            self.get_keys(
                    start=index,
                    count=1,
                    step=1,
                    iterations=iterations,
            )[0]
        )

    def get_key_for(self, address: Address):
        """
        Generates the key associated with the specified address.

        Note that this method will generate the wrong key if the input
        address was generated from a different key!
        """
        return self.get_key(
                index=address.key_index,
                iterations=address.security_level,
        )

    def get_keys(
            self,
            start: int,
            count: int = 1,
            step: int = 1,
            iterations: int = 1
    ) -> List[PrivateKey]:
        """
        Generates and returns one or more keys at the specified
        index(es).

        This is a one-time operation; if you want to create lots of keys
        across multiple contexts, consider invoking
        :py:meth:`create_iterator` and sharing the resulting generator
        object instead.

        Warning: This method may take awhile to run if the starting
        index and/or the number of requested keys is a large number!

        :param start:
            Starting index.
            Must be >= 0.

        :param count:
            Number of keys to generate.
            Must be > 0.

        :param step:
            Number of indexes to advance after each key.
            This may be any non-zero (positive or negative) integer.

        :param iterations:
            Number of transform iterations to apply to each key, also
            known as security level.
            Must be >= 1.

            Increasing this value makes key generation slower, but more
            resistant to brute-forcing.

        :return:
            Always returns a list, even if only one key is generated.

            The returned list will contain ``count`` keys, except when
            ``step * count < start`` (only applies when ``step`` is
            negative).
        """
        if count < 1:
            raise with_context(
                    exc=ValueError('``count`` must be positive.'),

                    context={
                        'start': start,
                        'count': count,
                        'step': step,
                        'iterations': iterations,
                    },
            )

        if not step:
            raise with_context(
                    exc=ValueError('``step`` must not be zero.'),

                    context={
                        'start': start,
                        'count': count,
                        'step': step,
                        'iterations': iterations,
                    },
            )

        iterator = self.create_iterator(start, step, iterations)

        keys = []
        for _ in range(count):
            try:
                next_key = next(iterator)
            except StopIteration:
                break
            else:
                keys.append(next_key)

        return keys

    def create_iterator(
            self,
            start: int = 0,
            step: int = 1,
            security_level: int = 1
    ) -> 'KeyIterator':
        """
        Creates a generator that can be used to progressively generate
        new keys.

        :param start:
            Starting index.

            Warning: This method may take awhile to reset if ``start``
            is a large number!

        :param step:
            Number of indexes to advance after each key.

            This value can be negative; the generator will exit if it
            reaches an index < 0.

            Warning: The generator may take awhile to advance between
            iterations if ``step`` is a large number!

        :param security_level:
            Number of _transform iterations to apply to each key.
            Must be >= 1.

            Increasing this value makes key generation slower, but more
            resistant to brute-forcing.
        """
        return KeyIterator(self.seed, start, step, security_level)


class KeyIterator(Iterator[PrivateKey]):
    """
    Creates PrivateKeys from a set of iteration parameters.
    """

    def __init__(
            self,
            seed: Seed,
            start: int,
            step: int,
            security_level: int
    ) -> None:
        super(KeyIterator, self).__init__()

        if start < 0:
            raise with_context(
                    exc=ValueError('``start`` cannot be negative.'),

                    context={
                        'start': start,
                        'step': step,
                        'security_level': security_level,
                    },
            )

        if security_level < 1:
            raise with_context(
                    exc=ValueError('``security_level`` must be >= 1.'),

                    context={
                        'start': start,
                        'step': step,
                        'security_level': security_level,
                    },
            )

        # In order to work correctly, the seed must be padded so that it
        # is a multiple of 81 trytes.
        seed += b'9' * (Hash.LEN - ((len(seed) % Hash.LEN) or Hash.LEN))

        self.security_level = security_level
        self.seed_as_trits = seed.as_trits()
        self.start = start
        self.step = step

        self.current = self.start

        self.fragment_length = FRAGMENT_LENGTH * TRITS_PER_TRYTE
        self.hashes_per_fragment = FRAGMENT_LENGTH // Hash.LEN

    def __iter__(self) -> 'KeyIterator':
        return self

    def __next__(self) -> PrivateKey:
        while self.current >= 0:
            sponge = self._create_sponge(self.current)

            key = [0] * (self.fragment_length * self.security_level)
            buffer = [0] * len(self.seed_as_trits)

            for fragment_seq in range(self.security_level):
                # Squeeze trits from the buffer and append them to the
                # key, one hash at a time.
                for hash_seq in range(self.hashes_per_fragment):
                    sponge.squeeze(buffer)

                    key_start = (
                            (fragment_seq * self.fragment_length) +
                            (hash_seq * HASH_LENGTH)
                    )

                    key_stop = key_start + HASH_LENGTH

                    # Ensure we only capture one hash from the buffer,
                    # in case it is longer than that (i.e., if the seed
                    # is longer than 81 trytes).
                    key[key_start:key_stop] = buffer[0:HASH_LENGTH]

            private_key = PrivateKey.from_trits(
                    key_index=self.current,
                    security_level=self.security_level,
                    trits=key,
            )

            self.advance()

            return private_key

    def advance(self) -> None:
        """
        Advances the generator without creating a key.
        """
        self.current += self.step

    def _create_sponge(self, index: int) -> Kerl:
        """
        Prepares the hash sponge for the generator.
        """
        seed = self.seed_as_trits[:]

        sponge = Kerl()
        sponge.absorb(add_trits(seed, trits_from_int(index)))

        # Squeeze all of the trits out of the sponge and re-absorb them.
        # Note that the sponge transforms several times per operation,
        # so this sequence is not as redundant as it looks at first
        # glance.
        sponge.squeeze(seed)
        sponge.reset()
        sponge.absorb(seed)

        return sponge


class SignatureFragmentGenerator(Iterator[TryteString]):
    """
    Used to generate signature fragments progressively.

    Each instance can generate 1 signature per fragment in the private
    key.
    """

    def __init__(self, private_key: PrivateKey, hash_: Hash) -> None:
        super(SignatureFragmentGenerator, self).__init__()

        self._key_chunks = private_key.iter_chunks(FRAGMENT_LENGTH)
        self._iteration = -1
        self._normalized_hash = normalize(hash_)
        self._sponge = Kerl()

    def __iter__(self) -> 'SignatureFragmentGenerator':
        return self

    def __len__(self) -> int:
        """
        Returns the number of fragments this generator can create.

        Note: This method always returns the same result, no matter how
        many iterations have been completed.
        """
        return len(self._key_chunks)

    def __next__(self) -> TryteString:
        """
        Returns the next signature fragment.
        """
        key_trytes: TryteString = next(self._key_chunks)
        self._iteration += 1

        # If the key is long enough, loop back around to the start.
        normalized_chunk = (
            self._normalized_hash[self._iteration % len(self._normalized_hash)]
        )

        signature_fragment = key_trytes.as_trits()

        # Build the signature, one hash at a time.
        for i in range(key_trytes.count_chunks(Hash.LEN)):
            hash_start = i * HASH_LENGTH
            hash_end = hash_start + HASH_LENGTH

            buffer: List[int] = signature_fragment[hash_start:hash_end]

            for _ in range(13 - normalized_chunk[i]):
                self._sponge.reset()
                self._sponge.absorb(buffer)
                self._sponge.squeeze(buffer)

            signature_fragment[hash_start:hash_end] = buffer

        return TryteString.from_trits(signature_fragment)


def validate_signature_fragments(
        fragments: Sequence[TryteString],
        hash_: Hash,
        public_key: TryteString,
        sponge_type: type = Kerl,
) -> bool:
    """
    Returns whether a sequence of signature fragments is valid.

    :param fragments:
      Sequence of signature fragments (usually
      :py:class:`iota.transaction.Fragment` instances).

    :param hash_:
      Hash used to generate the signature fragments (usually a
      :py:class:`iota.transaction.BundleHash` instance).

    :param public_key:
      The public key value used to verify the signature digest (usually a
      :py:class:`iota.types.Address` instance).

    :param sponge_type:
      The class used to create the cryptographic sponge (i.e., Curl or Kerl).
    """
    checksum = [0] * (HASH_LENGTH * len(fragments))
    normalized_hash = normalize(hash_)

    for i, fragment in enumerate(fragments):
        outer_sponge = sponge_type()

        # If there are more than 3 iterations, loop back around to the
        # start.
        normalized_chunk = normalized_hash[i % len(normalized_hash)]

        buffer = []
        for j, hash_trytes in enumerate(fragment.iter_chunks(Hash.LEN)):
            buffer: List[int] = hash_trytes.as_trits()
            inner_sponge = sponge_type()

            # Note the sign flip compared to
            # :py;class:`SignatureFragmentGenerator`.
            for _ in range(13 + normalized_chunk[j]):
                inner_sponge.reset()
                inner_sponge.absorb(buffer)
                inner_sponge.squeeze(buffer)

            outer_sponge.absorb(buffer)

        outer_sponge.squeeze(buffer)
        checksum[i * HASH_LENGTH:(i + 1) * HASH_LENGTH] = buffer

    actual_public_key = [0] * HASH_LENGTH
    addy_sponge = sponge_type()
    addy_sponge.absorb(checksum)
    addy_sponge.squeeze(actual_public_key)

    return actual_public_key == public_key.as_trits()
