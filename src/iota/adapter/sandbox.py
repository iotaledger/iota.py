# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional, Text, Union

from six import text_type

from iota.adapter import HttpAdapter, SplitResult
from iota.exceptions import with_context


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

  def __init__(self, uri, auth_token, poll_interval=DEFAULT_POLL_INTERVAL):
    # type: (Union[Text, SplitResult], Optional[Text], int) -> None
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
            '``poll_interval`` must be >= 1 '
            '(``exc.context`` has more info).',
          ),

        context = {
          'poll_interval': poll_interval,
        },
      )

    self.auth_token     = auth_token # type: Optional[Text]
    self.poll_interval  = poll_interval # type: int

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    if self.auth_token:
      kwargs.setdefault('headers', {})

      kwargs['headers']['Authorization'] =\
        'token {token}'.format(
          token = self.auth_token,
        )

    return super(SandboxAdapter, self).send_request(payload, **kwargs)
