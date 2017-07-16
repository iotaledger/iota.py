# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Tuple
from unittest import TestCase

from iota import Address, Bundle, BundleHash, BundleValidator, Fragment, Hash, \
  Tag, Transaction, TransactionHash


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

    self.assertListEqual(validator.errors, [])
    self.assertTrue(validator.is_valid())

  def test_pass_empty(self):
    """
    Bundle has no transactions.
    """
    validator = BundleValidator(Bundle())

    self.assertListEqual(validator.errors, [])
    self.assertTrue(validator.is_valid())

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
        'Transaction 1 has invalid signature (using 1 fragments).',
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
        'Transaction 1 has invalid signature (using 1 fragments).',
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
