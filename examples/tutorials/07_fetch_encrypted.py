"""
Decrypt data fetched from the Tangle.

simplecrypt library is needed for this example (`pip install simple-crypt`)!
"""
from iota import Iota
from simplecrypt import decrypt
from base64 import b64decode
from getpass import getpass

import json

# Declare an API object
api = Iota('https://nodes.devnet.iota.org:443', devnet=True)

# Prompt user for tail tx hash of the bundle
tail_hash = input('Tail transaction hash of the bundle: ')

print('Looking for bundle on the Tangle...')
# Fetch bundle
bundle = api.get_bundles([tail_hash])['bundles'][0]

print('Extracting data from bundle...')
# Get all messages from the bundle and concatenate them
b64_encrypted_data = "".join(bundle.get_messages())

# Decode from base64
encrypted_data = b64decode(b64_encrypted_data)

# Prompt for passwword
password = getpass('Password to be used for decryption:')

print('Decrypting data...')
# Decrypt data
# decrypt returns 'bytes' in Python 3, decode it into string
json_data = decrypt(password, encrypted_data).decode('utf-8')

# Convert JSON string to python dict object
data = json.loads(json_data)

print('Succesfully decrypted the following data:')
print(data)