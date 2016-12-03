# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterError
from iota.commands.attach_to_tangle import AttachToTangleCommand
from iota.types import TransactionId, TryteString
from test.commands import BaseFilterCommandTestCase


# noinspection SpellCheckingInspection
class AttachToTangleCommandTestCase(BaseFilterCommandTestCase):
  command_type = AttachToTangleCommand

  def test_happy_path(self):
    """Successful invocation of `attachToTangle`."""
    self.adapter.response = {
      'trytes': ['TRYTEVALUEHERE']
    }

    trunk_transaction =\
      TransactionId(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
      )

    branch_transaction =\
      TransactionId(
        b'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT'
        b'DTGAFLPLBZ9FOFWWTKMAZXZHFGQHUOXLXUALY9999'
      )

    min_weight_magnitude  = 20
    trytes                = [TryteString(b'TRYTVALUEHERE')]

    self.assertCommandSuccess(
      expected_response = {
        'trytes': [TryteString(b'TRYTEVALUEHERE')]
      },

      request = {
        'trunk_transaction':    trunk_transaction,
        'branch_transaction':   branch_transaction,
        'min_weight_magnitude': min_weight_magnitude,
        'trytes':               trytes,
      },
    )

  def test_compatible_types(self):
    """
    Calling `attachToTangle` with parameters that can be converted into
      the correct types.
    """
    self.adapter.response = {
      'trytes': ['TRYTEVALUEHERE', 'TRANSACTIONIDHERE']
    }

    self.assertCommandSuccess(
      expected_response = {
        'trytes': [
          TryteString(b'TRYTEVALUEHERE'),
          TryteString(b'TRANSACTIONIDHERE'),
        ],
      },

      request = {
        # Any value that can be converted into a TransactionId is valid
        #   here.
        'trunk_transaction':
          b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
          b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',

        'branch_transaction':
          TryteString(
            b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
            b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
          ),

        # This still has to be an int, however.
        'min_weight_magnitude': 30,

        'trytes': [
            # `trytes` can contain any value that can be converted into a
            #   TryteString.
            b'TRYTEVALUEHERE',

            # This is probably wrong, but maybe not.
            TransactionId(b'TRANSACTIONIDHERE'),
        ],
      },
    )

  # noinspection PyTypeChecker
  def test_error_trunk_transaction_invalid(self):
    """
    Attempting to call `attachToTangle`, but the `trunkTransaction`
      parameter is not valid.
    """
    branch_transaction =\
      TransactionId(
        b'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT'
        b'DTGAFLPLBZ9FOFWWTKMAZXZHFGQHUOXLXUALY9999'
      )

    trytes = [TryteString(b'TRYTEVALUEHERE')]

    with self.assertRaises(FilterError):
      self.command(
        # Bytes are allowed, but not strings.
        trunk_transaction = 'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT',

        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Now you're not making any sense.
        trunk_transaction = None,

        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Are you even listening to me?
        trunk_transaction = 42,

        branch_transaction = branch_transaction,
        trytes             = trytes,
      )

  # noinspection PyTypeChecker,PyUnresolvedReferences
  def test_error_branch_transaction_invalid(self):
    """
    Attempting to call `attachToTangle`, but the `branchTransaction`
      parameter is not valid.
    """
    trunk_transaction =\
      TransactionId(
        b'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT'
        b'DTGAFLPLBZ9FOFWWTKMAZXZHFGQHUOXLXUALY9999'
      )

    trytes = [TryteString(b'TRYTEVALUEHERE')]

    with self.assertRaises(FilterError):
      self.command(
        # Bytes are allowed, but not strings.
        branch_transaction = 'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT',

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Now you're not making any sense.
        branch_transaction = None,

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Are you even listening to me?
        branch_transaction = 42,

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

  # noinspection PyTypeChecker
  def test_error_min_weight_magnitude_invalid(self):
    """
    Attempting to call `attachToTangle`, but the `minWeightMagnitude`
      parameter is not valid.
    """
    trunk_transaction =\
      TransactionId(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
      )

    branch_transaction =\
      TransactionId(
        b'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT'
        b'DTGAFLPLBZ9FOFWWTKMAZXZHFGQHUOXLXUALY9999'
      )

    trytes = [TryteString(b'TRYTVALUEHERE')]

    with self.assertRaises(FilterError):
      self.command(
        # Nice try, but it's gotta be an int.
        min_weight_magnitude = 18.0,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Oh, come on.  You know what I meant!
        min_weight_magnitude = True,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # I swear you're doing this on purpose just to annoy me.
        min_weight_magnitude = 'eighteen',

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Better, but the minimum value for this parameter is 18.
        min_weight_magnitude = 17,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

  # noinspection PyTypeChecker
  def test_error_trytes_invalid(self):
    """
    Attempting to call `attachToTangle`, but the `trytes` parameter is
      not valid.
    """
    trunk_transaction =\
      TransactionId(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
      )

    branch_transaction =\
      TransactionId(
        b'P9KFSJVGSPLXAEBJSHWFZLGP9GGJTIO9YITDEHAT'
        b'DTGAFLPLBZ9FOFWWTKMAZXZHFGQHUOXLXUALY9999'
      )

    with self.assertRaises(FilterError):
      self.command(
        # It's gotta be a list.
        trytes = TryteString(b'TRYTEVALUEHERE'),

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )

    with self.assertRaises(FilterError):
      self.command(
        # Ok, you got the list part down, but you have to put something
        #   inside it.
        trytes = [],

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )

    with self.assertRaises(FilterError):
      self.command(
        # I hate you so much.
        trytes = [42],

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )
