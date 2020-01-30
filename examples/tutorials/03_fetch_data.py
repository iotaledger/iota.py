from iota import Iota, Address
from iota.codecs import TrytesDecodeError

# Declare an API object
api = Iota('https://nodes.devnet.iota.org:443', devnet=True)

# Address to fetch data from
# Replace with your random generated address from Tutorial 2. to fetch the data
# that you uploaded.
addy = Address(b'WWO9DRAUDDSDSTTUPKJRNPSYLWAVQBBXISLKLTNDPVKOPMUERDUELLUPHNT9L9YWBDKOLYVWRAFRKIBLP')

print('Fetching data from the Tangle...')
# Fetch the transaction objects of the address from the Tangle
response = api.find_transaction_objects(addresses=[addy])

if not response['transactions']:
    print('Couldn\'t find data for the given address.')
else:
    print('Found:')
    # Iterate over the fetched transaction objects
    for tx in response['transactions']:
        # data is in the signature_message_fragment attribute as trytes, we need
        # to decode it into a unicode string
        data = tx.signature_message_fragment.decode(errors='ignore')
        print(data)