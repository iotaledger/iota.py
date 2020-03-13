from typing import List, MutableSequence, Optional, Sequence

from iota.exceptions import with_context

__all__ = [
    'Curl',
    'HASH_LENGTH',
]

HASH_LENGTH = 243
"""
Number of trits in a hash.

Note: These constants are usually expressed in _trytes_ in PyOTA, but
for compatibility with other libraries, this value must be _trits_.
"""

STATE_LENGTH = 3 * HASH_LENGTH
"""
Number of trits that a Curl sponge stores internally.
"""

NUMBER_OF_ROUNDS = 81
"""
Number of iterations to perform per transform operation.

References:
  - :py:meth:`Curl._transform`.
"""

TRUTH_TABLE = [1, 0, -1, 1, -1, 0, -1, 1, 0]
"""
Lookup table, used to ensure that the result of a Curl operation is
deterministic but not reversible.

References:
  - :py:meth:`Curl._transform`.
"""


class Curl(object):
    """
    Python implementation of Curl.

    **IMPORTANT: Not thread-safe!**
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """
        Resets internal state.
        """
        self._state: List[int] = [0] * STATE_LENGTH

    def absorb(
            self,
            trits: Sequence[int],
            offset: Optional[int] = 0,
            length: Optional[int] = None
    ) -> None:
        """
        Absorb trits into the sponge.

        :param trits:
            Sequence of trits to absorb.

        :param offset:
            Starting offset in ``trits``.

        :param length:
            Number of trits to absorb.  Defaults to ``len(trits)``.
        """
        pad = ((len(trits) % HASH_LENGTH) or HASH_LENGTH)
        trits += [0] * (HASH_LENGTH - pad)

        if length is None:
            length = len(trits)

        if length < 1:
            raise with_context(
                exc=ValueError('Invalid length passed to ``absorb``.'),

                context={
                    'trits': trits,
                    'offset': offset,
                    'length': length,
                },
            )

        # Copy trits from ``trits`` into internal state, one hash at a
        # time, transforming internal state in between hashes.
        while offset < length:
            start = offset
            stop = min(start + HASH_LENGTH, length)

            # Copy the next hash worth of trits to internal state.
            #
            # Note that we always copy the trits to the start of the
            # state. ``self._state`` is 3 hashes long, but only the
            # first hash is "public"; the other 2 are only accessible to
            # :py:meth:`_transform`.
            self._state[0:stop - start] = trits[start:stop]

            # Transform.
            self._transform()

            # Move on to the next hash.
            offset += HASH_LENGTH

    def squeeze(
            self,
            trits: MutableSequence[int],
            offset: Optional[int] = 0,
            length: Optional[int] = HASH_LENGTH
    ) -> None:
        """
        Squeeze trits from the sponge.

        :param trits:
            Sequence that the squeezed trits will be copied to.
            Note: this object will be modified!

        :param offset:
            Starting offset in ``trits``.

        :param length:
            Number of trits to squeeze, default to ``HASH_LENGTH``
        """
        # Squeeze is kind of like the opposite of absorb; it copies
        # trits from internal state to the ``trits`` parameter, one hash
        # at a time, and transforming internal state in between hashes.
        #
        # However, only the first hash of the state is "public", so we
        # can simplify the implementation somewhat.

        # Ensure length can be mod by HASH_LENGTH
        if length % HASH_LENGTH != 0:
            raise with_context(
                exc=ValueError('Invalid length passed to ``squeeze`.'),

                context={
                    'trits': trits,
                    'offset': offset,
                    'length': length,
                })

        # Ensure that ``trits`` can hold at least one hash worth of
        # trits.
        trits.extend([0] * max(0, length - len(trits)))

        # Check trits with offset can handle hash length
        if len(trits) - offset < HASH_LENGTH:
            raise with_context(
                exc=ValueError('Invalid offset passed to ``squeeze``.'),

                context={
                    'trits': trits,
                    'offset': offset,
                    'length': length
                },
            )

        while length >= HASH_LENGTH:
            # Copy exactly one hash.
            trits[offset:offset + HASH_LENGTH] = self._state[0:HASH_LENGTH]

            # One hash worth of trits copied; now transform.
            self._transform()

            offset += HASH_LENGTH
            length -= HASH_LENGTH

    def _transform(self) -> None:
        """
        Transforms internal state.
        """
        # Copy some values locally so we can avoid global lookups in the
        # inner loop.
        #
        # References:
        #
        # - https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Local_Variables
        state_length = STATE_LENGTH
        truth_table = TRUTH_TABLE

        # Operate on a copy of ``self._state`` to eliminate dot lookups
        # in the inner loop.
        #
        # References:
        #
        # - https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Avoiding_dots...
        # - http://stackoverflow.com/a/2612990/
        prev_state = self._state[:]
        new_state = prev_state[:]

        # Note: This code looks significantly different from the C
        # implementation because it has been optimized to limit the
        # number of list item lookups (these are relatively slow in
        # Python).
        index = 0
        for _ in range(NUMBER_OF_ROUNDS):
            prev_trit = prev_state[index]

            for pos in range(state_length):
                index += (364 if index < 365 else -365)

                new_trit = prev_state[index]

                new_state[pos] = truth_table[prev_trit + (3 * new_trit) + 4]

                prev_trit = new_trit

            prev_state = new_state
            new_state = new_state[:]

        self._state = new_state
