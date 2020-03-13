import iota
from pprint import pprint

# Generate a random seed.
myseed = iota.crypto.types.Seed.random()
# Get an address generator.
addres_generator = iota.crypto.addresses.AddressGenerator(myseed)

# Instantiate API. Note the `local_pow=True` argument.
# This will cause PyOTA to do proof-of-work locally,
# by using the pyota-pow extension package. (if installed)
# Find it at: https://pypi.org/project/PyOTA-PoW/
api = iota.Iota("https://nodes.thetangle.org:443",myseed,local_pow=True)

# Generate two addresses
addys = addres_generator.get_addresses(1, count=2)
pprint('Generated addresses are:')
pprint(addys)

# Preparing transactions
pt = iota.ProposedTransaction(address = iota.Address(addys[0]),
                              message = iota.TryteString.from_unicode('Tx1: The PoW for this transaction was done by Pyota-Pow.'),
                              tag     = iota.Tag(b'LOCALATTACHINTERFACE99999'), # Up to 27 trytes
                              value   = 0)

pt2 = iota.ProposedTransaction(address = iota.Address(addys[1]),
                               message = iota.TryteString.from_unicode('Tx2: The PoW for this transaction was done by Pyota-Pow.'),
                               tag     = iota.Tag(b'LOCALATTACHINTERFACE99999'), # Up to 27 trytes
                               value   = 0)

# `send_transfer` will take care of the rest
response = api.send_transfer([pt,pt2])

pprint('Broadcasted bundle:')
pprint(response['bundle'].as_json_compatible())