# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional
from unittest import TestCase

from iota import IotaApi
from iota.adapter import BaseAdapter
from iota.types import TryteString


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

  def test_get_node_info_happy_path(self):
    """Successful invocation of `getNodeInfo`."""
    # noinspection SpellCheckingInspection
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

    adapter = MockAdapter(expected_response)
    api     = IotaApi(adapter)

    response = api.get_node_info()

    self.assertDictEqual(response, expected_response)

    self.assertIsInstance(response['latestMilestone'], TryteString)

    self.assertIsInstance(
      response['latestSolidSubtangleMilestone'],
      TryteString,
    )

    self.assertListEqual(
      adapter.requests,
      [({'command': 'getNodeInfo'}, {})],
    )
