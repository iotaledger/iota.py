# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List, Optional, Text, Tuple

from iota.crypto.signing import validate_signature_fragments
from iota.transaction.base import Bundle, Transaction

__all__ = [
  'BundleValidator',
]

class BundleValidator(object):
  """
  Checks a bundle and its transactions for problems.
  """
  def __init__(self, bundle):
    # type: (Bundle) -> None
    super(BundleValidator, self).__init__()

    self.bundle = bundle

    self._errors    = [] # type: Optional[List[Text]]
    self._validator = self._create_validator()

  @property
  def errors(self):
    # type: () -> List[Text]
    """
    Returns all errors found with the bundle.
    """
    try:
      self._errors.extend(self._validator) # type: List[Text]
    except StopIteration:
      pass

    return self._errors

  def is_valid(self):
    # type: () -> bool
    """
    Returns whether the bundle is valid.
    """
    if not self._errors:
      try:
        # We only have to check for a single error to determine if the
        # bundle is valid or not.
        self._errors.append(next(self._validator))
      except StopIteration:
        pass

    return not self._errors

  def _create_validator(self):
    # type: () -> Generator[Text]
    """
    Creates a generator that does all the work.
    """
    # Group transactions by address to make it easier to iterate over
    # inputs.
    grouped_transactions = self.bundle.group_transactions()

    # Define a few expected values.
    bundle_hash = self.bundle.hash
    last_index  = len(self.bundle) - 1

    # Track a few others as we go along.
    balance = 0

    # Check indices and balance first.
    # Note that we use a counter to keep track of the current index,
    # since at this point we can't trust that the transactions have
    # correct ``current_index`` values.
    counter = 0
    for group in grouped_transactions:
      for txn in group:
        balance += txn.value

        if txn.bundle_hash != bundle_hash:
          yield 'Transaction {i} has invalid bundle hash.'.format(
            i = counter,
          )

        if txn.current_index != counter:
          yield (
            'Transaction {i} has invalid current index value '
            '(expected {i}, actual {actual}).'.format(
              actual  = txn.current_index,
              i       = counter,
            )
          )

        if txn.last_index != last_index:
          yield (
            'Transaction {i} has invalid last index value '
            '(expected {expected}, actual {actual}).'.format(
              actual    = txn.last_index,
              expected  = last_index,
              i         = counter,
            )
          )

        counter += 1

    # Bundle must be balanced (spends must match inputs).
    if balance != 0:
      yield (
        'Bundle has invalid balance (expected 0, actual {actual}).'.format(
          actual = balance,
        )
      )

    # Signature validation is only meaningful if the transactions are
    # otherwise valid.
    if not self._errors:
      for group in grouped_transactions:
        # Signature validation only applies to inputs.
        if group[0].value >= 0:
          continue

        signature_valid = True
        signature_fragments = []
        for j, txn in enumerate(group): # type: Tuple[int, Transaction]
          if (j > 0) and (txn.value != 0):
            # Input is malformed; signature fragments after the first
            # should have zero value.
            yield (
              'Transaction {i} has invalid amount '
              '(expected 0, actual {actual}).'.format(
                actual = txn.value,

                # If we get to this point, we know that the
                # ``current_index`` value for each transaction can be
                # trusted.
                i = txn.current_index,
              )
            )

            # We won't be able to validate the signature, but continue
            # anyway, so that we can check that the other transactions
            # in the group have the correct ``value``.
            signature_valid = False
            continue

          signature_fragments.append(txn.signature_message_fragment)

        # After collecting the signature fragment from each transaction
        # in the group, run it through the validator.
        if signature_valid:
          signature_valid = validate_signature_fragments(
            fragments   = signature_fragments,
            hash_       = txn.bundle_hash,
            public_key  = txn.address,
          )

          if not signature_valid:
            yield (
              'Transaction {i} has invalid signature '
              '(using {fragments} fragments).'.format(
                fragments = len(signature_fragments),

                # If we get to this point, we know that the
                # ``current_index`` value for each transaction can be
                # trusted.
                i = group[0].current_index,
              )
            )
