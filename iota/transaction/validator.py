from typing import Generator, List, Optional, Type

from iota.crypto.kerl import Kerl
from iota.crypto.signing import validate_signature_fragments
from iota.transaction.base import Bundle, Transaction

__all__ = [
    'BundleValidator',
]

# In very rare cases, the IOTA protocol may switch hash algorithms.
# When this happens, the IOTA Foundation will create a snapshot, so
# that all new objects on the Tangle use the new hash algorithm.
#
# However, the snapshot will still contain references to addresses
# created using the legacy hash algorithm, so the bundle validator has
# to be able to use that as a fallback when validation fails.
SUPPORTED_SPONGE = Kerl
LEGACY_SPONGE = None  # Curl


class BundleValidator(object):
    """
    Checks a bundle and its transactions for problems.
    """

    def __init__(self, bundle: Bundle) -> None:
        super(BundleValidator, self).__init__()

        self.bundle = bundle

        self._errors: Optional[List[str]] = []
        self._validator = self._create_validator()

    @property
    def errors(self) -> List[str]:
        """
        Returns all errors found with the bundle.
        """
        try:
            self._errors.extend(self._validator)  # type: List[str]
        except StopIteration:
            pass

        return self._errors

    def is_valid(self) -> bool:
        """
        Returns whether the bundle is valid.
        """
        if not self._errors:
            try:
                # We only have to check for a single error to determine
                # if the bundle is valid or not.
                self._errors.append(next(self._validator))
            except StopIteration:
                pass

        return not self._errors

    def _create_validator(self) -> Generator[str, None, None]:
        """
        Creates a generator that does all the work.
        """
        # Group transactions by address to make it easier to iterate
        # over inputs.
        grouped_transactions = self.bundle.group_transactions()

        # Define a few expected values.
        bundle_hash = self.bundle.hash
        last_index = len(self.bundle) - 1

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
                        i=counter,
                    )

                if txn.current_index != counter:
                    yield (
                        'Transaction {i} has invalid current index value '
                        '(expected {i}, actual {actual}).'.format(
                            actual=txn.current_index,
                            i=counter,
                        )
                    )

                if txn.last_index != last_index:
                    yield (
                        'Transaction {i} has invalid last index value '
                        '(expected {expected}, actual {actual}).'.format(
                            actual=txn.last_index,
                            expected=last_index,
                            i=counter,
                        )
                    )

                counter += 1

        # Bundle must be balanced (spends must match inputs).
        if balance != 0:
            yield (
                'Bundle has invalid balance '
                '(expected 0, actual {actual}).'.format(
                    actual=balance,
                )
            )

        # Signature validation is only meaningful if the transactions
        # are otherwise valid.
        if not self._errors:
            signature_validation_queue: List[List[Transaction]] = []

            for group in grouped_transactions:
                # Signature validation only applies to inputs.
                if group[0].value >= 0:
                    continue

                validate_group_signature = True
                for j, txn in enumerate(group):
                    if (j > 0) and (txn.value != 0):
                        # Input is malformed; signature fragments after
                        # the first should have zero value.
                        yield (
                            'Transaction {i} has invalid value '
                            '(expected 0, actual {actual}).'.format(
                                actual=txn.value,

                                # If we get to this point, we know that
                                # the ``current_index`` value for each
                                # transaction can be trusted.
                                i=txn.current_index,
                            )
                        )

                        # We won't be able to validate the signature,
                        # but continue anyway, so that we can check that
                        # the other transactions in the group have the
                        # correct ``value``.
                        validate_group_signature = False
                        continue

                # After collecting the signature fragment from each
                # transaction in the group, queue them up to run through
                # the validator.
                #
                # We have to perform signature validation separately so
                # that we can try different algorithms (for
                # backwards-compatibility).
                #
                # References:
                #
                # - https://github.com/iotaledger/kerl#kerl-integration-in-iota
                if validate_group_signature:
                    signature_validation_queue.append(group)

            # Once we've finished checking the attributes from each
            # transaction in the bundle, go back and validate
            # signatures.
            if signature_validation_queue:
                # ``yield from`` is an option here, but for
                # compatibility with Python 2 clients, we will do it the
                # old-fashioned way.
                for error in self._get_bundle_signature_errors(
                        signature_validation_queue
                ):
                    yield error

    def _get_bundle_signature_errors(
            self,
            groups: List[List[Transaction]]
    ) -> List[str]:
        """
        Validates the signature fragments in the bundle.

        :return:
            List of error messages.
            If empty, signature fragments are valid.
        """
        # Start with the currently-supported hash algo.
        current_pos = None
        current_errors = []
        for current_pos, group in enumerate(groups):
            error = self._get_group_signature_error(group, SUPPORTED_SPONGE)
            if error:
                current_errors.append(error)

                # Pause and retry with the legacy algo.
                break

        # If validation failed, then go back and try with the legacy
        # algo (only applies if we are currently transitioning to a new
        # algo).
        if current_errors and LEGACY_SPONGE:
            for group in groups:
                if self._get_group_signature_error(group, LEGACY_SPONGE):
                    # Legacy algo doesn't work, either; no point in
                    # continuing.
                    break
            else:
                # If we get here, then we were able to validate the
                # signature fragments successfully using the legacy
                # algorithm.
                return []

        # If we get here, then validation also failed when using the
        # legacy algorithm.

        # At this point, we know that the bundle is invalid, but we will
        # continue validating with the supported algorithm anyway, so
        # that we can return an error message for every invalid input.
        current_errors.extend(filter(None, (
            self._get_group_signature_error(group, SUPPORTED_SPONGE)
            for group in groups[current_pos + 1:]
        )))

        return current_errors

    @staticmethod
    def _get_group_signature_error(
            group: List[Transaction],
            sponge_type: Type
    ) -> Optional[str]:
        """
        Validates the signature fragments for a group of transactions
        using the specified sponge type.

        Note: this method assumes that the transactions in the group
        have already passed basic validation (see
        :py:meth:`_create_validator`).

        :return:
          - ``None``:  Indicates that the signature fragments are valid.
          - ``str``:  Error message indicating the fragments are invalid.
        """
        validate_group_signature = validate_signature_fragments(
            fragments=[txn.signature_message_fragment for txn in group],
            hash_=group[0].bundle_hash,
            public_key=group[0].address,
            sponge_type=sponge_type,
        )

        if validate_group_signature:
            return None

        return (
            'Transaction {i} has invalid signature '
            '(using {fragments} fragments).'.format(
                fragments=len(group),
                i=group[0].current_index,
            )
        )
