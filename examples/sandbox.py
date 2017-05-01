# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota import *
from iota.adapter.sandbox import SandboxAdapter


# Create the API object.
iota =\
  Iota(
    # To use sandbox mode, inject a ``SandboxAdapter``.
    adapter = SandboxAdapter(
      # URI of the sandbox node.
      uri = 'https://sandbox.iota.org/api/v1/',

      # Access token used to authenticate requests.
      # Contact the node maintainer to get an access token.
      auth_token = 'auth token goes here',
    ),

    # Seed used for cryptographic functions.
    # If null, a random seed will be generated.
    seed = b'SEED9GOES9HERE',
  )

# Example of sending a transfer using the sandbox.
# For more information, see :py:meth:`Iota.send_transfer`.
# noinspection SpellCheckingInspection
iota.send_transfer(
  depth = 100,

  # One or more :py:class:`ProposedTransaction` objects to add to the
  # bundle.
  transfers = [
    ProposedTransaction(
      # Recipient of the transfer.
      address =
        Address(
          b'TESTVALUE9DONTUSEINPRODUCTION99999FBFFTG'
          b'QFWEHEL9KCAFXBJBXGE9HID9XCOHFIDABHDG9AHDR'
        ),

      # Amount of IOTA to transfer.
      # This value may be zero.
      value = 42,

      # Optional tag to attach to the transfer.
      tag = Tag(b'EXAMPLE'),

      # Optional message to include with the transfer.
      message = TryteString.from_string('Hello, Tangle!'),
    ),
  ],
)
