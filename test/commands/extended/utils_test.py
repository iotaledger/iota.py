# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

from iota.commands.extended.utils import iter_used_addresses

from iota import MockAdapter
from iota.crypto.types import Seed
from test import mock


class IterUsedAddressesTestCase(TestCase):
    def setUp(self):
        super(IterUsedAddressesTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.seed = Seed(trytes='S' * 81)
        self.address0 = 'A' * 81
        self.address1 = 'B' * 81
        self.address2 = 'C' * 81
        self.address3 = 'D' * 81

        # To speed up the tests, we will mock the address generator.
        def address_generator(ag, start, step=1):
            for addy in [self.address0, self.address1, self.address2,
                         self.address3][start::step]:
                yield addy
        self.mock_address_generator = address_generator

    def seed_unused_address(self):
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [False],
        })

    def get_all_used_addresses(self, start=0):
        return [address for address, _
                in iter_used_addresses(self.adapter, self.seed, start)]

    def test_fist_address_is_not_used(self):
        """
        The very fist address is not used. No address is returned.
        """
        # Address 0
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([], self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
            ]
        )

    def test_transactions_are_considered_used(self):
        """
        An address with a transaction is considered used.
        """
        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 1
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0], self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address1],
                },
            ]
        )

    def test_spent_from_is_considered_used(self):
        """
        An address that was spent from is considered used.
        """
        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [True],
        })

        # Address 1
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0], self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address1],
                },
            ]
        )

    def test_start_parameter_is_given(self):
        """
        The correct address is returned if a start parameter is given
        """
        # Address 1
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 2
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address1],
                             self.get_all_used_addresses(start=1))

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address2],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address2],
                },
            ]
        )

    def test_multiple_addresses_return(self):
        """
        A larger test that combines multiple cases and more than one address
        should be returned.
        Address 0: Was spent from
        Address 1: Has a transaction
        Address 2: Is not used. Should not be returned
        """

        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [True],
        })

        # Address 1
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 2
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0, self.address1],
                             self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address2],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address2],
                },
            ]
        )
