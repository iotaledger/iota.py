# Import neccessary modules
from iota import Iota
from pprint import pprint

# Declare an API object
api = Iota('https://nodes.devnet.iota.org:443')

# Request information about the node
response = api.get_node_info()

# Using pprint instead of print for a nicer looking result in the console
pprint(response)