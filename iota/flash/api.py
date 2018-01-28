from typing import Iterable

from iota.commands import discover_commands
from iota.crypto.types import Digest
from iota.flash.commands.create_transaction import CreateFlashTransactionCommand
from iota.flash.commands.multisig.compose_address import ComposeAddressNodeCommand
from iota.flash.types import FlashUser
from iota.multisig import MultisigIota

__all__ = [
  'FlashIota',
]


class FlashIota(MultisigIota):
  """
  Extends the IOTA API so that it can manage Flash channels.

  **CAUTION:** Make sure you understand how Flash channel work before
  attempting to use it.  If you are not careful, you could easily
  compromise the security of your private keys, send IOTAs to
  unspendable addresses, etc.

  References:
    - https://github.com/iotaledger/iota.flash.js
  """

  commands = discover_commands('iota.flash.commands')

  def compose_flash_address(self, digests):
    # type: (Iterable[Digest]) -> dict
    """
    Composes a multisig address for Flash channels from a collection of digests.

    :param digests:
      Digests to use to create the multisig address.

      IMPORTANT: In order to spend IOTAs from a multisig address, the
      signature must be generated from the corresponding private keys
      in the exact same order.

    :return:
      Dict with the following items::

         {
           'address': dict,
             The generated multisig address object.
         }
    """
    return ComposeAddressNodeCommand(self.adapter)(
      digests = digests,
    )

  def create_flash_transaction(self, user, transactions, close=False):
    # type: (FlashUser, Iterable[dict], bool) -> Iterable[dict]
    """

    :param user: Flash object of user storing relevant metadata of the channel
    :param transactions: list of transaction, wnich should be executed
    :param close: Flag indicating a closing of the channel
    :return:
      Dict with the following items::
         {
           'bundles': List[Bundles],,
             List of generated bundles.
         }
    """
    return CreateFlashTransactionCommand(self.adapter)(
      user=user,
      transactions=transactions,
      close=close
    )




