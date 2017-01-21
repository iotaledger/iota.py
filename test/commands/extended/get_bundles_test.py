# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Address, Bundle, BundleHash, Fragment, Hash, Iota, \
  Tag, Transaction, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.filters import Trytes
from six import binary_type, text_type


class GetBundlesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetBundlesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetBundlesRequestFilterTestCase, self).setUp()

    # noinspection SpellCheckingInspection
    self.transaction = (
      b'ORLSCIMM9ZONOUSPYYWLOEMXQZLYEHCBEDQSHZOG'
      b'OPZCZCDZYTDPGEEUXWUZ9FQYCT9OGS9PICOOX9999'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'transaction': TransactionHash(self.transaction)
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
      # Any TrytesCompatible value will work here.
      'transaction': binary_type(self.transaction),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'transaction': TransactionHash(self.transaction),
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'transaction': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'transaction': TransactionHash(self.transaction),

        # SAY "WHAT" AGAIN!
        'what': 'augh!',
      },

      {
        'what': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``transaction`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'transaction': text_type(self.transaction, 'ascii'),
      },

      {
        'transaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transaction_not_trytes(self):
    """
    ``transaction`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'transaction': b'not valid; must contain only uppercase and "9"',
      },

      {
        'transaction': [Trytes.CODE_NOT_TRYTES],
      },
    )


class GetBundlesCommandTestCase(TestCase):
  def setUp(self):
    super(GetBundlesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetBundlesCommand(self.adapter)

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getBundles,
      GetBundlesCommand,
    )

  # noinspection SpellCheckingInspection
  def test_single_transaction(self):
    """
    Getting a bundle that contains a single transaction.
    """
    transaction =\
      Transaction(
          current_index = 0,
          last_index    = 0,
          tag           = Tag(b''),
          timestamp     = 1484960990,
          value         = 0,

          # For this test, we will bypass signature/message
          # functionality.
          nonce                       = Hash(b''),
          signature_message_fragment  = Fragment(b''),

          # This value is computed automatically, so it has to be real.
          hash_ =
            TransactionHash(
              b'TAOICZV9ZSXIZINMNRLOLCWNLL9IDKGVWTJITNGU'
              b'HAIKLHZLBZWOQ9HJSODUDISTYGIYPWTYDCFMVRBQN'
            ),

          address =
            Address(
              b'TESTVALUE9DONTUSEINPRODUCTION99999OCSGVF'
              b'IBQA99KGTCPCZ9NHR9VGLGADDDIEGGPCGBDEDDTBC'
            ),

          bundle_hash =
            BundleHash(
              b'TESTVALUE9DONTUSEINPRODUCTION99999DIOAZD'
              b'M9AIUHXGVGBC9EMGI9SBVBAIXCBFJ9EELCPDRAD9U'
            ),

          branch_transaction_hash =
            TransactionHash(
              b'TESTVALUE9DONTUSEINPRODUCTION99999BBCEDI'
              b'ZHUDWBYDJEXHHAKDOCKEKDFIMB9AMCLFW9NBDEOFV'
            ),

          trunk_transaction_hash =
            TransactionHash(
              b'TESTVALUE9DONTUSEINPRODUCTION999999ARAYA'
              b'MHCB9DCFEIWEWDLBCDN9LCCBQBKGDDAECFIAAGDAS'
            ),
        )

    self.adapter.seed_response('getTrytes', {
      'trytes': [transaction.as_tryte_string()],
    })

    response = self.command(transaction=transaction.hash)

    bundle = response['bundles'][0] # type: Bundle
    self.assertEqual(len(bundle), 1)

    self.maxDiff = None
    self.assertDictEqual(
      bundle[0].as_json_compatible(),
      transaction.as_json_compatible(),
    )

  def test_multiple_transactions(self):
    """
    Getting a bundle that contains multiple transactions.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_non_tail_transaction(self):
    """
    Trying to get a bundle for a non-tail transaction.

    This is not valid; you have to start with a tail transaction.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_missing_transaction(self):
    """
    Unable to find the requested transaction.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
