
import json
from abc import ABCMeta, abstractmethod as abstract_method
from asyncio import Future
from collections import deque
from inspect import isabstract as is_abstract
from logging import DEBUG, Logger
from socket import getdefaulttimeout as get_default_timeout
from typing import Container, List, Optional, Tuple, Union, Any, Dict
from httpx import AsyncClient, Response, codes, BasicAuth
import asyncio

from iota.exceptions import with_context
from iota.json import JsonEncoder

__all__ = [
    'API_VERSION',
    'AdapterSpec',
    'BadApiResponse',
    'BaseAdapter',
    'HttpAdapter',
    'InvalidUri',
    'MockAdapter',
    'resolve_adapter',
]


API_VERSION = '1'
"""
API protocol version.
https://github.com/iotaledger/iota.py/issues/84
"""

# Custom types for type hints and docstrings.
AdapterSpec = Union[str, 'BaseAdapter']
"""
Placeholder that means “URI or adapter instance”.

Will be resolved to a correctly-configured adapter instance
upon API instance creation.
"""

# Load SplitResult for IDE type hinting and autocompletion.
from urllib.parse import SplitResult, urlsplit


def async_return(result: Any) -> Future:
  """
  Turns 'result' into a `Future` object with 'result' value.

  Important for mocking, as we can await the mock's return value.
  """
  f = asyncio.Future()
  f.set_result(result)
  return f


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


adapter_registry: Dict[str, 'AdapterMeta'] = {}
"""
Keeps track of available adapters and their supported protocols.
"""


def resolve_adapter(uri: AdapterSpec) -> 'BaseAdapter':
    """
    Given a URI, returns a properly-configured adapter instance.
    """
    if isinstance(uri, BaseAdapter):
        return uri

    parsed: SplitResult = urlsplit(uri)

    if not parsed.scheme:
        raise with_context(
            exc=InvalidUri(
                'URI must begin with "<protocol>://" (e.g., "udp://").',
            ),

            context={
                'parsed': parsed,
                'uri': uri,
            },
        )

    try:
        adapter_type = adapter_registry[parsed.scheme]
    except KeyError:
        raise with_context(
            exc=InvalidUri('Unrecognized protocol {protocol!r}.'.format(
                protocol=parsed.scheme,
            )),

            context={
                'parsed': parsed,
                'uri': uri,
            },
        )

    return adapter_type.configure(parsed)


class AdapterMeta(ABCMeta):
    """
    Automatically registers new adapter classes in ``adapter_registry``.
    """

    def __init__(cls, what, bases=None, dict=None) -> None:
        super(AdapterMeta, cls).__init__(what, bases, dict)

        if not is_abstract(cls):
            for protocol in getattr(cls, 'supported_protocols', ()):
                # Note that we will not overwrite existing registered
                # adapters.
                adapter_registry.setdefault(protocol, cls)

    def configure(cls, parsed: Union[str, SplitResult]) -> 'HttpAdapter':
        """
        Creates a new instance using the specified URI.

        :param parsed:
          Result of :py:func:`urllib.parse.urlsplit`.
        """
        return cls(parsed)


class BaseAdapter(object, metaclass=AdapterMeta):
    """
    Interface for IOTA API adapters.

    Adapters make it easy to customize the way an API instance
    communicates with a node.
    """
    supported_protocols: Tuple[str] = ()
    """
    Protocols that ``resolve_adapter`` can use to identify this adapter
    type.
    """

    def __init__(self) -> None:
        super(BaseAdapter, self).__init__()

        self._logger: Optional[Logger] = None
        self.local_pow: bool = False

    @abstract_method
    def get_uri(self) -> str:
        """
        Returns the URI that this adapter will use.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    @abstract_method
    def send_request(self, payload: dict, **kwargs: Any) -> dict:
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

    def set_logger(self, logger: Logger) -> 'BaseAdapter':
        """
        Attaches a logger instance to the adapter.
        The adapter will send information about API requests/responses
        to the logger.
        """
        self._logger = logger
        return self

    def _log(
            self,
            level: int,
            message: str,
            context: Optional[dict] = None
    ) -> None:
        """
        Sends a message to the instance's logger, if configured.
        """
        if self._logger:
            self._logger.log(level, message, extra={'context': context or {}})

    def set_local_pow(self, local_pow: bool) -> None:
        """
        Sets the local_pow attribute of the adapter. If it is true,
        attach_to_tangle command calls external interface to perform
        pow, instead of sending the request to a node.
        By default, it is set to false.
        """
        self.local_pow = local_pow


class HttpAdapter(BaseAdapter):
    """
    Sends standard HTTP(S) requests to the node.

    :param AdapterSpec uri:
        URI or adapter instance.

        If ``uri`` is a ``str``, it is parsed to extract ``scheme``,
        ``hostname`` and ``port``.

    :param Optional[int] timeout:
        Connection timeout in seconds.

    :param Optional[Tuple(str,str)] authentication:
        Credetentials for basic authentication with the node.

    :return:
        :py:class:`HttpAdapter` object.

    :raises InvalidUri:
        - if protocol is unsupported.
        - if hostname is empty.
        - if non-numeric port is supplied.
    """
    supported_protocols = ('http', 'https',)
    """
    Protocols supported by this adapter.
    """

    DEFAULT_HEADERS = {
        'Content-type': 'application/json',

        # https://github.com/iotaledger/iota.py/issues/84
        'X-IOTA-API-Version': API_VERSION,
    }
    """
    Default headers sent with every request.
    These can be overridden on a per-request basis, by specifying values
    in the ``headers`` kwarg.
    """

    def __init__(
            self,
            uri: Union[str, SplitResult],
            timeout: Optional[int] = None,
            authentication: Optional[Tuple[str, str]] = None
    ) -> None:
        super(HttpAdapter, self).__init__()

        self.client = AsyncClient()
        self.timeout = timeout
        self.authentication = authentication

        if isinstance(uri, str):
            uri: SplitResult = urlsplit(uri)

        if uri.scheme not in self.supported_protocols:
            raise with_context(
                exc=InvalidUri('Unsupported protocol {protocol!r}.'.format(
                    protocol=uri.scheme,
                )),

                context={
                    'uri': uri,
                },
            )

        if not uri.hostname:
            raise with_context(
                exc=InvalidUri(
                    'Empty hostname in URI {uri!r}.'.format(
                        uri=uri.geturl(),
                    ),
                ),

                context={
                    'uri': uri,
                },
            )

        try:
            uri.port
        except ValueError:
            raise with_context(
                exc=InvalidUri(
                    'Non-numeric port in URI {uri!r}.'.format(
                        uri=uri.geturl(),
                    ),
                ),

                context={
                    'uri': uri,
                },
            )

        self.uri = uri

    @property
    def node_url(self) -> str:
        """
        Returns the node URL.
        """
        return self.uri.geturl()

    def get_uri(self) -> str:
        return self.uri.geturl()

    async def send_request(self, payload: dict, **kwargs: Any) -> dict:
        kwargs.setdefault('headers', {})
        for key, value in self.DEFAULT_HEADERS.items():
            kwargs['headers'].setdefault(key, value)

        response = await self._send_http_request(
            # Use a custom JSON encoder that knows how to convert Tryte
            # values.
            payload=JsonEncoder().encode(payload),

            url=self.node_url,
            **kwargs
        )

        return self._interpret_response(response, payload, {codes['OK']})

    async def _send_http_request(
            self,
            url: str,
            payload: Optional[str],
            method: str = 'post',
            **kwargs: Any
    ) -> Response:
        """
        Sends the actual HTTP request.

        Split into its own method so that it can be mocked during unit
        tests.
        """
        kwargs.setdefault(
            'timeout',
            self.timeout if self.timeout else get_default_timeout(),
        )

        if self.authentication:
            kwargs.setdefault('auth', BasicAuth(*self.authentication))

        self._log(
            level=DEBUG,

            message='Sending {method} to {url}: {payload!r}'.format(
                method=method,
                payload=payload,
                url=url,
            ),

            context={
                'request_method': method,
                'request_kwargs': kwargs,
                'request_payload': payload,
                'request_url': url,
            },
        )
        response = await self.client.request(method=method, url=url, data=payload, **kwargs)

        self._log(
            level=DEBUG,

            message='Receiving {method} from {url}: {response!r}'.format(
                method=method,
                response=response.content,
                url=url,
            ),

            context={
                'request_method': method,
                'request_kwargs': kwargs,
                'request_payload': payload,
                'request_url': url,

                'response_headers': response.headers,
                'response_content': response.content,
            },
        )

        return response

    def _interpret_response(
            self,
            response: Response,
            payload: dict,
            expected_status: Container[int]
    ) -> dict:
        """
        Interprets the HTTP response from the node.

        :param response:
            The response object received from
            :py:meth:`_send_http_request`.

        :param payload:
            The request payload that was sent (used for debugging).

        :param expected_status:
            The response should match one of these status codes to be
            considered valid.
        """
        raw_content = response.text
        if not raw_content:
            raise with_context(
                exc=BadApiResponse(
                    'Empty {status} response from node.'.format(
                        status=response.status_code,
                    ),
                ),

                context={
                    'request': payload,
                },
            )

        try:
            decoded: dict = json.loads(raw_content)
        # :bc: py2k doesn't have JSONDecodeError
        except ValueError:
            raise with_context(
                exc=BadApiResponse(
                    'Non-JSON {status} response from node: '
                    '{raw_content}'.format(
                        status=response.status_code,
                        raw_content=raw_content,
                    )
                ),

                context={
                    'request': payload,
                    'raw_response': raw_content,
                },
            )

        if not isinstance(decoded, dict):
            raise with_context(
                exc=BadApiResponse(
                    'Malformed {status} response from node: {decoded!r}'.format(
                        status=response.status_code,
                        decoded=decoded,
                    ),
                ),

                context={
                    'request': payload,
                    'response': decoded,
                },
            )

        if response.status_code in expected_status:
            return decoded

        error = None
        try:
            if response.status_code == codes['BAD_REQUEST']:
                error = decoded['error']
            elif response.status_code == codes['INTERNAL_SERVER_ERROR']:
                error = decoded['exception']
        except KeyError:
            pass

        raise with_context(
            exc=BadApiResponse(
                '{status} response from node: {error}'.format(
                    error=error or decoded,
                    status=response.status_code,
                ),
            ),

            context={
                'request': payload,
                'response': decoded,
            },
        )


class MockAdapter(BaseAdapter):
    """
    A mock adapter used for simulating API responses without actually sending
    any requests to the node.

    This is particularly useful in unit and functional tests where you want
    to verify that your code works correctly in specific scenarios, without
    having to engineer your own subtangle.

    To use this adapter, you must first "seed" the responses that the
    adapter should return for each request.  The adapter will then return
    the appropriate seeded response each time it "sends" a request.

    :param ``None``:
        To construct a ``MockAdapter``, you don't need to supply any arguments.

    :return:
        :py:class:`MockAdapter` object.

    To configure an :py:class:`Iota` instance to use :py:class:`MockAdapter`,
    specify ``mock://`` as the node URI, or provide a :py:class:`MockAdapter`
    instance.

    Example usage::

        from iota import Iota, MockAdapter

        # Create API with a mock adapter.
        api = Iota('mock://')
        api = Iota(MockAdapter())

    """
    supported_protocols = ('mock',)

    @classmethod
    def configure(cls, uri):
        return cls()

    def __init__(self) -> None:
        super(MockAdapter, self).__init__()

        self.responses: Dict[str, deque] = {}
        self.requests: List[dict] = []

    def get_uri(self) -> str:
        return 'mock://'

    def seed_response(self, command: str, response: dict) -> 'MockAdapter':
        """
        Sets the response that the adapter will return for the specified
        command.

        You can seed multiple responses per command; the adapter will
        put them into a FIFO queue.  When a request comes in, the
        adapter will pop the corresponding response off of the queue.

        Note that you have to call :py:meth:`seed_response` once for each
        request you expect it to process. If :py:class:`MockAdapter` does not
        have a seeded response for a particular command, it will raise a
        ``BadApiResponse`` exception (simulates a 404 response).

        :param str command:
            The name of the command. Note that this is the camelCase version
            of the command name (e.g., ``getNodeInfo``, not ``get_node_info``).

        :param dict response:
             The response that the adapter will return.

        Example usage:

        .. code-block:: python

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

    async def send_request(self, payload: Dict, **kwargs: Any) -> dict:
        """
        Mimic asynchronous behavior of `HttpAdapter.send_request`.
        """
        # Store a snapshot so that we can inspect the request later.
        self.requests.append(dict(payload))

        command = payload['command']

        try:
            response = self.responses[command].popleft()
        except KeyError:
            raise with_context(
                exc=BadApiResponse(
                    'No seeded response for {command!r} '
                    '(expected one of: {seeds!r}).'.format(
                        command=command,
                        seeds=list(sorted(self.responses.keys())),
                    ),
                ),

                context={
                    'request': payload,
                },
            )
        except IndexError:
            raise with_context(
                exc=BadApiResponse(
                    '{command} called too many times; '
                    'no seeded responses left.'.format(
                        command=command,
                    ),
                ),

                context={
                    'request': payload,
                },
            )

        error = response.get('exception') or response.get('error')
        if error:
            raise with_context(BadApiResponse(error),
                               context={'request': payload})

        return await async_return(response)
