# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota
from iota.adapter import MockAdapter
from iota.commands.extended.get_inputs import GetInputsCommand, \
  GetInputsRequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes
from six import binary_type, text_type


class GetInputsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetInputsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetInputsRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = b'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':       Seed(self.seed),
      'start':      0,
      'end':        10,
      'threshold':  100,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    The request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      # ``seed`` can be any value that is convertible into a
      # TryteString.
      'seed': binary_type(self.seed),

      # These values must still be integers, however.
      'start':      42,
      'end':        86,
      'threshold':  99,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':       Seed(self.seed),
        'start':      42,
        'end':        86,
        'threshold':  99,
      },
    )

  def test_pass_optional_parameters_excluded(self):
    """
    The request contains only required parameters.
    """
    filter_ = self._filter({
      'seed': Seed(self.seed),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':       Seed(self.seed),
        'start':      0,
        'end':        None,
        'threshold':  None,
      }
    )

  def test_fail_empty_request(self):
    """
    The request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'seed': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'seed': Seed(self.seed),

        # Told you I did. Reckless is he. Now, matters are worse.
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

  def test_fail_start_string(self):
    """
    ``start`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'start': '0',

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_start_float(self):
    """
    ``start`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'start': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_start_too_small(self):
    """
    ``start`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'start': -1,

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_end_string(self):
    """
    ``end`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'end': '0',

        'seed': Seed(self.seed),
      },

      {
        'end': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_end_float(self):
    """
    ``end`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'end': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'end': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_end_too_small(self):
    """
    ``end`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'end': -1,

        'seed': Seed(self.seed),
      },

      {
        'end': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_end_occurs_before_start(self):
    """
    ``end`` is less than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  1,
        'end':    0,

        'seed': Seed(self.seed),
      },

      {
        'start': [GetInputsRequestFilter.CODE_INTERVAL_INVALID],
      },
    )

  def test_fail_interval_too_large(self):
    """
    ``end`` is way more than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  0,
        'end':    GetInputsRequestFilter.MAX_INTERVAL + 1,

        'seed': Seed(self.seed),
      },

      {
        'end':  [GetInputsRequestFilter.CODE_INTERVAL_TOO_BIG],
      },
    )

  def test_fail_threshold_string(self):
    """
    ``threshold`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'threshold': '0',

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_threshold_float(self):
    """
    ``threshold`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'threshold': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_threshold_too_small(self):
    """
    ``threshold`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'threshold': -1,

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Min.CODE_TOO_SMALL],
      },
    )


class GetInputsCommandTestCase(TestCase):
  def setUp(self):
    super(GetInputsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetInputsCommand(self.adapter)

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getInputs,
      GetInputsCommand,
    )

  def test_start_and_end_with_threshold(self):
    """
    ``start`` and ``end`` values provided, with ``threshold``.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_start_and_end_no_threshold(self):
    """
    ``start`` and ``end`` values provided, no ``threshold``.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_no_end_with_threshold(self):
    """
    No ``end`` value provided, with ``threshold``.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_no_end_no_threshold(self):
    """
    No ``end`` value provided, no ``threshold``.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
