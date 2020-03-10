"""
Generates a shiny new IOTA address that you can use for transfers!
"""

from argparse import ArgumentParser
from getpass import getpass as secure_input
from sys import argv
from typing import Optional, Text

from iota import Iota, __version__
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed


def main(uri, index, count, security, checksum):
    # type: (Text, int, Optional[int], Optional[int], bool) -> None
    seed = get_seed()

    # Create the API instance.
    # Note: If ``seed`` is null, a random seed will be generated.
    api = Iota(uri, seed)

    # If we generated a random seed, then we need to display it to the
    # user, or else they won't be able to use their new addresses!
    if not seed:
        print('A random seed has been generated. Press return to see it.')
        output_seed(api.seed)

    print('Generating addresses.  This may take a few minutes...')
    print('')

    # Here's where all the magic happens!
    api_response = api.get_new_addresses(index, count, security, checksum)
    for addy in api_response['addresses']:
        print(bytes(addy).decode('ascii'))

    print('')


def get_seed():
    # type: () -> bytes
    """
    Prompts the user securely for their seed.
    """
    print(
        'Enter seed and press return (typing will not be shown).  '
        'If empty, a random seed will be generated and displayed on the screen.'
    )
    seed = secure_input('')  # type: Text
    return seed.encode('ascii')


def output_seed(seed):
    # type: (Seed) -> None
    """
    Outputs the user's seed to stdout, along with lots of warnings
    about security.
    """
    print(
        'WARNING: Anyone who has your seed can spend your IOTAs! '
        'Clear the screen after recording your seed!'
    )
    input('')
    print('Your seed is:')
    print('')
    print(bytes(seed).decode('ascii'))
    print('')

    print(
        'Clear the screen to prevent shoulder surfing, '
        'and press return to continue.'
    )
    print('https://en.wikipedia.org/wiki/Shoulder_surfing_(computer_security)')
    input('')


if __name__ == '__main__':
    parser = ArgumentParser(
        description=__doc__,
        epilog='PyOTA v{version}'.format(version=__version__),
    )

    parser.add_argument(
        '--uri',
        type=str,
        default='http://localhost:14265/',

        help=(
            'URI of the node to connect to '
            '(defaults to http://localhost:14265/).'
        ),
    )

    parser.add_argument(
        '--index',
        type=int,
        default=0,
        help='Index of the key to generate.',
    )

    parser.add_argument(
        '--count',
        type=int,
        default=None,

        help=(
            'Number of addresses to generate. '
            'If not specified, the first unused address will be returned.'
        ),
    )

    parser.add_argument(
        '--security',
        type=int,
        default=AddressGenerator.DEFAULT_SECURITY_LEVEL,
        help=(
            'Security level to be used for the private key / address. '
            'Can be 1, 2 or 3'
        ),
    )

    parser.add_argument(
        '--with-checksum',
        action='store_true',
        default=False,
        dest='checksum',
        help='List the address with the checksum.',
    )

    main(**vars(parser.parse_args(argv[1:])))
