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

  .. note::
    Usually you don't have to construct :py:class:`ProposedMultisigBundle`
    bundle manually, :py:meth:`~iota.multisig.MultisigIota.prepare_multisig_transfer`
    does it for you.

  :param  Optional[Iterable[ProposedTransaction]] transactions:
    Proposed transactions that should be put into the proposed bundle.

  :param Optional[Iterable[Address]] inputs:
    Addresses that hold iotas to fund outgoing transactions in the bundle.
    Currently PyOTA supports only one mutlisig input address per bundle.

  :param Optional[Address] change_address:
    Due to the signatures scheme of IOTA, you can only spend once from an
    address. Therefore the library will always deduct the full available
    amount from an input address. The unused tokens will be sent to
    ``change_address`` if provided.

  :return: :py:class:`ProposedMultisigBundle` object.
  """
  def add_inputs(self, inputs: Iterable[MultisigAddress]) -> None:
    """
    Adds inputs to spend in the bundle.

    Note that each input may require multiple transactions, in order to
    hold the entire signature.

    :param Iterable[MultisigAddress] inputs:
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
