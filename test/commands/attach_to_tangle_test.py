# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from six import binary_type

from iota.commands.attach_to_tangle import AttachToTangleCommand
from iota.types import TransactionId, TryteString
from test import MockAdapter


# noinspection SpellCheckingInspection
class AttachToTangleCommandTestCase(TestCase):
  def setUp(self):
    super(AttachToTangleCommandTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.command  = AttachToTangleCommand(self.adapter)

  def test_happy_path(self):
    """Successful invocation of `attachToTangle`."""
    expected_response = {
      'trytes': ['TRYTEVALUEHERE']
    }

    self.adapter.response = expected_response

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

    response = self.command(
      trunk_transaction     = trunk_transaction,
      branch_transaction    = branch_transaction,
      min_weight_magnitude  = min_weight_magnitude,
      trytes                = trytes,
    )

    self.assertDictEqual(response, expected_response)

    self.assertListEqual(
      list(map(type, response['trytes'])),
      [TryteString],
    )

    self.assertListEqual(
      self.adapter.requests,
      [(
        {
          'command':            'attachToTangle',
          'minWeightMagnitude': min_weight_magnitude,

          # We can't send TryteString objects across the wire, so
          #   trytes were converted into ASCII for transport.
          'trunkTransaction':   binary_type(trunk_transaction),
          'branchTransaction':  binary_type(branch_transaction),
          'trytes':             [binary_type(trytes[0])],
        },

        {},
      )]
    )

  def test_compatible_types(self):
    """
    Calling `attachToTangle` with parameters that can be converted into
      the correct types.
    """
    self.command(
      # Any value that can be converted into a TransactionId is valid
      #   here.
      trunk_transaction =\
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',

      branch_transaction =\
        TryteString(
          b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
          b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
        ),

      # This still has to be an int, however.
      min_weight_magnitude = 30,

      # Just to be extra tricky, let's see what happens if `trytes` is
      #   a generator.
      trytes = (
        t for t in [
          # `trytes` can contain any value that can be converted into a
          #   TryteString.
          b'TRYTEVALUEHERE',

          # This is probably wrong, but maybe not.
          TransactionId(b'TRANSACTIONIDHERE'),
        ]
      ),
    )

    # Not interested in the response, but we should check to make sure
    #   that the incoming values were converted correctly.
    request = self.adapter.requests[0][0]

    self.assertDictEqual(
      request,

      {
        'command':            'attachToTangle',
        'minWeightMagnitude': 30,

        'trunkTransaction':
            b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
            b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
          ,

        'branchTransaction':
            b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
            b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
          ,

        'trytes': [
          b'TRYTEVALUEHERE',

          b'TRANSACTIONIDHERE99999999999999999999999'
          b'99999999999999999999999999999999999999999',
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

    with self.assertRaises(TypeError):
      self.command(
        # Now you're not making any sense.
        trunk_transaction = None,

        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
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

    with self.assertRaises(TypeError):
      self.command(
        # Now you're not making any sense.
        branch_transaction = None,

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(TypeError):
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

    with self.assertRaises(TypeError):
      self.command(
        # Nice try, but it's gotta be an int.
        min_weight_magnitude = 18.0,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.command(
        # Oh, come on.  You know what I meant!
        min_weight_magnitude = True,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.command(
        # I swear you're doing this on purpose just to annoy me.
        min_weight_magnitude = 'eighteen',

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.command(
        # This parameter is required.
        min_weight_magnitude = None,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(ValueError):
      self.command(
        # Minimum value for this parameter is 18.
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

    with self.assertRaises(TypeError):
      self.command(
        # It's gotta be a list.
        trytes = TryteString(b'TRYTEVALUEHERE'),

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )

    with self.assertRaises(ValueError):
      self.command(
        # Ok, you got the list part down, but you have to put something
        #   inside it.
        trytes = [],

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )
