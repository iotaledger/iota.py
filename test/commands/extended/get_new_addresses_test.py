# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Address, Iota
from iota.adapter import MockAdapter
from iota.commands.extended.get_new_addresses import GetNewAddressesCommand
from iota.crypto.types import Seed
from iota.filters import Trytes
from mock import patch
from six import binary_type, text_type


class GetNewAddressesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetNewAddressesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetNewAddressesRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = b'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':   Seed(self.seed),
      'index':  1,
      'count':  1,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_optional_parameters_excluded(self):
    """
    Request omits ``index`` and ``count``.
    """
    filter_ = self._filter({
      'seed':   Seed(self.seed),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':   Seed(self.seed),
        'index':  0,
        'count':  None,
      },
    )

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      # ``seed`` can be any value that is convertible to TryteString.
      'seed': binary_type(self.seed),

      # These values must be integers, however.
      'index': 100,
      'count': 8,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':   Seed(self.seed),
        'index':  100,
        'count':  8,
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'seed': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'seed':   Seed(self.seed),
        'index':  None,
        'count':  1,

        # Some men just want to watch the world burn.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_seed_null(self):
    """
    ``seed`` is null.
    """
    self.assertFilterErrors(
      {
        'seed': None,
      },

      {
        'seed': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_seed_wrong_type(self):
    """
    ``seed`` cannot be converted into a TryteString.
    """
    self.assertFilterErrors(
      {
        'seed': text_type(self.seed, 'ascii'),
      },

      {
        'seed': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_seed_malformed(self):
    """
    ``seed`` has the correct type, but it contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'seed': b'not valid; seeds can only contain uppercase and "9".',
      },

      {
        'seed': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_count_string(self):
    """
    ``count`` is a string value.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'count': '42',

        'seed': Seed(self.seed),
      },

      {
        'count': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_count_float(self):
    """
    ``count`` is a float value.
    """
    self.assertFilterErrors(
      {
        # Not valid, even with an empty fpart; it must be an int.
        'count': 42.0,

        'seed': Seed(self.seed),
      },

      {
        'count': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_count_too_small(self):
    """
    ``count`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'count':  0,
        'seed':   Seed(self.seed),
      },

      {
        'count': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_index_string(self):
    """
    ``index`` is a string value.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'index': '42',

        'seed': Seed(self.seed),
      },

      {
        'index': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_index_float(self):
    """
    ``index`` is a float value.
    """
    self.assertFilterErrors(
      {
        # Not valid, even with an empty fpart; it must be an int.
        'index': 42.0,

        'seed': Seed(self.seed),
      },

      {
        'index': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_index_too_small(self):
    """
    ``index`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'index':  -1,
        'seed':   Seed(self.seed),
      },

      {
        'index': [f.Min.CODE_TOO_SMALL],
      },
    )


# noinspection SpellCheckingInspection
class GetNewAddressesCommandTestCase(TestCase):
  def setUp(self):
    super(GetNewAddressesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetNewAddressesCommand(self.adapter)

    # Create a few TryteStrings we can reuse across tests.
    self.addy1 =\
      Address(
        b'ADDYONE999AHHKVD9SBEYWQFNVQSNTGYQSQ9AGWD'
        b'JDZKBYCVTODUHFEVVMNMPQMIXOVXVCZRUENAWYNTO'
      )

    self.addy2 =\
      Address(
        b'ADDYTWO999AGAQKYXHRMSFAQNPWCIYUYTXPWUEUR'
        b'VNZTCTFUPQ9ESTKNSSLLIZWDQISJVEWIJDVGIECXF'
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getNewAddresses,
      GetNewAddressesCommand,
    )

  def test_get_addresses_offline(self):
    """
    Generate addresses in offline mode (without filtering used
    addresses).
    """
    # To speed up the test, we will mock the address generator.
    # :py:class:`iota.crypto.addresses.AddressGenerator` already has
    # its own test case, so this does not impact the stability of the
    # codebase.
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      for addy in [self.addy1, self.addy2][start::step]:
        yield addy

    with patch(
        target  = 'iota.crypto.addresses.AddressGenerator.create_iterator',
        new     = create_generator,
    ):
      response = self.command(
        count = 2,
        index = 0,
        seed  = b'TESTSEED9DONTUSEINPRODUCTION99999',
      )

    self.assertDictEqual(response, {'addresses': [self.addy1, self.addy2]})

    # No API requests were made.
    self.assertListEqual(self.adapter.requests, [])

  def test_get_addresses_online(self):
    """
    Generate address in online mode (filtering used addresses).
    """
    # Pretend that ``self.addy1`` has already been used, but not
    # ``self.addy2``.
    self.adapter.seed_response('findTransactions', {
      'duration': 18,

      'hashes': [
        'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
        'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'duration': 1,
      'hashes':   [],
    })

    # To speed up the test, we will mock the address generator.
    # :py:class:`iota.crypto.addresses.AddressGenerator` already has
    # its own test case, so this does not impact the stability of the
    # codebase.
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      for addy in [self.addy1, self.addy2][start::step]:
        yield addy

    with patch(
        target  = 'iota.crypto.addresses.AddressGenerator.create_iterator',
        new     = create_generator,
    ):
      response = self.command(
        # If ``count`` is missing or ``None``, the command will operate
        # in online mode.
        # count = None,
        index = 0,
        seed  = b'TESTSEED9DONTUSEINPRODUCTION99999',
      )

    # The command determined that ``self.addy1`` was already used, so
    # it skipped that one.
    self.assertDictEqual(response, {'addresses': [self.addy2]})

    self.assertListEqual(
      self.adapter.requests,

      # The command issued two `findTransactions` API requests: one for
      # each address generated, until it found an unused address.
      [
        {
          'command':    'findTransactions',
          'addresses':  [self.addy1],
          'approvees':  [],
          'bundles':    [],
          'tags':       [],
        },

        {
          'command':    'findTransactions',
          'addresses':  [self.addy2],
          'approvees':  [],
          'bundles':    [],
          'tags':       [],
        },
      ],
    )
