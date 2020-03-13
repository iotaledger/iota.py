from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Bundle, Fragment, ProposedTransaction
from iota.adapter import MockAdapter, async_return
from iota.commands.core import GetBalancesCommand
from iota.crypto.types import Digest
from iota.multisig import MultisigIota, AsyncMultisigIota
from iota.multisig.commands import PrepareMultisigTransferCommand
from iota.multisig.types import MultisigAddress
from test import patch, MagicMock, async_test


class PrepareMultisigTransferRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PrepareMultisigTransferCommand(MockAdapter()).get_request_filter
  maxDiff = None
  skip_value_check = True

  def setUp(self):
    super(PrepareMultisigTransferRequestFilterTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    self.digest_1 =\
      Digest(
        trytes =
          b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
          b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
          b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAY',

        key_index = 0,
      )

    self.digest_2 =\
      Digest(
        trytes =
          b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
          b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
          b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLC',

        key_index = 0,
      )

    self.trytes_1 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999IIPEM9'
      b'LA9FLHEGHDACSA9DOBQHQCX9BBHCFDIIMACARHA9B'
    )

    self.trytes_2 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999BGUDVE'
      b'DGH9WFQDEDVETCOGEGCDI9RFHGFGXBI99EJICHNEM'
    )

    self.trytes_3 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999XBGEUC'
      b'LF9EIFXHM9KHQANBLBHFVGTEGBWHNAKFDGZHYGCHI'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'changeAddress':
        Address(self.trytes_1),

      'multisigInput':
        MultisigAddress(
          digests = [self.digest_1, self.digest_2],
          trytes  = self.trytes_2,
        ),

      'transfers':
        [
          ProposedTransaction(
            address = Address(self.trytes_3),
            value   = 42,
          ),
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
    txn =\
      ProposedTransaction(
        address = Address(self.trytes_3),
        value   = 42,
      )

    filter_ =\
      self._filter({
        # ``changeAddress`` can be any value that resolves to an
        # :py:class:`Address`.
        'changeAddress': self.trytes_1,

        # ``multisigInput`` must be a :py:class:`MultisigInput` object.
        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        # ``transfers`` must contain an array of
        # :py:class:`ProposedTransaction` objects.
        'transfers': [txn],
      })

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'changeAddress': Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers': [txn],
      },
    )

  def test_pass_optional_parameters_excluded(self):
    """
    Request omits optional parameters.
    """
    txn =\
      ProposedTransaction(
        address = Address(self.trytes_3),
        value   = 42,
      )

    filter_ =\
      self._filter({
        # ``changeAddress`` is optional.
        # Technically, it's required if there are unspent inputs, but
        # the filter has no way to know whether this is the case.
        # 'changeAddress': self.trytes_1,

        # These parameters are required.
        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers': [txn],
      })

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'changeAddress': None,

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers': [txn],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers':
          [
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 42,
            ),
          ],

        # Oh come on!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transfers_null(self):
    """
    ``transfers`` is null.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        # On second thought, I changed my mind.
        'transfers': None,
      },

      {
        'transfers': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transfers_wrong_type(self):
    """
    ``transfers`` is not an array.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        # ``transfers`` must be an array, even if there's only one
        # transaction.
        'transfers':
          ProposedTransaction(
            address = Address(self.trytes_3),
            value   = 42,
          ),
      },

      {
        'transfers': [f.Array.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transfers_empty(self):
    """
    ``transfers`` is an array, but it's empty.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        # This is a variation on the ``null`` test.
        'transfers': [],
      },

      {
        'transfers': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transfers_contents_invalid(self):
    """
    ``transfers`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers':
          [
            None,
            42,

            # This one's valid, actually; just making sure that the
            # filter doesn't cheat.
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 42,
            ),

            Address(self.trytes_3),
          ],
      },

      {
        'transfers.0': [f.Required.CODE_EMPTY],
        'transfers.1': [f.Type.CODE_WRONG_TYPE],
        'transfers.3': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_multisigInput_null(self):
    """
    ``multisigInput`` is null.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput': None,

        'transfers':
          [
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 0,
            ),
          ],
      },

      {
        'multisigInput': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_multisigInput_multiple(self):
    """
    ``multisigInput`` is an array.

    This is not valid; a bundle may only contain a single multisig
    input.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        'multisigInput':
          [
            MultisigAddress(
              digests = [self.digest_1, self.digest_2],
              trytes  = self.trytes_2,
            ),

            MultisigAddress(
              digests = [self.digest_1, self.digest_2],
              trytes  = self.trytes_2,
            )
          ],

        'transfers':
          [
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 42,
            ),
          ],
      },

      {
        'multisigInput': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_multisigInput_wrong_type(self):
    """
    ``multisigInput`` is not a MultisigAddress.
    """
    self.assertFilterErrors(
      {
        'changeAddress':
          Address(self.trytes_1),

        # This value must be a MultisigAddress, so that we know the
        # total security level of the digests used to create it.
        'multisigInput':
          Address(self.trytes_2),

        'transfers':
          [
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 42,
            ),
          ],
      },

      {
        'multisigInput': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_pass_changeAddress_multisig_address(self):
    """
    ``changeAddress`` is allowed to be a MultisigAddress.
    """
    change_addy =\
      MultisigAddress(
        digests = [self.digest_1, self.digest_2],
        trytes  = self.trytes_1
      )

    filter_ = self._filter({
      'changeAddress': change_addy,

      'multisigInput':
        MultisigAddress(
          digests = [self.digest_1, self.digest_2],
          trytes  = self.trytes_2,
        ),

      'transfers':
        [
          ProposedTransaction(
            address = Address(self.trytes_3),
            value   = 42,
          ),
        ],
    })

    self.assertFilterPasses(filter_)
    self.assertIs(filter_.cleaned_data['changeAddress'], change_addy)

  def test_fail_changeAddress_wrong_type(self):
    """
    ``changeAddress`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'changeAddress': 42,

        'multisigInput':
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        'transfers':
          [
            ProposedTransaction(
              address = Address(self.trytes_3),
              value   = 42,
            ),
          ],
      },

      {
        'changeAddress': [f.Type.CODE_WRONG_TYPE],
      },
    )


class PrepareMultisigTransferCommandTestCase(TestCase):
  def setUp(self):
    super(PrepareMultisigTransferCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = PrepareMultisigTransferCommand(self.adapter)

    # Define some tryte sequences that we can reuse between tests.
    self.digest_1 =\
      Digest(
        trytes =
          b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
          b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
          b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAY',

        key_index = 0,
      )

    self.digest_2 =\
      Digest(
        trytes =
          b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
          b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
          b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLC',

        key_index = 0,
      )

    self.trytes_1 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999IIPEM9'
      b'LA9FLHEGHDACSA9DOBQHQCX9BBHCFDIIMACARHA9B'
    )

    self.trytes_2 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999BGUDVE'
      b'DGH9WFQDEDVETCOGEGCDI9RFHGFGXBI99EJICHNEM'
    )

    self.trytes_3 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999XBGEUC'
      b'LF9EIFXHM9KHQANBLBHFVGTEGBWHNAKFDGZHYGCHI'
    )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.multisig.commands.prepare_multisig_transfer.PrepareMultisigTransferCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = MultisigIota(self.adapter)

      # Don't need to call with proper args here.
      response = api.prepare_multisig_transfer('transfer', 'multisig_input')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_wireup(self):
    """
    Verify that the command is wired up correctly. (async)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.multisig.commands.prepare_multisig_transfer.PrepareMultisigTransferCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncMultisigIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.prepare_multisig_transfer('transfer', 'multisig_input')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_happy_path(self):
    """
    Preparing a bundle with a multisig input.
    """
    self.adapter.seed_response(
      command = GetBalancesCommand.command,

      response = {
        'balances': [42],

        # Would it be cheeky to put "7½ million years" here?
        'duration': 86,
      },
    )

    pmt_result =\
      await self.command(
        transfers = [
          ProposedTransaction(
            address = Address(self.trytes_1),
            value   = 42,
          ),
        ],

        multisigInput =
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),
      )

    # The command returns the raw trytes.  This is useful in a
    # real-world scenario because trytes are easier to transfer between
    # each entity that needs to apply their signature.
    #
    # However, for purposes of this test, we will convert the trytes
    # back into a bundle so that we can inspect the end result more
    # easily.
    bundle = Bundle.from_tryte_strings(pmt_result['trytes'])

    #
    # This bundle looks almost identical to what you would expect from
    # :py:meth:`iota.api.Iota.prepare_transfer`, except:
    # - There are 4 inputs (to hold all of the signature fragments).
    # - The inputs are unsigned.
    #
    self.assertEqual(len(bundle), 5)

    # Spend Transaction
    txn_1 = bundle[0]
    self.assertEqual(txn_1.address, self.trytes_1)
    self.assertEqual(txn_1.value, 42)

    # Input 1, Part 1 of 4
    txn_2 = bundle[1]
    self.assertEqual(txn_2.address, self.trytes_2)
    self.assertEqual(txn_2.value, -42)
    self.assertEqual(txn_2.signature_message_fragment, Fragment(b''))

    # Input 1, Part 2 of 4
    txn_3 = bundle[2]
    self.assertEqual(txn_3.address, self.trytes_2)
    self.assertEqual(txn_3.value, 0)
    self.assertEqual(txn_3.signature_message_fragment, Fragment(b''))

    # Input 1, Part 3 of 4
    txn_4 = bundle[3]
    self.assertEqual(txn_4.address, self.trytes_2)
    self.assertEqual(txn_4.value, 0)
    self.assertEqual(txn_4.signature_message_fragment, Fragment(b''))

    # Input 1, Part 4 of 4
    txn_5 = bundle[4]
    self.assertEqual(txn_5.address, self.trytes_2)
    self.assertEqual(txn_5.value, 0)
    self.assertEqual(txn_5.signature_message_fragment, Fragment(b''))

  @async_test
  async def test_unspent_inputs_with_change_address(self):
    """
    The bundle has unspent inputs, so it uses the provided change
    address.
    """
    self.adapter.seed_response(
      command = GetBalancesCommand.command,

      response = {
        'balances': [101],
        'duration': 86,
      },
    )

    pmt_result =\
      await self.command(
        transfers = [
          ProposedTransaction(
            address = Address(self.trytes_1),
            value   = 42,
          ),
        ],

        multisigInput =
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        changeAddress = Address(self.trytes_3),
      )

    bundle = Bundle.from_tryte_strings(pmt_result['trytes'])

    self.assertEqual(len(bundle), 6)

    # Spend Transaction
    txn_1 = bundle[0]
    self.assertEqual(txn_1.address, self.trytes_1)
    self.assertEqual(txn_1.value, 42)

    # Input 1, Part 1 of 4
    txn_2 = bundle[1]
    self.assertEqual(txn_2.address, self.trytes_2)
    self.assertEqual(txn_2.value, -101)
    self.assertEqual(txn_2.signature_message_fragment, Fragment(b''))

    # Input 1, Part 2 of 4
    txn_3 = bundle[2]
    self.assertEqual(txn_3.address, self.trytes_2)
    self.assertEqual(txn_3.value, 0)
    self.assertEqual(txn_3.signature_message_fragment, Fragment(b''))

    # Input 1, Part 3 of 4
    txn_4 = bundle[3]
    self.assertEqual(txn_4.address, self.trytes_2)
    self.assertEqual(txn_4.value, 0)
    self.assertEqual(txn_4.signature_message_fragment, Fragment(b''))

    # Input 1, Part 4 of 4
    txn_5 = bundle[4]
    self.assertEqual(txn_5.address, self.trytes_2)
    self.assertEqual(txn_5.value, 0)
    self.assertEqual(txn_5.signature_message_fragment, Fragment(b''))

    # Change
    txn_6 = bundle[5]
    self.assertEqual(txn_6.address, self.trytes_3)
    self.assertEqual(txn_6.value, 59)

  @async_test
  async def test_error_zero_iotas_transferred(self):
    """
    The bundle doesn't spend any IOTAs.

    This is considered an error case because
    :py:meth:`MultisigIota.prepare_multisig_transfer` is specialized
    for generating bundles that require multisig inputs.  Any bundle
    that doesn't require multisig functionality should be generated
    using :py:meth:`iota.api.Iota.prepare_transfer` instead.
    """
    with self.assertRaises(ValueError):
      await self.command(
        transfers = [
          ProposedTransaction(
            address = Address(self.trytes_1),
            value   = 0,
          ),
        ],

        multisigInput =
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),
      )

  @async_test
  async def test_error_insufficient_inputs(self):
    """
    The multisig input does not contain sufficient IOTAs to cover the
    spends.
    """
    self.adapter.seed_response(
      command = GetBalancesCommand.command,

      response = {
        'balances': [42],
        'duration': 86,
      },
    )

    with self.assertRaises(ValueError):
      await self.command(
        transfers = [
          ProposedTransaction(
            address = Address(self.trytes_1),
            value   = 101,
          ),
        ],

        multisigInput =
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),
      )

  @async_test
  async def test_error_unspent_inputs_no_change_address(self):
    """
    The bundle has unspent inputs, but no change address was specified.

    Unlike :py:meth:`iota.api.Iota.prepare_transfer` where all of the
    inputs are owned by the same seed, creating a multisig transfer
    usually involves multiple people.

    It would be unfair to the participants of the transaction if we
    were to automatically generate a change address using the seed of
    whoever happened to invoke the
    :py:meth:`MultisigIota.prepare_multisig_transfer` method!
    """
    self.adapter.seed_response(
      command = GetBalancesCommand.command,

      response = {
        'balances': [101],
        'duration': 86,
      },
    )

    with self.assertRaises(ValueError):
      await self.command(
        transfers = [
          ProposedTransaction(
            address = Address(self.trytes_1),
            value   = 42,
          ),
        ],

        multisigInput =
          MultisigAddress(
            digests = [self.digest_1, self.digest_2],
            trytes  = self.trytes_2,
          ),

        # changeAddress = Address(self.trytes_3),
      )
