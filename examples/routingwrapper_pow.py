# coding=utf-8
"""
Simple example using the RoutingWrapper to route API requests to different nodes.
See: https://github.com/iotaledger/documentation/blob/iota.lib.py/1.2.x/source/includes/_adapters.md#routingwrapper
"""
from iota import *
from iota.adapter.wrappers import RoutingWrapper

api =\
  Iota(
    # Send PoW requests to local node.
    # All other requests go to light wallet node.
    RoutingWrapper('http://service.iotasupport.com:14265')
      .add_route('attachToTangle', 'http://localhost:14265'),

    # Seed used for cryptographic functions.
    seed = b'SEED9GOES9HERE'
  )

# Example of sending a transfer using the adapter.
bundle = api.send_transfer(
  depth = 100,
  transfers = [
    ProposedTransaction(
      # Recipient of the transfer.
      address =
        Address(
          #b'TESTVALUE9DONTUSEINPRODUCTION99999FBFFTG'
          #b'QFWEHEL9KCAFXBJBXGE9HID9XCOHFIDABHDG9AHDR'
        ),

      # Amount of IOTA to transfer.
      # This value may be zero.
      value = 1,

      # Optional tag to attach to the transfer.
      tag = Tag(b'ADAPT'),

      # Optional message to include with the transfer.
      message = TryteString.from_string('Hello!'),
    ),
  ],
)
