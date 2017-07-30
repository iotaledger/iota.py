# coding=utf-8
"""
Example script that shows how to use PyOTA to send a transfer to an address.
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from getpass import getpass as secure_input
from sys import argv

from iota import *
from iota import __version__
from six import binary_type, moves as compat, text_type


def main(uri):
  # type: (Text, int, Optional[int], bool) -> None

  seed = get_seed()

  if not seed:
      print("No seed entered, transfer cancelled.")
      return

  addressString = get_address()

  if not addressString:
      print("No address entered, transfer cancelled.")
      return

  value = get_value()

  print("Sending " + str(value) + "iota to address: " + addressString)

  # Create the API instance.
  api = Iota(uri, seed)

  bundle = api.send_transfer(
    depth = 100,
    transfers = [
      ProposedTransaction(
        address = Address(bytearray(addressString)),
        value = value,
        tag = Tag(b'EXAMPLE'),
        message = TryteString.from_string('Hello!'),
      ),
    ],
  )

  print('Transfer complete')


def get_seed():
  # type: () -> binary_type
  """
  Prompts the user securely for their seed.
  """
  print(
    'Enter seed to send from and press return (typing will not be shown).  '
  )
  seed = secure_input('')

  if seed == '':
      return None

  return seed.encode('ascii')


def get_address():
   # type: () -> binary_type
   """
   Prompts the user for the address to send to.
   """
   print(
     'Enter address to send to.'
   )
   address = secure_input('')

   if address == '':
     print("No address")
     return None

   return address


def get_value():
  """
  Prompts the user for the value to send.
  """

  try:
    valueStr = secure_input("Enter a value to send: ")
    value = int(valueStr)
    return value
  except ValueError:
    print("Invalid amoumt, defaulting to 0.")
    return 0

if __name__ == '__main__':

  parser = ArgumentParser(
    description = __doc__,
    epilog      = 'PyOTA v{version}'.format(version=__version__),
  )

  parser.add_argument(
    '--uri',
      type    = text_type,
      default = 'http://localhost:14265/',
      help =
        'URI of the node to connect to '
        '(defaults to http://localhost:14265/).',
  )

  main(**vars(parser.parse_args(argv[1:])))
