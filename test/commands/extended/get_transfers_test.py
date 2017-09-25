# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import Address, Bundle, Iota, Tag, Transaction, TryteString
from iota.adapter import MockAdapter
from iota.commands.extended.get_transfers import GetTransfersCommand, \
  GetTransfersRequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes
from test import mock


class GetTransfersRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTransfersCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetTransfersRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = 'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':             Seed(self.seed),
      'start':            0,
      'stop':             10,
      'inclusionStates':  True,
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
      # ``seed`` can be any TrytesCompatible value.
      'seed': bytearray(self.seed.encode('ascii')),

      # These values must still be integers/bools, however.
      'start':            42,
      'stop':             86,
      'inclusionStates':  True,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':             Seed(self.seed),
        'start':            42,
        'stop':             86,
        'inclusionStates':  True,
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
        'seed':             Seed(self.seed),
        'start':            0,
        'stop':             None,
        'inclusionStates':  False,
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

        # Your rules are really beginning to annoy me.
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

  def test_fail_stop_string(self):
    """
    ``stop`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'stop': '0',

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_stop_float(self):
    """
    ``stop`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'stop': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_stop_too_small(self):
    """
    ``stop`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'stop': -1,

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_stop_occurs_before_start(self):
    """
    ``stop`` is less than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  1,
        'stop':   0,

        'seed': Seed(self.seed),
      },

      {
        'start': [GetTransfersRequestFilter.CODE_INTERVAL_INVALID],
      },
    )

  def test_fail_interval_too_large(self):
    """
    ``stop`` is way more than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  0,
        'stop':   GetTransfersRequestFilter.MAX_INTERVAL + 1,

        'seed': Seed(self.seed),
      },

      {
        'stop':  [GetTransfersRequestFilter.CODE_INTERVAL_TOO_BIG],
      },
    )

  def test_fail_inclusion_states_wrong_type(self):
    """
    ``inclusionStates`` is not a boolean.
    """
    self.assertFilterErrors(
      {
        'inclusionStates': '1',

        'seed': Seed(self.seed),
      },

      {
        'inclusionStates': [f.Type.CODE_WRONG_TYPE],
      },
    )


# noinspection SpellCheckingInspection
class GetTransfersCommandTestCase(TestCase):
  def setUp(self):
    super(GetTransfersCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetTransfersCommand(self.adapter)

    # Define some tryte sequences we can re-use between tests.
    self.addy1 =\
      Address(
        b'TESTVALUEONE9DONTUSEINPRODUCTION99999YDZ'
        b'E9TAFAJGJA9CECKDAEPHBICDR9LHFCOFRBQDHC9IG'
      )

    self.addy2 =\
      Address(
        b'TESTVALUETWO9DONTUSEINPRODUCTION99999TES'
        b'GINEIDLEEHRAOGEBMDLENFDAFCHEIHZ9EBZDD9YHL'
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getTransfers,
      GetTransfersCommand,
    )

  def test_full_scan(self):
    """
    Scanning the Tangle for all transfers.
    """
    # To speed up the test, we will mock the address generator.
    # :py:class:`iota.crypto.addresses.AddressGenerator` already has
    # its own test case, so this does not impact the stability of the
    # codebase.
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      for addy in [self.addy1, self.addy2][start::step]:
        yield addy

    # The first address received IOTA.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 42,

        'hashes': [
          'TESTVALUEFIVE9DONTUSEINPRODUCTION99999VH'
          'YHRHJETGYCAFZGABTEUBWCWAS9WF99UHBHRHLIOFJ',
        ],
      },
    )

    # The second address is unused.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 1,
        'hashes':   [],
      },
    )

    self.adapter.seed_response(
      'getTrytes',

      {
        'duration': 99,

        # Thankfully, we do not have to seed a realistic response for
        # ``getTrytes``, as we will be mocking the ``getBundles``
        # command that uses on it.
        'trytes': [''],
      },
    )

    bundle = Bundle([
      Transaction(
        address = self.addy1,
        timestamp = 1483033814,

        # These values are not relevant to the test.
        hash_ = None,
        signature_message_fragment = None,
        value = 42,
        tag = Tag(b''),
        current_index = 0,
        last_index = 0,
        bundle_hash = None,
        trunk_transaction_hash = None,
        branch_transaction_hash = None,
        attachment_timestamp = 1483033814,
        attachment_timestamp_lower_bound = 12,
        attachment_timestamp_upper_bound = 0,
        nonce = None,
      )
    ])

    mock_get_bundles =\
      mock.Mock(return_value={
        'bundles': [bundle],
      })

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        create_generator,
    ):
      with mock.patch(
          'iota.commands.extended.get_bundles.GetBundlesCommand._execute',
          mock_get_bundles,
      ):
        response = self.command(seed=Seed.random())

    self.assertDictEqual(
      response,

      {
        'bundles': [bundle],
      },
    )

  def test_no_transactions(self):
    """
    There are no transactions for the specified seed.
    """
    # To speed up the test, we will mock the address generator.
    # :py:class:`iota.crypto.addresses.AddressGenerator` already has
    # its own test case, so this does not impact the stability of the
    # codebase.
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      for addy in [self.addy1][start::step]:
        yield addy

    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 1,
        'hashes':   [],
      },
    )

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        create_generator,
    ):
      response = self.command(seed=Seed.random())

    self.assertDictEqual(response, {'bundles': []})

  def test_start(self):
    """
    Scanning the Tangle for all transfers, with start index.
    """
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      # Inject an invalid value into the generator, to ensure it is
      # skipped.
      for addy in [None, self.addy1, self.addy2][start::step]:
        yield addy

    # The first address received IOTA.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 42,

        'hashes': [
          'TESTVALUEFIVE9DONTUSEINPRODUCTION99999VH'
          'YHRHJETGYCAFZGABTEUBWCWAS9WF99UHBHRHLIOFJ',
        ],
      },
    )

    # The second address is unused.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 1,
        'hashes':   [],
      },
    )

    self.adapter.seed_response(
      'getTrytes',

      {
        'duration': 99,
        'trytes':   [''],
      },
    )

    bundle = Bundle([
      Transaction(
        address = self.addy1,
        timestamp = 1483033814,

        # These values are not relevant to the test.
        hash_ = None,
        signature_message_fragment = None,
        value = 42,
        tag = Tag(b''),
        current_index = 0,
        last_index = 0,
        bundle_hash = None,
        trunk_transaction_hash = None,
        branch_transaction_hash = None,
        attachment_timestamp = 1483033814,
        attachment_timestamp_lower_bound = 12,
        attachment_timestamp_upper_bound = 0,
        nonce = None,
      )
    ])

    mock_get_bundles = mock.Mock(return_value={
      'bundles': [bundle],
    })

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        create_generator,
    ):
      with mock.patch(
          'iota.commands.extended.get_bundles.GetBundlesCommand._execute',
          mock_get_bundles,
      ):
        response = self.command(seed=Seed.random(), start=1)

    self.assertDictEqual(
      response,

      {
        'bundles': [bundle],
      },
    )

  def test_stop(self):
    """
    Scanning the Tangle for all transfers, with stop index.
    """
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      # Inject an invalid value into the generator, to ensure it is
      # skipped.
      for addy in [self.addy1, None][start::step]:
        yield addy

    # The first address received IOTA.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 42,

        'hashes': [
          'TESTVALUEFIVE9DONTUSEINPRODUCTION99999VH'
          'YHRHJETGYCAFZGABTEUBWCWAS9WF99UHBHRHLIOFJ',
        ],
      },
    )

    self.adapter.seed_response(
      'getTrytes',

      {
        'duration': 99,
        'trytes':   [''],
      },
    )

    bundle = Bundle([
      Transaction(
        address = self.addy1,
        timestamp = 1483033814,

        # These values are not relevant to the test.
        hash_ = None,
        signature_message_fragment = None,
        value = 42,
        tag = Tag(b''),
        current_index = 0,
        last_index = 0,
        bundle_hash = None,
        trunk_transaction_hash = None,
        branch_transaction_hash = None,
        attachment_timestamp = 1483033814,
        attachment_timestamp_lower_bound = 12,
        attachment_timestamp_upper_bound = 0,
        nonce = None,
      )
    ])

    mock_get_bundles = mock.Mock(return_value={
      'bundles': [bundle],
    })

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        create_generator,
    ):
      with mock.patch(
          'iota.commands.extended.get_bundles.GetBundlesCommand._execute',
          mock_get_bundles,
      ):
        response = self.command(seed=Seed.random(), stop=1)

    self.assertDictEqual(
      response,

      {
        'bundles': [bundle],
      },
    )

  def test_get_inclusion_states(self):
    """
    Fetching inclusion states with transactions.
    """
    # noinspection PyUnusedLocal
    def create_generator(ag, start, step=1):
      for addy in [self.addy1][start::step]:
        yield addy

    # The first address received IOTA.
    self.adapter.seed_response(
      'findTransactions',

      {
        'duration': 42,

        'hashes': [
          'TESTVALUEFIVE9DONTUSEINPRODUCTION99999VH'
          'YHRHJETGYCAFZGABTEUBWCWAS9WF99UHBHRHLIOFJ',
        ],
      },
    )

    # For this test, we have to generate a real TryteString.
    transaction_trytes =\
      TryteString(
        b'KMYUMNEUAYODAQSNGWTAERRRHNZBZCOLMVVOBTVWLOFYCJKYMGRAMH9RQ9MTZOSZMH'
        b'QNZFHFEJEDFQ99HSUNVOTULDJGXEDULS9ZHABVDZODJUMCNWVCPNSCUVKVYWCEXBHW'
        b'RBZBSWFPQLWZWMUPGQIGAEGOVE9DDXBVCIPKQYCFZFBELTSMVFSIXLPTACTKAFMCTK'
        b'CPYD9BWDJMLKWAOBDSJNQYAHS9GFIQKZCROLFZJVUEIVXVNBRRLEIWTYVHURUXHSCG'
        b'DKEIEGPOCXKCYWIBUG9ABYCALYJVFLBNGMS9ARHGTQXBZFLENXCJVKHPVKD9KSAEOL'
        b'FFVAJCNKLDVHOCDARWUNKARDYMVKFKRSMUTYOUXSBFFYTKRREBDJZTLVUROQFCBXQN'
        b'SXDDYTZTEBRSXOBMLXHJKSJAVOOVCXATOWNQDWHT9CCUAAJUJKDOQLMAEZACSNFKXZ'
        b'IGWDQEUEFRZYAOSDNVMSXWYLVDAUXZSHNHAIBEMNPFUGORYUETNJK9UCEMSUJYBBDK'
        b'BHIPKEINQCGOVYCPKUPJMUCUVZOJSIWYRFMFXYUVSMOUALAQBWIMXBUBXSAETGKJRP'
        b'AHVAXHQJDMEVSRFYEXUSIEBKMGYCUKFD9JPGUV9AIYUVCRUURKMYUHMVE9OJCYYWTQ'
        b'WUWFMTBZYFXASHHVCMSWXKBRQFHHQVEQMEULJRWZKLWFFSGGKEHUZZFNDNITSRAUH9'
        b'PQK9OGLYMVBSHXQLLZHOBBIM9KVUWDLHZRDKQQVLQXGWYXEEVQPDZUO9PVXMALOMRQ'
        b'VCTHGIZLILSCFKTBRESYZGBZKHXEODNDJZ9GK9ROWYXNGFHZCCBHHZEYEOGWXRGSUD'
        b'SUZFUAUBXVXZHCUVJSYBWTCYCEDYKZNGWFZYKSQLW9FUYMWDVXKZEWT9SCVMQCODZK'
        b'DRNKTINTPNOJOLGQJDAJMFWRFSWZJLYZGSTSIDSXLUJBZRZNLEDNBKAUNGTCYUPDRW'
        b'JOCEBQ9YG9IZLLRMJITISJOTLQMOGXVQIZXHMTJVMMWM9FOIOT9KFZMANEPOEOV9HX'
        b'JNEGURUKRWDGYNPVGAWMWQVABIJNL9MDXKONEPMYACOZ9BE9UZMAFTKYWPFWIQWAPK'
        b'GUXQTOQVWYYVZYGQDLBIQDVOZIWGOMGOBAUARICQZVNXD9UVEFBBAJKQBHRHXTBUOW'
        b'VBFKYQWZWTMMXVKZRIZUBVPQ9XHLJHFHWFZUIZVSNAKBDHDFGJCYQETOMEDTOXIUT9'
        b'OAJVIHWAGTCNPEZTERMMN9EZEWSJHKQAUMXPBZTNQOEQCVXIMAAYO9NIUFLTCFIMK9'
        b'9AFAGWJFA9VOFPUDJLRAMORGSUDBLWWKXEDZ9XPQUZSGANGESHKKGGQSGSYDCRLHZD'
        b'PKA9HKYBKLKKCXYRQQIPXCFETJJDZYPCLUNHGBKEJDRCIHEXKCQQNOV9QFHLGFXOCR'
        b'HPAFCUTPMY9NOZVQHROYJSCMGRSVMOBWADAZNFIAHWGIQUUZBOVODSFAUNRTXSDU9W'
        b'EIRBXQNRSJXFRAQGHA9DYOQJGLVZUJKAQ9CTUOTT9ZKQOQNNLJDUPDXZJYPRCVLRZT'
        b'UCZPNBREYCCKHK9FUWGITAJATFPUOFLZDHPNJYUTXFGNYJOBRD9BVHKZENFXIUYDTL'
        b'CE9JYIIYMXMCXMWTHOLTQFKFHDLVPGMQNITEUXSYLAQULCZOJVBIPYP9M9X9QCNKBX'
        b'W9DVJEQFFY9KQVMKNVTAHQVRXUKEM9FZOJLHAGEECZBUHOQFZOSPRXKZOCCKAOHMSV'
        b'QCFG9CWAHKVWNA9QTLYQI9NKOSHWJCNGPJBLEQPUIWJBIOAWKLBXUCERTSL9FVCLYN'
        b'ADPYTPKJOIEMAQGWBVGSRCZINXEJODUDCT9FHOUMQM9ZHRMBJYSOMPNMEAJGEHICJI'
        b'PVXRKCYX9RZVT9TDZIMXGZJAIYJRGIVMSOICSUINRBQILMJOUQYXCYNJ9WGGJFHYTU'
        b'LWOIPUXXFNTIFNOJRZFSQQNAWBQZOLHHLVGHEPWTKKQEVIPVWZUN9ZBICZ9DZZBVII'
        b'BF9EPHARZJUFJGBQXQFQIBUECAWRSEKYJNYKNSVBCOWTFBZ9NAHFSAMRBPEYGPRGKW'
        b'WTWACZOAPEOECUO9OTMGABJVAIICIPXGSXACVINSYEQFTRCQPCEJXZCY9XZWVWVJRZ'
        b'CYEYNFUUBKPWCHICGJZXKE9GSUDXZYUAPLHAKAHYHDXNPHENTERYMMBQOPSQIDENXK'
        b'LKCEYCPVTZQLEEJVYJZV9BWU999999999999999999999999999FFL999999999999'
        b'9999999999999RJQGVD99999999999A99999999USGBXHGJUEWAUAKNPPRHJXDDMQV'
        b'YDSYZJSDWFYLOQVFGBOSLE9KHFDLDYHUYTXVSFAFCOCLQUHJXTEIQRNBTLHEGJFGVF'
        b'DJCE9IKAOCSYHLCLWPVVNWNESKLYAJG9FGGZOFXCEYOTWLVIJUHGY9QCU9FMZJY999'
        b'9999HYBUYQKKRNAVDPVGYBTVDZ9SVQBLCCVLJTPEQWWOIG9CQZIFQKCROH9YHUCNJT'
        b'SYPBVZVBNESX999999D9TARGPQTNIYRZURQGVHCAWEDRBJIIEJIUZYENVE9LLJQMXH'
        b'GSUUYUCPSOWBCXVFDCHHAZUDC9LUODYWO'
      )

    self.adapter.seed_response(
      'getTrytes',

      {
        'duration': 99,
        'trytes':   [binary_type(transaction_trytes)],
      },
    )

    transaction = Transaction.from_tryte_string(transaction_trytes)

    mock_get_bundles = mock.Mock(return_value={
      'bundles': [Bundle([transaction])],
    })

    mock_get_latest_inclusion = mock.Mock(return_value={
      'states': {
        transaction.hash: True,
      },
    })

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        create_generator,
    ):
      with mock.patch(
          'iota.commands.extended.get_bundles.GetBundlesCommand._execute',
          mock_get_bundles,
      ):
        with mock.patch(
          'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand._execute',
          mock_get_latest_inclusion,
        ):
          response = self.command(
            seed = Seed.random(),

            inclusionStates = True,

            # To keep the test focused, only retrieve a single
            # transaction.
            start = 0,
            stop  = 1,
          )

    bundle = response['bundles'][0] # type: Bundle
    self.assertTrue(bundle[0].is_confirmed)
