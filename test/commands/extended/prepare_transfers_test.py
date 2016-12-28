# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Address, Iota, ProposedTransaction, Tag, TryteString
from iota.commands.extended.prepare_transfers import PrepareTransfersCommand
from iota.crypto.types import Seed
from iota.filters import Trytes
from six import binary_type, text_type
from test import MockAdapter


class PrepareTransfersRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PrepareTransfersCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(PrepareTransfersRequestFilterTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    self.trytes1 = (
      b'TESTVALUEONE9DONTUSEINPRODUCTION99999JBW'
      b'GEC99GBXFFBCHAEJHLC9DX9EEPAI9ICVCKBX9FFII'
    )

    self.trytes2 = (
      b'TESTVALUETWO9DONTUSEINPRODUCTION99999THZ'
      b'BODYHZM99IR9KOXLZXVUOJM9LQKCQJBWMTY999999'
    )

    self.trytes3 = (
      b'TESTVALUETHREE9DONTUSEINPRODUCTIONG99999'
      b'GTQ9CSNUFPYW9MBQ9LFQJSORCF9LGTY9BWQFY9999'
    )

    self.trytes4 = (
      b'TESTVALUEFOUR9DONTUSEINPRODUCTION99999ZQ'
      b'HOGCBZCOTZVZRFBEHQKHENBIZWDTUQXTOVWEXRIK9'
    )

    self.transfer1 =\
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUEFIVE9DONTUSEINPRODUCTION99999MG'
            b'AAAHJDZ9BBG9U9R9XEOHCBVCLCWCCCCBQCQGG9WHK'
          ),

        value = 42,
      )

    self.transfer2 =\
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUESIX9DONTUSEINPRODUCTION99999GGT'
            b'FODSHHELBDERDCDRBCINDCGQEI9NAWDJBC9TGPFME'
          ),

        value = 86,
      )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'change_address': Address(self.trytes1),
      'seed':           Seed(self.trytes2),
      'transfers':      [self.transfer1, self.transfer2],

      'inputs': [
        Address(self.trytes3),
        Address(self.trytes4),
      ],

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
      # Any TrytesCompatible value works here.
      'change_address': binary_type(self.trytes1),
      'seed':           bytearray(self.trytes2),

      'inputs': [
        binary_type(self.trytes3),
        bytearray(self.trytes4),
      ],

      # These still have to have the correct type, however.
      'transfers': [self.transfer1, self.transfer2],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'change_address': Address(self.trytes1),
        'seed':           Seed(self.trytes2),
        'transfers':      [self.transfer1, self.transfer2],

        'inputs': [
          Address(self.trytes3),
          Address(self.trytes4),
        ],
      },
    )

  def test_pass_optional_parameters_omitted(self):
    """
    Request omits optional parameters.
    """
    filter_ = self._filter({
      'seed':       Seed(self.trytes1),
      'transfers':  [self.transfer1],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':       Seed(self.trytes1),
        'transfers':  [self.transfer1],

        # These parameters are set to their default values.
        'change_address': None,
        'inputs':         None,
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'seed':       [f.FilterMapper.CODE_MISSING_KEY],
        'transfers':  [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'seed': Seed(self.trytes1),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],

        # You guys give up? Or are you thirsty for more?
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

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'seed': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_seed_wrong_type(self):
    """
    ``seed`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'seed': text_type(self.trytes1, 'ascii'),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'seed': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_seed_not_trytes(self):
    """
    ``seed`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'seed': b'not valid; must contain only uppercase and "9"',

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'seed': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_transfers_wrong_type(self):
    """
    ``transfers`` is not an array.
    """
    self.assertFilterErrors(
      {
        # It's gotta be an array, even if there's only one transaction.
        'transfers':
          ProposedTransaction(address=Address(self.trytes2), value=42),

        'seed': Seed(self.trytes1),
      },

      {
        'transfers': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transfers_empty(self):
    """
    ``transfers`` is an array, but it is empty.
    """
    self.assertFilterErrors(
      {
        'transfers': [],

        'seed': Seed(self.trytes1),
      },

      {
        'transfers': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transfers_contents_invalid(self):
    """
    ``transfers`` is a non-empty array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'transfers': [
          None,

          # This value is valid; just adding it to make sure the filter
          # doesn't cheat!
          ProposedTransaction(address=Address(self.trytes2), value=42),

          {'address': Address(self.trytes2), 'value': 42},
        ],

        'seed': Seed(self.trytes1),
      },

      {
        'transfers.0': [f.Required.CODE_EMPTY],
        'transfers.2': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_change_address_wrong_type(self):
    """
    ``change_address`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'change_address': text_type(self.trytes3, 'ascii'),

        'seed': Seed(self.trytes1),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'change_address': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_change_address_not_trytes(self):
    """
    ``change_address`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'change_address': b'not valid; must contain only uppercase and "9"',

        'seed': Seed(self.trytes1),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'change_address': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_inputs_wrong_type(self):
    """
    ``inputs`` is not an array.
    """
    self.assertFilterErrors(
      {
        # Must be an array, even if there's only one input.
        'inputs': Address(self.trytes3),

        'seed': Seed(self.trytes1),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'inputs': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_inputs_contents_invalid(self):
    """
    ``inputs`` is a non-empty array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'inputs': [
          b'',
          text_type(self.trytes1, 'ascii'),
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          TryteString(self.trytes1),

          2130706433,
          b'9' * 82,
        ],

        'seed': Seed(self.trytes1),

        'transfers': [
          ProposedTransaction(address=Address(self.trytes2), value=42),
        ],
      },

      {
        'inputs.0':  [f.Required.CODE_EMPTY],
        'inputs.1':  [f.Type.CODE_WRONG_TYPE],
        'inputs.2':  [f.Type.CODE_WRONG_TYPE],
        'inputs.3':  [f.Required.CODE_EMPTY],
        'inputs.4':  [Trytes.CODE_NOT_TRYTES],
        'inputs.6':  [f.Type.CODE_WRONG_TYPE],
        'inputs.7':  [Trytes.CODE_WRONG_FORMAT],
      },
    )


# noinspection SpellCheckingInspection
class PrepareTransfersCommandTestCase(TestCase):
  def setUp(self):
    super(PrepareTransfersCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = PrepareTransfersCommand(self.adapter)

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).prepareTransfers,
      PrepareTransfersCommand,
    )

  def test_pass_inputs_not_needed(self):
    """
    Preparing a bundle that does not transfer any IOTAs.
    """
    response = self.command(
      seed = Seed.random(),

      transfers = [
        ProposedTransaction(
          value = 0,
          address = Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999KJUPKN'
            b'RMTHKVJYWNBKBGCKOQWBTKBOBJIZZYQITTFJZKLOI'
          ),
          tag = Tag(b'PYOTA9UNIT9TESTS9'),

          # Normally, it's not necessary to specify the timestamp for a
          # transaction, but for unit tests, it's kind of important (:
          timestamp = 1482938294,
        ),

        ProposedTransaction(
          value = 0,
          address = Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999YMSWGX'
            b'VNDMLXPT9HMVAOWUUZMLSJZFWGKDVGXPSQAWAEBJN'
          ),

          timestamp = 1482938294,
        ),
      ],
    )

    self.assertDictEqual(
      response,

      {
        # Transactions that don't require signatures aren't too
        # interesting.  Things will get more exciting in subsequent
        # tests.
        'trytes': [
          TryteString(
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'99999999999TESTVALUE9DONTUSEINPRODUCTION99999YMSWGXVNDMLXPT9HMVA'
            b'OWUUZMLSJZFWGKDVGXPSQAWAEBJN999999999999999999999999999999999999'
            b'999999999999999999NYBKIVD99A99999999A999999999EBBXLEONGGJMRUPZAO'
            b'HRAIOIEXDSZGQCXRWQMZNDUEQYYKDOSPHOI9KXZTCSBEUBW9WBHILISLYOZWIG99'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999'
          ),

          TryteString(
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'99999999999TESTVALUE9DONTUSEINPRODUCTION99999KJUPKNRMTHKVJYWNBKB'
            b'GCKOQWBTKBOBJIZZYQITTFJZKLOI999999999999999999999999999PYOTA9UNI'
            b'T9TESTS99999999999NYBKIVD99999999999A999999999EBBXLEONGGJMRUPZAO'
            b'HRAIOIEXDSZGQCXRWQMZNDUEQYYKDOSPHOI9KXZTCSBEUBW9WBHILISLYOZWIG99'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999999'
          ),
        ],
      },
    )

  def test_pass_inputs_explicit(self):
    """
    Preparing a bundle with specified inputs.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_inputs_explicit_insufficient(self):
    """
    Specified inputs are not sufficient to cover spend amount.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_inputs_implicit(self):
    """
    Preparing a bundle that finds inputs to use automatically.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_inputs_implicit_insufficient(self):
    """
    Account's total balance is not enough to cover spend amount.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_change_address_auto_generated(self):
    """
    Preparing a bundle with an auto-generated change address.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
