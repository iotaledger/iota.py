# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List
from unittest import TestCase

from mock import patch

from iota import Address, TryteString
from iota.crypto.addresses import AddressGenerator


# noinspection SpellCheckingInspection
class AddressGeneratorTestCase(TestCase):
  def setUp(self):
    super(AddressGeneratorTestCase, self).setUp()

    # Addresses that correspond to the digests defined in
    # :py:meth:`_mock_digest_gen`.
    self.addy0 =\
      Address(
        b'VOPYUSDRHYGGOHLAYDWCLLOFWBLK99PYYKENW9IQ'
        b'IVIOYMLCCPXGICDBZKCQVJLDWWJLTTUVIXCTOZ9TN'
      )

    self.addy1 =\
      Address(
        b'SKKMQAGLZMXWSXRVVRFWMGN9TIXDACQMCXZJRPMS'
        b'UFNSXMFOGEBZZPUJBVKVSJNYPSGSXQIUHTRKECVQE'
      )

    self.addy2 =\
      Address(
        b'VMMFSGEYJ9SANRULNIMKEZUYVRTWMVR9UKCYDZXW'
        b'9TENBWIRMFODOSNMDH9QOVBLQWALOHMSBGEVIXSXY'
      )

    self.addy3 =\
      Address(
        b'G9PLHPOMET9NWIBGRGMIF9HFVETTWGKCXWGFYRNG'
        b'CFANWBQFGMFKITZBJDSYLGXYUIQVCMXFWSWFRNHRV'
      )

  def test_get_addresses_single(self):
    """
    Generating a single address.
    """
    # Seed is not important for this test; it is only used by
    # :py:class:`KeyGenerator`, which we will mock in this test.
    ag = AddressGenerator(seed=b'')

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      addresses = ag.get_addresses(start=0)

    self.assertListEqual(addresses, [self.addy0])

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      # You can provide any positive integer as the ``start`` value.
      addresses = ag.get_addresses(start=2)

    self.assertListEqual(addresses, [self.addy2])

  def test_get_addresses_multiple(self):
    """
    Generating multiple addresses in one go.
    """
    # Seed is not important for this test; it is only used by
    # :py:class:`KeyGenerator`, which we will mock in this test.
    ag = AddressGenerator(seed=b'')

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      addresses = ag.get_addresses(start=1, count=2)

    self.assertListEqual(addresses, [self.addy1, self.addy2])

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
    # Seed is not important for this test; it is only used by
    # :py:class:`KeyGenerator`, which we will mock in this test.
    ag = AddressGenerator(seed=b'')

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      addresses = ag.get_addresses(start=1, count=2, step=-1)

    self.assertListEqual(
      addresses,

      # This is the same as ``ag.get_addresses(start=0, count=2)``, but
      # the order is reversed.
      [self.addy1, self.addy0],
    )

  def test_generator(self):
    """
    Creating a generator.
    """
    # Seed is not important for this test; it is only used by
    # :py:class:`KeyGenerator`, which we will mock in this test.
    ag = AddressGenerator(seed=b'')

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      generator = ag.create_generator()

      self.assertEqual(next(generator), self.addy0)
      self.assertEqual(next(generator), self.addy1)
      # ... ad infinitum ...

  def test_generator_with_offset(self):
    """
    Creating a generator that starts at an offset greater than 0.
    """
    # Seed is not important for this test; it is only used by
    # :py:class:`KeyGenerator`, which we will mock in this test.
    ag = AddressGenerator(seed=b'')

    # noinspection PyUnresolvedReferences
    with patch.object(ag, '_create_digest_generator', self._mock_digest_gen):
      generator = ag.create_generator(start=1, step=2)

      self.assertEqual(next(generator), self.addy1)
      self.assertEqual(next(generator), self.addy3)

  @staticmethod
  def _mock_digest_gen(start, step):
    # type: (int, int) -> Generator[List[int]]
    """
    Mocks the behavior of :py:class:`KeyGenerator`, to speed up unit
    tests.

    Note that :py:class:`KeyGenerator` has its own test case, so we're
    not impacting the stability of the codebase by doing this.
    """
    digests = [
      b'KDWISSPKPF9DZNKMYEVPPYI9CXMFZRAAKCQNMFJI'
      b'JIQLT9IPMEVVNYBTIBTN9CBCJMYTUMSRJAEMUUMIA',

      b'XUWRYOZQYEVM9CRZZPZQRTAHBMLM9EYMZZIYRFV9'
      b'GZST9XGK9LWUDGIXCCRFLWHUJPYQ9MMYDZEMAJZOI',

      b'SEJHPHEF9NXPPZQUOVGZNUZSP9DQOBRVSAGADUAD'
      b'EPRDFQJPXTOJGFPEXUPRQUYTTSD9GVPXTWWZQSGXA',

      b'LNXDEKQCP9OXMBNDUJCZIMVRVGJLKFVMMRPHROSH'
      b'XCWW9M9QGYVUMPXCR9ANPEPVGBI9WOERTFDAGKCVZ',
    ]

    # This should still behave like the real thing, so that we can
    # verify that :py:class`AddressGenerator` is invoking the key
    # generator correctly.
    for d in digests[start::step]:
      yield TryteString(d).as_trits()
