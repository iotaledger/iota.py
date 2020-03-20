from iota import Iota, Seed, Address, TryteString, ProposedTransaction, Tag

# Put your seed here from Tutorial 4.a, or a seed that owns tokens (devnet)
my_seed = Seed(b'YOURSEEDFROMTHEPREVIOUSTUTORIAL')

# Declare an API object
api = Iota(
    adapter='https://nodes.devnet.iota.org:443',
    seed=my_seed,
    devnet=True,
)

# Addres to receive 1i
# Feel free to replace it. For example, run the code from Tutorial 4.a
# and use that newly generated address with a 'fresh' seed.
receiver = Address(b'WWUTQBO99YDCBVBPAPVCANW9ATSNUPPLCPGDQXGQEVLUBSFHCEWOA9DIYYOXJONDIRHYPXQXOYXDPHREZ')

print('Constructing transfer of 1i...')
# Create the transfer object
tx = ProposedTransaction(
    address=receiver,
    value=1,
    message=TryteString.from_unicode('I just sent you 1i, use it wisely!'),
    tag=Tag('VALUETX'),
)

print('Preparing bundle and sending it to the network...')
# Prepare the transfer and send it to the network
response = api.send_transfer(transfers=[tx])

print('Check your transaction on the Tangle!')
print('https://utils.iota.org/bundle/%s/devnet' % response['bundle'].hash)