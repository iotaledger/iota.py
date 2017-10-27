# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from abc import ABCMeta, abstractmethod as abstract_method
from collections import deque
from inspect import isabstract as is_abstract
from logging import DEBUG, Logger
from socket import getdefaulttimeout as get_default_timeout
from typing import Container, Dict, List, Optional, Text, Tuple, Union

from requests import Response, codes, request
from six import PY2, binary_type, iteritems, moves as compat, text_type, \
  with_metaclass

from iota.exceptions import with_context
from iota.json import JsonEncoder

__all__ = [
  'API_VERSION',
  'AdapterSpec',
  'BadApiResponse',
  'InvalidUri',
]

if PY2:
  # Fix an error when importing this package using the ``imp`` library
  # (note: ``imp`` is deprecated since Python 3.4 in favor of
  # ``importlib``).
  # https://docs.python.org/3/library/imp.html
  # https://travis-ci.org/iotaledger/iota.lib.py/jobs/191974244
  __all__ = map(binary_type, __all__)


API_VERSION = '1'
"""
API protocol version.
https://github.com/iotaledger/iota.lib.py/issues/84
"""


# Custom types for type hints and docstrings.
AdapterSpec = Union[Text, 'BaseAdapter']

# Load SplitResult for IDE type hinting and autocompletion.
if PY2:
  # noinspection PyCompatibility,PyUnresolvedReferences
  from urlparse import SplitResult
else:
  # noinspection PyCompatibility,PyUnresolvedReferences
  from urllib.parse import SplitResult


class BadApiResponse(ValueError):
  """
  Indicates that a non-success response was received from the node.
  """
  pass


class InvalidUri(ValueError):
  """
  Indicates that an invalid URI was provided to `resolve_adapter`.
  """
  pass


adapter_registry = {} # type: Dict[Text, AdapterMeta]
"""
Keeps track of available adapters and their supported protocols.
"""


def resolve_adapter(uri):
  # type: (AdapterSpec) -> BaseAdapter
  """
  Given a URI, returns a properly-configured adapter instance.
  """
  if isinstance(uri, BaseAdapter):
    return uri

  parsed = compat.urllib_parse.urlsplit(uri) # type: SplitResult

  if not parsed.scheme:
    raise with_context(
      exc = InvalidUri(
        'URI must begin with "<protocol>://" (e.g., "udp://").',
      ),

      context = {
        'parsed': parsed,
        'uri':    uri,
      },
    )

  try:
    adapter_type = adapter_registry[parsed.scheme]
  except KeyError:
    raise with_context(
      exc = InvalidUri('Unrecognized protocol {protocol!r}.'.format(
        protocol = parsed.scheme,
      )),

      context = {
        'parsed': parsed,
        'uri':    uri,
      },
    )

  return adapter_type.configure(parsed)


class AdapterMeta(ABCMeta):
  """
  Automatically registers new adapter classes in ``adapter_registry``.
  """
  # noinspection PyShadowingBuiltins
  def __init__(cls, what, bases=None, dict=None):
    super(AdapterMeta, cls).__init__(what, bases, dict)

    if not is_abstract(cls):
      for protocol in getattr(cls, 'supported_protocols', ()):
        # Note that we will not overwrite existing registered adapters.
        adapter_registry.setdefault(protocol, cls)

  def configure(cls, parsed):
    # type: (Union[Text, SplitResult]) -> HttpAdapter
    """
    Creates a new instance using the specified URI.

    :param parsed:
      Result of :py:func:`urllib.parse.urlsplit`.
    """
    return cls(parsed)


class BaseAdapter(with_metaclass(AdapterMeta)):
  """
  Interface for IOTA API adapters.

  Adapters make it easy to customize the way an StrictIota instance
  communicates with a node.
  """
  supported_protocols = () # type: Tuple[Text]
  """
  Protocols that ``resolve_adapter`` can use to identify this adapter
  type.
  """

  def __init__(self):
    super(BaseAdapter, self).__init__()

    self._logger = None # type: Logger

  @abstract_method
  def get_uri(self):
    # type: () -> Text
    """
    Returns the URI that this adapter will use.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  @abstract_method
  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    """
    Sends an API request to the node.

    :param payload:
      JSON payload.

    :param kwargs:
      Additional keyword arguments for the adapter.

    :return:
      Decoded response from the node.

    :raise:
      - :py:class:`BadApiResponse` if a non-success response was
        received.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  def set_logger(self, logger):
    # type: (Logger) -> BaseAdapter
    """
    Attaches a logger instance to the adapter.
    The adapter will send information about API requests/responses to
    the logger.
    """
    self._logger = logger
    return self

  def _log(self, level, message, context=None):
    # type: (int, Text, Optional[dict]) -> None
    """
    Sends a message to the instance's logger, if configured.
    """
    if self._logger:
      self._logger.log(level, message, extra={'context': context or {}})


class HttpAdapter(BaseAdapter):
  """
  Sends standard HTTP requests.
  """
  supported_protocols = ('http', 'https',)

  DEFAULT_HEADERS = {
    'Content-type': 'application/json',

    # https://github.com/iotaledger/iota.lib.py/issues/84
    'X-IOTA-API-Version': API_VERSION,
  }
  """
  Default headers sent with every request.
  These can be overridden on a per-request basis, by specifying values
  in the ``headers`` kwarg.
  """

  def __init__(self, uri):
    # type: (Union[Text, SplitResult]) -> None
    super(HttpAdapter, self).__init__()

    if isinstance(uri, text_type):
      uri = compat.urllib_parse.urlsplit(uri) # type: SplitResult

    if uri.scheme not in self.supported_protocols:
      raise with_context(
        exc = InvalidUri('Unsupported protocol {protocol!r}.'.format(
          protocol = uri.scheme,
        )),

        context = {
          'uri': uri,
        },
      )

    if not uri.hostname:
      raise with_context(
        exc = InvalidUri(
          'Empty hostname in URI {uri!r}.'.format(
            uri = uri.geturl(),
          ),
        ),

        context = {
          'uri': uri,
        },
      )

    try:
      # noinspection PyStatementEffect
      uri.port
    except ValueError:
      raise with_context(
        exc = InvalidUri(
          'Non-numeric port in URI {uri!r}.'.format(
            uri = uri.geturl(),
          ),
        ),

        context = {
          'uri': uri,
        },
      )

    self.uri = uri

  @property
  def node_url(self):
    # type: () -> Text
    """
    Returns the node URL.
    """
    return self.uri.geturl()

  def get_uri(self):
    # type: () -> Text
    return self.uri.geturl()

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    kwargs.setdefault('headers', {})
    for key, value in iteritems(self.DEFAULT_HEADERS):
      kwargs['headers'].setdefault(key, value)

    response = self._send_http_request(
      # Use a custom JSON encoder that knows how to convert Tryte values.
      payload = JsonEncoder().encode(payload),

      url = self.node_url,
      **kwargs
    )

    return self._interpret_response(response, payload, {codes['ok']})

  def _send_http_request(self, url, payload, method='post', **kwargs):
    # type: (Text, Optional[Text], Text, dict) -> Response
    """
    Sends the actual HTTP request.

    Split into its own method so that it can be mocked during unit
    tests.
    """
    kwargs.setdefault('timeout', get_default_timeout())

    self._log(
      level = DEBUG,

      message = 'Sending {method} to {url}: {payload!r}'.format(
        method  = method,
        payload = payload,
        url     = url,
      ),

      context = {
        'request_method':   method,
        'request_kwargs':   kwargs,
        'request_payload':  payload,
        'request_url':      url,
      },
    )

    response = request(method=method, url=url, data=payload, **kwargs)

    self._log(
      level = DEBUG,

      message = 'Receiving {method} from {url}: {response!r}'.format(
        method    = method,
        response  = response.content,
        url       = url,
      ),

      context = {
        'request_method':   method,
        'request_kwargs':   kwargs,
        'request_payload':  payload,
        'request_url':      url,

        'response_headers': response.headers,
        'response_content': response.content,
      },
    )

    return response

  def _interpret_response(self, response, payload, expected_status):
    # type: (Response, dict, Container[int]) -> dict
    """
    Interprets the HTTP response from the node.

    :param response:
      The response object received from :py:meth:`_send_http_request`.

    :param payload:
      The request payload that was sent (used for debugging).

    :param expected_status:
      The response should match one of these status codes to be
      considered valid.
    """
    raw_content = response.text
    if not raw_content:
      raise with_context(
        exc = BadApiResponse(
          'Empty {status} response from node.'.format(
            status = response.status_code,
          ),
        ),

        context = {
          'request': payload,
        },
      )

    try:
      decoded = json.loads(raw_content) # type: dict
    # :bc: py2k doesn't have JSONDecodeError
    except ValueError:
      raise with_context(
        exc = BadApiResponse(
          'Non-JSON {status} response from node: {raw_content}'.format(
            status      = response.status_code,
            raw_content = raw_content,
          )
        ),

        context = {
          'request':      payload,
          'raw_response': raw_content,
        },
      )

    if not isinstance(decoded, dict):
      raise with_context(
        exc = BadApiResponse(
          'Malformed {status} response from node: {decoded!r}'.format(
            status  = response.status_code,
            decoded = decoded,
          ),
        ),

        context = {
          'request':  payload,
          'response': decoded,
        },
      )

    if response.status_code in expected_status:
      return decoded

    error = None
    try:
      if response.status_code == codes['bad_request']:
        error = decoded['error']
      elif response.status_code == codes['internal_server_error']:
        error = decoded['exception']
    except KeyError:
      pass

    raise with_context(
      exc = BadApiResponse(
        '{status} response from node: {error}'.format(
          error   = error or decoded,
          status  = response.status_code,
        ),
      ),

      context = {
        'request':  payload,
        'response': decoded,
      },
    )


class MockAdapter(BaseAdapter):
  """
  An mock adapter used for simulating API responses.

  To use this adapter, you must first "seed" the responses that the
  adapter should return for each request.  The adapter will then return
  the appropriate seeded response each time it "sends" a request.
  """
  supported_protocols = ('mock',)

  # noinspection PyUnusedLocal
  @classmethod
  def configure(cls, uri):
    return cls()

  def __init__(self):
    super(MockAdapter, self).__init__()

    self.responses  = {} # type: Dict[Text, deque]
    self.requests   = [] # type: List[dict]

  def get_uri(self):
    return 'mock://'

  def seed_response(self, command, response):
    # type: (Text, dict) -> MockAdapter
    """
    Sets the response that the adapter will return for the specified
    command.

    You can seed multiple responses per command; the adapter will put
    them into a FIFO queue.  When a request comes in, the adapter will
    pop the corresponding response off of the queue.

    Example::

       adapter.seed_response('sayHello', {'message': 'Hi!'})
       adapter.seed_response('sayHello', {'message': 'Hello!'})

       adapter.send_request({'command': 'sayHello'})
       # {'message': 'Hi!'}

       adapter.send_request({'command': 'sayHello'})
       # {'message': 'Hello!'}
    """
    if command not in self.responses:
      self.responses[command] = deque()

    self.responses[command].append(response)
    return self

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    # Store a snapshot so that we can inspect the request later.
    self.requests.append(dict(payload))

    command = payload['command']

    try:
      response = self.responses[command].popleft()
    except KeyError:
      raise with_context(
        exc = BadApiResponse(
          'No seeded response for {command!r} '
          '(expected one of: {seeds!r}).'.format(
            command = command,
            seeds   = list(sorted(self.responses.keys())),
          ),
        ),

        context = {
          'request': payload,
        },
      )
    except IndexError:
      raise with_context(
        exc = BadApiResponse(
          '{command} called too many times; no seeded responses left.'.format(
            command = command,
          ),
        ),

        context = {
          'request': payload,
        },
      )

    error = response.get('exception') or response.get('error')
    if error:
      raise with_context(BadApiResponse(error), context={'request': payload})

    return response
