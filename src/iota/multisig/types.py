# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from operator import attrgetter
from typing import Iterable, Optional

from iota import Address, TrytesCompatible
from iota.crypto.types import Digest

__all__ = [
  'MultisigAddress',
]


class MultisigAddress(Address):
  """
  An address that was generated using digests from multiple private
  keys.

  In order to spend inputs from a multisig address, the same private
  keys must be used, in the same order that the corresponding digests
  were used to generate the address.
  """
  def __init__(self, trytes, digests, balance=None):
    # type: (TrytesCompatible, Iterable[Digest], Optional[int]) -> None
    # Key index is meaningless for multisig addresses.
    super(MultisigAddress, self).__init__(trytes, balance, key_index=None)

    self.digests = digests

    self.security_level = sum(map(attrgetter('security_level'), self.digests))

  def as_json_compatible(self):
    # type: () -> dict
    return {
      'trytes':   self._trytes.decode('ascii'),
      'balance':  self.balance,
      'digests':  self.digests,
    }
