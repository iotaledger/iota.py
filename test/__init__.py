# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Dict, List, Optional, Text

from iota.adapter import BaseAdapter, BadApiResponse


class MockAdapter(BaseAdapter):
  """An adapter for StrictIota that always returns a mocked response."""
  supported_protocols = ('mock',)

  # noinspection PyUnusedLocal
  @classmethod
  def configure(cls, uri):
    return cls()

  def __init__(self):
    # type: (Optional[dict]) -> None
    super(MockAdapter, self).__init__()

    self.responses  = {} # type: Dict[Text, dict]
    self.requests   = [] # type: List[dict]

  def seed_response(self, command, response):
    # type: (Text, dict) -> MockAdapter
    """
    Sets the response that the adapter will return for the specified
    command.
    """
    self.responses[command] = response
    return self

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    # Store a snapshot so that we can inspect the request later.
    self.requests.append(payload.copy())

    command = payload['command']

    try:
      response = self.responses[command]
    except KeyError:
      raise BadApiResponse(
        'Unknown request {command!r} (expected one of: {seeds!r}).'.format(
          command = command,
          seeds   = list(sorted(self.responses.keys())),
        ),
      )

    error = response.get('exception') or response.get('error')
    if error:
      raise BadApiResponse(error)

    return response
