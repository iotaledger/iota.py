from iota import Address
from iota.crypto.types import Seed
from iota.flash.api import FlashIota
from iota.flash.types import FlashUser, FlashState

ONE_SEED = Seed(b'USERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSERONEUSER')
ONE_SETTLEMENT = Address(b'USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9U')
TWO_SEED = Seed(b'USERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSERTWOUSER')
TWO_SETTLEMENT = Address(b'USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9U')

# General channel configuration
SECURITY = 2  # security level
SIGNERS_COUNT = 2  # number of parties taking signing part in the channel
TREE_DEPTH = 4  # Flash tree depth
CHANNEL_BALANCE = 2000  # total channel Balance
DEPOSITS = [1000, 1000]  # users deposits

############################################
# (0) Initialize Flash objects
############################################

print('(0) Initializing Flash objects')

# user one
iota_one = FlashIota(adapter='http://localhost:14265', seed=ONE_SEED)
flash_one = FlashState(signers_count=SIGNERS_COUNT,
                       balance=CHANNEL_BALANCE,
                       deposit=list(DEPOSITS))
user_one = FlashUser(user_index=0,
                     seed=ONE_SEED,
                     index=0,
                     security=SECURITY,
                     depth=TREE_DEPTH,
                     flash=flash_one)

# user two
flash_two = FlashState(signers_count=SIGNERS_COUNT,
                       balance=CHANNEL_BALANCE,
                       deposit=list(DEPOSITS))
user_two = FlashUser(user_index=1,
                     seed=TWO_SEED,
                     index=0,
                     security=SECURITY,
                     depth=TREE_DEPTH,
                     flash=flash_two)
iota_two = FlashIota(adapter='http://localhost:14265', seed=TWO_SEED)
############################################
# (1) Generate Digests
############################################

print('(1) Generating digests for each user')

for _ in range(TREE_DEPTH + 1):
  digest = iota_one.get_digests(index=user_one.index, security_level=user_one.security)['digests']
  user_one.index += 1
  user_one.partial_digests.append(digest[0])

for _ in range(TREE_DEPTH + 1):
  digest = iota_two.get_digests(index=user_two.index, security_level=user_two.security)['digests']
  user_two.index += 1
  user_two.partial_digests.append(digest[0])

############################################
# (2) Create Multisignature Addresses
############################################

print('(2) Creating multisignature addresses')

all_digests = list(zip(user_one.partial_digests, user_two.partial_digests))
one_multisigs = [iota_one.compose_flash_address(digests) for digests in all_digests]
two_multisigs = [iota_two.compose_flash_address(digests) for digests in all_digests]

############################################
# (3) Organize Addresses for use
############################################

print('(3) Organizing addresses for use')

# Set remainder address (Same on both users)
flash_one.remainder_address = one_multisigs.pop(0)
flash_two.remainder_address = two_multisigs.pop(0)

# Nest trees
for i in range(1, len(one_multisigs)):
  one_multisigs[i - 1]['children'].append(one_multisigs[i])
for i in range(1, len(two_multisigs)):
  two_multisigs[i - 1]['children'].append(two_multisigs[i])

# Set deposit address
flash_one.deposit_address = one_multisigs[0]
flash_two.deposit_address = two_multisigs[0]

# Set root of tree
flash_one.root = one_multisigs[0]
flash_two.root = two_multisigs[0]

# Set settlement addresses (Usually sent over when the digests are.)
settlement_addresses = [ONE_SETTLEMENT, TWO_SETTLEMENT]
flash_one.settlement_addresses = settlement_addresses
flash_two.settlement_addresses = settlement_addresses

# Set digest/key index
user_one.index = len(user_one.partial_digests)
user_two.index = len(user_two.partial_digests)

############################################
# (4) Compose Transaction from user one
############################################
print('(4) Compose transactions. Sending 200 tokens to', TWO_SETTLEMENT)

transfers = [{
  'value': 200,
  'address': TWO_SETTLEMENT
}]
bundles = iota_one.create_flash_transaction(user=user_one, transactions=transfers)

# ToDO

############################################
# (5) Sign Bundles
############################################

print('(5) Signing bundles')

# ToDO

############################################
# (6) Apply Signed Bundles
############################################

print('(6) Applying signed bundles')

# ToDO

############################################
# (7) Close Channel
############################################

print('(7) Closing channel')

# ToDO
