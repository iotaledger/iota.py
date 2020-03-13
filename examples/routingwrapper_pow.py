"""
Simple example using the RoutingWrapper to route API requests to
different nodes.

References:

- https://pyota.readthedocs.io/en/develop/adapters.html#routingwrapper
"""
from iota import Address, Iota, ProposedTransaction, Tag, TryteString
from iota.adapter.wrappers import RoutingWrapper

# Send PoW requests to local node.
# All other requests go to light wallet node.
router = RoutingWrapper('http://service.iotasupport.com:14265')
router.add_route('attachToTangle', 'http://localhost:14265')

api = Iota(router, seed=b'SEED9GOES9HERE')

# Example of sending a transfer using the adapter.
bundle = api.send_transfer(
    depth=3,

    transfers=[
        ProposedTransaction(
            # Recipient of the transfer.
            address=Address(
                # b'TESTVALUE9DONTUSEINPRODUCTION99999FBFFTG'
                # b'QFWEHEL9KCAFXBJBXGE9HID9XCOHFIDABHDG9AHDR'
            ),

            # Amount of IOTA to transfer.
            # This value may be zero.
            value=1,

            # Optional tag to attach to the transfer.
            tag=Tag(b'ADAPT'),

            # Optional message to include with the transfer.
            message=TryteString.from_string('Hello!'),
        ),
    ],
)
