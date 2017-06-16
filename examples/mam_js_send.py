# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import codecs
import json
from argparse import ArgumentParser
from pprint import pformat
from subprocess import PIPE, run
from typing import List, Optional, Text

import filters as f
from six import binary_type, text_type

from iota import Bundle, Iota, TransactionTrytes
from iota.bin import IotaCommandLineApp
from iota.json import JsonEncoder
from iota.crypto.addresses import AddressGenerator
from iota.filters import Trytes


class IotaMamExample(IotaCommandLineApp):
  """
  Shows how to integrate the ``mam.client.js`` Javascript library into a
  Python script, until MAM functionality is implemented in PyOTA.

  In order to execute this script, you must install Node and the
  ``mam.client.js`` library.

  See https://github.com/iotaledger/mam.client.js for more information.
  """
  def execute(self, api, **arguments):
    # type: (Iota, ...) -> int
    channel_key_index     = arguments['channel_key_index'] # type: int
    count                 = arguments['count'] # type: int
    depth                 = arguments['depth'] # type: int
    dry_run               = arguments['dry_run'] # type: bool
    mam_encrypt_path      = arguments['mam_encrypt_path'] # type: Text
    min_weight_magnitude  = arguments['min_weight_magnitude'] # type: int
    message_encoding      = arguments['message_encoding'] # type: Text
    message_file          = arguments['message_file'] # type: Optional[Text]
    security_level        = arguments['security_level'] # type: int
    start                 = arguments['start'] # type: int

    if message_file:
      with codecs.open(message_file, 'r', message_encoding) as f_: # type: codecs.StreamReaderWriter
        message = f_.read()

    else:
      self.stdout.write(
        'Enter message to send.  Press Ctrl-D on a blank line when done.\n\n',
      )

      message = self.stdin.read().strip()
      self.stdout.write('\n')

    # Generating the encrypted message may take a little while, so we
    # should provide some feedback to the user so that they know that
    # their input is being processed (this is especially important if
    # the user typed in their message, so that they don't press ^D
    # again, thinking that the program didn't register the first one).
    self.stdout.write('Encrypting message...\n')

    proc =\
      run(
        args = [
          # mam_encrypt.js
          mam_encrypt_path,

          # Required arguments
          binary_type(api.seed),
          message,

          # Options
          '--channel-key-index', text_type(channel_key_index),
          '--start', text_type(start),
          '--count', text_type(count),
          '--security-level', text_type(security_level),
        ],

        check   = True,
        stdout  = PIPE,
        stderr  = self.stderr,
      )

    # The output of the JS script is a collection of transaction
    # trytes, encoded as JSON.
    filter_ =\
      f.FilterRunner(
        starting_filter =
            f.Required
          | f.Unicode
          | f.JsonDecode
          | f.Array
          | f.FilterRepeater(
                f.ByteString(encoding='ascii')
              | Trytes(result_type=TransactionTrytes)
            ),

        incoming_data = proc.stdout,
      )

    if not filter_.is_valid():
      self.stderr.write(
        'Invalid output from {mam_encrypt_path}:\n'
        '\n'
        'Output:\n'
        '{output}\n'
        '\n'
        'Errors:\n'
        '{errors}\n'.format(
          errors            = pformat(filter_.get_errors(with_context=True)),
          mam_encrypt_path  = mam_encrypt_path,
          output            = proc.stdout,
        ),
      )

      return 2

    transaction_trytes = filter_.cleaned_data # type: List[TransactionTrytes]

    bundle = Bundle.from_tryte_strings(transaction_trytes)

    if dry_run:
      self.stdout.write('Transactions:\n\n')
      self.stdout.write(json.dumps(bundle, cls=JsonEncoder, indent=2))
    else:
      api.send_trytes(
        depth                 = depth,
        trytes                = transaction_trytes,
        min_weight_magnitude  = min_weight_magnitude,
      )

      self.stdout.write('Message broadcast successfully!\n')
      self.stdout.write(
        'Bundle ID: {bundle_hash}\n'.format(
          bundle_hash = bundle.hash,
        ),
      )

    return 0

  def create_argument_parser(self):
    # type: () -> ArgumentParser
    parser = super(IotaMamExample, self).create_argument_parser()

    parser.add_argument(
      'mam_encrypt_path',

        help = 'Path to `mam_encrypt.js` script.',
    )

    parser.add_argument(
      '--channel-key-index',
        default = 0,
        dest    = 'channel_key_index',
        type    = int,

        help = 'Index of the key used to establish the channel.',
    )

    parser.add_argument(
      '--start',
        default = 0,
        type    = int,

        help = 'Index of the first key used to encrypt the message.',
    )

    parser.add_argument(
      '--count',
        default = 1,
        type    = int,

        help = 'Number of keys to use to encrypt the message.',
    )

    parser.add_argument(
      '--security-level',
        default = AddressGenerator.DEFAULT_SECURITY_LEVEL,
        type    = int,

        help = 'Number of iterations to use when generating keys.',
    )

    parser.add_argument(
      '--message-file',
        dest = 'message_file',

        help =
          'Path to file containing the message to send. '
          'If not provided, you will be prompted for the message via stdin.',
    )

    parser.add_argument(
      '--message-encoding',
        dest    = 'message_encoding',
        default = 'utf-8',

        help = 'Encoding used to interpret message.',
    )

    parser.add_argument(
      '--depth',
        default = 3,
        type    = int,

        help = 'Depth at which to attach the resulting transactions.',
    )

    parser.add_argument(
      '--min-weight-magnitude',
        dest  = 'min_weight_magnitude',
        type  = int,

        help =
          'Min weight magnitude, used by the node to calibrate PoW. '
          'If not provided, a default value will be used.',
    )

    parser.add_argument(
      '--dry-run',
        action  = 'store_true',
        default = False,
        dest    = 'dry_run',

        help =
          'If set, resulting transactions will be sent to stdout instead of'
          'broadcasting to the Tangle.',
    )

    return parser


if __name__ == '__main__':
  IotaMamExample().main()
