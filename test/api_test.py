# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional
from unittest import TestCase

from iota import IotaApi
from iota.adapter import BaseAdapter
from iota.types import TryteString, TransactionId


class MockAdapter(BaseAdapter):
  """An adapter for IotaApi that always returns a mocked response."""
  supported_protocols = ('mock',)

  def __init__(self, response=None):
    # type: (Optional[dict]) -> None
    super(MockAdapter, self).__init__()

    self.response = response

    self.requests = []

  def send_request(self, payload, **kwargs):
    self.requests.append((payload, kwargs))
    return self.response


class IotaApiTestCase(TestCase):
  def test_init_with_uri(self):
    """
    Passing a URI to the initializer instead of an adapter instance.
    """
    api = IotaApi('mock://')
    self.assertIsInstance(api.adapter, MockAdapter)

  def test_custom_command(self):
    """Sending an experimental/unsupported command."""
    expected_response = {'message': 'Hello, IOTA!'}

    adapter = MockAdapter(expected_response)
    api     = IotaApi(adapter)

    response = api.helloWorld()

    self.assertEqual(response, expected_response)

    self.assertListEqual(
      adapter.requests,
      [({'command': 'helloWorld'}, {})],
    )

  def test_custom_command_with_arguments(self):
    """Sending an experimental/unsupported command with arguments."""
    expected_response = {'message': 'Hello, IOTA!'}

    adapter = MockAdapter(expected_response)
    api     = IotaApi(adapter)

    response = api.helloWorld(foo='bar', baz='luhrmann')

    self.assertEqual(response, expected_response)

    self.assertListEqual(
      adapter.requests,
      [({'command': 'helloWorld', 'foo': 'bar', 'baz': 'luhrmann'}, {})],
    )


# noinspection SpellCheckingInspection
class AttachToTangleTestCase(TestCase):
  def setUp(self):
    super(AttachToTangleTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.api      = IotaApi(self.adapter)

  def test_happy_path(self):
    """Successful invocation of `attachToTangle`."""
    expected_response = {
      'trytes':['TRYTEVALUEHERE']
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

    response = self.api.attach_to_tangle(
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
          'trunkTransaction':   trunk_transaction.trytes,
          'branchTransaction':  branch_transaction.trytes,
          'minWeightMagnitude': min_weight_magnitude,
          'trytes':             [trytes[0].trytes],
        },

        {},
      )]
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
      self.api.attach_to_tangle(
        # Nope; the trytes have to be in a container.
        trunk_transaction =
          b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
          b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',

        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Sorry, not good enough; it's gotta be a TransactionId.
        trunk_transaction =
          TryteString(
            b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
            b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
          ),

        branch_transaction = branch_transaction,
        trytes             = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Now you're not making any sense.
        trunk_transaction = None,

        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Are you even listening to me?
        trunk_transaction = 42,

        branch_transaction = branch_transaction,
        trytes             = trytes,
      )

  # noinspection PyTypeChecker
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
      self.api.attach_to_tangle(
        # Nope; the trytes have to be in a container.
        branch_transaction =
          b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
          b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Sorry, not good enough; it's gotta be a TransactionId.
        branch_transaction =
          TryteString(
            b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
            b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
          ),

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Now you're not making any sense.
        branch_transaction = None,

        trunk_transaction = trunk_transaction,
        trytes            = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
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
      self.api.attach_to_tangle(
        # Nice try, but it's gotta be an int.
        min_weight_magnitude = 18.0,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # Oh, come on.  You know what I meant!
        min_weight_magnitude = True,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # I swear you're doing this on purpose just to annoy me.
        min_weight_magnitude = 'eighteen',

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # This parameter is required.
        min_weight_magnitude = None,

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
        trytes              = trytes,
      )

    with self.assertRaises(ValueError):
      self.api.attach_to_tangle(
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
      self.api.attach_to_tangle(
        # It's gotta be a list.
        trytes = TryteString(b'TRYTEVALUEHERE'),

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )

    with self.assertRaises(ValueError):
      self.api.attach_to_tangle(
        # Ok, you got the list part down, but you have to put something
        #   inside it.
        trytes = [],

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )

    with self.assertRaises(TypeError):
      self.api.attach_to_tangle(
        # No, no, no!  They all have to be TryteStrings!
        trytes = [TryteString(b'TRYTEVALUEHERE'), b'QUACK'],

        trunk_transaction   = trunk_transaction,
        branch_transaction  = branch_transaction,
      )


# noinspection SpellCheckingInspection
class GetNodeInfoTestCase(TestCase):
  def setUp(self):
    super(GetNodeInfoTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.api      = IotaApi(self.adapter)

  def test_get_node_info_happy_path(self):
    """Successful invocation of `getNodeInfo`."""
    expected_response = {
      'appName': 'IRI',
      'appVersion': '1.0.8.nu',
      'duration': 1,
      'jreAvailableProcessors': 4,
      'jreFreeMemory': 91707424,
      'jreMaxMemory': 1908932608,
      'jreTotalMemory': 122683392,
      'latestMilestone': 'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJRFKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
      'latestMilestoneIndex': 107,
      'latestSolidSubtangleMilestone': 'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJRFKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
      'latestSolidSubtangleMilestoneIndex': 107,
      'neighbors': 2,
      'packetsQueueSize': 0,
      'time': 1477037811737,
      'tips': 3,
      'transactionsToRequest': 0
    }

    self.adapter.response = expected_response

    response = self.api.get_node_info()

    self.assertDictEqual(response, expected_response)

    self.assertIsInstance(response['latestMilestone'], TryteString)

    self.assertIsInstance(
      response['latestSolidSubtangleMilestone'],
      TryteString,
    )

    self.assertListEqual(
      self.adapter.requests,
      [({'command': 'getNodeInfo'}, {})],
    )
