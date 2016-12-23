# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from collections import defaultdict
from typing import Dict, List, Optional, Text

from iota import BadApiResponse
from iota.adapter import BaseAdapter
from iota.exceptions import with_context


class MockAdapter(BaseAdapter):
  """
  An adapter for IotaApi that always returns a mocked response.
  """
  supported_protocols = ('mock',)

  # noinspection PyUnusedLocal
  @classmethod
  def configure(cls, uri):
    return cls()

  def __init__(self):
    # type: (Optional[dict]) -> None
    super(MockAdapter, self).__init__()

    self.responses  = defaultdict(list) # type: Dict[Text, List[dict]]
    self.requests   = [] # type: List[dict]

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
    self.responses[command].append(response)
    return self

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    # Store a snapshot so that we can inspect the request later.
    self.requests.append(dict(payload))

    command = payload['command']

    try:
      response = self.responses[command].pop(0)
    except (KeyError, IndexError):
      raise with_context(
        exc = BadApiResponse(
          'Unknown request {command!r} (expected one of: {seeds!r}).'.format(
            command = command,
            seeds   = list(sorted(self.responses.keys())),
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
