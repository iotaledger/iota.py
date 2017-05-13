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
from test import mock


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
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(MemoryAddressCacheTestCase, self).setUp()

    # Define some values we can reuse across tests.
    self.seed =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999JCQEVD'
        b'XENAEEIA9FU9YGTBDEZGRGZ9VE9CLFSHUAGBODMAY',
      )

    self.addy_1 =\
      Address(
        trytes =
          b'YWEZSDHGKJMLAFTVLMXOOZTWL9DNFMXP9ZVEBFQD'
          b'LSTDIVRQSLBVIKGTYVKZZHOLGCGNB9JSZECIRNAJB',

        key_index       = 0,
        security_level  = 2,
      )

    self.addy_2 =\
      Address(
        trytes =
          b'KPBNMBSXNJLOJPRQXWEPMYFDKHMJMNPRORQRBXSK'
          b'LWPVGCAAMNNUDUVJVVMJGRAFQTDYZHMHK9NXWAUYB',

        key_index       = 1,
        security_level  = 2,
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

    generator_1 = AddressGenerator(self.seed)

    # The second time we try to generate the same address, it is
    # fetched from the cache.
    generated_addy_1 = generator_1.get_addresses(self.addy_1.key_index)[0]
    generated_addy_2 = generator_1.get_addresses(self.addy_1.key_index)[0]
    self.assertEqual(id(generated_addy_2), id(generated_addy_1))

    # Create a new AddressGenerator and verify it uses the same
    # cache.
    generator_2 = AddressGenerator(generator_1.seed)

    # Cache is global, so the cached address is returned again.
    generated_addy_3 = generator_2.get_addresses(self.addy_1.key_index)[0]
    self.assertEqual(id(generated_addy_3), id(generated_addy_1))

  def test_local_cache(self):
    """
    Installing a cache only for a single instance of
    :py:class:`AddressGenerator`.
    """
    # Install the cache locally.
    generator_1 = AddressGenerator(seed=self.seed, security_level=2)
    generator_1.cache = MemoryAddressCache()

    # The second time we try to generate the same address, it is
    # fetched from the cache.
    generated_addy_1 = generator_1.get_addresses(self.addy_1.key_index)[0]
    generated_addy_2 = generator_1.get_addresses(self.addy_1.key_index)[0]
    self.assertEqual(id(generated_addy_2), id(generated_addy_1))

    # Create a new instance to verify it has its own cache.
    generator_2 = AddressGenerator(seed=self.seed, security_level=2)
    generated_addy_3 = generator_2.get_addresses(self.addy_1.key_index)[0]

    # The generator has its own cache instance, so even though the
    # resulting address is the same, it is not fetched from cache.
    self.assertEqual(generated_addy_3, generated_addy_1)
    self.assertNotEqual(id(generated_addy_3), id(generated_addy_1))

  def test_cache_miss_key_index(self):
    """
    Cached addresses are keyed by key index.
    """
    AddressGenerator.cache = MemoryAddressCache()

    # Populate the cache.
    generator_1 = AddressGenerator(seed=self.seed, security_level=2)
    generator_1.get_addresses(self.addy_1.key_index)

    # Same seed, same security level, different key index.
    generator_2 = AddressGenerator(seed=self.seed, security_level=2)
    generated_addy = generator_2.get_addresses(self.addy_2.key_index)[0]

    # Different key index, so cached address is not returned.
    self.assertEqual(generated_addy, self.addy_2)

  def test_cache_miss_security_level(self):
    """
    Cached addresses are also keyed by security level.
    """
    AddressGenerator.cache = MemoryAddressCache()

    # Populate the cache.
    generator_1 = AddressGenerator(seed=self.seed, security_level=2)
    generator_1.get_addresses(self.addy_1.key_index)

    # Same seed, same key index, but different security level.
    generator_2 = AddressGenerator(seed=self.seed, security_level=3)
    generated_addy = generator_2.get_addresses(self.addy_1.key_index)[0]

    # Different security level, so the cached address is not returned.
    # noinspection SpellCheckingInspection
    self.assertEqual(
      generated_addy,

      Address(
        b'AJZTKXRPHBPDTOWMXPSNXTNTVSMVROCZQBQFTEQO'
        b'MEACOUCB9PCRINJCCQTHERSHCI9WRIGBVHZQKCERK',
      ),
    )

  def test_cache_miss_seed(self):
    """
    Cached addresses are keyed by seed.
    """
    AddressGenerator.cache = MemoryAddressCache()

    # Populate the cache.
    generator_1 = AddressGenerator(seed=self.seed, security_level=2)
    generator_1.get_addresses(self.addy_1.key_index)

    # Same key index, same security level, but different seed.
    # noinspection SpellCheckingInspection
    generator_2 =\
      AddressGenerator(
        seed =
          Seed(
            b'TESTVALUE9DONTUSEINPRODUCTION99999BCIGM9'
            b'ZEF9HCDAWAFHUBDCBEYDGEBGQEP9ACBGFAACWFYEP',
          ),

        security_level = 2,
      )

    # Different seed, so cached address is not returned.
    # noinspection SpellCheckingInspection
    self.assertEqual(
      generator_2.get_addresses(self.addy_1.key_index)[0],

      Address(
        b'FMYUDWUDWSWRLCFTEFJXP9IDZNCLTCFJLF9MXVCW'
        b'SSAEUGGDXKFML9CDEA9LNKNLWYVEDHLJNTXBWQSZT',
      ),
    )

  def test_thread_safety(self):
    """
    Address cache is thread-safe, eliminating invalid cache misses when
    multiple threads attempt to access the cache concurrently.
    """
    AddressGenerator.cache = MemoryAddressCache()

    generated = []

    def get_address():
      generator = AddressGenerator(self.seed)
      generated.extend(generator.get_addresses(0))

    # noinspection PyUnusedLocal
    def mock_generate_address(address_generator, key_iterator):
      # type: (AddressGenerator, KeyIterator) -> Address
      # Insert a teensy delay, to make it more likely that multiple
      # threads hit the cache concurrently.
      sleep(0.01)

      # Note that in this test, the address generator always returns a
      # new instance.
      return Address(
        key_index       = key_iterator.current,
        security_level  = key_iterator.security_level,
        trytes          = self.addy_1,
      )

    with mock.patch(
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
      self.assertEqual(id(actual), id(expected))
