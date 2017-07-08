# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import Hash, TryteString
from iota.adapter import MockAdapter
from iota.crypto import FRAGMENT_LENGTH
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Digest, PrivateKey, Seed
from iota.filters import Trytes
from iota.multisig import MultisigIota
from iota.multisig.commands import GetDigestsCommand
from test import mock


class GetDigestsCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetDigestsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetDigestsCommand(self.adapter)

    # Define some tryte sequences that we can reuse between tests.
    self.key1 = PrivateKey(TryteString(b'KEYONE', pad=FRAGMENT_LENGTH), 0)
    self.key2 = PrivateKey(TryteString(b'KEYTWO', pad=FRAGMENT_LENGTH), 1)

    self.digest1 = Digest(TryteString(b'DIGESTONE', pad=Hash.LEN), 0)
    self.digest2 = Digest(TryteString(b'DIGESTTWO', pad=Hash.LEN), 1)

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      MultisigIota(self.adapter).getDigests,
      GetDigestsCommand,
    )

  def test_generate_single_digest(self):
    """
    Generating a single digest.
    """
    seed = Seed.random()

    mock_get_private_keys = mock.Mock(return_value={'keys': [self.key1]})

    with mock.patch(
        'iota.multisig.commands.get_private_keys.GetPrivateKeysCommand._execute',
        mock_get_private_keys
    ):
      # noinspection PyUnresolvedReferences
      with mock.patch.object(self.key1, 'get_digest') as mock_get_digest_1: # type: mock.MagicMock
        mock_get_digest_1.return_value = self.digest1

        result = self.command(seed=seed, index=0, count=1, securityLevel=1)

    self.assertDictEqual(result, {'digests': [self.digest1]})

    mock_get_private_keys.assert_called_once_with({
      'count':          1,
      'index':          0,
      'securityLevel':  1,
      'seed':           seed,
    })

  def test_generate_multiple_digests(self):
    """
    Generating multiple digests.
    """
    seed = Seed.random()

    mock_get_private_keys =\
      mock.Mock(return_value={'keys': [self.key1, self.key2]})

    with mock.patch(
        'iota.multisig.commands.get_private_keys.GetPrivateKeysCommand._execute',
        mock_get_private_keys
    ):
      # noinspection PyUnresolvedReferences
      with mock.patch.object(self.key1, 'get_digest') as mock_get_digest_1: # type: mock.MagicMock
        mock_get_digest_1.return_value = self.digest1

        # noinspection PyUnresolvedReferences
        with mock.patch.object(self.key2, 'get_digest') as mock_get_digest_2: # type: mock.MagicMock
          mock_get_digest_2.return_value = self.digest2

          result = self.command(seed=seed, index=0, count=2, securityLevel=1)

    self.assertDictEqual(result, {'digests': [self.digest1, self.digest2]})

    mock_get_private_keys.assert_called_once_with({
      'count':          2,
      'index':          0,
      'securityLevel':  1,
      'seed':           seed,
    })


class GetDigestsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetDigestsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetDigestsRequestFilterTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    # noinspection SpellCheckingInspection
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
        'seed':           Seed(self.seed),
        'index':          None,
        'count':          1,
        'securityLevel':  1,

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
