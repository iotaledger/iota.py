from iota import Iota, Seed

# Generate a random seed, or use one you already have (for the devnet)
print('Generating a random seed...')
my_seed = Seed.random()
# my_seed = Seed(b'MYCUSTOMSEED')
print('Your seed is: ' + str(my_seed))

# Declare an API object
api = Iota(
    adapter='https://nodes.devnet.iota.org:443',
    seed=my_seed,
    devnet=True,
)

print('Generating the first unused address...')
# Generate the first unused address from the seed
response = api.get_new_addresses()

addy = response['addresses'][0]

print('Your new address is: ' + str(addy))
print('Go to https://faucet.devnet.iota.org/ and enter you address to receive free devnet tokens.')