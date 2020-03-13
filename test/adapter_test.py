import json
import socket
from typing import Text
from unittest import TestCase

import httpx
from iota import BadApiResponse, InvalidUri, TryteString
from iota.adapter import API_VERSION, HttpAdapter, MockAdapter, \
  resolve_adapter, async_return
from test import mock, async_test

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
  # type: (Text, int) -> httpx.Response
  """
  Creates an HTTP Response object for a test.
  """
  return httpx.Response(
    status,
    request=httpx.Request('post','https://localhost:14265/'),
    content=content
  )


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

  @async_test
  async def test_success_response(self):
    """
    Simulates sending a command to the node and getting a success
    response.
    """
    adapter = HttpAdapter('http://localhost:14265')

    payload = {'command': 'helloWorld'}
    expected_result = {'message': 'Hello, IOTA!'}

    mocked_response = create_http_response(json.dumps(expected_result))
    mocked_sender   = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      result = await adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    # https://github.com/iotaledger/iota.py/issues/84
    mocked_sender.assert_called_once_with(
      headers = {
        'Content-type':       'application/json',
        'X-IOTA-API-Version': API_VERSION,
      },

      payload = json.dumps(payload),
      url     = adapter.node_url,
    )

  @async_test
  async def test_error_response(self):
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

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),
      '400 response from node: {error}'.format(error=error_message),
    )

  @async_test
  async def test_exception_response(self):
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

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),
      '500 response from node: {error}'.format(error=error_message),
    )

  @async_test
  async def test_non_200_status(self):
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

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),
      '429 response from node: {decoded}'.format(decoded=decoded_response),
    )

  @async_test
  async def test_empty_response(self):
    """
    The response is empty.
    """
    adapter = HttpAdapter('http://localhost:14265')

    mocked_response = create_http_response('')

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),
      'Empty 200 response from node.',
    )

  @async_test
  async def test_non_json_response(self):
    """
    The response is not JSON.
    """
    adapter = HttpAdapter('http://localhost:14265')

    invalid_response  = 'EHLO iotatoken.com' # Erm...
    mocked_response   = create_http_response(invalid_response)

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),
      'Non-JSON 200 response from node: ' + invalid_response,
    )

  @async_test
  async def test_non_object_response(self):
    """
    The response is valid JSON, but it's not an object.
    """
    adapter = HttpAdapter('http://localhost:14265')

    invalid_response  = ['message', 'Hello, IOTA!']
    mocked_response   = create_http_response(json.dumps(invalid_response))

    mocked_sender = mock.Mock(return_value=async_return(mocked_response))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        await adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      str(context.exception),

      'Malformed 200 response from node: {response!r}'.format(
        response = invalid_response,
      ),
    )

  @async_test
  async def test_default_timeout(self):
    # create adapter
    mock_payload = {'dummy': 'payload'}
    adapter = HttpAdapter('http://localhost:14265')

    # mock for returning dummy response
    mocked_request = mock.Mock(
      return_value=async_return(
        mock.Mock(text='{ "dummy": "payload"}', status_code=200)
      )
    )

    with mock.patch('iota.adapter.AsyncClient.request', mocked_request):
      # test with default timeout
      await adapter.send_request(payload=mock_payload)

    # Was the default timeout correctly injected into the request?
    _, kwargs = mocked_request.call_args
    self.assertEqual(kwargs['timeout'], socket.getdefaulttimeout())

  @async_test
  async def test_instance_attribute_timeout(self):
    # mock for returning dummy response
    mocked_request = mock.Mock(
      return_value=async_return(
        mock.Mock(text='{ "dummy": "payload"}', status_code=200)
      )
    )

    # create adapter
    mock_payload = {'dummy': 'payload'}
    adapter = HttpAdapter('http://localhost:14265')

    # test with explicit attribute
    adapter.timeout = 77
    with mock.patch('iota.adapter.AsyncClient.request', mocked_request):
      await adapter.send_request(payload=mock_payload)
    _, kwargs = mocked_request.call_args
    self.assertEqual(kwargs['timeout'], 77)

  @async_test
  async def test_argument_overriding_attribute_timeout(self):
    # mock for returning dummy response
    mocked_request = mock.Mock(
      return_value=async_return(
        mock.Mock(text='{ "dummy": "payload"}', status_code=200)
      )
    )

    # create adapter
    mock_payload = {'dummy': 'payload'}
    adapter = HttpAdapter('http://localhost:14265')

    # test with timeout in kwargs
    adapter.timeout = 77
    with mock.patch('iota.adapter.AsyncClient.request', mocked_request):
      await adapter.send_request(payload=mock_payload, timeout=88)
    _, kwargs = mocked_request.call_args
    self.assertEqual(kwargs['timeout'], 88)

  @async_test
  async def test_argument_overriding_init_timeout(self):
    # mock for returning dummy response
    mocked_request = mock.Mock(
      return_value=async_return(
        mock.Mock(text='{ "dummy": "payload"}', status_code=200)
      )
    )

    # create adapter
    mock_payload = {'dummy': 'payload'}
    adapter = HttpAdapter('http://localhost:14265')

    # test with timeout at adapter creation
    adapter = HttpAdapter('http://localhost:14265', timeout=99)
    with mock.patch('iota.adapter.AsyncClient.request', mocked_request):
      await adapter.send_request(payload=mock_payload)
    _, kwargs = mocked_request.call_args
    self.assertEqual(kwargs['timeout'], 99)

  @async_test
  async def test_trytes_in_request(self):
    """
    Sending a request that includes trytes.
    """
    adapter = HttpAdapter('http://localhost:14265')

    # Response is not important for this test; we just need to make
    # sure that the request is converted correctly.
    mocked_sender = mock.Mock(return_value=async_return(create_http_response('{}')))

    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      await adapter.send_request({
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
