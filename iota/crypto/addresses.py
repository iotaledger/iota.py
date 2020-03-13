from typing import Generator, Iterable, List

from iota import Address, TRITS_PER_TRYTE, TrytesCompatible
from iota.crypto.kerl import Kerl
from iota.crypto.signing import KeyGenerator, KeyIterator
from iota.crypto.types import Digest, PrivateKey, Seed
from iota.exceptions import with_context

__all__ = [
    'AddressGenerator',
]


class AddressGenerator(Iterable[Address]):
    """
    Generates new addresses using a standard algorithm.

    .. note::
        This class does not check if addresses have already been used;
        if you want to exclude used addresses, invoke
        :py:meth:`iota.Iota.get_new_addresses` instead.

        Note also that :py:meth:`iota.Iota.get_new_addresses` uses
        ``AddressGenerator`` internally, so you get the best of both worlds
        when you use the API (:

    :param TrytesCompatible seed:
        The seed to derive addresses from.

    :param int security_level:
        When generating a new address, you can specify a security level for it.
        The security level of an address affects how long the private key is,
        how secure a spent address is against brute-force attacks, and how many
        transactions are needed to contain the signature.

        Could be either 1, 2 or 3.

        Reference:

        - https://docs.iota.org/docs/getting-started/0.1/clients/security-levels

    :param bool checksum:
        Whether to generate address with or without checksum.

    :returns: :py:class:`iota.crypto.addresses.AddressGenerator` object.
    """
    DEFAULT_SECURITY_LEVEL = 2
    """
    Default number of iterations to use when creating digests, used to
    create addresses.
  
    Note: this also impacts a few other things like length of
    transaction signatures.
  
    References:

    - :py:meth:`iota.transaction.ProposedBundle.sign_inputs`
    - :py:class:`iota.transaction.BundleValidator`
    """

    def __init__(
            self,
            seed: TrytesCompatible,
            security_level: int = DEFAULT_SECURITY_LEVEL,
            checksum: bool = False,
    ) -> None:
        super(AddressGenerator, self).__init__()

        self.security_level = security_level
        self.checksum = checksum
        self.seed = Seed(seed)

    def __iter__(self) -> Generator[Address, None, None]:
        """
        Returns a generator for creating new addresses, starting at
        index 0 and potentially continuing on forever.
        """
        return self.create_iterator()

    def get_addresses(
            self,
            start: int,
            count: int = 1,
            step: int = 1
    ) -> List[Address]:
        """
        Generates and returns one or more addresses at the specified
        index(es).

        This is a one-time operation; if you want to create lots of
        addresses across multiple contexts, consider invoking
        :py:meth:`create_iterator` and sharing the resulting generator
        object instead.

        .. warning::
            This method may take awhile to run if the starting
            index and/or the number of requested addresses is a large number!

        :param int start:
            Starting index.
            Must be >= 0.

        :param int count:
            Number of addresses to generate.
            Must be > 0.

        :param int step:
            Number of indexes to advance after each address.
            This may be any non-zero (positive or negative) integer.

        :return:
            ``List[Address]``

            Always returns a list, even if only one address is generated.

            The returned list will contain ``count`` addresses, except
            when ``step * count < start`` (only applies when ``step`` is
            negative).

        :raises ValueError:
            - if ``count`` is lower than 1.
            - if ``step`` is zero.
        """
        if count < 1:
            raise with_context(
                exc=ValueError('``count`` must be positive.'),

                context={
                    'start': start,
                    'count': count,
                    'step': step,
                },
            )

        if not step:
            raise with_context(
                exc=ValueError('``step`` must not be zero.'),

                context={
                    'start': start,
                    'count': count,
                    'step': step,
                },
            )

        generator = self.create_iterator(start, step)

        addresses = []
        for _ in range(count):
            try:
                next_addy = next(generator)
            except StopIteration:
                break
            else:
                addresses.append(next_addy)

        return addresses

    def create_iterator(
            self,
            start: int = 0,
            step: int = 1
    ) -> Generator[Address, None, None]:
        """
        Creates an iterator that can be used to progressively generate new
        addresses.

        Returns an iterator that will create addresses endlessly.
        Use this if you have a feature that needs to generate addresses
        “on demand”.

        :param int start:
            Starting index.

            .. warning::
                This method may take awhile to reset if ``start`` is a large
                number!

        :param int step:
            Number of indexes to advance after each address.

            .. warning::
                The generator may take awhile to advance between
                iterations if ``step`` is a large number!

        :return:
            ``Generator[Address, None, None]`` object that you can iterate to
            generate addresses.
        """
        key_iterator = (
            KeyGenerator(self.seed).create_iterator(
                start,
                step,
                self.security_level,
            )
        )

        while True:
            yield self._generate_address(key_iterator)

    @staticmethod
    def address_from_digest(digest: Digest) -> Address:
        """
        Generates an address from a private key digest.
        """
        address_trits: List[int] = [0] * (Address.LEN * TRITS_PER_TRYTE)

        sponge = Kerl()
        sponge.absorb(digest.as_trits())
        sponge.squeeze(address_trits)

        return Address.from_trits(
            trits=address_trits,

            key_index=digest.key_index,
            security_level=digest.security_level,
        )

    def _generate_address(self, key_iterator: KeyIterator) -> Address:
        """
        Generates a new address.

        Used in the event of a cache miss.
        """
        if self.checksum:
            return (
                self.address_from_digest(
                    digest=self._get_digest(key_iterator),
                ).with_valid_checksum()
            )
        else:
            return self.address_from_digest(self._get_digest(key_iterator))

    @staticmethod
    def _get_digest(key_iterator: KeyIterator) -> Digest:
        """
        Extracts parameters for :py:meth:`address_from_digest`.

        Split into a separate method so that it can be mocked during
        unit tests.
        """
        private_key: PrivateKey = next(key_iterator)
        return private_key.get_digest()
