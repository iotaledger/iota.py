# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from typing import Tuple

from iota import Address, Bundle, BundleHash, Fragment, Hash, \
  Tag, Transaction, TransactionHash, TransactionTrytes
from iota.transaction.validator import BundleValidator


class BundleTestCase(TestCase):
  def setUp(self):
    super(BundleTestCase, self).setUp()

    # noinspection SpellCheckingInspection
    self.bundle = Bundle([
      # This transaction does not have a message.
      Transaction(
        signature_message_fragment = Fragment(b''),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999A9PG9A'
            b'XCQANAWGJBTFWEAEQCN9WBZB9BJAIIY9UDLIGFOAA'
          ),

        current_index           = 0,
        last_index              = 7,
        value                   = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # This transaction has something that can't be decoded as a UTF-8
      # sequence.
      Transaction(
        signature_message_fragment =
          Fragment(b'OHCFVELH9GYEMHCF9GPHBGIEWHZFU'),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999HAA9UA'
            b'MHCGKEUGYFUBIARAXBFASGLCHCBEVGTBDCSAEBTBM'
          ),

        current_index           = 1,
        last_index              = 7,
        value                   = 10,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # This transaction has a message that fits into a single
      # fragment.
      Transaction(
        signature_message_fragment =
          Fragment.from_string('Hello, world!'),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999D99HEA'
            b'M9XADCPFJDFANCIHR9OBDHTAGGE9TGCI9EO9ZCRBN'
          ),

        current_index           = 2,
        last_index              = 7,
        value                   = 20,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # This transaction has a message that spans multiple fragments.
      Transaction(
        signature_message_fragment =
          Fragment(
            b'J9GAQBCDCDSCEAADCDFDBDXCBDVCQAGAEAGDPCXCSCEANBTCTCDDEACCWCCDIDVC'
            b'WCHDEAPCHDEA9DPCGDHDSAJ9GAOBFDSASASAEAQBCDCDSCEAADCDFDBDXCBDVCQA'
            b'EAYBEANBTCTCDDEACCWCCDIDVCWCHDQAGAEAGDPCXCSCEAVBCDCDBDEDIDPCKD9D'
            b'EABDTCFDJDCDIDGD9DMDSAJ9EAEAGANBCDEAMDCDIDEAWCPCJDTCSASASAEATCFD'
            b'QAEAHDWCPCHDEAXCGDSASASAGAJ9GASASASAEAPCBDEAPCBDGDKDTCFDEAUCCDFD'
            b'EAMDCDIDIBGAEAXCBDHDTCFDFDIDDDHDTCSCEANBTCTCDDEACCWCCDIDVCWCHDEA'
            b'ADPCYCTCGDHDXCRCPC9D9DMDSAEAGAHCTCGDSAEASBEAWCPCJDTCSAGAJ9CCWCTC'
            b'EAHDKDCDEAADTCBDEAGDWCXCJDTCFDTCSCEAKDXCHDWCEATCLDDDTCRCHDPCBDRC'
            b'MDSAEACCWCTCXCFDEAKDPCXCHDXCBDVCEAWCPCSCEABDCDHDEAQCTCTCBDEAXCBD'
            b'EAJDPCXCBDSAJ9GACCWCTCFDTCEAFDTCPC9D9DMDEAXCGDEACDBDTCIBGAEAQCFD'
            b'TCPCHDWCTCSCEAZBWCCDIDRCWCVCSAJ9GACCWCTCFDTCEAFDTCPC9D9DMDEAXCGD'
            b'EACDBDTCQAGAEARCCDBDUCXCFDADTCSCEANBTCTCDDEACCWCCDIDVCWCHDSAJ9GA'
            b'CCCDEAOBJDTCFDMDHDWCXCBDVCIBEACCCDEAHDWCTCEAVCFDTCPCHDEA9CIDTCGD'
            b'HDXCCDBDEACDUCEAVBXCUCTCQAEAHDWCTCEADCBDXCJDTCFDGDTCEAPCBDSCEAOB'
            b'JDTCFDMDHDWCXCBDVCIBGAJ9GAHCTCGDSAGAJ9LBCDHDWCEACDUCEAHDWCTCEAAD'
            b'TCBDEAWCPCSCEAQCTCTCBDEAHDFDPCXCBDTCSCEAUCCDFDEAHDWCXCGDEAADCDAD'
            b'TCBDHDEBEAHDWCTCXCFDEA9DXCJDTCGDEAWCPCSCEAQCTCTCBDEAPCJ9EAEADDFD'
            b'TCDDPCFDPCHDXCCDBDEAUCCDFDEAXCHDEBEAHDWCTCMDEAWCPCSCEAQCTCTCBDEA'
            b'GDTC9DTCRCHDTCSCEAPCHDEAQCXCFDHDWCEAPCGDEAHDWCCDGDTCEAKDWCCDEAKD'
            b'CDID9DSCJ9EAEAKDXCHDBDTCGDGDEAHDWCTCEAPCBDGDKDTCFDEBEAQCIDHDEATC'
            b'JDTCBDEAGDCDEAHDWCTCMDEAUCCDIDBDSCEAHDWCTCADGDTC9DJDTCGDEAVCPCGD'
            b'DDXCBDVCEAPCBDSCEAGDEDIDXCFDADXCBDVCJ9EAEA9DXCZCTCEATCLDRCXCHDTC'
            b'SCEARCWCXC9DSCFDTCBDSAJ9GAKBBDSCEAMDCDIDLAFDTCEAFDTCPCSCMDEAHDCD'
            b'EAVCXCJDTCEAXCHDEAHDCDEAIDGDIBGAEAIDFDVCTCSCEAVBCDCDBDEDIDPCKD9D'
            b'SAJ9GASBEAPCADSAGAJ9GAXBCDKDIBGAJ9GAXBCDKDQAGAEAGDPCXCSCEANBTCTC'
            b'DDEACCWCCDIDVCWCHDSAJ9CCWCTCMDEAQCCDHDWCEA9DXCRCZCTCSCEAHDWCTCXC'
            b'FDEASCFDMDEA9DXCDDGDSAJ9GACCWCCDIDVCWCEASBEASCCDBDLAHDEAHDWCXCBD'
            b'ZCQAGAEAPCSCSCTCSCEANBTCTCDDEACCWCCDIDVCWCHDQAEAGAHDWCPCHDEAMDCD'
            b'IDLAFDTCEAVCCDXCBDVCEAHDCDEA9DXCZCTCEAXCHDSAGAJ9GANBCDTCGDBDLAHD'
            b'EAADPCHDHDTCFDQAGAEAGDPCXCSCEAZBWCCDIDRCWCVCSAEAGAFCTCEAADIDGDHD'
            b'EAZCBDCDKDEAXCHDFAEAXBCDKDFAGAJ9GAXBCDKDIBGAEATCBDEDIDXCFDTCSCEA'
            b'NBTCTCDDEACCWCCDIDVCWCHDSAJ9GAHCTCGDFAEAXBCDKDFAGAJ9GAKB9D9DEAFD'
            b'XCVCWCHDQAGAEAGDPCXCSCEAHDWCTCEARCCDADDDIDHDTCFDEAPCBDSCEAGDTCHD'
            b'HD9DTCSCEAXCBDHDCDEAGDXC9DTCBDRCTCEAPCVCPCXCBDSAJ9EAEACCWCTCEAHD'
            b'KDCDEAADTCB'
          ),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999A9PG9A'
            b'XCQANAWGJBTFWEAEQCN9WBZB9BJAIIY9UDLIGFOAA'
          ),

        current_index           = 3,
        last_index              = 7,
        value                   = 30,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      Transaction(
        signature_message_fragment =
          Fragment(
            b'DEAUCXCSCVCTCHDTCSCSAEACCWCTCEAHDTCBDGDXCCDBDEAKDPCGDEAIDBDQCTCP'
            b'CFDPCQC9DTCSAJ9GAHCCDIDLAFDTCEAFDTCPC9D9DMDEABDCDHDEAVCCDXCBDVCE'
            b'AHDCDEA9DXCZCTCEAXCHDQAGAEACDQCGDTCFDJDTCSCEANBTCTCDDEACCWCCDIDV'
            b'CWCHDSAJ9GACCTC9D9DEAIDGDFAGAJ9GAKB9D9DEAFDXCVCWCHDQAGAEAGDPCXCS'
            b'CEANBTCTCDDEACCWCCDIDVCWCHDSAEAGACCWCTCEAKBBDGDKDTCFDEAHDCDEAHDW'
            b'CTCEAQBFDTCPCHDEA9CIDTCGDHDXCCDBDSASASAGAJ9GAHCTCGDIBGAJ9GAYBUCE'
            b'AVBXCUCTCQAEAHDWCTCEADCBDXCJDTCFDGDTCEAPCBDSCEAOBJDTCFDMDHDWCXCB'
            b'DVCSASASAGAEAGDPCXCSCEANBTCTCDDEACCWCCDIDVCWCHDSAJ9GAHCTCGDIBIBG'
            b'AJ9GASBGDSASASAGAJ9GAHCTCGDIBFAGAJ9GAPBCDFDHDMDRAHDKDCDQAGAEAGDP'
            b'CXCSCEANBTCTCDDEACCWCCDIDVCWCHDQAEAKDXCHDWCEAXCBDUCXCBDXCHDTCEAA'
            b'DPCYCTCGDHDMDEAPCBDSCEARCPC9DADSAJ9EAEAEAEAEAEAEAEA'
          ),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999A9PG9A'
            b'XCQANAWGJBTFWEAEQCN9WBZB9BJAIIY9UDLIGFOAA'
          ),

        current_index           = 4,
        last_index              = 7,
        value                   = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # Input, Part 1 of 2
      Transaction(
        # Make the signature look like a message, so we can verify that
        # the Bundle skips it correctly.
        signature_message_fragment =
          Fragment.from_string('This is a signature, not a message!'),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999WGSBUA'
            b'HDVHYHOBHGP9VCGIZHNCAAQFJGE9YHEHEFTDAGXHY'
          ),

        current_index           = 5,
        last_index              = 7,
        value                   = -100,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # Input, Part 2 of 2
      Transaction(
        # Make the signature look like a message, so we can verify that
        # the Bundle skips it correctly.
        signature_message_fragment =
          Fragment.from_string('This is a signature, not a message!'),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999WGSBUA'
            b'HDVHYHOBHGP9VCGIZHNCAAQFJGE9YHEHEFTDAGXHY'
          ),

        current_index           = 6,
        last_index              = 7,
        value                   = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),

      # Change
      Transaction(
        # It's unusual for a change transaction to have a message, but
        # half the fun of unit tests is designing unusual scenarios!
        signature_message_fragment =
          Fragment.from_string('I can haz change?'),

        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999FFYALH'
            b'N9ACYCP99GZBSDK9CECFI9RAIH9BRCCAHAIAWEFAN'
          ),

        current_index           = 7,
        last_index              = 7,
        value                   = 40,

        # These values are not relevant to the tests.
        branch_transaction_hash = TransactionHash(b''),
        bundle_hash             = BundleHash(b''),
        hash_                   = TransactionHash(b''),
        nonce                   = Hash(b''),
        tag                     = Tag(b''),
        timestamp               = 1485020456,
        trunk_transaction_hash  = TransactionHash(b''),
      ),
    ])

  def test_get_messages_errors_drop(self):
    """
    Decoding messages from a bundle, with ``errors='drop'``.
    """
    messages = self.bundle.get_messages('drop')

    self.assertEqual(len(messages), 3)

    self.assertEqual(messages[0], 'Hello, world!')

    # noinspection SpellCheckingInspection
    self.assertEqual(
      messages[1],

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
        ''',
    )

    self.assertEqual(messages[2], 'I can haz change?')

  def test_get_messages_errors_strict(self):
    """
    Decoding messages from a bundle, with ``errors='strict'``.
    """
    with self.assertRaises(UnicodeDecodeError):
      self.bundle.get_messages('strict')

  def test_get_messages_errors_ignore(self):
    """
    Decoding messages from a bundle, with ``errors='ignore'``.
    """
    messages = self.bundle.get_messages('ignore')

    self.assertEqual(len(messages), 4)

    # The only message that is treated differently is the invalid one.
    self.assertEqual(messages[0], '祝你好运\x15')

  def test_get_messages_errors_replace(self):
    """
    Decoding messages from a bundle, with ``errors='replace'``.
    """
    messages = self.bundle.get_messages('replace')

    self.assertEqual(len(messages), 4)

    # The only message that is treated differently is the invalid one.
    self.assertEqual(messages[0], '祝你好运�\x15')


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

  def test_from_tryte_string_with_hash(self):
    """
    Initializing a Transaction object from a TryteString, with a
    pre-computed hash.
    """
    # noinspection SpellCheckingInspection
    txn_hash =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999VALCXC'
        b'DHTDZBVCAAIEZCQCXGEFYBXHNDJFZEBEVELA9HHEJ'
      )

    txn = Transaction.from_tryte_string(b'', hash_=txn_hash)

    self.assertEqual(txn.hash, txn_hash)

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
