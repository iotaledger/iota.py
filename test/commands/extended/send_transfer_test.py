# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type, text_type

from iota import Address, Bundle, Iota, ProposedTransaction, \
  TransactionTrytes, TryteString
from iota.adapter import MockAdapter
from iota.commands.extended.send_transfer import SendTransferCommand
from iota.crypto.types import Seed
from iota.filters import Trytes
from test import mock


class SendTransferRequestFilterTestCase(BaseFilterTestCase):
  filter_type = SendTransferCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(SendTransferRequestFilterTestCase, self).setUp()

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
      'changeAddress':      Address(self.trytes1),
      'depth':              100,
      'minWeightMagnitude': 18,
      'seed':               Seed(self.trytes2),

      'inputs': [
        Address(self.trytes3),
        Address(self.trytes4),
      ],

      'transfers': [
        self.transfer1,
        self.transfer2
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
      # Any TrytesCompatible values will work here.
      'changeAddress':  binary_type(self.trytes1),
      'seed':           bytearray(self.trytes2),

      'inputs': [
        binary_type(self.trytes3),
        bytearray(self.trytes4),
      ],

      # These values must have the correct type, however.
      'transfers': [
        self.transfer1,
        self.transfer2
      ],

      'depth':              100,
      'minWeightMagnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'changeAddress':      Address(self.trytes1),
        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes2),

        'inputs': [
          Address(self.trytes3),
          Address(self.trytes4),
        ],

        'transfers': [
          self.transfer1,
          self.transfer2
        ],
      }
    )

  def test_pass_optional_parameters_omitted(self):
    """
    Request omits optional parameters.
    """
    filter_ = self._filter({
      'depth':              100,
      'minWeightMagnitude': 13,
      'seed':               Seed(self.trytes2),

      'transfers': [
        self.transfer1,
        self.transfer2
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'changeAddress':      None,
        'inputs':             None,

        'depth':              100,
        'minWeightMagnitude': 13,
        'seed':               Seed(self.trytes2),

        'transfers': [
          self.transfer1,
          self.transfer2
        ],
      }
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'depth':              [f.FilterMapper.CODE_MISSING_KEY],
        'minWeightMagnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'seed':               [f.FilterMapper.CODE_MISSING_KEY],
        'transfers':          [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],

        # Maybe he's not that smart; maybe he's like a worker bee who
        # only knows how to push buttons or something.
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

        'depth':              100,
        'minWeightMagnitude': 18,
        'transfers':          [self.transfer1],
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
        'seed': 42,

        'depth':              100,
        'minWeightMagnitude': 18,
        'transfers':          [self.transfer1],
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

        'depth':              100,
        'minWeightMagnitude': 18,
        'transfers':          [self.transfer1],
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
        'transfers': self.transfer1,

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
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

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
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

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
      },

      {
        'transfers.0': [f.Required.CODE_EMPTY],
        'transfers.2': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_change_address_wrong_type(self):
    """
    ``changeAddress`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'changeAddress': 42,

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'changeAddress': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_change_address_not_trytes(self):
    """
    ``changeAddress`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'changeAddress': b'not valid; must contain only uppercase and "9"',

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'changeAddress': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_inputs_wrong_type(self):
    """
    ``inputs`` is not an array.
    """
    self.assertFilterErrors(
      {
        # Must be an array, even if there's only one input.
        'inputs': Address(self.trytes4),

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
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
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          TryteString(self.trytes4),

          2130706433,
          b'9' * 82,
        ],

        'depth':              100,
        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'inputs.0':  [f.Required.CODE_EMPTY],
        'inputs.1':  [f.Type.CODE_WRONG_TYPE],
        'inputs.2':  [f.Required.CODE_EMPTY],
        'inputs.3':  [Trytes.CODE_NOT_TRYTES],
        'inputs.5':  [f.Type.CODE_WRONG_TYPE],
        'inputs.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )

  def test_fail_depth_null(self):
    """
    ``depth`` is null.
    """
    self.assertFilterErrors(
      {
        'depth': None,

        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'depth': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_depth_string(self):
    """
    ``depth`` is a string.
    """
    self.assertFilterErrors(
      {
        # Too ambiguous; it must be an int.
        'depth': '2',

        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_float(self):
    """
    ``depth`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are invalid.
        'depth': 100.0,

        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_too_small(self):
    """
    ``depth`` is < 1.
    """
    self.assertFilterErrors(
      {
        'depth': 0,

        'minWeightMagnitude': 18,
        'seed':               Seed(self.trytes1),
        'transfers':          [self.transfer1],
      },

      {
        'depth': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_min_weight_magnitude_null(self):
    """
    ``minWeightMagnitude`` is null.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': None,

        'depth':      100,
        'seed':       Seed(self.trytes1),
        'transfers':  [self.transfer1],
      },

      {
        'minWeightMagnitude': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """
    ``minWeightMagnitude`` is a string.
    """
    self.assertFilterErrors(
      {
        # Nope; it's gotta be an int.
        'minWeightMagnitude': '18',

        'depth':      100,
        'seed':       Seed(self.trytes1),
        'transfers':  [self.transfer1],
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """
    ``minWeightMagnitude`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are invalid.
        'minWeightMagnitude': 18.0,

        'depth':      100,
        'seed':       Seed(self.trytes1),
        'transfers':  [self.transfer1],
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``minWeightMagnitude`` is < 1.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': 0,

        'depth':      100,
        'seed':       Seed(self.trytes1),
        'transfers':  [self.transfer1],
      },

      {
        'minWeightMagnitude': [f.Min.CODE_TOO_SMALL],
      },
    )


class SendTransferCommandTestCase(TestCase):
  def setUp(self):
    super(SendTransferCommandTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.command  = SendTransferCommand(self.adapter)

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).sendTransfer,
      SendTransferCommand,
    )

  def test_happy_path(self):
    """
    Sending a transfer successfully.
    """
    # noinspection SpellCheckingInspection
    transaction1 =\
      TransactionTrytes(
          b'GYPRVHBEZOOFXSHQBLCYW9ICTCISLHDBNMMVYD9JJHQMPQCTIQAQTJNNNJ9IDXLRCC'
          b'OYOXYPCLR9PBEY9ORZIEPPDNTI9CQWYZUOTAVBXPSBOFEQAPFLWXSWUIUSJMSJIIIZ'
          b'WIKIRH9GCOEVZFKNXEVCUCIIWZQCQEUVRZOCMEL9AMGXJNMLJCIA9UWGRPPHCEOPTS'
          b'VPKPPPCMQXYBHMSODTWUOABPKWFFFQJHCBVYXLHEWPD9YUDFTGNCYAKQKVEZYRBQRB'
          b'XIAUX9SVEDUKGMTWQIYXRGSWYRK9SRONVGTW9YGHSZRIXWGPCCUCDRMAXBPDFVHSRY'
          b'WHGB9DQSQFQKSNICGPIPTRZINYRXQAFSWSEWIFRMSBMGTNYPRWFSOIIWWT9IDSELM9'
          b'JUOOWFNCCSHUSMGNROBFJX9JQ9XT9PKEGQYQAWAFPRVRRVQPUQBHLSNTEFCDKBWRCD'
          b'X9EYOBB9KPMTLNNQLADBDLZPRVBCKVCYQEOLARJYAGTBFR9QLPKZBOYWZQOVKCVYRG'
          b'YI9ZEFIQRKYXLJBZJDBJDJVQZCGYQMROVHNDBLGNLQODPUXFNTADDVYNZJUVPGB9LV'
          b'PJIYLAPBOEHPMRWUIAJXVQOEM9ROEYUOTNLXVVQEYRQWDTQGDLEYFIYNDPRAIXOZEB'
          b'CS9P99AZTQQLKEILEVXMSHBIDHLXKUOMMNFKPYHONKEYDCHMUNTTNRYVMMEYHPGASP'
          b'ZXASKRUPWQSHDMU9VPS99ZZ9SJJYFUJFFMFORBYDILBXCAVJDPDFHTTTIYOVGLRDYR'
          b'TKHXJORJVYRPTDH9ZCPZ9ZADXZFRSFPIQKWLBRNTWJHXTOAUOL9FVGTUMMPYGYICJD'
          b'XMOESEVDJWLMCVTJLPIEKBE9JTHDQWV9MRMEWFLPWGJFLUXI9BXPSVWCMUWLZSEWHB'
          b'DZKXOLYNOZAPOYLQVZAQMOHGTTQEUAOVKVRRGAHNGPUEKHFVPVCOYSJAWHZU9DRROH'
          b'BETBAFTATVAUGOEGCAYUXACLSSHHVYDHMDGJP9AUCLWLNTFEVGQGHQXSKEMVOVSKQE'
          b'EWHWZUDTYOBGCURRZSJZLFVQQAAYQO9TRLFFN9HTDQXBSPPJYXMNGLLBHOMNVXNOWE'
          b'IDMJVCLLDFHBDONQJCJVLBLCSMDOUQCKKCQJMGTSTHBXPXAMLMSXRIPUBMBAWBFNLH'
          b'LUJTRJLDERLZFUBUSMF999XNHLEEXEENQJNOFFPNPQ9PQICHSATPLZVMVIWLRTKYPI'
          b'XNFGYWOJSQDAXGFHKZPFLPXQEHCYEAGTIWIJEZTAVLNUMAFWGGLXMBNUQTOFCNLJTC'
          b'DMWVVZGVBSEBCPFSM99FLOIDTCLUGPSEDLOKZUAEVBLWNMODGZBWOVQT9DPFOTSKRA'
          b'BQAVOQ9RXWBMAKFYNDCZOJGTCIDMQSQQSODKDXTPFLNOKSIZEOY9HFUTLQRXQMEPGO'
          b'XQGLLPNSXAUCYPGZMNWMQWSWCKAQYKXJTWINSGPPZG9HLDLEAWUWEVCTVRCBDFOXKU'
          b'ROXH9HXXAXVPEJFRSLOGRVGYZASTEBAQNXJJROCYRTDPYFUIQJVDHAKEG9YACV9HCP'
          b'JUEUKOYFNWDXCCJBIFQKYOXGRDHVTHEQUMHO999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999999999999999999999999999999999999'
          b'999999999999RKWEEVD99A99999999A99999999NFDPEEZCWVYLKZGSLCQNOFUSENI'
          b'XRHWWTZFBXMPSQHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PGTKORV9IKTJZQ'
          b'UBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999'
          b'999TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSK'
          b'UCUEMD9M9SQJ999999999999999999999999999999999999999999999999999999'
          b'999999999999999999999999999999999'
        )

    mock_prepare_transfer =\
      mock.Mock(return_value={
        'trytes': [transaction1],
      })

    mock_send_trytes =\
      mock.Mock(return_value={
        'trytes': [transaction1],
      })

    with mock.patch(
        'iota.commands.extended.prepare_transfer.PrepareTransferCommand._execute',
        mock_prepare_transfer,
    ):
      with mock.patch(
          'iota.commands.extended.send_trytes.SendTrytesCommand._execute',
          mock_send_trytes,
      ):
        response = self.command(
          depth               = 100,
          minWeightMagnitude  = 18,
          seed                = Seed.random(),

          transfers = [
            ProposedTransaction(
              address =
                Address(
                  b'9999999999999999999999999999999999999999'
                  b'99999999999999999999999999999999999999999'
                ),

              value = 0,
            ),
          ],
        )

    bundle = response['bundle'] # type: Bundle
    self.assertEqual(len(bundle), 1)
    self.assertEqual(bundle[0].as_tryte_string(), transaction1)
