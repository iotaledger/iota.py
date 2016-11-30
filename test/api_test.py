# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional
from unittest import TestCase

from iota import IotaApi
from iota.adapter import BaseAdapter


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

  def test_supported_command(self):
    """Sending a supported command."""
    expected_response = {'appName': 'IRI', 'appVersion': '1.1.1'}

    adapter = MockAdapter(expected_response)
    api     = IotaApi(adapter)

    response = api.get_node_info()

    self.assertEqual(response, expected_response)

    self.assertListEqual(adapter.requests, [({'command': 'getNodeInfo'}, {})])
