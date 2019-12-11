# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Iterable, Optional

from iota import Address, Iota, ProposedTransaction
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Digest
from iota.multisig import commands
from iota.multisig.types import MultisigAddress

__all__ = [
    'MultisigIota',
]


class MultisigIota(Iota):
    """
    Extends the IOTA API so that it can send multi-signature
    transactions.

    .. caution::
        Make sure you understand how multisig works before attempting to
        use it.  If you are not careful, you could easily compromise the
        security of your private keys, send IOTAs to unspendable
        addresses, etc.

    References:

    - https://github.com/iotaledger/wiki/blob/master/multisigs.md
    """

    def create_multisig_address(self, digests):
        # type: (Iterable[Digest]) -> dict
        """
        Generates a multisig address from a collection of digests.

        :param digests:
            Digests to use to create the multisig address.

            .. important::
                In order to spend IOTAs from a multisig address, the
                signature must be generated from the corresponding private
                keys in the exact same order.

        :return:
            Dict with the following items::

                {
                    'address': MultisigAddress,
                        The generated multisig address.
                }
        """
        return commands.CreateMultisigAddressCommand(self.adapter)(
            digests=digests,
        )

    def get_digests(
            self,
            index=0,
            count=1,
            security_level=AddressGenerator.DEFAULT_SECURITY_LEVEL,
    ):
        # type: (int, int, int) -> dict
        """
        Generates one or more key digests from the seed.

        Digests are safe to share; use them to generate multisig
        addresses.

        :param index:
            The starting key index.

        :param count:
            Number of digests to generate.

        :param security_level:
            Number of iterations to use when generating new addresses.

            Larger values take longer, but the resulting signatures are
            more secure.

            This value must be between 1 and 3, inclusive.

        :return:
            Dict with the following items::

                {
                    'digests': List[Digest],
                        Always contains a list, even if only one digest
                        was generated.
                }
        """
        return commands.GetDigestsCommand(self.adapter)(
            seed=self.seed,
            index=index,
            count=count,
            securityLevel=security_level,
        )

    def get_private_keys(
            self,
            index=0,
            count=1,
            security_level=AddressGenerator.DEFAULT_SECURITY_LEVEL,
    ):
        # type: (int, int, int) -> dict
        """
        Generates one or more private keys from the seed.

        As the name implies, private keys should not be shared.
        However, in a few cases it may be necessary (e.g., for M-of-N
        transactions).

        :param index:
            The starting key index.

        :param count:
            Number of keys to generate.

        :param security_level:
            Number of iterations to use when generating new keys.

            Larger values take longer, but the resulting signatures are
            more secure.

            This value must be between 1 and 3, inclusive.

        :return:
            Dict with the following items::

                {
                    'keys': List[PrivateKey],
                        Always contains a list, even if only one key was
                        generated.
                }

        References:

        - :py:class:`iota.crypto.signing.KeyGenerator`
        - https://github.com/iotaledger/wiki/blob/master/multisigs.md#how-m-of-n-works
        """
        return commands.GetPrivateKeysCommand(self.adapter)(
            seed=self.seed,
            index=index,
            count=count,
            securityLevel=security_level,
        )

    def prepare_multisig_transfer(
            self,
            transfers,  # type: Iterable[ProposedTransaction]
            multisig_input,  # type: MultisigAddress
            change_address=None,  # type: Optional[Address]
    ):
        # type: (...) -> dict
        """
        Prepares a bundle that authorizes the spending of IOTAs from a
        multisig address.

        .. note::
            This method is used exclusively to spend IOTAs from a
            multisig address.

            If you want to spend IOTAs from non-multisig addresses, or
            if you want to create 0-value transfers (i.e., that don't
            require inputs), use
            :py:meth:`iota.api.Iota.prepare_transfer` instead.

        :param transfers:
            Transaction objects to prepare.

            .. important::
                Must include at least one transaction that spends IOTAs
                (i.e., has a nonzero ``value``).  If you want to prepare
                a bundle that does not spend any IOTAs, use
                :py:meth:`iota.api.prepare_transfer` instead.

        :param multisig_input:
            The multisig address to use as the input for the transfers.

            .. note::
                This method only supports creating a bundle with a
                single multisig input.

                If you would like to spend from multiple multisig
                addresses in the same bundle, create the
                :py:class:`iota.multisig.transaction.ProposedMultisigBundle`
                object manually.

        :param change_address:
            If inputs are provided, any unspent amount will be sent to
            this address.

            If the bundle has no unspent inputs, ``change_address` is
            ignored.

            .. important::
                Unlike :py:meth:`iota.api.Iota.prepare_transfer`, this
                method will NOT generate a change address automatically.
                If there are unspent inputs and ``change_address`` is
                empty, an exception will be raised.

                This is because multisig transactions typically involve
                multiple individuals, and it would be unfair to the
                participants if we generated a change address
                automatically using the seed of whoever happened to run
                the ``prepare_multisig_transfer`` method!

                .. danger::
                    Note that this protective measure is not a
                    substitute for due diligence!

                    Always verify the details of every transaction in a
                    bundle (including the change transaction) before
                    signing the input(s)!

        :return:
            Dict containing the following values::

                {
                    'trytes': List[TransactionTrytes],
                        Finalized bundle, as trytes.
                        The input transactions are not signed.
                }

          In order to authorize the spending of IOTAs from the multisig
          input, you must generate the correct private keys and invoke
          the :py:meth:`iota.crypto.types.PrivateKey.sign_input_at`
          method for each key, in the correct order.

          Once the correct signatures are applied, you can then perform
          proof of work (``attachToTangle``) and broadcast the bundle
          using :py:meth:`iota.api.Iota.send_trytes`.
        """
        return commands.PrepareMultisigTransferCommand(self.adapter)(
            changeAddress=change_address,
            multisigInput=multisig_input,
            transfers=transfers,
        )
