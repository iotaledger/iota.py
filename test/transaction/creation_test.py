# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address, Fragment, ProposedBundle, ProposedTransaction, Tag, \
  TryteString
from iota.crypto.signing import KeyGenerator
from iota.crypto.types import Seed
from iota.transaction.types import BundleHash


class ProposedBundleTestCase(TestCase):
  def setUp(self):
    super(ProposedBundleTestCase, self).setUp()

    # We will use a seed to generate addresses and private keys, to
    # ensure a realistic scenario (and because the alternative is to
    # inject mocks all over the place!).
    # noinspection SpellCheckingInspection
    self.seed =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999RLC9CS'
        b'ZUILGDTLJMRCJSDVEEJO9A9LHAEHMNAMVXRMOXTBN'
      )

    # To speed things up a little bit, though, we can pre-generate a
    # few addresses to use as inputs.

    # noinspection SpellCheckingInspection
    self.input_0_bal_eq_42 =\
      Address(
        balance         = 42,
        key_index       = 0,
        security_level  = 1,

        trytes =
          b'JBLDCCSI9VKU9ZHNZCUTC9NLQIIJX9SIKUJNKNKE'
          b'9KKMHXFMIXHLKQQAVTTNPRCZENGLIPALHKLNKTXCU',
      )

    # noinspection SpellCheckingInspection
    self.input_1_bal_eq_40 =\
      Address(
        balance         = 40,
        key_index       = 1,
        security_level  = 1,

        trytes =
          b'KHWHSTISMVVSDCOMHVFIFCTINWZT9EHJUATYSMCX'
          b'DSMZXPL9KXREBBYHJGRBCYVGPJQEHEDPXLBDJNQNX',
      )

    # noinspection SpellCheckingInspection
    self.input_2_bal_eq_2 =\
      Address(
        balance         = 2,
        key_index       = 2,
        security_level  = 1,

        trytes =
          b'GOAAMRU9EALPO9GKBOWUVZVQEJMB9CSGIZJATHRB'
          b'TRRJPNTSQRZTASRBTQCRFAIDOGTWSHIDGOUUULQIG',
      )

    # noinspection SpellCheckingInspection
    self.input_3_bal_eq_100 =\
      Address(
        balance         = 100,
        key_index       = 3,
        security_level  = 1,

        trytes =
          b'9LPQCSJGYUJMLWKMLJ9KYUYJ9RMDBZZWPHXMGKRG'
          b'YLOAZNKJR9VDYSONVAJRIPVWCOZKFMEKUSWHPSDDZ',
      )

    # noinspection SpellCheckingInspection
    self.input_4_bal_eq_42_sl_2 =\
      Address(
        balance         = 42,
        key_index       = 4,
        security_level  = 2,

        trytes =
          b'NVGLHFZWLEQAWBDJXCWJBMVBVNXEG9DALNBTAYMK'
          b'EMMJ9BCDVVHJJLSTQW9JEJXUUX9JNFGALBNASRDUD',
      )

    # noinspection SpellCheckingInspection
    self.input_5_bal_eq_42_sl_3 =\
      Address(
        balance         = 42,
        key_index       = 5,
        security_level  = 3,

        trytes =
          b'XXYRPQ9BDZGKZZQLYNSBDD9HZLI9OFRK9TZCTU9P'
          b'FAJYXZIZGO9BWLOCNGVMTLFQFMGJWYRMLXSCW9UTQ',
      )

    self.bundle = ProposedBundle()

  def test_add_transaction_short_message(self):
    """
    Adding a transaction to a bundle, with a message short enough to
    fit inside a single transaction.
    """
    # noinspection SpellCheckingInspection
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
    # noinspection SpellCheckingInspection
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

      # Now you know....
      # Eh, who am I kidding?  You probably knew before I did (:
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
    # noinspection SpellCheckingInspection
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
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999VELDTF'
          b'QHDFTHIHFE9II9WFFDFHEATEI99GEDC9BAUH9EBGZ'
        ),

        value = 29,
    ))

    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999OGVEEF'
          b'BCYAM9ZEAADBGBHH9BPBOHFEGCFAM9DESCCHODZ9Y'
        ),

      value = 13,
    ))

    self.bundle.add_inputs([
      self.input_1_bal_eq_40,
      self.input_2_bal_eq_2,
    ])

    # Just to be tricky, add an unnecessary change address, just to
    # make sure the bundle ignores it.
    # noinspection SpellCheckingInspection
    self.bundle.send_unspent_inputs_to(
      Address(
        b'TESTVALUE9DONTUSEINPRODUCTION99999FDCDFD'
        b'VAF9NFLCSCSFFCLCW9KFL9TCAAO9IIHATCREAHGEA'
      ),
    )

    self.bundle.finalize()

    # All of the addresses that we generate for this test case have
    # security level set to 1, so we only need 1 transaction per
    # input (4 total, including the spends).
    #
    # Also note: because the transaction is already balanced, no change
    # transaction is necessary.
    self.assertEqual(len(self.bundle), 4)

  def test_add_inputs_with_change(self):
    """
    Adding inputs to a bundle results in unspent inputs.
    """
    tag = Tag(b'CHANGE9TXN')

    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999VELDTF'
          b'QHDFTHIHFE9II9WFFDFHEATEI99GEDC9BAUH9EBGZ'
        ),

        value = 29,
    ))

    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999OGVEEF'
          b'BCYAM9ZEAADBGBHH9BPBOHFEGCFAM9DESCCHODZ9Y'
        ),

      tag   = tag,
      value = 13,
    ))

    self.bundle.add_inputs([self.input_3_bal_eq_100])

    # noinspection SpellCheckingInspection
    change_address =\
      Address(
        b'TESTVALUE9DONTUSEINPRODUCTION99999KAFGVC'
        b'IBLHS9JBZCEFDELEGFDCZGIEGCPFEIQEYGA9UFPAE'
      )

    self.bundle.send_unspent_inputs_to(change_address)

    self.bundle.finalize()

    # 2 spends + 1 input (with security level 1) + 1 change
    self.assertEqual(len(self.bundle), 4)

    change_txn = self.bundle[-1]
    self.assertEqual(change_txn.address, change_address)
    self.assertEqual(change_txn.value, 58)
    self.assertEqual(change_txn.tag, tag)

  def test_add_inputs_security_level(self):
    """
    Each input's security level determines the number of transactions
    we will need in order to store the entire signature.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
            b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH',
          ),

        value = 84,
      ),
    )

    self.bundle.add_inputs([
      self.input_4_bal_eq_42_sl_2,
      self.input_5_bal_eq_42_sl_3,
    ])

    self.bundle.finalize()

    # Each input's security level determines how many transactions will
    # be needed to hold all of its signature fragments:
    # 1 spend + 2 fragments for input 0 + 3 fragments for input 1
    self.assertEqual(len(self.bundle), 6)

  def test_add_inputs_error_already_finalized(self):
    """
    Attempting to add inputs to a bundle that is already finalized.
    """
    # Add 1 transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
            b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH',
          ),

        value = 0,
      ),
    )

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      # Even though no inputs are provided, it's still an error; you
      # shouldn't even be calling ``add_inputs`` once the bundle is
      # finalized!
      self.bundle.add_inputs([])

  def test_send_unspent_inputs_to_error_already_finalized(self):
    """
    Invoking ``send_unspent_inputs_to`` on a bundle that is already
    finalized.
    """
    # Add 1 transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
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
    # Add 1 transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
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
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999IGEFUG'
          b'LIHIJGJGZ9CGRENCRHF9XFEAWD9ILFWEJFKDLITCC'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42, self.input_2_bal_eq_2])

    # Bundle spends 42 IOTAs, but inputs total 44 IOTAs.
    self.assertEqual(self.bundle.balance, -2)

    # In order to finalize this bundle, we need to specify a change
    # address.
    with self.assertRaises(ValueError):
      self.bundle.finalize()

  def test_finalize_error_positive_balance(self):
    """
    Attempting to finalize a bundle with insufficient inputs.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999IGEFUG'
          b'LIHIJGJGZ9CGRENCRHF9XFEAWD9ILFWEJFKDLITCC'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_1_bal_eq_40])

    # Bundle spends 42 IOTAs, but inputs total only 40 IOTAs.
    self.assertEqual(self.bundle.balance, 2)

    # In order to finalize this bundle, we need to provide additional
    # inputs.
    with self.assertRaises(ValueError):
      self.bundle.finalize()

  def test_finalize_insecure_bundle(self):
    """
    When finalizing, the bundle detects an insecure bundle hash.

    References:
      - https://github.com/iotaledger/iota.lib.py/issues/84
    """
    # noinspection SpellCheckingInspection
    bundle =\
      ProposedBundle([
        ProposedTransaction(
          address =\
            Address(
              '9XV9RJGFJJZWITDPKSQXRTHCKJAIZZY9BYLBEQUX'
              'UNCLITRQDR9CCD99AANMXYEKD9GLJGVB9HIAGRIBQ',
            ),

          tag       = Tag('PPDIDNQDJZGUQKOWJ9JZRCKOVGP'),
          timestamp = 1509136296,
          value     = 0,
        ),
      ])

    bundle.finalize()

    # The resulting bundle hash is insecure (contains a [1, 1, 1]), so
    # the legacy tag is manipulated until a secure hash is generated.
    # noinspection SpellCheckingInspection
    self.assertEqual(bundle[0].legacy_tag, Tag('ZTDIDNQDJZGUQKOWJ9JZRCKOVGP'))

    # The proper tag is left alone, however.
    # noinspection SpellCheckingInspection
    self.assertEqual(bundle[0].tag, Tag('PPDIDNQDJZGUQKOWJ9JZRCKOVGP'))

    # The bundle hash takes the modified legacy tag into account.
    # noinspection SpellCheckingInspection
    self.assertEqual(
      bundle.hash,

      BundleHash(
        'NYSJSEGCWESDAFLIFCNJFWGZ9PCYDOT9VCSALKBD'
        '9UUNKBJAJCB9KVMTHZDPRDDXC9UFJQBJBQFUPJKFC',
      )
    )

  def test_sign_inputs(self):
    """
    Signing inputs in a finalized bundle, using a key generator.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_1_bal_eq_40, self.input_2_bal_eq_2])
    self.bundle.finalize()

    self.bundle.sign_inputs(KeyGenerator(self.seed))

    # Quick sanity check:
    # 1 spend + 2 inputs (security level 1) = 3 transactions.
    # Applying signatures should not introduce any new transactions
    # into the bundle.
    #
    # Note: we will see what happens when we use inputs with different
    # security levels in the next test.
    self.assertEqual(len(self.bundle), 3)

    # The spending transaction does not have a signature.
    self.assertEqual(
      self.bundle[0].signature_message_fragment,
      Fragment(b''),
    )

    # The signature fragments are really long, and we already have unit
    # tests for the signature fragment generator, so to keep this test
    # focused, we are only interested in whether a signature fragment
    # gets applied.
    #
    # References:
    #   - :py:class:`test.crypto.signing_test.SignatureFragmentGeneratorTestCase`
    for i in range(1, len(self.bundle)):
      if self.bundle[i].signature_message_fragment == Fragment(b''):
        self.fail(
          "Transaction {i}'s signature fragment is unexpectedly empty!".format(
            i = i,
          ),
        )

  def test_sign_inputs_security_level(self):
    """
    You may include inputs with different security levels in the same
    bundle.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
            b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH',
          ),

        value = 84,
      ),
    )

    self.bundle.add_inputs([
      self.input_4_bal_eq_42_sl_2,
      self.input_5_bal_eq_42_sl_3,
    ])

    self.bundle.finalize()

    self.bundle.sign_inputs(KeyGenerator(self.seed))

    # Quick sanity check.
    self.assertEqual(len(self.bundle), 6)

    # The spending transaction does not have a signature.
    self.assertEqual(
      self.bundle[0].signature_message_fragment,
      Fragment(b''),
    )

    # The signature fragments are really long, and we already have unit
    # tests for the signature fragment generator, so to keep this test
    # focused, we are only interested in whether a signature fragment
    # gets applied.
    #
    # References:
    #   - :py:class:`test.crypto.signing_test.SignatureFragmentGeneratorTestCase`
    for i in range(1, len(self.bundle)):
      if self.bundle[i].signature_message_fragment == Fragment(b''):
        self.fail(
          "Transaction {i}'s signature fragment is unexpectedly empty!".format(
            i = i,
          ),
        )

  def test_sign_inputs_error_not_finalized(self):
    """
    Attempting to sign inputs in a bundle that hasn't been finalized
    yet.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])

    # Oops; did we forget something?
    # self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.sign_inputs(KeyGenerator(b''))

  def test_sign_input_at_single_fragment(self):
    """
    Signing an input at the specified index, only 1 fragment needed.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])
    self.bundle.finalize()

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_0_bal_eq_42)

    self.bundle.sign_input_at(1, private_key)

    # Only 2 transactions are needed for this bundle:
    # 1 spend + 1 input (security level = 1).
    self.assertEqual(len(self.bundle), 2)

    # The spending transaction does not have a signature.
    self.assertEqual(
      self.bundle[0].signature_message_fragment,
      Fragment(b''),
    )

    # The signature fragments are really long, and we already have unit
    # tests for the signature fragment generator, so to keep this test
    # focused, we are only interested in whether a signature fragment
    # gets applied.
    #
    # References:
    #   - :py:class:`test.crypto.signing_test.SignatureFragmentGeneratorTestCase`
    for i in range(1, len(self.bundle)):
      if self.bundle[i].signature_message_fragment == Fragment(b''):
        self.fail(
          "Transaction {i}'s signature fragment is unexpectedly empty!".format(
            i = i,
          ),
        )

  def test_sign_input_at_multiple_fragments(self):
    """
    Signing an input at the specified index, multiple fragments needed.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_5_bal_eq_42_sl_3])
    self.bundle.finalize()

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_5_bal_eq_42_sl_3)

    self.bundle.sign_input_at(1, private_key)

    # 1 spend + 3 inputs (security level = 3).
    self.assertEqual(len(self.bundle), 4)

    # The spending transaction does not have a signature.
    self.assertEqual(
      self.bundle[0].signature_message_fragment,
      Fragment(b''),
    )

    # The signature fragments are really long, and we already have unit
    # tests for the signature fragment generator, so to keep this test
    # focused, we are only interested in whether a signature fragment
    # gets applied.
    #
    # References:
    #   - :py:class:`test.crypto.signing_test.SignatureFragmentGeneratorTestCase`
    for i in range(1, len(self.bundle)):
      if self.bundle[i].signature_message_fragment == Fragment(b''):
        self.fail(
          "Transaction {i}'s signature fragment is unexpectedly empty!".format(
            i = i,
          ),
        )

  def test_sign_input_at_error_not_finalized(self):
    """
    Cannot sign inputs because the bundle isn't finalized yet.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])

    # Oops; did we forget something?
    # self.bundle.finalize()

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_0_bal_eq_42)

    with self.assertRaises(RuntimeError):
      self.bundle.sign_input_at(1, private_key)

  def test_sign_input_at_error_index_invalid(self):
    """
    The specified index doesn't exist in the bundle.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])
    self.bundle.finalize()

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_0_bal_eq_42)

    with self.assertRaises(IndexError):
      self.bundle.sign_input_at(2, private_key)

  def test_sign_input_at_error_index_not_input(self):
    """
    The specified index references a transaction that is not an input.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])
    self.bundle.finalize()

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_0_bal_eq_42)

    with self.assertRaises(ValueError):
      # You can't sign the spend transaction, silly!
      self.bundle.sign_input_at(0, private_key)

  def test_sign_input_at_error_already_signed(self):
    """
    Attempting to sign an input that is already signed.
    """
    # Add a transaction so that we can finalize the bundle.
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(ProposedTransaction(
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999QARFLF'
          b'TDVATBVFTFCGEHLFJBMHPBOBOHFBSGAGWCM9PG9GX'
        ),

      value = 42,
    ))

    self.bundle.add_inputs([self.input_0_bal_eq_42])
    self.bundle.finalize()

    # The existing signature fragment doesn't have to be valid; it just
    # has to be not empty.
    self.bundle[1].signature_message_fragment = Fragment(b'A')

    private_key =\
      KeyGenerator(self.seed).get_key_for(self.input_0_bal_eq_42)

    with self.assertRaises(ValueError):
      self.bundle.sign_input_at(1, private_key)
