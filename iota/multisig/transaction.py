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

    if not inputs or len(inputs) != 1:
      raise ValueError(
        '{cls} requires input MultisigAddresses and currently only supports 1'
        ' input.'
        .format(cls=type(self).__name__),
      )

    # Validate all addresses
    for address in inputs:
      exc = None
      security_level = address.security_level
      exception_context = {'actual_input': address}

      if not isinstance(address, MultisigAddress):
        exc = TypeError(
          'Incorrect input type for {cls} '
          '(expected {expected}, actual {actual}).'.format(
            actual    = type(address).__name__,
            cls       = type(self).__name__,
            expected  = MultisigAddress.__name__,
          ),
        )
      elif security_level < 1:
        exception_context['security_level'] = security_level
        exc = ValueError(
          'Unable to determine security level for {type} '
          '(is ``digests`` populated correctly?).'.format(
            type = type(address).__name__,
          ),
        )
      elif not address.balance:
        exc = ValueError(
          'Cannot add input with empty/unknown balance to {type} '
          '(use ``Iota.get_balances`` to get balance first).'.format(
            type = type(self).__name__,
          ),
        )

      if exc is not None:
        raise with_context(exc=exc, context=exception_context)

    map(self._create_input_transactions, inputs)
