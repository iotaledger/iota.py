# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals


# noinspection SpellCheckingInspection
from unittest import TestCase

from iota.commands.get_node_info import GetNodeInfoCommand
from iota.types import TryteString
from test import MockAdapter


class GetNodeInfoTestCase(TestCase):
  def setUp(self):
    super(GetNodeInfoTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.command  = GetNodeInfoCommand(self.adapter)

  def test_happy_path(self):
    """Successful invocation of `getNodeInfo`."""
    expected_response = {
      'appName': 'IRI',
      'appVersion': '1.0.8.nu',
      'duration': 1,
      'jreAvailableProcessors': 4,
      'jreFreeMemory': 91707424,
      'jreMaxMemory': 1908932608,
      'jreTotalMemory': 122683392,
      'latestMilestone': 'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJRFKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
      'latestMilestoneIndex': 107,
      'latestSolidSubtangleMilestone': 'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJRFKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
      'latestSolidSubtangleMilestoneIndex': 107,
      'neighbors': 2,
      'packetsQueueSize': 0,
      'time': 1477037811737,
      'tips': 3,
      'transactionsToRequest': 0
    }

    self.adapter.response = expected_response

    response = self.command()

    self.assertDictEqual(response, expected_response)

    self.assertIsInstance(response['latestMilestone'], TryteString)

    self.assertIsInstance(
      response['latestSolidSubtangleMilestone'],
      TryteString,
    )

    self.assertListEqual(
      self.adapter.requests,
      [({'command': 'getNodeInfo'}, {})],
    )
