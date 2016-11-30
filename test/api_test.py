# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import IotaApi
from iota.adapter import HttpAdapter


class IotaApiTestCase(TestCase):
  def test_init_with_uri(self):
    """
    Passing a URI to the initializer instead of an adapter instance.
    """
    api = IotaApi('udp://localhost:14265/')
    self.assertIsInstance(api.adapter, HttpAdapter)
