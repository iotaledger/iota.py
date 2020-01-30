"""
Encrypt data and store it on the Tangle.

simplecrypt library is needed for this example (`pip install simple-crypt`)!
"""
from iota import Iota, TryteString, Tag, ProposedTransaction
from simplecrypt import encrypt
from base64 import b64encode
from getpass import getpass

import json

# Declare an API object
api = Iota(
    adapter='https://nodes.devnet.iota.org:443',
    seed=b'YOURSEEDFROMTHEPREVIOUSTUTORIAL',
    devnet=True,
)

# Some confidential information
data = {
    'name' : 'James Bond',
    'age' : '32',
    'job' : 'agent',
    'address' : 'London',
}

# Convert to JSON format
json_data = json.dumps(data)

# Ask user for a password to use for encryption
password = getpass('Please supply a password for encryption:')

print('Encrypting data...')
# Encrypt data
# Note, that in Python 3, encrypt returns 'bytes'
cipher = encrypt(password, json_data)

# Encode to base64, output contains only ASCII chars
b64_cipher = b64encode(cipher)

print('Constructing transaction locally...')
# Convert to trytes
trytes_encrypted_data = TryteString.from_bytes(b64_cipher)

# Generate an address from your seed to post the transfer to
my_address = api.get_new_addresses(index=42)['addresses'][0]

# Tag is optional here
my_tag = Tag(b'CONFIDENTIALINFORMATION')

# Prepare a transaction object
tx = ProposedTransaction(
    address=my_address,
    value=0,
    tag=my_tag,
    message=trytes_encrypted_data,
)

print('Sending transfer...')
# Send the transaction to the network
response = api.send_transfer([tx])

print('Check your transaction on the Tangle!')
print('https://utils.iota.org/transaction/%s/devnet' % response['bundle'][0].hash)
print('Tail transaction hash of the bundle is: %s' % response['bundle'].tail_transaction.hash)