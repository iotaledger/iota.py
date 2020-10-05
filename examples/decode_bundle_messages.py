from iota import Iota
from iota import TryteString
from iota.commands.extended.utils import get_bundles_from_transaction_hashes as goget

# declare node; change as you see fit
api = Iota('https://nodes.thetangle.org:443')

# this MWE assumes that you already have you already have a bundle hash; one is declared here as an example
bundle_hash = [TryteString('YXPOLGAAEWVBCHH9CGOPNJXE9HQHHLJFTDQKKLHFGOHOWKZQGHOQVZSCVIRKDEJVGDQPT99WOZHVCUYDC')]

# return all transactions in the bundle
bundle_transactions = api.find_transactions( bundles = bundle_hash )['hashes']

# return transaction objects for each tranaction in bundle
transaction_objs = vars(goget(api.adapter,bundle_transactions,False)[0])['transactions']

# string together message across transactions
message = ''
for t in transaction_objs:
	message = message + str(vars(t)['signature_message_fragment'])

# print message decoded:
print TryteString(message).decode()
