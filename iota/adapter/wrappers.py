from abc import ABCMeta, abstractmethod as abstract_method
from typing import Dict, Any

from iota.adapter import AdapterSpec, BaseAdapter, resolve_adapter

__all__ = [
    'RoutingWrapper',
]


class BaseWrapper(BaseAdapter, metaclass=ABCMeta):
    """
    Base functionality for "adapter wrappers", used to extend the
    functionality of IOTA adapters.
    """

    def __init__(self, adapter: AdapterSpec) -> None:
        super(BaseWrapper, self).__init__()

        if not isinstance(adapter, BaseAdapter):
            adapter = resolve_adapter(adapter)

        self.adapter: BaseAdapter = adapter

    def get_uri(self) -> str:
        return self.adapter.get_uri()

    @abstract_method
    def send_request(self, payload: dict, **kwargs: Any) -> dict:
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )


class RoutingWrapper(BaseWrapper):
    """
    Routes commands (API requests) to different nodes depending on the command
    name.

    This allows you to, for example, send POW requests to a local node,
    while routing all other requests to a remote one.

    Once you've initialized the :py:class:`RoutingWrapper`, invoke its
    :py:meth:`add_route` method to specify a different adapter to use for a
    particular command.

    :param AdapterSpec default_adapter:
        RoutingWrapper must be initialized with a default URI/adapter.
        This is the adapter that will be used for any command that doesn’t have
        a route associated with it.

    :return:
        :py:class:`RoutingWrapper` object.

    Example usage:

    .. code-block:: python

        from iota import Iota
        from iota.adapter.wrappers import RoutingWrapper

        # Route POW to localhost, everything else to 'https://nodes.thetangle.org:443'.
        api = Iota(
          RoutingWrapper('https://nodes.thetangle.org:443.'')
            .add_route('attachToTangle', 'http://localhost:14265')
            .add_route('interruptAttachingToTangle', 'http://localhost:14265')
        )

    .. note::

        A common use case for :py:class:`RoutingWrapper` is to perform
        proof-of-work on a specific (local) node, but let all other requests go to another node.
        Take care when you use :py:class:`RoutingWrapper` adapter and ``local_pow``
        parameter together in an API instance (see :py:class:`iota.Iota`), because the behavior might not
        be obvious.

        ``local_pow`` tells the API to perform proof-of-work (:py:meth:`iota.Iota.attach_to_tangle`)
        without relying on an actual node. It does this by calling an extension
        package `PyOTA-PoW <https://pypi.org/project/PyOTA-PoW/>`_ that does the
        job. In PyOTA, this means the request doesn't reach the adapter, it
        is redirected before.
        As a consequence,  ``local_pow`` has precedence over the route that is
        defined in :py:class:`RoutingWrapper`.
    """

    def __init__(self, default_adapter: AdapterSpec) -> None:
        """
        :param default_adapter:
            Adapter to use for any routes not listed in ``routes``.
        """
        super(RoutingWrapper, self).__init__(default_adapter)

        # Try to limit the number of distinct adapter instances we create
        # when resolving URIs.
        self.adapter_aliases: Dict[AdapterSpec, BaseAdapter] = {}

        self.routes: Dict[str, BaseAdapter] = {}

    def add_route(self, command: str, adapter: AdapterSpec) -> 'RoutingWrapper':
        """
        Adds a route to the wrapper.

        :param str command:
            The name of the command. Note that this is the camelCase version of
            the command name (e.g., ``attachToTangle``, not ``attach_to_tangle``).

        :param AdapterSpec adapter:
            The adapter object or URI to route requests to.

        :return:
            The :py:class:`RoutingWrapper` object it was called on. Useful for
            chaining the operation of adding routes in code.

        See :py:class:`RoutingWrapper` for example usage.
        """
        if not isinstance(adapter, BaseAdapter):
            try:
                adapter = self.adapter_aliases[adapter]
            except KeyError:
                self.adapter_aliases[adapter] = adapter = resolve_adapter(
                    adapter
                )

        self.routes[command] = adapter

        return self

    def get_adapter(self, command: str) -> BaseAdapter:
        """
        Return the adapter for the specified command.
        """
        return self.routes.get(command, self.adapter)

    async def send_request(self, payload: dict, **kwargs: Any) -> dict:
        command = payload.get('command')

        return await self.get_adapter(command).send_request(payload, **kwargs)
