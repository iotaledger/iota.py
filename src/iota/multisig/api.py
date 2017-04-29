# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable

from iota import Iota
from iota.commands import discover_commands
from iota.crypto.types import Digest
from iota.multisig import commands

__all__ = [
  'MultisigIota',
]

class MultisigIota(Iota):
  """
  Extends the IOTA API so that it can send multi-signature
  transactions.

  **CAUTION:** Make sure you understand how multisig works before
  attempting to use it.  If you are not careful, you could easily
  compromise the security of your private keys, send IOTAs to
  inaccessible addresses, etc.

  References:
    - https://github.com/iotaledger/wiki/blob/master/multisigs.md
  """
  commands = discover_commands('iota.multisig.commands')

  def create_multisig_address(self, digests):
    # type: (Iterable[Digest]) -> dict
    """
    Generates a multisig address from a collection of digests.

    :param digests:
      Digests to use to create the multisig address.

      IMPORTANT: In order to spend IOTAs from a multisig address, the
      signature must be generated from the corresponding private keys
      in the exact same order.

    :return:
      Dict with the following items::

         {
           'address': MultisigAddress,
             The generated multisig address.
         }
    """
    return commands.CreateMultisigAddressCommand(self.adapter)(
      digests = digests,
    )

  def get_digests(self, index=0, count=1):
    # type: (int, int) -> dict
    """
    Generates one or more key digests from the seed.

    Digests are safe to share; use them to generate multisig addresses.

    :param index:
      The starting key index.

    :param count:
      Number of digests to generate.

    :return:
      Dict with the following items::

         {
           'digests': List[Digest],
             Always contains a list, even if only one digest was
             generated.
         }
    """
    return commands.GetDigestsCommand(self.adapter)(
      seed  = self.seed,
      index = index,
      count = count,
    )

  def get_private_keys(self, index=0, count=1):
    # type: (int, int) -> dict
    """
    Generates one or more private keys from the seed.

    As the name implies, private keys should not be shared.  However,
    in a few cases it may be necessary (e.g., for M-of-N transactions).

    :param index:
      The starting key index.

    :param count:
      Number of keys to generate.

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
      seed  = self.seed,
      index = index,
      count = count,
    )
