# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address, Bundle, BundleHash, Fragment, Hash, \
  Tag, Transaction, TransactionHash, TransactionTrytes, TryteString, Nonce


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

        current_index                     = 0,
        last_index                        = 7,
        value                             = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 1,
        last_index                        = 7,
        value                             = 10,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 2,
        last_index                        = 7,
        value                             = 20,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 4,
        last_index                        = 7,
        value                             = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 5,
        last_index                        = 7,
        value                             = -100,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 6,
        last_index                        = 7,
        value                             = 0,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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

        current_index                     = 7,
        last_index                        = 7,
        value                             = 40,

        # These values are not relevant to the tests.
        branch_transaction_hash           = TransactionHash(b''),
        bundle_hash                       = BundleHash(b''),
        hash_                             = TransactionHash(b''),
        nonce                             = Nonce(b''),
        timestamp                         = 1485020456,
        trunk_transaction_hash            = TransactionHash(b''),
        tag                               = Tag(b''),
        attachment_timestamp              = 1485020456,
        attachment_timestamp_upper_bound  = 1485020456,
        attachment_timestamp_lower_bound  = 1485020456,
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


class TransactionTestCase(TestCase):
  """
  If you need to generate values for these tests using the JS lib, you
  can leverage the following functions:

  - ``lib/utils/utils.js:transactionObject``:  Convert a sequence of
    trytes into an object that you can manipulate easily.
  - ``lib/utils/utils.js:transactionTrytes``:  Convert an object back
    into a tryte sequence.
  """
  # noinspection SpellCheckingInspection
  def test_from_tryte_string(self):
    """
    Initializing a Transaction object from a TryteString.

    References:
      - http://iotasupport.com/news/index.php/2016/12/02/fixing-the-latest-solid-subtangle-milestone-issue/
    """
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
        b'UCUEMD9M9SQJ999999999999999999999999999999999RKWEEVD99RKWEEVD99RKW'
        b'EEVD99999999999999999999999999999'
      )

    transaction = Transaction.from_tryte_string(trytes)

    self.assertIsInstance(transaction, Transaction)

    self.assertEqual(
      transaction.hash,

      Hash(
        b'JBVVEWEPYNZ9KRHNUUTRENXXAVXT9MKAVPAUQ9SJ'
        b'NSIHDCPQM9LJHIZGXO9PIRWUUVBOXNCBE9XJGMOZF'
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
    self.assertEqual(transaction.legacy_tag, Tag(b'999999999999999999999999999'))
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
    
    self.assertEqual(transaction.tag, Tag(b'999999999999999999999999999'))
    self.assertEqual(transaction.attachment_timestamp,1480690413)
    self.assertEqual(transaction.attachment_timestamp_lower_bound,1480690413)
    self.assertEqual(transaction.attachment_timestamp_upper_bound,1480690413)

    self.assertEqual(
      transaction.nonce,

      Nonce(
        b'999999999999999999999999999'
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
          b'SYABNCYPLULQQBTDCUWJPVVMYNWHKEHGAZPKRBGE'
          b'QKEHUIKJCHWGAUKLSYMDOUUBMXPKCPTNFWUFU9JKW'
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
          b'99999999999999999999999999999999999999999'
          b'9999999999999999999999999999999999999999'
        ),

      value         = 0,
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
        
      tag                               = Tag(b'999999999999999999999999999'),
      attachment_timestamp              = 1480690413,
      attachment_timestamp_lower_bound  = 1480690413,
      attachment_timestamp_upper_bound  = 1480690413,
      

      nonce =
        Nonce(
          b'999999999999999999999999999'
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
        b'UCUEMD9M9SQJ999999999999999999999999999999999RKWEEVD99RKWEEVD99RKW'
        b'EEVD99999999999999999999999999999'
      ),
    )
