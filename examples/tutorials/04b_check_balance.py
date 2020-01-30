from iota import Iota, Address
import time

# Put your address from Tutorial 4.a here
my_address = Address(b'YOURADDRESSFROMTHEPREVIOUSTUTORIAL')

# Declare an API object
api = Iota(adapter='https://nodes.devnet.iota.org:443', devnet=True)

# Script actually runs until you load up your address
success = False

while not success:
    print('Checking balance on the Tangle for a specific address...')
    # API method to check balance
    response = api.get_balances(addresses=[my_address])

    # response['balances'] is a list!
    if response['balances'][0]:
        print('Found the following information for address ' + str(my_address) + ':')
        print('Balance: ' + str(response['balances'][0]) + 'i')
        success = True
    else:
        print('Zero balance found, retrying in 30 seconds...')
        time.sleep(30)