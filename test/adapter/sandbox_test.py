# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from collections import deque
from unittest import TestCase

from six import text_type

from iota import BadApiResponse
from iota.adapter import API_VERSION
from iota.adapter.sandbox import SandboxAdapter
from test import mock
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
    mocked_sender = mock.Mock(return_value=mocked_response)

    payload = {'command': 'helloWorld'}

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    mocked_sender.assert_called_once_with(
      payload = json.dumps(payload),
      url     = adapter.node_url,

      # Auth token automatically added to the HTTP request.
      headers = {
        'Authorization':      'token ACCESS-TOKEN',
        'Content-type':       'application/json',
        'X-IOTA-API-Version': API_VERSION,
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

    mocked_sender = mock.Mock(wraps=_send_http_request)
    mocked_waiter = mock.Mock()

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      # mock.Mock ``_wait_to_poll`` so that it returns immediately, instead
      # of waiting for 15 seconds.  Bad for production, good for tests.
      # noinspection PyUnresolvedReferences
      with mock.patch.object(adapter, '_wait_to_poll', mocked_waiter):
        result = adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(result, expected_result)

  def test_sandbox_command_fails(self):
    """
    A sandbox command fails after an interval.
    """
    adapter = SandboxAdapter('https://localhost', 'ACCESS-TOKEN')

    error_message = "You didn't say the magic word!"

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
            'message': error_message,
          },
        })),
      ])

    # noinspection PyUnusedLocal
    def _send_http_request(*args, **kwargs):
      return responses.popleft()

    mocked_sender = mock.Mock(wraps=_send_http_request)
    mocked_waiter = mock.Mock()

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      # mock.Mock ``_wait_to_poll`` so that it returns immediately, instead
      # of waiting for 15 seconds.  Bad for production, good for tests.
      # noinspection PyUnresolvedReferences
      with mock.patch.object(adapter, '_wait_to_poll', mocked_waiter):
        with self.assertRaises(BadApiResponse) as context:
          adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(text_type(context.exception), error_message)

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
    mocked_sender = mock.Mock(return_value=mocked_response)

    payload = {'command': 'helloWorld'}

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      result = adapter.send_request(payload)

    self.assertEqual(result, expected_result)

    mocked_sender.assert_called_once_with(
      payload = json.dumps(payload),
      url     = adapter.node_url,

      headers = {
        # No auth token, so no Authorization header.
        # 'Authorization':  'token ACCESS-TOKEN',
        'Content-type':       'application/json',
        'X-IOTA-API-Version': API_VERSION,
      },
    )

  def test_error_job_takes_too_long(self):
    """
    A job takes too long to complete, and we lose interest.
    """
    adapter =\
      SandboxAdapter(
        uri           = 'https://localhost',
        auth_token    = 'token',
        poll_interval = 15,
        max_polls     = 2,
      )

    responses =\
      deque([
        # The first request creates the job.
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

        # The next two times we poll, the job is still in progress.
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
      ])

    # noinspection PyUnusedLocal
    def _send_http_request(*args, **kwargs):
      return responses.popleft()

    mocked_sender = mock.Mock(wraps=_send_http_request)
    mocked_waiter = mock.Mock()

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      # mock.Mock ``_wait_to_poll`` so that it returns immediately, instead
      # of waiting for 15 seconds.  Bad for production, good for tests.
      # noinspection PyUnresolvedReferences
      with mock.patch.object(adapter, '_wait_to_poll', mocked_waiter):
        with self.assertRaises(BadApiResponse) as context:
          adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),

      '``helloWorld`` job timed out after 30 seconds '
      '(``exc.context`` has more info).',
    )

  def test_error_non_200_response(self):
    """
    The node sends back a non-200 response.
    """
    adapter = SandboxAdapter('https://localhost', 'ACCESS-TOKEN')

    decoded_response = {
      'message': 'You have reached maximum request limit.',
    }

    mocked_sender = mock.Mock(return_value=create_http_response(
      status  = 429,
      content = json.dumps(decoded_response),
    ))

    # noinspection PyUnresolvedReferences
    with mock.patch.object(adapter, '_send_http_request', mocked_sender):
      with self.assertRaises(BadApiResponse) as context:
        adapter.send_request({'command': 'helloWorld'})

    self.assertEqual(
      text_type(context.exception),
      '429 response from node: {decoded}'.format(decoded=decoded_response),
    )

  def test_error_auth_token_wrong_type(self):
    """
    ``auth_token`` is not a string.
    """
    with self.assertRaises(TypeError):
      # Nope; it has to be a unicode string.
      # noinspection PyTypeChecker
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
    ``poll_interval`` is not an int.
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

  def test_error_max_polls_null(self):
    """
    ``max_polls`` is None.
    """
    with self.assertRaises(TypeError):
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', max_polls=None)

  def test_max_polls_wrong_type(self):
    """
    ``max_polls`` is not an int.
    """
    with self.assertRaises(TypeError):
      # ``max_polls`` must be an int.
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', max_polls=2.0)

  def test_max_polls_too_small(self):
    """
    ``max_polls`` is < 1.
    """
    with self.assertRaises(ValueError):
      # noinspection PyTypeChecker
      SandboxAdapter('https://localhost', 'token', max_polls=0)
