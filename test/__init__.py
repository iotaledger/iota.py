# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional

from iota.adapter import BaseAdapter


class MockAdapter(BaseAdapter):
  """An adapter for IotaApi that always returns a mocked response."""
  supported_protocols = ('mock',)

  def __init__(self, response=None):
    # type: (Optional[dict]) -> None
    super(MockAdapter, self).__init__()

    self.response = response or {}
    self.requests = []

  def send_request(self, payload, **kwargs):
    self.requests.append((payload, kwargs))
    return self.response
