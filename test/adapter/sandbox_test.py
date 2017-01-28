# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from collections import deque
from unittest import TestCase

from mock import Mock, patch

from iota import BadApiResponse
from iota.adapter.sandbox import SandboxAdapter
from test.adapter_test import create_http_response


class SandboxAdapterTestCase(TestCase):
  def test_regular_command(self):
    """
    Sending a non-sandbox command to the node.
    """
    adapter = SandboxAdapter('https://localhost', 'ACCESS-TOKEN')

    expected_result = {
      'message': 'Hello, IOTA!',
    }

    mocked_response = create_http_response(json.dumps(expected_result))
    mocked_sender = Mock(return_value=mocked_response)

    payload = {'command': 'helloWorld'}

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    mocked_sender.assert_called_once_with(
      payload = json.dumps(payload),
      url     = adapter.node_url,

      # Auth token automatically added to the HTTP request.
      headers = {
        'Authorization': 'token ACCESS-TOKEN',
      },
    )

  def test_sandbox_command_succeeds(self):
    """
    Sending a sandbox command to the node.
    """
    adapter = SandboxAdapter('https://localhost', 'ACCESS-TOKEN')

    expected_result = {
      'message': 'Hello, IOTA!',
    }

    # Simulate responses from the node.
    responses =\
      deque([
        # The first request creates the job.
        # Note that the response has a 202 status.
        create_http_response(status=202, content=json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'QUEUED',
          'createdAt':  1483574581,
          'startedAt':  None,
          'finishedAt': None,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },
        })),

        # The job is still running when we poll.
        create_http_response(json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'RUNNING',
          'createdAt':  1483574581,
          'startedAt':  1483574589,
          'finishedAt': None,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },
        })),

        # The job has finished by the next polling request.
        create_http_response(json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'FINISHED',
          'createdAt':  1483574581,
          'startedAt':  1483574589,
          'finishedAt': 1483574604,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },

          'helloWorldResponse': expected_result,
        })),
      ])

    # noinspection PyUnusedLocal
    def _send_http_request(*args, **kwargs):
      return responses.popleft()

    mocked_sender = Mock(wraps=_send_http_request)
    mocked_waiter = Mock()

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      # Mock ``_wait_to_poll`` so that it returns immediately, instead
      # of waiting for 15 seconds.  Bad for production, good for tests.
      # noinspection PyUnresolvedReferences
      with patch.object(adapter, '_wait_to_poll', mocked_waiter):
        result = adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(result, expected_result)

  def test_sandbox_command_fails(self):
    """
    A sandbox command fails after an interval.
    """
    adapter = SandboxAdapter('https://localhost', 'ACCESS-TOKEN')

    # Simulate responses from the node.
    responses =\
      deque([
        # The first request creates the job.
        # Note that the response has a 202 status.
        create_http_response(status=202, content=json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'QUEUED',
          'createdAt':  1483574581,
          'startedAt':  None,
          'finishedAt': None,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },
        })),

        # The job is still running when we poll.
        create_http_response(json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'RUNNING',
          'createdAt':  1483574581,
          'startedAt':  1483574589,
          'finishedAt': None,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },
        })),

        # The job has finished by the next polling request.
        create_http_response(json.dumps({
          'id':         '70fef55d-6933-49fb-ae17-ec5d02bc9117',
          'status':     'FAILED',
          'createdAt':  1483574581,
          'startedAt':  1483574589,
          'finishedAt': 1483574604,
          'command':    'helloWorld',

          'helloWorldRequest': {
            'command': 'helloWorld',
          },

          'error': {
            'message': "You didn't say the magic word!"
          },
        })),
      ])

    # noinspection PyUnusedLocal
    def _send_http_request(*args, **kwargs):
      return responses.popleft()

    mocked_sender = Mock(wraps=_send_http_request)
    mocked_waiter = Mock()

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      # Mock ``_wait_to_poll`` so that it returns immediately, instead
      # of waiting for 15 seconds.  Bad for production, good for tests.
      # noinspection PyUnresolvedReferences
      with patch.object(adapter, '_wait_to_poll', mocked_waiter):
        with self.assertRaises(BadApiResponse):
          adapter.send_request({'command': 'helloWorld'})

  def test_regular_command_null_token(self):
    """
    Sending commands to a sandbox that doesn't require authorization.

    This is generally not recommended, but the sandbox node may use
    other methods to control access (e.g., listen only on loopback
    interface, use IP address whitelist, etc.).
    """
    # No access token.
    adapter = SandboxAdapter('https://localhost', None)

    expected_result = {
      'message': 'Hello, IOTA!',
    }

    mocked_response = create_http_response(json.dumps(expected_result))
    mocked_sender = Mock(return_value=mocked_response)

    payload = {'command': 'helloWorld'}

    # noinspection PyUnresolvedReferences
    with patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    mocked_sender.assert_called_once_with(
      payload = json.dumps(payload),
      url     = adapter.node_url,

      # No auth token, so no Authorization header.
      # headers = {
      #   'Authorization': 'token ACCESS-TOKEN',
      # },
    )

  def test_error_auth_token_wrong_type(self):
    """
    ``auth_token`` is not a string.
    """
    with self.assertRaises(TypeError):
      # Nope; it has to be a unicode string.
      SandboxAdapter('https://localhost', b'not valid')

  def test_error_auth_token_empty(self):
    """
    ``auth_token`` is an empty string.
    """
    with self.assertRaises(ValueError):
      # If the node does not require authorization, use ``None``.
      SandboxAdapter('https://localhost', '')

  def test_error_poll_interval_null(self):
    """
    ``poll_interval`` is ``None``.

    The implications of allowing this are cool to think about...
    but not implemented yet.
    """
    with self.assertRaises(TypeError):
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', None)

  def test_error_poll_interval_wrong_type(self):
    """
    ``poll_interval`` is not an int or float.
    """
    with self.assertRaises(TypeError):
      # ``poll_interval`` must be an int.
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', 42.0)

  def test_error_poll_interval_too_small(self):
    """
    ``poll_interval`` is < 1.
    """
    with self.assertRaises(ValueError):
      SandboxAdapter('https://localhost', 'token', 0)
