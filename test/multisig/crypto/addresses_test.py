# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address
from iota.crypto.types import Digest
from iota.multisig.crypto.addresses import MultisigAddressBuilder


class MultisigAddressBuilderTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(MultisigAddressBuilderTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    self.digest_1 =\
      Digest(
        trytes =
          b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
          b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
          b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAYXQPLLUDJNCYMUAJBE9XXYYDQ9JYANVMAOEN9'
          b'NKGJR9HUNJKV9YYBQLOQLXBIEBIMPL9IAWXATKLEMOCVP',

        key_index = 0,
      )

    self.digest_2 =\
      Digest(
        trytes =
          b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
          b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
          b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLCJDXJSTHQNB9IRIOIOQOLHFFUOERZSJAWJHFD'
          b'PLCOKKFBOYWOF9WGHLCWONJKICPFDXXWNWBKDVCDFKRZJ',

        key_index = 0,
      )

  def test_success_multiple_digests(self):
    """
    Generating a multisig address from multiple digests.
    """
    builder = MultisigAddressBuilder()
    builder.add_digest(self.digest_1)
    builder.add_digest(self.digest_2)
    addy = builder.get_address()

    # noinspection SpellCheckingInspection
    self.assertEqual(
      addy,

      Address(
        b'DKXUXQCELGAABFFTCNPHTTGZJSUATFPUUZLVIIRHQ'
        b'YGPFKRLATYZZUSDULVWUXFGNAYN99W9ZQSENSP9D'
      ),
    )

  def test_success_single_digest(self):
    """
    Generating a "multisig" address from a single digest.

    This does the same thing as generating a regular address from the
    corresponding key.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_error_no_digests(self):
    """
    Attempting to generate a multisig addresses without providing any
    digests.

    I mean, why even bother, right?
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_success_get_multiple_addresses(self):
    """
    You can continue adding digests to the address builder even after
    extracting an address.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
