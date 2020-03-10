from unittest import TestCase
from iota import TransactionHash, BundleHash, Fragment, TransactionTrytes, \
  Nonce


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
      bytes(txn),

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

  def test_random(self):
    """
    Creating a random TransactionHash object.
    """
    random_tx_hash = TransactionHash.random()
    self.assertEqual(len(random_tx_hash), TransactionHash.LEN)

class BundleHashTestCase(TestCase):
  def test_random(self):
    """
    Creating a random BundleHash object.
    """
    random_bundle_hash = BundleHash.random()
    self.assertEqual(len(random_bundle_hash), BundleHash.LEN)

class FragmentTestCase(TestCase):
  def test_random(self):
    """
    Creating a random Fragment object.
    """
    random_fragment = Fragment.random()
    self.assertEqual(len(random_fragment), Fragment.LEN)

class TransactionTrytesTestCase(TestCase):
  def test_random(self):
    """
    Creating a random TransactionTrytes object.
    """
    random_tx_trytes = TransactionTrytes.random()
    self.assertEqual(len(random_tx_trytes), TransactionTrytes.LEN)

class NonceTestCase(TestCase):
  def test_random(self):
    """
    Creating a random Nonce object.
    """
    random_nonce = Nonce.random()
    self.assertEqual(len(random_nonce), Nonce.LEN)