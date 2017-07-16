# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from time import sleep
from typing import Container, Optional, Text, Union

from requests import Response, codes
from six import moves as compat, text_type

from iota.adapter import BadApiResponse, HttpAdapter, SplitResult
from iota.exceptions import with_context

__all__ = [
  'SandboxAdapter',
]


STATUS_ABORTED  = 'ABORTED'
STATUS_FAILED   = 'FAILED'
STATUS_FINISHED = 'FINISHED'
STATUS_QUEUED   = 'QUEUED'
STATUS_RUNNING  = 'RUNNING'

class SandboxAdapter(HttpAdapter):
  """
  HTTP adapter that sends requests to remote nodes operating in
  "sandbox" mode.

  In sandbox mode, the node will only accept authenticated requests
  from clients, and certain jobs are completed asynchronously.

  Note: for compatibility with Iota APIs, SandboxAdapter still operates
  synchronously; it blocks until it determines that a job has completed
  successfully.

  References:
    - https://github.com/iotaledger/iota.lib.py/issues/19
    - https://github.com/iotaledger/documentation/blob/sandbox/source/index.html.md
  """
  DEFAULT_POLL_INTERVAL = 15
  """
  Number of seconds to wait between requests to check job status.
  """

  DEFAULT_MAX_POLLS = 8
  """
  Maximum number of times to poll for job status before giving up.
  """

  def __init__(
      self,
      uri,
      auth_token,
      poll_interval = DEFAULT_POLL_INTERVAL,
      max_polls     = DEFAULT_MAX_POLLS,
  ):
    # type: (Union[Text, SplitResult], Optional[Text], int, int) -> None
    """
    :param uri:
      URI of the node to connect to.
      ``https://` URIs are recommended!

      Note: Make sure the URI specifies the correct path!

      Example:

      - Incorrect: ``https://sandbox.iota:14265``
      - Correct:   ``https://sandbox.iota:14265/api/v1/``

    :param auth_token:
      Authorization token used to authenticate requests.

      Contact the node's maintainer to obtain a token.

      If ``None``, the adapter will not include authorization metadata
      with requests.

    :param poll_interval:
      Number of seconds to wait between requests to check job status.
      Must be a positive integer.

      Smaller values will cause the adapter to return a result sooner
      (once the node completes the job), but it increases traffic to
      the node (which may trip a rate limiter and/or incur additional
      costs).

    :param max_polls:
      Max number of times to poll for job status before giving up.
      Must be a positive integer.

      This is effectively a timeout setting for asynchronous jobs;
      multiply by ``poll_interval`` to get the timeout duration.
    """
    super(SandboxAdapter, self).__init__(uri)

    if not (isinstance(auth_token, text_type) or (auth_token is None)):
      raise with_context(
        exc =
          TypeError(
            '``auth_token`` must be a unicode string or ``None`` '
            '(``exc.context`` has more info).'
          ),

        context = {
          'auth_token': auth_token,
        },
      )

    if auth_token == '':
      raise with_context(
        exc =
          ValueError(
            'Set ``auth_token=None`` if requests do not require authorization '
            '(``exc.context`` has more info).',
          ),

        context = {
          'auth_token': auth_token,
        },
      )

    if not isinstance(poll_interval, int):
      raise with_context(
        exc =
          TypeError(
            '``poll_interval`` must be an int '
            '(``exc.context`` has more info).',
          ),

        context = {
          'poll_interval': poll_interval,
        },
      )

    if poll_interval < 1:
      raise with_context(
        exc =
          ValueError(
            '``poll_interval`` must be > 0 '
            '(``exc.context`` has more info).',
          ),

        context = {
          'poll_interval': poll_interval,
        },
      )

    if not isinstance(max_polls, int):
      raise with_context(
        exc =
          TypeError(
            '``max_polls`` must be an int '
            '(``exc.context`` has more info).',
          ),

        context = {
          'max_polls': max_polls,
        },
      )

    if max_polls < 1:
      raise with_context(
        exc =
          ValueError(
            '``max_polls`` must be > 0 '
            '(``exc.context`` has more info).',
          ),

        context = {
          'max_polls': max_polls,
        },
      )

    self.auth_token     = auth_token # type: Optional[Text]
    self.poll_interval  = poll_interval # type: int
    self.max_polls      = max_polls # type: int

  @property
  def node_url(self):
    return compat.urllib_parse.urlunsplit((
      self.uri.scheme,
      self.uri.netloc,
      self.uri.path.rstrip('/') + '/commands',
      self.uri.query,
      self.uri.fragment,
    ))

  @property
  def authorization_header(self):
    # type: () -> Text
    """
    Returns the value to use for the ``Authorization`` header.
    """
    return 'token {auth_token}'.format(auth_token=self.auth_token)

  def get_jobs_url(self, job_id):
    # type: (Text) -> Text
    """
    Returns the URL to check job status.

    :param job_id:
      The ID of the job to check.
    """
    return compat.urllib_parse.urlunsplit((
      self.uri.scheme,
      self.uri.netloc,
      self.uri.path.rstrip('/') + '/jobs/' + job_id,
      self.uri.query,
      self.uri.fragment,
    ))

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    if self.auth_token:
      kwargs.setdefault('headers', {})
      kwargs['headers']['Authorization'] = self.authorization_header

    return super(SandboxAdapter, self).send_request(payload, **kwargs)

  def _interpret_response(self, response, payload, expected_status):
    # type: (Response, dict, Container[int], bool) -> dict
    decoded =\
      super(SandboxAdapter, self)._interpret_response(
        response        = response,
        payload         = payload,
        expected_status = {codes['ok'], codes['accepted']},
      )

    # Check to see if the request was queued for asynchronous
    # execution.
    if response.status_code == codes['accepted']:
      poll_count = 0
      while decoded['status'] in (STATUS_QUEUED, STATUS_RUNNING):
        if poll_count >= self.max_polls:
          raise with_context(
            exc =
              BadApiResponse(
                '``{command}`` job timed out after {duration} seconds '
                '(``exc.context`` has more info).'.format(
                  command   = decoded['command'],
                  duration  = self.poll_interval * self.max_polls,
                ),
              ),

            context = {
              'request':  payload,
              'response': decoded,
            },
          )

        self._wait_to_poll()
        poll_count += 1

        poll_response = self._send_http_request(
          headers = {'Authorization': self.authorization_header},
          method  = 'get',
          payload = None,
          url     = self.get_jobs_url(decoded['id']),
        )

        decoded =\
          super(SandboxAdapter, self)._interpret_response(
            response        = poll_response,
            payload         = payload,
            expected_status = {codes['ok']},
          )

      if decoded['status'] == STATUS_FINISHED:
        return decoded['{command}Response'.format(command=decoded['command'])]

      raise with_context(
        exc = BadApiResponse(
              decoded.get('error', {}).get('message')
          or  'Command {status}: {decoded}'.format(
                decoded = decoded,
                status  = decoded['status'].lower(),
              ),
        ),

        context = {
          'request':  payload,
          'response': decoded,
        },
      )

    return decoded

  def _wait_to_poll(self):
    """
    Waits for 1 interval (according to :py:attr:`poll_interval`).

    Implemented as a separate method so that it can be mocked during
    unit tests ("Do you bite your thumb at us, sir?").
    """
    sleep(self.poll_interval)
