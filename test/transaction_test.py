# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Tuple
from unittest import TestCase

from mock import patch

from iota import Address, Bundle, BundleHash, Fragment, Hash, ProposedBundle, \
  ProposedTransaction, Tag, Transaction, TransactionHash, TransactionTrytes, \
  TryteString, trits_from_int
from iota.crypto.addresses import AddressGenerator
from iota.crypto.signing import KeyGenerator
from iota.transaction import BundleValidator
from six import binary_type


class BundleValidatorTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(BundleValidatorTestCase, self).setUp()

    # Define a valid bundle that will serve as the happy path.
    # We will mangle it in various ways to trigger validation errors.
    self.bundle = Bundle([
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
          Hash(
            b'LIJVXBVTYMEEPCKJRIQTGAKWJRAMYNPJEGHEWAUL'
            b'XPBBUQPCJTJPRZTISQPJRJGMSBGQLER9OXYQXFGQO'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'KFCQSGDYENCECCPNNZDVDTBINCBRBERPTQIHFH9G'
            b'YLTCSGUFMVWWSAHVZFXDVEZO9UHAUIU9LNX999999'
          ),

        signature_message_fragment = Fragment(b''),

        current_index = 0,
        last_index    = 3,
        tag           = Tag(b''),
        timestamp     = 1483033814,
        value         = 1,
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
          Hash(
            b'VRYLDCKEWZJXPQVSWOJVYVBJSCWZQEVKPBG9KGEZ'
            b'GPRQFKFSRNBPXCSVQNJINBRNEPIKAXNHOTJFIVYJO'
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

        current_index = 1,
        last_index    = 3,
        tag           = Tag(b''),
        timestamp     = 1483033814,
        value         = -99,
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
          Hash(
            b'AAKVYZOEZSOXTX9LOLHZYLNAS9CXBLSWVZQAMRGW'
            b'YW9GHHMVIOHWBMTXHDBXRTF9DEFFQFQESNVJORNXK'
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

        current_index = 2,
        last_index    = 3,
        tag           = Tag(b''),
        timestamp     = 1483033814,
        value         = 0,
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
          Hash(
            b'TPGXQFUGNEYYFFKPFWJSXKTWEUKUFTRJCQKKXLXL'
            b'PSOHBZTGIBFPGLSVRIVYAC9NZMOMZLARFZYCNNRCM'
          ),

        trunk_transaction_hash =
          TransactionHash(
            b'UKGIAYNLALFGJOVUZYJGNIOZSXBBZDXVQLUMHGQE'
            b'PZJWYDMGTPJIQXS9GOKXR9WIGWFRWRSKGCJ999999'
          ),

        signature_message_fragment = Fragment(b''),

        current_index = 3,
        last_index    = 3,
        tag           = Tag(b''),
        timestamp     = 1483033814,
        value         = 98,
      ),
    ])

  def test_pass_happy_path(self):
    """
    Bundle passes validation.
    """
    validator = BundleValidator(self.bundle)

    self.assertTrue(validator.is_valid())
    self.assertListEqual(validator.errors, [])

  def test_pass_empty(self):
    """
    Bundle has no transactions.
    """
    validator = BundleValidator(Bundle())

    self.assertTrue(validator.is_valid())
    self.assertListEqual(validator.errors, [])

  def test_fail_balance_positive(self):
    """
    The bundle balance is > 0.
    """
    self.bundle.transactions[0].value += 1

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Bundle has invalid balance (expected 0, actual 1).',
      ],
    )

  def test_fail_balance_negative(self):
    """
    The bundle balance is < 0.
    """
    self.bundle.transactions[3].value -= 1

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Bundle has invalid balance (expected 0, actual -1).',
      ],
    )

  def test_fail_bundle_hash_invalid(self):
    """
    One of the transactions has an invalid ``bundle_hash`` value.
    """
    # noinspection SpellCheckingInspection
    self.bundle.transactions[3].bundle_hash =\
      BundleHash(
        b'NFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
        b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PG'
      )

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Transaction 3 has invalid bundle hash.',
      ],
    )

  def test_fail_current_index_invalid(self):
    """
    One of the transactions has an invalid ``current_index`` value.
    """
    self.bundle.transactions[3].current_index = 4

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Transaction 3 has invalid current index value '
        '(expected 3, actual 4).',
      ],
    )

  def test_fail_last_index_invalid(self):
    """
    One of the transactions has an invalid ``last_index`` value.
    """
    self.bundle.transactions[0].last_index = 2

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Transaction 0 has invalid last index value '
        '(expected 3, actual 2).'
      ],
    )

  def test_fail_missing_signature_fragment_underflow(self):
    """
    The last transaction in the bundle is an input, and its second
    signature fragment is missing.
    """
    # Remove the last input's second signature fragment, and the change
    # transaction.
    del self.bundle.transactions[-2:]
    for (i, txn) in enumerate(self.bundle): # type: Tuple[int, Transaction]
      txn.current_index = i
      txn.last_index    = 1

    # Fix bundle balance, since we removed the change transaction.
    self.bundle[1].value = -self.bundle[0].value

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Reached end of bundle while looking for '
        'signature fragment 2 for transaction 1.'
      ],
    )

  def test_fail_signature_fragment_address_wrong(self):
    """
    The second signature fragment for an input is associated with the
    wrong address.
    """
    # noinspection SpellCheckingInspection
    self.bundle[2].address =\
      Address(
        b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9P'
        b'GNFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
      )

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Unable to find signature fragment 2 for transaction 1.'
      ],
    )

  def test_fail_signature_fragment_value_wrong(self):
    """
    The second signature fragment for an input has a nonzero balance.
    """
    self.bundle[2].value = -1
    self.bundle[-1].value += 1

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Transaction 2 has invalid amount (expected 0, actual -1).',
      ],
    )

  def test_fail_signature_invalid(self):
    """
    One of the input signatures fails validation.
    """
    self.bundle[2].signature_message_fragment[:-1] = b'9'

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      [
        'Transaction 1 has invalid signature (using 2 fragments).',
      ],
    )

  def test_fail_multiple_errors(self):
    """
    The bundle has multiple problems.
    """
    del self.bundle.transactions[2]

    validator = BundleValidator(self.bundle)

    self.assertFalse(validator.is_valid())

    self.assertListEqual(
      validator.errors,

      # Note that there is no error about the missing signature
      # fragment for transaction 1.  The bundle fails some basic
      # consistency checks, so we don't even bother to validate
      # signatures.
      [
        'Transaction 0 has invalid last index value '
        '(expected 2, actual 3).',

        'Transaction 1 has invalid last index value '
        '(expected 2, actual 3).',

        'Transaction 2 has invalid current index value '
        '(expected 2, actual 3).',

        'Transaction 2 has invalid last index value '
        '(expected 2, actual 3).',
      ],
    )


# noinspection SpellCheckingInspection
class ProposedBundleTestCase(TestCase):
  def setUp(self):
    super(ProposedBundleTestCase, self).setUp()

    self.bundle = ProposedBundle()

  def test_add_transaction_short_message(self):
    """
    Adding a transaction to a bundle, with a message short enough to
    fit inside a single transaction.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999AETEXB'
          b'D9YBTH9EMFKF9CAHJIAIKDBEPAMH99DEN9DAJETGN'
        ),

      message = TryteString.from_string('Hello, IOTA!'),
      value   = 42,
    ))

    # We can fit the message inside a single fragment, so only one
    # transaction is necessary.
    self.assertEqual(len(self.bundle), 1)

  def test_add_transaction_long_message(self):
    """
    Adding a transaction to a bundle, with a message so long that it
    has to be split into multiple transactions.
    """
    address = Address(
      b'TESTVALUE9DONTUSEINPRODUCTION99999N9GIUF'
      b'HCFIUGLBSCKELC9IYENFPHCEWHIDCHCGGEH9OFZBN'
    )

    tag = Tag.from_string('H2G2')

    self.bundle.add_transaction(ProposedTransaction(
      address = address,
      tag     = tag,

      message = TryteString.from_string(
        '''
"Good morning," said Deep Thought at last.
"Er... Good morning, O Deep Thought," said Loonquawl nervously.
  "Do you have... er, that is..."
"... an answer for you?" interrupted Deep Thought majestically. "Yes. I have."
The two men shivered with expectancy. Their waiting had not been in vain.
"There really is one?" breathed Phouchg.
"There really is one," confirmed Deep Thought.
"To Everything? To the great Question of Life, the Universe and Everything?"
"Yes."
Both of the men had been trained for this moment; their lives had been a
  preparation for it; they had been selected at birth as those who would
  witness the answer; but even so they found themselves gasping and squirming
  like excited children.
"And you're ready to give it to us?" urged Loonquawl.
"I am."
"Now?"
"Now," said Deep Thought.
They both licked their dry lips.
"Though I don't think," added Deep Thought, "that you're going to like it."
"Doesn't matter," said Phouchg. "We must know it! Now!"
"Now?" enquired Deep Thought.
"Yes! Now!"
"All right," said the computer and settled into silence again.
  The two men fidgeted. The tension was unbearable.
"You're really not going to like it," observed Deep Thought.
"Tell us!"
"All right," said Deep Thought. "The Answer to the Great Question..."
"Yes?"
"Of Life, the Universe and Everything..." said Deep Thought.
"Yes??"
"Is..."
"Yes?!"
"Forty-two," said Deep Thought, with infinite majesty and calm.
        '''
      ),

      # Now you know...
      value = 42,
    ))

    # Because the message is too long to fit into a single fragment,
    # the transaction is split into two parts.
    self.assertEqual(len(self.bundle), 2)

    txn1 = self.bundle[0]
    self.assertEqual(txn1.address, address)
    self.assertEqual(txn1.tag, tag)
    self.assertEqual(txn1.value, 42)

    txn2 = self.bundle[1]
    self.assertEqual(txn2.address, address)
    self.assertEqual(txn2.tag, tag)
    # Supplementary transactions are assigned zero IOTA value.
    self.assertEqual(txn2.value, 0)

  def test_add_transaction_error_already_finalized(self):
    """
    Attempting to add a transaction to a bundle that is already
    finalized.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION999999DCBIE'
          b'U9AIE9H9BCKGMCVCUGYDKDLCAEOHOHZGW9KGS9VGH'
        ),

        value = 0,
    ))
    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.add_transaction(ProposedTransaction(
        address = Address(b''),
        value   = 0,
      ))

  def test_add_transaction_error_negative_value(self):
    """
    Attempting to add a transaction with a negative value to a bundle.

    Use :py:meth:`ProposedBundle.add_inputs` to add inputs to a bundle.
    """
    with self.assertRaises(ValueError):
      self.bundle.add_transaction(ProposedTransaction(
        address = Address(b''),
        value   = -1,
      ))

  def test_add_inputs_no_change(self):
    """
    Adding inputs to cover the exact amount of the bundle spend.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999VELDTF'
          b'QHDFTHIHFE9II9WFFDFHEATEI99GEDC9BAUH9EBGZ'
        ),

        value = 29,
    ))

    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999OGVEEF'
          b'BCYAM9ZEAADBGBHH9BPBOHFEGCFAM9DESCCHODZ9Y'
        ),

      value = 13,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999VAFFMC'
          b'X9AABIH9AEEGJHKFSHTGYHSFR9DEH9MEDAGGIGK9E',

        balance   = 40,
        key_index = 0,
      ),

      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999VDR9AD'
          b'OEH9YGGHGDVBCAREVBDHOFAGNDZCPBBAAIUCDGQ9Z',

        balance   = 2,
        key_index = 1,
      ),
    ])

    # Because transaction signatures are so large, each input
    # transaction must be split into multiple parts.
    expected_length = 2 + (2 * AddressGenerator.DIGEST_ITERATIONS)

    self.assertEqual(len(self.bundle), expected_length)

    self.bundle.send_unspent_inputs_to(
      Address(
        b'TESTVALUE9DONTUSEINPRODUCTION99999FDCDFD'
        b'VAF9NFLCSCSFFCLCW9KFL9TCAAO9IIHATCREAHGEA'
      ),
    )
    self.bundle.finalize()

    # Because the transaction is already balanced, no change
    # transaction is necessary.
    self.assertEqual(len(self.bundle), expected_length)


  def test_add_inputs_with_change(self):
    """
    Adding inputs to a bundle results in unspent inputs.
    """
    tag = Tag(b'CHANGE9TXN')

    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999VELDTF'
          b'QHDFTHIHFE9II9WFFDFHEATEI99GEDC9BAUH9EBGZ'
        ),

        value = 29,
    ))

    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999OGVEEF'
          b'BCYAM9ZEAADBGBHH9BPBOHFEGCFAM9DESCCHODZ9Y'
        ),

      tag   = tag,
      value = 13,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999VAFFMC'
          b'X9AABIH9AEEGJHKFSHTGYHSFR9DEH9MEDAGGIGK9E',

        balance   = 40,
        key_index = 0,
      ),

      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999VDR9AD'
          b'OEH9YGGHGDVBCAREVBDHOFAGNDZCPBBAAIUCDGQ9Z',

        balance   = 20,
        key_index = 1,
      ),
    ])

    change_address =\
      Address(
        b'TESTVALUE9DONTUSEINPRODUCTION99999KAFGVC'
        b'IBLHS9JBZCEFDELEGFDCZGIEGCPFEIQEYGA9UFPAE'
      )

    self.bundle.send_unspent_inputs_to(change_address)

    # The change transaction is not created until the bundle is
    # finalized.
    expected_length = 2 + (2 * AddressGenerator.DIGEST_ITERATIONS)

    self.assertEqual(len(self.bundle), expected_length)

    self.bundle.finalize()

    self.assertEqual(len(self.bundle), expected_length + 1)

    change_txn = self.bundle[-1]
    self.assertEqual(change_txn.address, change_address)
    self.assertEqual(change_txn.value, 18)
    self.assertEqual(change_txn.tag, tag)

  def test_add_inputs_error_already_finalized(self):
    """
    Attempting to add inputs to a bundle that is already finalized.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
          b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH'
        ),

      value = 0,
    ))

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.add_inputs([])

  def test_send_unspent_inputs_to_error_already_finalized(self):
    """
    Invoking ``send_unspent_inputs_to`` on a bundle that is already
    finalized.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
          b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH'
        ),

      value = 0,
    ))

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.send_unspent_inputs_to(Address(b''))

  def test_finalize_error_already_finalized(self):
    """
    Attempting to finalize a bundle that is already finalized.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
          b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH'
        ),

      value = 0,
    ))

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.finalize()

  def test_finalize_error_no_transactions(self):
    """
    Attempting to finalize a bundle with no transactions.
    """
    with self.assertRaises(ValueError):
      self.bundle.finalize()

  def test_finalize_error_negative_balance(self):
    """
    Attempting to finalize a bundle with unspent inputs.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999IGEFUG'
          b'LIHIJGJGZ9CGRENCRHF9XFEAWD9ILFWEJFKDLITCC'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999LAHFJ9'
          b'Z9QEHGIHTAQFWFAHYEKFDBXHSBM9K9T9S9SBTF99W',

        balance   = 43,
        key_index = 0,
      ),
    ])

    # Bundle spends 42 IOTAs, but inputs total 43 IOTAs.
    self.assertEqual(self.bundle.balance, -1)

    # In order to finalize this bundle, we would need to specify a
    # change address.
    with self.assertRaises(ValueError):
      self.bundle.finalize()

  def test_finalize_error_positive_balance(self):
    """
    Attempting to finalize a bundle with insufficient inputs.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999IGEFUG'
          b'LIHIJGJGZ9CGRENCRHF9XFEAWD9ILFWEJFKDLITCC'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999LAHFJ9'
          b'Z9QEHGIHTAQFWFAHYEKFDBXHSBM9K9T9S9SBTF99W',

        balance   = 41,
        key_index = 0,
      ),
    ])

    # Bundle spends 42 IOTAs, but inputs total only 41 IOTAs.
    self.assertEqual(self.bundle.balance, 1)

    # In order to finalize this bundle, we would need to specify
    # additional inputs.
    with self.assertRaises(ValueError):
      self.bundle.finalize()

  def test_sign_inputs(self):
    """
    Signing inputs in a finalized bundle.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999UGYFU9'
          b'TGMHNEN9S9CAIDUBGETHJHFHRAHGRGVF9GTDYHXCE',

        balance   = 42,
        key_index = 0,
      )
    ])

    self.bundle.finalize()

    # Mock the signature generator to improve test performance.
    # We already have unit tests for signature generation; all we need
    # to do here is verify that the method is invoked correctly.
    # noinspection PyUnusedLocal
    def mock_signature_generator(bundle, key_generator, txn):
      for i in range(AddressGenerator.DIGEST_ITERATIONS):
        yield Fragment.from_trits(trits_from_int(i))

    with patch(
        'iota.transaction.ProposedBundle._create_signature_fragment_generator',
        mock_signature_generator,
    ):
      self.bundle.sign_inputs(KeyGenerator(b''))

    self.assertEqual(
      len(self.bundle),

      # Spend txn + input fragments
      1 + AddressGenerator.DIGEST_ITERATIONS,
    )

    # The spending transaction does not have a signature.
    self.assertEqual(
      self.bundle[0].signature_message_fragment,
      Fragment(b''),
    )

    for j in range(AddressGenerator.DIGEST_ITERATIONS):
      self.assertEqual(
        self.bundle[j+1].signature_message_fragment,
        Fragment.from_trits(trits_from_int(j)),
      )

  def test_sign_inputs_error_not_finalized(self):
    """
    Attempting to sign inputs in a bundle that hasn't been finalized
    yet.
    """
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999UGYFU9'
          b'TGMHNEN9S9CAIDUBGETHJHFHRAHGRGVF9GTDYHXCE',

        balance   = 42,
        key_index = 0,
      )
    ])

    with self.assertRaises(RuntimeError):
      self.bundle.sign_inputs(KeyGenerator(b''))


# noinspection SpellCheckingInspection
class TransactionHashTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Transaction hashes are automatically padded to 81 trytes.
    """
    txn = TransactionHash(
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC'
    )

    self.assertEqual(
      binary_type(txn),

      # Note the extra 9's added to the end.
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
    )

  def test_init_error_too_long(self):
    """
    Attempting to create a transaction hash longer than 81 trytes.
    """
    with self.assertRaises(ValueError):
      TransactionHash(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC99999'
      )


class TransactionTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def test_from_tryte_string(self):
    """
    Initializing a Transaction object from a TryteString.
    """
    # :see: http://iotasupport.com/news/index.php/2016/12/02/fixing-the-latest-solid-subtangle-milestone-issue/
    trytes =\
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

    transaction = Transaction.from_tryte_string(trytes)

    self.assertIsInstance(transaction, Transaction)

    self.assertEqual(
      transaction.hash,

      Hash(
        b'QODOAEJHCFUYFTTPRONYSMMSFDNFWFX9UCMESVWA'
        b'FCVUQYOIJGJMBMGQSFIAFQFMVECYIFXHRGHHEOTMK'
      ),
    )

    self.assertEqual(
      transaction.signature_message_fragment,

      Fragment(
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
        b'999999999'
      ),
    )

    self.assertEqual(
      transaction.address,

      Address(
        b'9999999999999999999999999999999999999999'
        b'99999999999999999999999999999999999999999'
      ),
    )

    self.assertEqual(transaction.value, 0)
    self.assertEqual(transaction.tag, Tag(b'999999999999999999999999999'))
    self.assertEqual(transaction.timestamp, 1480690413)
    self.assertEqual(transaction.current_index, 1)
    self.assertEqual(transaction.last_index, 1)

    self.assertEqual(
      transaction.bundle_hash,

      BundleHash(
        b'NFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
        b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PG'
      ),
    )

    self.assertEqual(
      transaction.trunk_transaction_hash,

      TransactionHash(
        b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
        b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
      ),
    )

    self.assertEqual(
      transaction.branch_transaction_hash,

      TransactionHash(
        b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
        b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
      ),
    )

    self.assertEqual(
      transaction.nonce,

      Hash(
        b'9999999999999999999999999999999999999999'
        b'99999999999999999999999999999999999999999'
      ),
    )

  # noinspection SpellCheckingInspection
  def test_as_tryte_string(self):
    """
    Converting a Transaction into a TryteString.
    """
    transaction = Transaction(
      hash_ =
        TransactionHash(
          b'QODOAEJHCFUYFTTPRONYSMMSFDNFWFX9UCMESVWA'
          b'FCVUQYOIJGJMBMGQSFIAFQFMVECYIFXHRGHHEOTMK'
        ),

      signature_message_fragment =
        Fragment(
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
          b'999999999'
        ),

      address =
        Address(
          b'9999999999999999999999999999999999999999'
          b'99999999999999999999999999999999999999999'
        ),

      value         = 0,
      tag           = Tag(b'999999999999999999999999999'),
      timestamp     = 1480690413,
      current_index = 1,
      last_index    = 1,

      bundle_hash =
        BundleHash(
          b'NFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
          b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PG'
        ),

      trunk_transaction_hash =
        TransactionHash(
          b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
          b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
        ),

      branch_transaction_hash =
        TransactionHash(
          b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
          b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
        ),

      nonce =
        Hash(
          b'9999999999999999999999999999999999999999'
          b'99999999999999999999999999999999999999999'
        ),
    )

    self.assertEqual(
      transaction.as_tryte_string(),

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
        b'999999999999999999999999999999999',
      ),
    )
