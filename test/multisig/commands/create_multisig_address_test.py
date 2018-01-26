# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import TryteString
from iota.adapter import MockAdapter
from iota.crypto.types import Digest
from iota.filters import Trytes
from iota.multisig import MultisigIota
from iota.multisig.commands import CreateMultisigAddressCommand
from iota.multisig.types import MultisigAddress


class CreateMultisigAddressCommandTestCase(TestCase):
    # noinspection SpellCheckingInspection
    def setUp(self):
        super(CreateMultisigAddressCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = CreateMultisigAddressCommand(self.adapter)

        # Define some tryte sequences that we can reuse between tests.
        self.digest_1 = \
            Digest(
                trytes=b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
                b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
                b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAY',

                key_index=0,
            )

        self.digest_2 = \
            Digest(
                trytes=b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
                b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
                b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLC',

                key_index=0,
            )

    def test_wireup(self):
        """
    Verify that the command is wired up correctly.
    """
        self.assertIsInstance(
            MultisigIota(self.adapter).createMultisigAddress,
            CreateMultisigAddressCommand,
        )

    def test_happy_path(self):
        """
    Generating a multisig address.
    """
        result = self.command(digests=[self.digest_1, self.digest_2])

        # noinspection SpellCheckingInspection
        self.assertDictEqual(
            result,

            {
                'address':
                    MultisigAddress(
                        trytes=b'ZYKDKGXTMGINTQLUMVNBBI9XCEI9BWYF9YOPCBFT'
                        b'UUJZWM9YIWHNYZEWOPEVRVLKZCPRKLCQD9BR9FVLC',

                        digests=[self.digest_1, self.digest_2],
                    ),
            },
        )


class CreateMultisigAddressRequestFilterTestCase(BaseFilterTestCase):
    filter_type = CreateMultisigAddressCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    # noinspection SpellCheckingInspection
    def setUp(self):
        super(CreateMultisigAddressRequestFilterTestCase, self).setUp()

        # Define some tryte sequences that we can reuse between tests.
        self.digest_1 = \
            Digest(
                trytes=b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
                b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
                b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAY',

                key_index=0,
            )

        self.digest_2 = \
            Digest(
                trytes=b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
                b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
                b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLC',

                key_index=0,
            )

    def test_pass_happy_path(self):
        """
    Request is valid.
    """
        request = {
            'digests': [self.digest_1, self.digest_2],
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_pass_compatible_types(self):
        """
    Request contains values that can be converted to the expected
    types.
    """
        filter_ = self._filter({
            # ``digests`` may contain any values that can be converted into
            # :py:class:`Digest` objects.
            'digests': [binary_type(self.digest_1), TryteString(self.digest_2)],
        })

        self.assertFilterPasses(filter_)

        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'digests': [self.digest_1, self.digest_2],
            },
        )

    def test_fail_empty(self):
        """
    Request is empty.
    """
        self.assertFilterErrors(
            {},

            {
                'digests': [f.FilterMapper.CODE_MISSING_KEY],
            },
        )

    def test_fail_unexpected_parameters(self):
        """
    Request contains unexpected parameters.
    """
        self.assertFilterErrors(
            {
                'digests': [self.digest_1, self.digest_2],

                # Oh, and I suppose that's completely inconspicuous.
                'foo': 'bar',
            },

            {
                'foo': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )

    def test_fail_digests_null(self):
        """
    ``digests`` is null.
    """
        self.assertFilterErrors(
            {
                'digests': None,
            },

            {
                'digests': [f.Required.CODE_EMPTY],
            },
        )

    def test_fail_digests_wrong_type(self):
        """
    ``digests`` is not an array.
    """
        self.assertFilterErrors(
            {
                'digests': self.digest_1,
            },

            {
                'digests': [f.Array.CODE_WRONG_TYPE],
            },
        )

    def test_fail_digests_empty(self):
        """
    ``digests`` is an array, but it's empty.
    """
        self.assertFilterErrors(
            {
                'digests': [],
            },

            {
                'digests': [f.Required.CODE_EMPTY],
            },
        )

    def test_fail_digests_contents_invalid(self):
        """
    ``digests`` is an array, but it contains invalid values.
    """
        self.assertFilterErrors(
            {
                'digests': [
                    b'',
                    True,
                    None,
                    b'not valid trytes',

                    # This is actually valid; I just added it to make sure the
                    # filter isn't cheating!
                    TryteString(self.digest_1),

                    2130706433,
                ],
            },

            {
                'digests.0': [f.Required.CODE_EMPTY],
                'digests.1': [f.Type.CODE_WRONG_TYPE],
                'digests.2': [f.Required.CODE_EMPTY],
                'digests.3': [Trytes.CODE_NOT_TRYTES],
                'digests.5': [f.Type.CODE_WRONG_TYPE],
            },
        )
