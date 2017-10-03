# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import Address, Bundle, BundleHash, Fragment, Iota, Nonce, Tag, \
  Transaction, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.extended.replay_bundle import ReplayBundleCommand
from iota.filters import Trytes
from test import mock


class ReplayBundleRequestFilterTestCase(BaseFilterTestCase):
  filter_type = ReplayBundleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(ReplayBundleRequestFilterTestCase, self).setUp()

    self.trytes1 = (
      b'TESTVALUEONE9DONTUSEINPRODUCTION99999DAU'
      b'9WFSFWBSFT9QATCXFIIKDVFLHIIJGGFCDYENBEDCF'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'depth':              100,
      'minWeightMagnitude': 18,
      'transaction':        TransactionHash(self.trytes1),
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
      # This can be any TrytesCompatible value.
      'transaction': binary_type(self.trytes1),

      # These values must still be ints, however.
      'depth':              100,
      'minWeightMagnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'depth':              100,
        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
      },
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
        'transaction':        [f.FilterMapper.CODE_MISSING_KEY],
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
        'transaction':        TransactionHash(self.trytes1),

        # That's a real nasty habit you got there.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_null(self):
    """
    ``transaction`` is null.
    """
    self.assertFilterErrors(
      {
        'transaction': None,

        'depth':              100,
        'minWeightMagnitude': 18,
      },

      {
        'transaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``transaction`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'transaction': 42,

        'depth':              100,
        'minWeightMagnitude': 18,
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

        'depth':              100,
        'minWeightMagnitude': 18,
      },

      {
        'transaction': [Trytes.CODE_NOT_TRYTES],
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
        'transaction':        TransactionHash(self.trytes1),
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
        # Too ambiguous; it's gotta be an int.
        'depth': '4',

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
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
        # Even with an empty fpart, float value is not valid.
        'depth': 8.0,

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
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
        'transaction':        TransactionHash(self.trytes1),
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

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
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
        # It's gotta be an int!
        'minWeightMagnitude': '18',

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
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
        # Even with an empty fpart, float values are not valid.
        'minWeightMagnitude': 18.0,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
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

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'minWeightMagnitude': [f.Min.CODE_TOO_SMALL],
      },
    )


class ReplayBundleCommandTestCase(TestCase):
  def setUp(self):
    super(ReplayBundleCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = ReplayBundleCommand(self.adapter)

  def test_wireup(self):
    """
    Verifies that the command is wired-up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).replayBundle,
      ReplayBundleCommand,
    )

  def test_happy_path(self):
    """
    Successfully replaying a bundle.
    """
    # noinspection SpellCheckingInspection
    bundle = Bundle([
      # "Spend" transaction, Part 1 of 1
      Transaction(
        hash_ =
          TransactionHash(
            b'LUQJUUDAZIHSTPBLCZYXWXYKXTFCOCQJ9EHXKLEB'
            b'IJBPSRFSBYRBYODDAZ9NPKPYSMPVNEFXYZQ999999'
          ),

        address =
          Address(
            b'FZXUHBBLASPIMBDIHYTDFCDFIRII9LRJPXFTQTPO'
            b'VLEIFE9NWTFPPQZHDCXYUOUCXHHNRPKCIROYYTWSA'
          ),

        branch_transaction_hash =
          TransactionHash(
            b'UKGIAYNLALFGJOVUZYJGNIOZSXBBZDXVQLUMHGQE'
            b'PZJWYDMGTPJIQXS9GOKXR9WIGWFRWRSKGCJ999999'
          ),

        bundle_hash =
          BundleHash(
            b'ZSATLX9HDENCIARERVLWYHXPQETFL9QKTNC9LUOL'
            b'CDXKKW9MYTLZJDXBNOHURUXSYWMGGD9UDGLHCSZO9'
          ),

        nonce =
          Nonce(
            b'LIJVXBVTYMEEPCKJRIQTGAKWJRA'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'KFCQSGDYENCECCPNNZDVDTBINCBRBERPTQIHFH9G'
            b'YLTCSGUFMVWWSAHVZFXDVEZO9UHAUIU9LNX999999'
          ),

        signature_message_fragment = Fragment(b''),

        current_index                     = 0,
        last_index                        = 3,
        tag                               = Tag(b''),
        timestamp                         = 1483033814,
        value                             = 1,
        attachment_timestamp              = 0,
        attachment_timestamp_lower_bound  = 0,
        attachment_timestamp_upper_bound  = 0,
      ),

      # Input #1, Part 1 of 2
      Transaction(
        hash_ =
          TransactionHash(
            b'KFCQSGDYENCECCPNNZDVDTBINCBRBERPTQIHFH9G'
            b'YLTCSGUFMVWWSAHVZFXDVEZO9UHAUIU9LNX999999'
          ),

        address =
          Address(
            b'GMHOSRRGXJLDPVWRWVSRWI9BCIVLUXWKTJYZATIA'
            b'RAZRUCRGTWXWP9SZPFOVAMLISUPQUKHNDMITUJKIB'
          ),

        branch_transaction_hash =
          TransactionHash(
            b'UKGIAYNLALFGJOVUZYJGNIOZSXBBZDXVQLUMHGQE'
            b'PZJWYDMGTPJIQXS9GOKXR9WIGWFRWRSKGCJ999999'
          ),

        bundle_hash =
          BundleHash(
            b'ZSATLX9HDENCIARERVLWYHXPQETFL9QKTNC9LUOL'
            b'CDXKKW9MYTLZJDXBNOHURUXSYWMGGD9UDGLHCSZO9'
          ),

        nonce =
          Nonce(
            b'VRYLDCKEWZJXPQVSWOJVYVBJSCW'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'QSTUKDIBYAZIQVEOMFGKQPHAIPBHUPSDQFFKKHRA'
            b'ABYMYMQDHMTEWCM9IMZHQMGXOTWNSJYHRNA999999'
          ),

        signature_message_fragment =
          Fragment(
            b'XS9OVIXHIGGR9IYQBHGMFAHPZBWLIBNAQPFMPVYUZDOLLFDJIPZEMIOGVANQJSCU'
            b'IPDNNUNAMWEL9OFXXK9NV9UTCRBYTARBJHPQYJYKNAQGMATG9EXQMHGXY9QOHPBA'
            b'FEVABDYMCXORXHBMPLEWJYGYFFBWVXAUXHGLTABBKOQMZLFAYWDAKEOMJPJX9TMT'
            b'GXIJXZTKRRIPAMYY9UNSPPEGFPJE9NFSJFWKYOFZRMPBXZDNQUEKLRUVPXMCTQRE'
            b'ZWICSCVXN9VBLN9DRINRPAZTYJYXPGGRZJLMYXGCLUQNZ9NJGH9GFQPKKVK9N9WR'
            b'IJXDNKUMLLJUVIQRGPHEVWTXQHRLRCWQJCHTPASCVLRGPNWSIUKWIBMDJJ9EUTQ9'
            b'NXZZEJFWY9LCJJSOEPXWETUBKKVZNUKTLUPEPDBLUWCQGYTOXZ9NZUXHBDOUYQBP'
            b'MNECVJ9HGWA9AWU9VHGETWKBU9YZEZGEQKMVTAKPLCZVWKQFXDEFBPKNUCQDSPWA'
            b'LMPFTUFGRFDZH9PQHJ9WXZPCDWGMNASVVEUXEGWATM9ZIMCEEXTHCXFLYG9LQAKV'
            b'UOGORP9UUWYFTWGZ9OFOGSP9KDNPDSQKEMMISEMWQDVFKCSQXSP9RUMNUQJOBACU'
            b'MPIXCGBJLQQGB9GDSMUUUSYWIY9ZNIAIZBJYTAJKJKZIBFPMGDWUEPXSO9HUJRNV'
            b'QE9OTVUPKBVNVUBSILVZEDPC9AMEYAIATE9JEIQQWIMGCZXMHOPXPFUTEPJEATJN'
            b'QWDFZQ9OGPNBFUHLJDJZQJLXCFEUDPZKVCPEBTNBRYNIIKJHUV9EUFVMB9AHTARQ'
            b'DN9TZ9JPAPCEXSYHZPAQLBJMNQ9R9KPWVZLDLFNHYCCQBFVEPMEZSXAB9GOKGOGC'
            b'SOVL9XJSAQYSECY9UUNSVQSJB9BZVYRUURNUDMZVBJTMIDQUKQLMVW99XFDWTOPR'
            b'UBRPKS9BGEAQPIODAMJAILNCH9UVYVWSDCZXZWLO9XJJZ9FQOL9F9ZJDNGMUGFKJ'
            b'PCYURGYBGYRVKPEBKMJPZZGDKZKT9UBFSJEELREWOYDQZVUPVSGPZYIDVOJGNTXC'
            b'OFGCHBGVZPQDNRKAQNVJEYKYTKHTFBJRDMKVSHEWADNYIQOAUFXYMZKNJPLXGYFX'
            b'DTCVDDBUHBDPG9WLNMWPSCCCGVTIOOLEECXKNVAYNNTDLJMDGDGSKOGWO9UYXTTF'
            b'FCRZEDDQNN9ZODTETGMGGUXOYECGNMHGMGXHZSPODIBMBATJJHSPQHDUCZOMWQNI'
            b'CUZG9LAMBOQRQQDIPIBMIDCIAJBBBNDUAIEMFCEASHPUJPFPPXNDUVGDNNYBRRTW'
            b'SPXGXMCSUXYJSTFIRUIDNEUSVKNIDKIBRQNMEDCYQOMJYTMGRZLYHBUYXCRGSAXR'
            b'ZVHTZEAKNAUKJPFGPOGQLTDMSOXR9NVOIAIMCBVWOF9FXAZUKKZKHJEGHFNLUB9B'
            b'TGAICGQGAYZRRHSFIDTNIJPHIHCXTHQUSKJRSVAWFUXLBYA99QKMGLHDNUHOPEW9'
            b'OFNWPDXXRVZREUIQKSVSDCFIJ99TSGSZ9KU9JGE9VXDVVOLMGNMUGSHUZAOFCIMK'
            b'CPEWMG9IHUZAILQCANIUUG9JNEZMT9EONSN9CWWQOTFBEPZRTTJTQFSTQTBERKGE'
            b'NGFFIYMZMCFBYNIOBPOFOIYPUMYYPRXEHUJEVVELOPNXAPCYFXQ9ORMSFICDOZTS'
            b'GQOMDI9FKEKRIMZTWSIWMYAUSBIN9TPFSMQZCYGVPVWKSFZXPE9BP9ALNWQOVJGM'
            b'SCSJSTNUTMUAJUIQTITPPOHG9NKIFRNXSCMDAEW9LSUCTCXITSTZSBYMPOMSMTXP'
            b'CEBEOAUJK9STIZRXUORRQBCYJPCNHFKEVY9YBJL9QGLVUCSZKOLHD9BDNKIVJX9T'
            b'PPXQVGAXUSQQYGFDWQRZPKZKKWB9ZBFXTUGUGOAQLDTJPQXPUPHNATSGILEQCSQX'
            b'X9IAGIVKUW9MVNGKTSCYDMPSVWXCGLXEHWKRPVARKJFWGRYFCATYNZDTRZDGNZAI'
            b'OULYHRIPACAZLN9YHOFDSZYIRZJEGDUZBHFFWWQRNOLLWKZZENKOWQQYHGLMBMPF'
            b'HE9VHDDTBZYHMKQGZNCSLACYRCGYSFFTZQJUSZGJTZKKLWAEBGCRLXQRADCSFQYZ'
            b'G9CM9VLMQZA'
          ),

        current_index                     = 1,
        last_index                        = 3,
        tag                               = Tag(b''),
        timestamp                         = 1483033814,
        value                             = -99,
        attachment_timestamp              = 0,
        attachment_timestamp_lower_bound  = 0,
        attachment_timestamp_upper_bound  = 0,
      ),

      # Input #1, Part 2 of 2
      Transaction(
        hash_ =
          TransactionHash(
            b'QSTUKDIBYAZIQVEOMFGKQPHAIPBHUPSDQFFKKHRA'
            b'ABYMYMQDHMTEWCM9IMZHQMGXOTWNSJYHRNA999999'
          ),

        address =
          Address(
            b'GMHOSRRGXJLDPVWRWVSRWI9BCIVLUXWKTJYZATIA'
            b'RAZRUCRGTWXWP9SZPFOVAMLISUPQUKHNDMITUJKIB'
          ),

        branch_transaction_hash =
          TransactionHash(
            b'UKGIAYNLALFGJOVUZYJGNIOZSXBBZDXVQLUMHGQE'
            b'PZJWYDMGTPJIQXS9GOKXR9WIGWFRWRSKGCJ999999'
          ),

        bundle_hash =
          BundleHash(
            b'ZSATLX9HDENCIARERVLWYHXPQETFL9QKTNC9LUOL'
            b'CDXKKW9MYTLZJDXBNOHURUXSYWMGGD9UDGLHCSZO9'
          ),

        nonce =
          Nonce(
            b'AAKVYZOEZSOXTX9LOLHZYLNAS9C'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'ZYQGVZABMFVLJXHXXJMVAXOXHRJTTQUVDIIQOOXN'
            b'NDPQGDFDRIDQMUWJGCQKKLGEUQRBFAJWZBC999999'
          ),

        signature_message_fragment =
          Fragment(
            b'YSNEGUCUHXEEFXPQEABV9ATGQMMXEVGMZWKKAFAVOVGUECOZZJFQDNRBCSXCOTBD'
            b'BRUJ9HF9CITXQI9ZQGZFKCXMFZTOYHUTCXDIBIMTBKVXMMTPNKRDRLQESLWFZSQQ'
            b'9BCGKVIZAHBWYTNXG9OWOXHAMQECMOVKN9SOEVJBBARPXUXYUQVFPYXWXQQMDIVP'
            b'VITRWTNNBY9CYBHXJTZUVIPJJG9WLTNMFVPXGYZCNOGSLGVMS9YXXNSV9AYPXZTA'
            b'QJYUNUFBCSZBZNKWCPMVMOGFIDENTOOOCPRDJTNGQRLA9YKMLYZQRO9QQJMCSYVF'
            b'YLISFIWQQYMWMHUOEZPATYCEZARLWLAMCZWYWJZVD9WWKYJURTOLITFFRXQUBKST'
            b'DG9CKDBLPXTPCIMKEKRGEXJGLRL9ZST9VOLV9NOFZLIMVOZBDZJUQISUWZKOJCRN'
            b'YRBRJLCTNPV9QIWQJZDQFVPSTW9BJYWHNRVQTITWJYB9HBUQBXTAGK9BZCHYWYPE'
            b'IREDOXCYRW9UXVSLZBBPAFIUEJABMBYKSUPNWVVKAFQJKDAYYRDICTGOTWWDSFLG'
            b'BQFZZ9NBEHZHPHVQUYEETIRUDM9V9LBXFUXTUGUMZG9HRBLXCKMMWWMK9VTKVZSA'
            b'PRSMJVBLFFDHTYCPDXKBUYYLZDPW9EVXANPZOPBASQUPRNCDGHNUK9NDUQSULUZI'
            b'VMIJTPUGMZPCYR9AERBAGUYNGVEHWIIADAAPPMYQOAGBQCXEDTQOGHWHHSWDFZLC'
            b'DVLNPYMGDPZWOZURT9OZKDJKFECXSFIALXJDRJWMWMTNUUNVDUCJAZLDRN9ZWLHH'
            b'SNXDWULUBNLVRDJZQMKCTRCKULKS9VARFZSRYZCPNH9FHXCAFWKPNGOPOFMYXJLE'
            b'LTKUHSZVDQRDJIGQRGOSKYWDCU9EBJMXQDBKTBNQTIZNCALHRNTHKN99WOBQVVEV'
            b'HEDTDRKFPGLIWOSPLAAELQQXDCDWPIFED9OEUPYPKHZBOHPQGQGSEKO9BFIQFYZK'
            b'YEULWSIBZVSPXBGOJTTYBVIIIPAXGL9ZJNNIELFYAUOUBRDWLJJMSAXHQOYGOWDV'
            b'HHPISRZFSHPDLNQDFWRHLWNAJPYM9REAJLZDIAIVLQBFAUJIQKVHJDFPXENI9ZM9'
            b'SFNGSQHDFEDC9CQVXAXTQVLWYMVSLEDCOVNSQLSANLVA9TWSY9BHAJKOCGI9YLAB'
            b'VROCBJRVXRWBKNUXCAXJIAYWSFRDZHIPQSNBRYNKZAFXHDUENVLHFHYIKH9IANFV'
            b'FKWVFJCSEELVTDDUHBPIYNFLTJLINNORIMDEAXMN9LGNGBWVWYWQIPWKBFDKNDOX'
            b'WFKGBAMZIUFYA9DXGAL9OQQTJAUUXTINWZSQUTPUKUMOZCGOBKKFBXCVR9AGTAQS'
            b'SVGTUBBHSIRHFRSIR9SKSZPXQFG9AOYAHZNQR9AHSEFCKWCJHUTLREDVGBQYVBZR'
            b'CZDXFG9PTSAWQOURYKNWYAZNASV9UMUYUMFCQSFDHZD99WUMCORLYTIZMRGNBAY9'
            b'UJYJMMRCLJP9XVLXTAZOHNVVYSCOSDHGUOPXIRBJDXJUCJYLQKUJOTNJCPRBDOKV'
            b'ZEMIGZRNJOQKFFAXQVGGY9YRJORZCOD9REIIIDDTRQ9TJWTFYRKOPLAFNUUPCHXA'
            b'WVPYUQXAFFCTYAESWAFUTQQYZRQVLVZW9OWAAJMPSAEPKWXVEZVTVPQEEBVXNZJP'
            b'ZU9JJSIAEPIT9HE99XNAUYOAKRIFQQJQTFIMWEOKLCH9JKCQTGZPEGWORFB9ARNS'
            b'DPYKRONBONYOGEVEFXGTMQTQBEMFQWEMIDSGAVEQHVHAPSMTCJ9FMEYBWAQWWJCE'
            b'ABUUMMVNDMSBORFLHVIIDOUQHHXQKXTVGRAYTLMECCSVZOZM9JKUWIGGFLMMDGBU'
            b'DBIHJFUINVOKSFTOGFCZEMIBSZNGPL9HXWGTNNAKYIMDITCRMSHFR9BDSFGHXQMR'
            b'ACZOVUOTSJSKMNHNYIFEOD9CVBWYVVMG9ZDNR9FOIXSZSTIO9GLOLPLMW9RPAJYB'
            b'WTCKV9JMSEVGD9ZPEGKXF9XYQMUMJPWTMFZJODFIEYNLI9PWODSPPW9MVJOWZQZU'
            b'CIKXCVVXDKWHXV99GOEZ9CMGUH9OWGLLISNZEPSAPEDHVRKKGFFNGBXFLDBQTTQL'
            b'WVLUITJQ9JM'
          ),

        current_index                     = 2,
        last_index                        = 3,
        tag                               = Tag(b''),
        timestamp                         = 1483033814,
        value                             = 0,
        attachment_timestamp              = 0,
        attachment_timestamp_lower_bound  = 0,
        attachment_timestamp_upper_bound  = 0,
      ),

      # "Change" transaction, Part 1 of 1
      Transaction(
        hash_ =
          TransactionHash(
            b'ZYQGVZABMFVLJXHXXJMVAXOXHRJTTQUVDIIQOOXN'
            b'NDPQGDFDRIDQMUWJGCQKKLGEUQRBFAJWZBC999999'
          ),

        address =
          Address(
            b'YOTMYW9YLZQCSLHB9WRSTZDYYYGUUWLVDRHFQFEX'
            b'UVOQARTQWZGLBU9DVSRDPCWYWQZHLFHY9NGLPZRAQ'
          ),

        branch_transaction_hash =
          TransactionHash(
            b'QCHKLZZBG9XQMNGCDVXZGDRXIJMFZP9XUGAWNNVP'
            b'GXBWB9NVEKEFMUWOEACULFUR9Q9XCWPBRNF999999'
          ),

        bundle_hash =
          BundleHash(
            b'ZSATLX9HDENCIARERVLWYHXPQETFL9QKTNC9LUOL'
            b'CDXKKW9MYTLZJDXBNOHURUXSYWMGGD9UDGLHCSZO9'
          ),

        nonce =
          Nonce(
            b'TPGXQFUGNEYYFFKPFWJSXKTWEUK'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'UKGIAYNLALFGJOVUZYJGNIOZSXBBZDXVQLUMHGQE'
            b'PZJWYDMGTPJIQXS9GOKXR9WIGWFRWRSKGCJ999999'
          ),

        signature_message_fragment = Fragment(b''),

        current_index                     = 3,
        last_index                        = 3,
        tag                               = Tag(b''),
        timestamp                         = 1483033814,
        value                             = 98,
        attachment_timestamp              = 0,
        attachment_timestamp_lower_bound  = 0,
        attachment_timestamp_upper_bound  = 0,
      ),
    ])

    mock_get_bundles =\
      mock.Mock(return_value={
        'bundles': [bundle],
      })

    send_trytes_response = {
      'trytes': bundle.as_tryte_strings(),
    }

    def mock_send_trytes(_,request):
      """
      Ensures that the correct trytes are sent to the ``sendTrytes`` command
      to replay the bundle.

      References:
        - https://github.com/iotaledger/iota.lib.py/issues/74
      """
      self.assertEqual(request['trytes'], send_trytes_response['trytes'])
      return send_trytes_response

    with mock.patch(
        'iota.commands.extended.get_bundles.GetBundlesCommand._execute',
        mock_get_bundles,
    ):
      with mock.patch(
          'iota.commands.extended.send_trytes.SendTrytesCommand._execute',
          mock_send_trytes,
      ):
        response = self.command(
          depth               = 100,
          minWeightMagnitude  = 18,
          transaction         = bundle[0].hash,
        )

    self.assertDictEqual(response, send_trytes_response)
