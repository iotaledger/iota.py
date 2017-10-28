# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from typing import Text
from unittest import TestCase

import requests
from iota import BadApiResponse, InvalidUri, TryteString
from iota.adapter import API_VERSION, HttpAdapter, MockAdapter, resolve_adapter
from six import BytesIO, text_type
from test import mock


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

  def test_http(self):
    """
    Resolving a valid ``http://`` URI.
    """
    adapter = resolve_adapter('http://localhost:14265/')
    self.assertIsInstance(adapter, HttpAdapter)

  def test_https(self):
    """
    Resolving a valid ``https://`` URI.
    """
    adapter = resolve_adapter('https://localhost:14265/')
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


def create_http_response(content, status=200):
  # type: (Text, int) -> requests.Response
  """
  Creates an HTTP Response object for a test.

  References:
    - :py:meth:`requests.adapters.HTTPAdapter.build_response`
  """
  response = requests.Response()

  response.encoding     = 'utf-8'
  response.status_code  = status
  response.raw          = BytesIO(content.encode('utf-8'))

  return response


class HttpAdapterTestCase(TestCase):
  def test_http(self):
    """
    Configuring HttpAdapter using a valid ``http://`` URI.
    """
    uri     = 'http://localhost:14265/'
    adapter = HttpAdapter(uri)

    self.assertEqual(adapter.node_url, uri)

  def test_https(self):
    """
    Configuring HttpAdapter using a valid ``https://`` URI.
    """
    uri     = 'https://localhost:14265/'
    adapter = HttpAdapter(uri)

    self.assertEqual(adapter.node_url, uri)

  def test_ipv4_address(self):
    """
    Configuring an HttpAdapter using an IPv4 address.
    """
    uri     = 'http://127.0.0.1:8080/'
    adapter = HttpAdapter(uri)

    self.assertEqual(adapter.node_url, uri)

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
      HttpAdapter.configure('http://:14265')

  def test_configure_error_non_numeric_port(self):
    """
    Attempting to configure HttpAdapter with non-numeric port.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('http://localhost:iota/')

  def test_configure_error_udp(self):
    """
    UDP is not a valid protocol for ``HttpAdapter``.
    """
    with self.assertRaises(InvalidUri):
      HttpAdapter.configure('udp://localhost:14265')

  def test_success_response(self):
    """
    Simulates sending a command to the node and getting a success
    response.
    """
    adapter = HttpAdapter('http://localhost:14265')

    payload = {'command': 'helloWorld'}
    expected_result = {'message': 'Hello, IOTA!'}

    mocked_response = create_http_response(json.dumps(expected_result))
    mocked_sender   = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    # https://github.com/iotaledger/iota.lib.py/issues/84
    mocked_sender.assert_called_once_with(
      headers = {
        'Content-type':       'application/json',
        'X-IOTA-API-Version': API_VERSION,
      },

      payload = json.dumps(payload),
      url     = adapter.node_url,
    )

  def test_error_response(self):
    """
    Simulates sending a command to the node and getting an error
    response.
    """
    adapter = HttpAdapter('http://localhost:14265')

    error_message = 'Command \u0027helloWorld\u0027 is unknown'

    mocked_response = create_http_response(
      status = 400,

      content = json.dumps({
        'error':    error_message,
        'duration': 42,
      }),
    )

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      '400 response from node: {error}'.format(error=error_message),
    )

  def test_exception_response(self):
    """
    Simulates sending a command to the node and getting an exception
    response.
    """
    adapter = HttpAdapter('http://localhost:14265')

    error_message = 'java.lang.ArrayIndexOutOfBoundsException: 4'

    mocked_response = create_http_response(
      status = 500,

      content = json.dumps({
        'exception':  error_message,
        'duration':   16,
      }),
    )

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      '500 response from node: {error}'.format(error=error_message),
    )

  def test_non_200_status(self):
    """
    The node sends back a non-200 response that we don't know how to
    handle.
    """
    adapter = HttpAdapter('http://localhost')

    decoded_response = {'message': 'Request limit exceeded.'}

    mocked_response = create_http_response(
      status  = 429,
      content = json.dumps(decoded_response),
    )

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      '429 response from node: {decoded}'.format(decoded=decoded_response),
    )

  def test_empty_response(self):
    """
    The response is empty.
    """
    adapter = HttpAdapter('http://localhost:14265')

    mocked_response = create_http_response('')

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      'Empty 200 response from node.',
    )

  def test_non_json_response(self):
    """
    The response is not JSON.
    """
    adapter = HttpAdapter('http://localhost:14265')

    invalid_response  = 'EHLO iotatoken.com' # Erm...
    mocked_response   = create_http_response(invalid_response)

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      'Non-JSON 200 response from node: ' + invalid_response,
    )

  def test_non_object_response(self):
    """
    The response is valid JSON, but it's not an object.
    """
    adapter = HttpAdapter('http://localhost:14265')

    invalid_response  = ['message', 'Hello, IOTA!']
    mocked_response   = create_http_response(json.dumps(invalid_response))

    mocked_sender = mock.Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),

      'Malformed 200 response from node: {response!r}'.format(
        response = invalid_response,
      ),
    )

  # noinspection SpellCheckingInspection
  @staticmethod
  def test_trytes_in_request():
    """
    Sending a request that includes trytes.
    """
    adapter = HttpAdapter('http://localhost:14265')

    # Response is not important for this test; we just need to make
    # sure that the request is converted correctly.
    mocked_sender = mock.Mock(return_value=create_http_response('{}'))

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
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
      url = adapter.node_url,

      payload = json.dumps({
        'command': 'helloWorld',

        # Tryte sequences are converted to strings for transport.
        'trytes': [
          'RBTC9D9DCDQAEASBYBCCKBFA',
          'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
        ],
      }),

      headers = {
        'Content-type':       'application/json',
        'X-IOTA-API-Version': API_VERSION,
      },
    )
