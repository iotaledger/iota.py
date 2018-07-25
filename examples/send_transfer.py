# coding=utf-8
"""
Example script that shows how to use PyOTA to send a transfer to an address.
"""
from iota import Address, Iota, Tag, TryteString
from iota.transaction.creation import ProposedTransaction

SEED1 = b"THE9SEED9OF9THE9WALLET9SENDING9GOES9HERE"

ADDRESS_WITH_CHECKSUM_SECURITY_LEVEL_2 = (
    b"RECEIVING9WALLET9ADDRESS9GOES9HERE9WITH9CHECKSUM9AND9SECURITY9LEVEL9B"
)

# Create the API instance.
api = Iota(
    # URI of a locally running node.
    'http://localhost:14265/',

    # Seed used for cryptographic functions.
    seed=SEED1,
)

# For more information, see :py:meth:`Iota.send_transfer`.
api.send_transfer(
    depth=3,

    # One or more :py:class:`ProposedTransaction` objects to add to the
    # bundle.
    transfers=[
        ProposedTransaction(
            # Recipient of the transfer.
            address=Address(
                ADDRESS_WITH_CHECKSUM_SECURITY_LEVEL_2,
            ),

            # Amount of IOTA to transfer.
            # This value may be zero.
            value=1,

            # Optional tag to attach to the transfer.
            tag=Tag(b'EXAMPLE'),

            # Optional message to include with the transfer.
            message=TryteString.from_string('Hello!'),
        ),
    ],
)
