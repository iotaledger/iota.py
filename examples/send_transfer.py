"""
Example script that shows how to use PyOTA to send a transfer to an address.
"""
from argparse import ArgumentParser
from sys import argv

from iota import (
  __version__,
  Address,
  Iota,
  ProposedTransaction,
  Tag,
  TryteString,
)
from .address_generator import get_seed, output_seed


def main(address, depth, message, tag, uri, value):
    # Ensure seed is not displayed in cleartext.
    seed = get_seed()
    # Create the API instance.
    api = Iota(uri, seed)

    if not seed:
        print('A random seed has been generated. Press return to see it.')
        output_seed(api.seed)

    print('Starting transfer.')
    # For more information, see :py:meth:`Iota.send_transfer`.
    api.send_transfer(
        depth=depth,
        # One or more :py:class:`ProposedTransaction` objects to add to the
        # bundle.
        transfers=[
            ProposedTransaction(
                # Recipient of the transfer.
                address=Address(address),

                # Amount of IOTA to transfer.
                # By default this is a zero value transfer.
                value=value,

                # Optional tag to attach to the transfer.
                tag=Tag(tag),

                # Optional message to include with the transfer.
                message=TryteString.from_string(message),
            ),
        ],
    )
    print('Transfer complete.')

if __name__ == '__main__':
    parser = ArgumentParser(
        description=__doc__,
        epilog='PyOTA v{version}'.format(version=__version__),
    )

    parser.add_argument(
        '--address',
        type=str,
        default=b'RECEIVINGWALLETADDRESSGOESHERE9WITHCHECKSUMANDSECURITYLEVELB999999999999999999999999999999',
        help=
        'Receiving address'
        '(defaults to RECEIVINGWALLETADDRESSGOESHERE9WITHCHECKSUMANDSECURITYLEVELB999999999999999999999999999999).',
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help=
        'Depth at which to attach the bundle.'
        '(defaults to 3).',
    )

    parser.add_argument(
        '--message',
        type=str,
        default='Hello World!',
        help=
        'Transfer message.'
        '(defaults to Hello World!).',
    )

    parser.add_argument(
        '--tag',
        type=str,
        default=b'EXAMPLE',
        help=
        'Transfer tag'
        '(defaults to EXAMPLE).',
    )

    parser.add_argument(
        '--uri',
        type=str,
        default='http://localhost:14265/',
        help=
        'URI of the node to connect to.'
        '(defaults to http://localhost:14265/).',
    )

    parser.add_argument(
        '--value',
        type=int,
        default=0,
        help=
        'Value to transfer'
        '(defaults to 0).',
    )

    main(**vars(parser.parse_args(argv[1:])))

