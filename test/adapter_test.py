# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from typing import Text
from unittest import TestCase

import requests
from mock import Mock, patch
from six import BytesIO, text_type as text

from iota import BadApiResponse, HttpAdapter


class HttpAdapterTestCase(TestCase):
  def setUp(self):
    super(HttpAdapterTestCase, self).setUp()

    self.adapter = HttpAdapter('localhost')

  def test_success_response(self):
    """
    Simulates sending a command to the node and getting a success
      response.
    """
    expected_result = {
      'message': 'Hello, IOTA!',
    }

    mocked_response = self._create_response(json.dumps(expected_result))
    mocked_sender   = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(self.adapter, '_send_http_request', mocked_sender):
      result = self.adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(result, expected_result)

  def test_error_response(self):
    """
    Simulates sending a command to the node and getting an error
      response.
    """
    expected_result = 'Command \u0027helloWorld\u0027 is unknown'

    mocked_response = self._create_response(json.dumps({
      'error':    expected_result,
      'duration': 42,
    }))

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(self.adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        self.adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text(context.exception), expected_result)

  def test_empty_response(self):
    """The response is empty."""
    mocked_response = self._create_response('')

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(self.adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        self.adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text(context.exception), 'Empty response from node.')

  def test_non_json_response(self):
    """The response is not JSON."""
    invalid_response  = 'EHLO iotatoken.com' # Erm...
    mocked_response   = self._create_response(invalid_response)

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(self.adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        self.adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text(context.exception),
      'Non-JSON response from node: ' + invalid_response,
    )

  def test_non_object_response(self):
    """The response is valid JSON, but it's not an object."""
    invalid_response  = '["message", "Hello, IOTA!"]'
    mocked_response   = self._create_response(invalid_response)

    mocked_sender = Mock(return_value=mocked_response)

    # noinspection PyUnresolvedReferences
    with patch.object(self.adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        self.adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text(context.exception),
      'Invalid response from node: ' + invalid_response,
    )

  @staticmethod
  def _create_response(content):
    # type: (Text) -> requests.Response
    """Creates a Response object for a test."""
    # :see: requests.adapters.HTTPAdapter.build_response
    response = requests.Response()

    # Response status is always 200, even for an error.
    # :see: https://github.com/iotaledger/iri/issues/9
    response.status_code = 200

    response.encoding = 'utf-8'
    response.raw = BytesIO(content.encode('utf-8'))

    return response
