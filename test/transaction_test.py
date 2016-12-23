# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address, BundleHash, Hash, Tag, Transaction, \
  TransactionHash, TryteString
from six import binary_type


class ProposedBundleTestCase(TestCase):
  def test_add_transaction_short_message(self):
    """
    Adding a transaction to a bundle, with a message short enough to
    fit inside a single transaction.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_transaction_long_message(self):
    """
    Adding a transaction to a bundle, with a message so long that it
    has to be split into multiple transactions.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_transaction_error_already_finalized(self):
    """
    Attempting to add a transaction to a bundle that is already
    finalized.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_transaction_error_negative_value(self):
    """
    Attempting to add a transaction with a negative value to a bundle.

    Use :py:meth:`ProposedBundle.add_inputs` to add inputs to a bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_inputs_balanced(self):
    """
    Adding inputs to cover the exact amount of the bundle spend.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_inputs_with_change(self):
    """
    Adding inputs to a bundle results in unspent inputs.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_add_inputs_error_already_finalized(self):
    """
    Attempting to add inputs to a bundle that is already finalized.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_send_unspent_inputs_to_unbalanced(self):
    """
    Invoking ``send_unspent_inputs_to`` on an unbalanced bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_send_unspent_inputs_to_balanced(self):
    """
    Invoking ``send_unspent_inputs_to`` on a balanced bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_send_unspent_inputs_to_error_already_finalized(self):
    """
    Invoking ``send_unspent_inputs_to`` on a bundle that is already
    finalized.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_finalize_happy_path(self):
    """
    Finalizing a bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_finalize_error_already_finalized(self):
    """
    Attempting to finalize a bundle that is already finalized.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_finalize_error_unbalanced(self):
    """
    Attempting to finalize an unbalanced bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_sign_inputs(self):
    """
    Signing inputs in a finalized bundle.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_sign_inputs_error_not_finalized(self):
    """
    Attempting to sign inputs in a bundle that hasn't been finalized
    yet.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


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
    trytes = (
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

      TryteString(
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
      transaction.bundle_id,

      BundleHash(
        b'NFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
        b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PG'
      ),
    )

    self.assertEqual(
      transaction.trunk_transaction_id,

      TransactionHash(
        b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
        b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
      ),
    )

    self.assertEqual(
      transaction.branch_transaction_id,

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

  def test_from_tryte_string_error_too_short(self):
    """
    Attempting to create a Transaction from a TryteString that is too
    short.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_from_tryte_string_error_too_long(self):
    """
    Attempting to create a Transaction from a TryteString that is too
    long.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  # noinspection SpellCheckingInspection
  def test_as_tryte_string(self):
    """
    Converting a Transaction into a TryteString.
    """
    transaction = Transaction(
      hash_ =
        Hash(
          b'QODOAEJHCFUYFTTPRONYSMMSFDNFWFX9UCMESVWA'
          b'FCVUQYOIJGJMBMGQSFIAFQFMVECYIFXHRGHHEOTMK'
        ),

      signature_message_fragment =
        TryteString(
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

      bundle_id =
        BundleHash(
          b'NFDPEEZCWVYLKZGSLCQNOFUSENIXRHWWTZFBXMPS'
          b'QHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PG'
        ),

      trunk_transaction_id =
        TransactionHash(
          b'TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJN'
          b'QZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999999'
        ),

      branch_transaction_id =
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
    )