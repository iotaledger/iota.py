# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from typing import Text
from unittest import TestCase

import requests
from mock import Mock, patch
from six import BytesIO, text_type as text

from iota import BadApiResponse, DEFAULT_PORT, InvalidUri, TryteString
from iota.adapter import HttpAdapter, MockAdapter, resolve_adapter


class ResolveAdapterTestCase(TestCase):
  """
  Unit tests for :py:func:`resolve_adapter`.
  """
  def test_adapter_instance(self):
    """
    Resolving an adapter instance.
    """
    adapter = MockAdapter()
    self.assertIs(resolve_adapter(adapter), adapter)

  def test_udp(self):
    """
    Resolving a valid udp:// URI.
    """
    adapter = resolve_adapter('udp://localhost:14265/')
    self.assertIsInstance(adapter, HttpAdapter)

  def test_http(self):
    """
    Resolving a valid http:// URI.
    """
    adapter = resolve_adapter('http://localhost:14265/')
    self.assertIsInstance(adapter, HttpAdapter)

  def test_missing_protocol(self):
    """
    The URI does not include a protocol.
    """
    with self.assertRaises(InvalidUri):
      resolve_adapter('localhost:14265')

  def test_unknown_protocol(self):
    """
    The URI references a protocol that has no associated adapter.
    """
    with self.assertRaises(InvalidUri):
      resolve_adapter('foobar://localhost:14265')


class HttpAdapterTestCase(TestCase):
  def test_configure_udp(self):
    """
    Configuring an HttpAdapter using a valid udp:// URI.
    """
    adapter = HttpAdapter.configure('udp://localhost:14265/')

    self.assertEqual(adapter.host, 'localhost')
    self.assertEqual(adapter.port, 14265)
    self.assertEqual(adapter.path, '/')

  def test_configure_http(self):
    """
    Configuring HttpAdapter using a valid http:// URI.
    """
    adapter = HttpAdapter.configure('http://localhost:14265/')

    self.assertEqual(adapter.host, 'localhost')
    self.assertEqual(adapter.port, 14265)
    self.assertEqual(adapter.path, '/')

  def test_configure_ipv4_address(self):
    """
    Configuring an HttpAdapter using an IPv4 address.
    """
    adapter = HttpAdapter.configure('udp://127.0.0.1:8080/')

    self.assertEqual(adapter.host, '127.0.0.1')
    self.assertEqual(adapter.port, 8080)
    self.assertEqual(adapter.path, '/')

  def test_configure_default_port_udp(self):
    """
    Implicitly use default UDP port for HttpAdapter.
    """
    adapter = HttpAdapter.configure('udp://iotatoken.com/')

    self.assertEqual(adapter.host, 'iotatoken.com')
    self.assertEqual(adapter.port, DEFAULT_PORT)
    self.assertEqual(adapter.path, '/')

  def test_configure_default_port_http(self):
    """
    Implicitly use default HTTP port for HttpAdapter.
    """
    adapter = HttpAdapter.configure('http://iotatoken.com/')

    self.assertEqual(adapter.host, 'iotatoken.com')
    self.assertEqual(adapter.port, 80)
    self.assertEqual(adapter.path, '/')

  def test_configure_path(self):
    """
    Specifying a different path for HttpAdapter.
    """
    adapter = HttpAdapter.configure('http://iotatoken.com:443/node')

    self.assertEqual(adapter.host, 'iotatoken.com')
    self.assertEqual(adapter.port, 443)
    self.assertEqual(adapter.path, '/node')

  def test_configure_custom_path_default_port(self):
    """
    Configuring HttpAdapter to use a custom path but implicitly use
    default port.
    """
    adapter = HttpAdapter.configure('http://iotatoken.com/node')

    self.assertEqual(adapter.host, 'iotatoken.com')
    self.assertEqual(adapter.port, 80)
    self.assertEqual(adapter.path, '/node')

  def test_configure_default_path(self):
    """
    Implicitly use default path for HttpAdapter.
    """
    adapter = HttpAdapter.configure('udp://example.com:8000')

    self.assertEqual(adapter.host, 'example.com')
    self.assertEqual(adapter.port, 8000)
    self.assertEqual(adapter.path, '/')

  def test_configure_default_port_and_path(self):
    """
    Implicitly use default port and path for HttpAdapter.
    """
    adapter = HttpAdapter.configure('udp://localhost')

    self.assertEqual(adapter.host, 'localhost')
    self.assertEqual(adapter.port, DEFAULT_PORT)
    self.assertEqual(adapter.path, '/')

  def test_configure_error_missing_protocol(self):
    """
    Forgetting to add the protocol to the URI.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('localhost:14265')

  def test_configure_error_invalid_protocol(self):
    """
    Attempting to configure HttpAdapter with unsupported protocol.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('ftp://localhost:14265/')

  def test_configure_error_empty_host(self):
    """
    Attempting to configure HttpAdapter with empty host.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('udp://:14265')

  def test_configure_error_non_numeric_port(self):
    """
    Attempting to configure HttpAdapter with non-numeric port.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('udp://localhost:iota/')

  def test_success_response(self):
    """
    Simulates sending a command to the node and getting a success
    response.
    """
    adapter = HttpAdapter('localhost')

    expected_result = {
      'message': 'Hello, IOTA!',
    }

    mocked_response = self._create_response(json.dumps(expected_result))
    mocked_sender   = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(result, expected_result)

  def test_error_response(self):
    """
    Simulates sending a command to the node and getting an error
    response.
    """
    adapter = HttpAdapter('localhost')

    expected_result = 'Command \u0027helloWorld\u0027 is unknown'

    mocked_response = self._create_response(json.dumps({
      'error':    expected_result,
      'duration': 42,
    }))

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text(context.exception), expected_result)

  def test_exception_response(self):
    """
    Simulates sending a command to the node and getting an exception
    response.
    """
    adapter = HttpAdapter('localhost')

    expected_result = 'java.lang.ArrayIndexOutOfBoundsException: 4'

    mocked_response = self._create_response(json.dumps({
      'exception':  'java.lang.ArrayIndexOutOfBoundsException: 4',
      'duration':   16
    }))

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text(context.exception), expected_result)

  def test_empty_response(self):
    """
    The response is empty.
    """
    adapter = HttpAdapter('localhost')

    mocked_response = self._create_response('')

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text(context.exception), 'Empty response from node.')

  def test_non_json_response(self):
    """
    The response is not JSON.
    """
    adapter = HttpAdapter('localhost')

    invalid_response  = 'EHLO iotatoken.com' # Erm...
    mocked_response   = self._create_response(invalid_response)

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text(context.exception),
      'Non-JSON response from node: ' + invalid_response,
    )

  def test_non_object_response(self):
    """
    The response is valid JSON, but it's not an object.
    """
    adapter = HttpAdapter('localhost')

    invalid_response  = '["message", "Hello, IOTA!"]'
    mocked_response   = self._create_response(invalid_response)

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text(context.exception),
      'Invalid response from node: ' + invalid_response,
    )

  # noinspection SpellCheckingInspection
  def test_trytes_in_request(self):
    """
    Sending a request that includes trytes.
    """
    adapter = HttpAdapter('localhost')

    # Response is not important for this test; we just need to make
    # sure that the request is converted correctly.
    mocked_sender = Mock(return_value=self._create_response('{}'))

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      adapter.send_request({
        'command':  'helloWorld',
        'trytes': [
          TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA'),

          TryteString(
            b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
          ),
        ],
      })

    mocked_sender.assert_called_once_with(
      payload = json.dumps({
        'command': 'helloWorld',

        # Tryte sequences are converted to strings for transport.
        'trytes': [
          'RBTC9D9DCDQAEASBYBCCKBFA',
          'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
        ],
      }),
    )

  @staticmethod
  def _create_response(content):
    # type: (Text) -> requests.Response
    """
    Creates a Response object for a test.
    """
    # :py:meth:`requests.adapters.HTTPAdapter.build_response`
    response = requests.Response()

    # Response status is always 200, even for an error.
    # https://github.com/iotaledger/iri/issues/9
    response.status_code = 200

    response.encoding = 'utf-8'
    response.raw = BytesIO(content.encode('utf-8'))

    return response
