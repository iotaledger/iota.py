# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota import Iota
from iota.commands import discover_commands
from iota.multisig import commands


class MultisigIota(Iota):
  """
  Extends the IOTA API so that it can send multi-signature
  transactions.

  References:
    - https://github.com/iotaledger/wiki/blob/master/multisigs.md
  """
  commands = discover_commands('iota.multisig.commands')

  def get_private_keys(self, index=0, count=1):
    # type: (int, int) -> dict
    """
    Generates one or more private keys from the seed.

    :return:
      Dict with the following items::

         {
           'keys': List[PrivateKey],
             Always contains a list, even if only one key was
             generated.
         }

    References:
      - :py:class:`iota.crypto.signing.KeyGenerator`
    """
    return commands.GetPrivateKeysCommand(self.adapter)(
      seed  = self.seed,
      index = index,
      count = count,
    )
