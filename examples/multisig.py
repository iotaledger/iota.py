# coding=utf-8
"""
Example of how to use PyOTA's multisig feature.

This script will generate a multisig address using private keys from
three different seeds, prepare a bundle, sign the inputs, and then
finally broadcast the transactions to the Tangle.

References:
  - https://github.com/iotaledger/wiki/blob/master/multisigs.md
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List

from iota import Address, Bundle, BundleValidator, ProposedTransaction, Tag, \
  TransactionTrytes, TryteString
from iota.crypto.types import Digest, PrivateKey, Seed
from iota.multisig import MultisigIota
from iota.multisig.types import MultisigAddress

"""
Step 1:  Each participant generates one or more digests that will be
used to create the multisig address.

For this example, we will create digests from 3 different private
keys, each owned by a different seed.

Note that this part normally happens on separate computers, so that
participants don't have to share their seeds.
"""

##
# Create digest 1 of 3.
#
# noinspection SpellCheckingInspection
api_1 =\
  MultisigIota(
    adapter = 'http://localhost:14265',

    seed =
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999XKMYQP'
        b'OIFGQSMIIWCQVMBSOKZASRQOFSIUSSHNDKVL9PJVS',
      ),
  )

gd_result =\
  api_1.get_digests(
    # Starting key index.
    index = 0,

    # Number of digests to generate.
    count = 1,

    # Security level of the resulting digests.
    # Must be a value between 1 (faster) and 3 (more secure).
    security_level = 3,
  )

# ``get_digests`` returns a dict which contains 1 or more digests,
# depending on what value we used for ``count``.
digest_1 = gd_result['digests'][0] # type: Digest

##
# Create digest 2 of 3.
#
# noinspection SpellCheckingInspection
api_2 =\
  MultisigIota(
    adapter = 'http://localhost:14265',

    seed =
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999DDWDKI'
        b'FFBZVQHHINYDWRSMGGPZUERNLEAYMLFPHRXEWRNST',
      ),
  )

# You can use any starting index that you want.
# For maximum security, each index should be used only once.
gd_result = api_2.get_digests(index=42, count=1, security_level=3)

digest_2 = gd_result['digests'][0] # type: Digest

##
# Create digest 3 of 3.
#
# noinspection SpellCheckingInspection
api_3 =\
  MultisigIota(
    adapter = 'http://localhost:14265',

    seed =
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999JYFRTI'
        b'WMKVVBAIEIYZDWLUVOYTZBKPKLLUMPDF9PPFLO9KT',
      ),
  )

# It is not necessary for every digest to have the same security level.
gd_result = api_3.get_digests(index=8, count=1, security_level=2)

digest_3 = gd_result['digests'][0] # type: Digest


"""
Step 2:  Collect the digests and create a multisig address.

Note that digests are safe to share with other users, so this step is
typically performed on a single instance.

IMPORTANT: Keep track of the order that digests are used; you will
need to ensure that the same order is used to sign inputs!
"""

cma_result =\
  api_1.create_multisig_address(digests=[digest_1, digest_2, digest_3])

# For consistency, every API command returns a dict, even if it only
# has a single value.
multisig_address = cma_result['address'] # type: MultisigAddress


"""
Step 3:  Prepare the bundle.

This step occurs some time later, after the multisig address has
received some IOTAs.

IMPORTANT:  In IOTA, it is unsafe to spend from a single address
multiple times.  Take care to spend ALL of the IOTAs controlled by the
multisig address, or generate a new multisig address that will receive
the change from the transaction!
"""

# noinspection SpellCheckingInspection
pmt_result =\
  api_1.prepare_multisig_transfer(
    # These are the transactions that will spend the IOTAs.
    # You can divide up the IOTAs to send to multiple addresses if you
    # want, but to keep this example focused, we will only include a
    # single spend transaction.
    transfers = [
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999NDGYBC'
            b'QZJFGGWZ9GBQFKDOLWMVILARZRHJMSYFZETZTHTZR',
          ),

        value = 42,

        # If you'd like, you may include an optional tag and/or
        # message.
        tag = Tag(b'KITTEHS'),
        message = TryteString.from_string('thanx fur cheezburgers'),
      ),
    ],

    # Specify our multisig address as the input for the spend
    # transaction(s).
    # Note that PyOTA currently only allows one multisig input per
    # bundle (although the protocol does not impose a limit).
    multisig_input = multisig_address,

    # If there will be change from this transaction, you MUST specify
    # the change address!  Unlike regular transfers, multisig transfers
    # will NOT automatically generate a change address; that wouldn't
    # be fair to the other participants!
    change_address = None,
  )

prepared_trytes = pmt_result['trytes'] # type: List[TransactionTrytes]


"""
Step 4:  Sign the inputs.

Note that we must apply signatures in the same order as when we created
the multisig address!

This step normally happens on separate computers, so that participants
don't have to share their private keys (except when doing m-of-n).

https://github.com/iotaledger/wiki/blob/master/multisigs.md#how-m-of-n-works

For this example, the structure of the bundle looks like this:

- Transaction 0:  Spend IOTAs.
- Transactions 1-8:  Transactions that will hold the signature
  fragments for the multisig input:
  - 1-3:  Generated from ``digest_1`` (security level 3).
  - 4-6:  Generated from ``digest_2`` (security level 3).
  - 7-8:  Generated from ``digest_3`` (security level 2).

Note that transactions 1-8 don't have signatures yet; we need the
corresponding private keys in order to create those!
"""
bundle = Bundle.from_tryte_strings(prepared_trytes)

# Note that we must use the same parameters that we provided to the
# ``get_digests`` method, in order to generate the correct value to
# sign the input!
gpk_result = api_1.get_private_keys(index=0, count=1, security_level=3)
private_key_1 = gpk_result['keys'][0] # type: PrivateKey
private_key_1.sign_input_transactions(bundle, 1)

gpk_result = api_2.get_private_keys(index=42, count=1, security_level=3)
private_key_2 = gpk_result['keys'][0] # type: PrivateKey
private_key_2.sign_input_transactions(bundle, 4)

gpk_result = api_3.get_private_keys(index=8, count=1, security_level=2)
private_key_3 = gpk_result['keys'][0] # type: PrivateKey
private_key_3.sign_input_transactions(bundle, 7)

# Once we've applied the signatures, convert the Bundle back into tryte
# sequences so that we can broadcast them to the tangle.
signed_trytes = bundle.as_tryte_strings()

"""
Step 4.5 (Optional):  Validate the signatures.

This step is purely optional.  We are including it in this example
script so that you can see that the resulting signature fragments are
valid.
"""
validator = BundleValidator(bundle)
if not validator.is_valid():
  raise ValueError(
    'Bundle failed validation:\n{errors}'.format(
      errors = '\n'.join(('  - ' + e) for e in validator.errors),
    ),
  )

"""
Step 5:  Broadcast the bundle.

Note that this step works the same as any other transfer.
"""
api_1.send_trytes(trytes=signed_trytes, depth=3)
