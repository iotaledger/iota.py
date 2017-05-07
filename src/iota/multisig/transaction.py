# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable

from iota import ProposedBundle
from iota.exceptions import with_context
from iota.multisig.types import MultisigAddress

__all__ = [
  'ProposedMultisigBundle',
]

class ProposedMultisigBundle(ProposedBundle):
  """
  A collection of proposed transactions, with multisig inputs.

  Note: at this time, only a single multisig input is supported per
  bundle.
  """
  def add_inputs(self, inputs):
    # type: (Iterable[MultisigAddress]) -> None
    """
    Adds inputs to spend in the bundle.

    Note that each input may require multiple transactions, in order to
    hold the entire signature.

    :param inputs:
      MultisigAddresses to use as the inputs for this bundle.

      Note: at this time, only a single multisig input is supported.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    count = 0
    for addy in inputs:
      if count > 0:
        raise ValueError(
          '{cls} only supports 1 input.'.format(cls=type(self).__name__),
        )

      if not isinstance(addy, MultisigAddress):
        raise with_context(
          exc =
            TypeError(
              'Incorrect input type for {cls} '
              '(expected {expected}, actual {actual}).'.format(
                actual    = type(addy).__name__,
                cls       = type(self).__name__,
                expected  = MultisigAddress.__name__,
              ),
            ),

          context = {
            'actual_input': addy,
          },
        )

      security_level = addy.security_level
      if security_level < 1:
        raise with_context(
          exc =
            ValueError(
              'Unable to determine security level for {type} '
              '(is ``digests`` populated correctly?).'.format(
                type = type(addy).__name__,
              ),
            ),

          context = {
            'actual_input':   addy,
            'security_level': security_level,
          },
        )

      if not addy.balance:
        raise with_context(
          exc =
            ValueError(
              'Cannot add input with empty/unknown balance to {type} '
              '(use ``Iota.get_balances`` to get balance first).'.format(
                type = type(self).__name__,
              ),
            ),

          context = {
            'actual_input': addy,
          },
        )

      self._create_input_transactions(addy)

      count += 1
