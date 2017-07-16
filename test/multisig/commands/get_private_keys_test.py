# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import TryteString
from iota.adapter import MockAdapter
from iota.crypto import FRAGMENT_LENGTH
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import PrivateKey, Seed
from iota.filters import Trytes
from iota.multisig import MultisigIota
from iota.multisig.commands import GetPrivateKeysCommand
from test import mock


class GetPrivateKeysCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetPrivateKeysCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetPrivateKeysCommand(self.adapter)

    #
    # Create a few tryte sequences we can reuse across tests.
    #
    # Note that these are not realistic values for private keys (a real
    # private key's length is a multiple of 2187 trytes), but we're
    # going to mock the KeyGenerator functionality anyway, so we just
    # need something that's short enough to be easy to compare.
    #
    self.trytes1 = TryteString(b'KEYONE', pad=FRAGMENT_LENGTH)
    self.trytes2 = TryteString(b'KEYTWO', pad=FRAGMENT_LENGTH)

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      MultisigIota(self.adapter).getPrivateKeys,
      GetPrivateKeysCommand,
    )

  def test_generate_single_key(self):
    """
    Generating a single key.
    """
    keys = [PrivateKey(self.trytes1, 0)]

    mock_get_keys = mock.Mock(return_value=keys)
    with mock.patch('iota.crypto.signing.KeyGenerator.get_keys', mock_get_keys):
      result = self.command(seed=Seed.random(), securityLevel=2)

    self.assertDictEqual(result, {'keys': keys})
    mock_get_keys.assert_called_once_with(
      count       = 1,
      iterations  = 2,
      start       = 0,
    )

  def test_generate_multiple_keys(self):
    """
    Generating multiple keys.
    """
    keys = [PrivateKey(self.trytes1, 0), PrivateKey(self.trytes2, 1)]

    mock_get_keys = mock.Mock(return_value=keys)
    with mock.patch('iota.crypto.signing.KeyGenerator.get_keys', mock_get_keys):
      result =\
        self.command(
          count         = 2,
          index         = 0,
          securityLevel = 1,
          seed          = Seed.random(),
        )

    self.assertDictEqual(result, {'keys': keys})
    mock_get_keys.assert_called_once_with(
      count       = 2,
      iterations  = 1,
      start       = 0,
    )


class GetPrivateKeysRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetPrivateKeysCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetPrivateKeysRequestFilterTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    self.seed = b'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':           Seed(self.seed),
      'index':          1,
      'count':          1,
      'securityLevel':  1,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_optional_parameters_excluded(self):
    """
    Request omits optional parameters.
    """
    filter_ = self._filter({
      'seed': Seed(self.seed),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':           Seed(self.seed),
        'index':          0,
        'count':          1,
        'securityLevel':  AddressGenerator.DEFAULT_SECURITY_LEVEL,
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
      'index':          100,
      'count':          8,
      'securityLevel':  1,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':           Seed(self.seed),
        'index':          100,
        'count':          8,
        'securityLevel':  1,
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
        'seed': 42,
      },

      {
        'seed': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_seed_malformed(self):
    """
    ``seed`` has an allowed type, but it contains invalid characters.
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

  def test_fail_securityLevel_string(self):
    """
    ``securityLevel`` is a string value.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  '1',
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_securityLevel_float(self):
    """
    ``securityLevel`` is a float value.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  1.0,
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_securityLevel_too_small(self):
    """
    ``securityLevel`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  0,
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Min.CODE_TOO_SMALL],
      },
    )
