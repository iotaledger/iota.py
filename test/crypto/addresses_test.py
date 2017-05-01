# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from threading import Thread
from time import sleep
from unittest import TestCase

from iota import Address
from iota.crypto.addresses import AddressGenerator, MemoryAddressCache
from iota.crypto.signing import KeyIterator
from iota.crypto.types import Seed
from mock import Mock, patch


class AddressGeneratorTestCase(TestCase):
  maxDiff = None

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(AddressGeneratorTestCase, self).setUp()

    self.seed_1 =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION999999GFDDC'
        b'PFIIEHBCWFN9KHRBEIHHREFCKBVGUGEDXCFHDFPAL',
      )

    self.seed_2 =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999DCZGVE'
        b'JIZEKEGEEHYE9DOHCHLHMGAFDGEEQFUDVGGDGHRDR',
      )

  def test_get_addresses_single(self):
    """
    Generating a single address.
    """
    ag = AddressGenerator(self.seed_1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0),

      [
        Address(
          b'NWQBMJEBSYFCRKGLNUQZJIOQOMNMYPCIRVSVJLP9'
          b'OFV9CZ99LFGZHDKOUDGRVJXUDPUPCVOQBKSZLPU9K',
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10),

      [
        Address(
          b'AQNURLEH9IRPVDWNRLO9JHSY9OWTKHKIJOWSPKPW'
          b'RQLMUI9KOGSXMONCXPEJMRK9MPYQXKZLNYJXNDUUZ',
        ),
      ],
    )

  def test_get_addresses_multiple(self):
    """
    Generating multiple addresses in one go.
    """
    ag = AddressGenerator(self.seed_2)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'SZWZMYQYWGXWAAVQSDTIOFGTZP9PWIDDUHHNGRDP'
          b'RCGNSXRNYWBEZIORKNNLNZHJ9QYMFYZIJJ9RFPBJT'
        ),

        Address(
          b'N9KY9HCT9VTI99FFRIIBHQZIJOVSLFVWPOIFSHWL'
          b'CCIVYLIDBKJLVQFYJNPIUNATUUCIRHUHNLFBCAXIY'
        ),

        Address(
          b'BH9BWJWHIHLJSHBYBENHLQQBOCQOOMAEJJFFBCSE'
          b'IMDVPDULGD9HBPNQKWBPM9SIDIMGUOGTPWMQSVVHZ'
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10, count=3),

      [
        Address(
          b'CCKZUWMILLQLLLIFNXBFGGPXFHNROQQOYYBMLIEOLB'
          b'PVIVFJMQAVCCGKVGNRTKAZQLKYWMTBUEVBPGZMN',
        ),

        Address(
          b'XWXALLEBVQXVRYLGPPJUL9RAIUKUXERBEMVTZJOMRB'
          b'CGXNYA99PN9DKOPAWDSIPIRUBKFQUBQFUOKZMQW',
        ),

        Address(
          b'CLYKQDU9WRHEJZSLMZKVDIWLHZKEIITWXDAHFFSQCP'
          b'LADQKLUQLSECZMIOUDSLXRWEDAEHKRVWQRGZMLI',
        ),
      ],
    )

  def test_get_addresses_error_start_too_small(self):
    """
    Providing a negative ``start`` value to ``get_addresses``.

    :py:class:`AddressGenerator` can potentially generate an infinite
    number of addresses, so there is no "end" to offset against.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=-1)

  def test_get_addresses_error_count_too_small(self):
    """
    Providing a ``count`` value less than 1 to ``get_addresses``.

    :py:class:`AddressGenerator` can potentially generate an infinite
    number of addresses, so there is no "end" to offset against.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=0, count=0)

  def test_get_addresses_error_step_zero(self):
    """
    Providing a ``step`` value of 0 to ``get_addresses``.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=0, step=0)

  def test_get_addresses_step_negative(self):
    """
    Providing a negative ``step`` value to ``get_addresses``.

    This is probably a weird use case, but what the heck.
    """
    ag = AddressGenerator(self.seed_1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=1, count=2, step=-1),

      [
        Address(
          b'DUOVVF9WCNAEOHHWUYUFSYOOWZPDVVD9JKFLQN9Z'
          b'DPAKKHSBKLTRFHD9UHIWGKSGAWCOMDG9GBPYISPWR',
        ),

        Address(
          b'NWQBMJEBSYFCRKGLNUQZJIOQOMNMYPCIRVSVJLP9'
          b'OFV9CZ99LFGZHDKOUDGRVJXUDPUPCVOQBKSZLPU9K',
        ),
      ],
    )

  def test_generator(self):
    """
    Creating a generator.
    """
    ag = AddressGenerator(self.seed_2)

    generator = ag.create_iterator()

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'SZWZMYQYWGXWAAVQSDTIOFGTZP9PWIDDUHHNGRDP'
        b'RCGNSXRNYWBEZIORKNNLNZHJ9QYMFYZIJJ9RFPBJT',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'N9KY9HCT9VTI99FFRIIBHQZIJOVSLFVWPOIFSHWL'
        b'CCIVYLIDBKJLVQFYJNPIUNATUUCIRHUHNLFBCAXIY',
      ),
    )

    # ... ad infinitum ...

  def test_generator_with_offset(self):
    """
    Creating a generator that starts at an offset greater than 0.
    """
    ag = AddressGenerator(self.seed_1)

    generator = ag.create_iterator(start=1, step=2)

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'DUOVVF9WCNAEOHHWUYUFSYOOWZPDVVD9JKFLQN9Z'
        b'DPAKKHSBKLTRFHD9UHIWGKSGAWCOMDG9GBPYISPWR',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'ZFIRBTDSLFAEDRAFORR9LETRUNRHTACYQPBV9VHR'
        b'EGVIGSKFQABGVLQPLFTAD9OHLPMAVKWBBDIKZSAOG',
      ),
    )

  def test_security_level_lowered(self):
    """
    Generating addresses with a lower security level.
    """
    ag = AddressGenerator(self.seed_1, security_level=1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'QTGZZPTYYFMFG9UCTOREALIZZJ9VEASMBFLMZARF'
          b'LENFSNPSITZZVXH9IGPVIRAVRYMXYVXQBUORWVILF',
        ),

        Address(
          b'FHOFBSATJIGMLKGGPWEBIBWIPELKTEAMAQTEDNUN'
          b'HOJBVBAIGTPLMKSGBHWZGNXTLRMFZXASV9FNZGBNY',
        ),

        Address(
          b'VRYXJWWGQIKDLI9R9KFECQXCLYNBHUMCWEYDTOTZ'
          b'GITLQIRDZCOBWXAOTVPGKBQBXKZAZAFRLZTDBRBXW',
        ),
      ],
    )

  def test_security_level_elevated(self):
    """
    Generating addresses with a higher security level.
    """
    ag = AddressGenerator(self.seed_1, security_level=3)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'ZWJEPOOWHOZYEMGJCJAWDETMBUEHOYFHAGOFINQA'
          b'CSGFNHXTMDHVHVAWQHQEBLDXKOQVKHEIU9QWLWPSV',
        ),

        Address(
          b'TNCURBUSWSCMWKJMZFW9SDUTVMQRAHTWVPYQFDRZ'
          b'ALTMDEMCVWEVWYIJZMKOCEPSJKRV9EGDDDCLMCJBL',
        ),

        Address(
          b'HHZUZEKUTMBBIFZDUBVSEXEPEDWATWOBBGVCHBMI'
          b'MBVRLDDLBBWWMECJGNSXFJOCPOFSEZOHDGPVADYCK',
        ),
      ],
    )


class MemoryAddressCacheTestCase(TestCase):
  def setUp(self):
    super(MemoryAddressCacheTestCase, self).setUp()

    # Define some values we can reuse across tests.
    # noinspection SpellCheckingInspection
    self.addy =\
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999J9XDHH'
          b'LHKET9PHTEUAHFFCDCP9ECIDPALFMFSCTCIHMD9CY',

        key_index = 42,
      )

  def tearDown(self):
    super(MemoryAddressCacheTestCase, self).tearDown()

    # Disable the global cache, in case the test installed one.
    AddressGenerator.cache = None

  def test_global_cache(self):
    """
    Installing a cache that affects all :py:class:`AddressGenerator`
    instances.
    """
    # Install the cache globally.
    AddressGenerator.cache = MemoryAddressCache()

    mock_generate_address = Mock(return_value=self.addy)

    with patch(
        'iota.crypto.addresses.AddressGenerator._generate_address',
        mock_generate_address,
    ):
      generator1 = AddressGenerator(Seed.random())

      addy1 = generator1.get_addresses(42)
      mock_generate_address.assert_called_once()

      # The second time we try to generate the same address, it is
      # fetched from the cache.
      addy2 = generator1.get_addresses(42)
      mock_generate_address.assert_called_once()
      self.assertEqual(addy2, addy1)

      # Create a new AddressGenerator and verify it uses the same
      # cache.
      generator2 = AddressGenerator(generator1.seed)

      # Cache is global, so the cached address is returned again.
      addy3 = generator2.get_addresses(42)
      mock_generate_address.assert_called_once()
      self.assertEqual(addy3, addy1)

  def test_local_cache(self):
    """
    Installing a cache only for a single instance of
    :py:class:`AddressGenerator`.
    """
    mock_generate_address = Mock(return_value=self.addy)

    with patch(
        'iota.crypto.addresses.AddressGenerator._generate_address',
        mock_generate_address,
    ):
      generator1 = AddressGenerator(Seed.random())

      # Install the cache locally.
      generator1.cache = MemoryAddressCache()

      addy1 = generator1.get_addresses(42)
      mock_generate_address.assert_called_once()

      # The second time we try to generate the same address, it is
      # fetched from the cache.
      addy2 = generator1.get_addresses(42)
      mock_generate_address.assert_called_once()
      self.assertEqual(addy2, addy1)

      # Create a new instance to verify it has its own cache.
      generator2 = AddressGenerator(generator1.seed)

      # The generator has its own cache instance, so even though the
      # resulting address is the same, it is not fetched from cache.
      addy3 = generator2.get_addresses(42)
      self.assertEqual(mock_generate_address.call_count, 2)
      self.assertEqual(addy3, addy1)

  def test_cache_miss_key_index(self):
    """
    Cached addresses are keyed by key index.
    """
    AddressGenerator.cache = MemoryAddressCache()

    mock_generate_address = Mock(return_value=self.addy)

    with patch(
        'iota.crypto.addresses.AddressGenerator._generate_address',
        mock_generate_address,
    ):
      generator = AddressGenerator(Seed.random())

      generator.get_addresses(42)
      mock_generate_address.assert_called_once()

      generator.get_addresses(43)
      self.assertEqual(mock_generate_address.call_count, 2)

  def test_cache_miss_seed(self):
    """
    Cached addresses are keyed by seed.
    """
    AddressGenerator.cache = MemoryAddressCache()

    mock_generate_address = Mock(return_value=self.addy)

    with patch(
        'iota.crypto.addresses.AddressGenerator._generate_address',
        mock_generate_address,
    ):
      generator1 = AddressGenerator(Seed.random())
      generator1.get_addresses(42)
      mock_generate_address.assert_called_once()

      generator2 = AddressGenerator(Seed.random())
      generator2.get_addresses(42)
      self.assertEqual(mock_generate_address.call_count, 2)

  def test_thread_safety(self):
    """
    Address cache is thread-safe, eliminating invalid cache misses when
    multiple threads attempt to access the cache concurrently.
    """
    AddressGenerator.cache = MemoryAddressCache()

    seed = Seed.random()

    generated = []

    def get_address():
      generator = AddressGenerator(seed)
      generated.extend(generator.get_addresses(0))

    # noinspection PyUnusedLocal
    def mock_generate_address(address_generator, key_iterator):
      # type: (AddressGenerator, KeyIterator) -> Address
      # Insert a teensy delay, to make it more likely that multiple
      # threads hit the cache concurrently.
      sleep(0.01)

      # Note that in this test, the address generator always returns a
      # new instance.
      return Address(self.addy, key_index=key_iterator.current)

    with patch(
        'iota.crypto.addresses.AddressGenerator._generate_address',
        mock_generate_address,
    ):
      threads = [Thread(target=get_address) for _ in range(100)]

      for t in threads:
        t.start()

      for t in threads:
        t.join()

    # Quick sanity check.
    self.assertEqual(len(generated), len(threads))

    # If the cache is operating in a thread-safe manner, then it will
    # always return the exact same instance, given the same seed and
    # key index.
    expected = generated[0]
    for actual in generated[1:]:
      # Compare `id` values instead of using ``self.assertIs`` because
      # the failure message is a bit easier to understand.
      self.assertEqual(id(actual), id(expected))
