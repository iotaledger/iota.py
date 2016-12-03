# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands.get_node_info import GetNodeInfoCommand
from iota.types import TryteString
from test.commands import BaseFilterCommandTestCase


# noinspection SpellCheckingInspection
class GetNodeInfoCommandTestCase(BaseFilterCommandTestCase):
  command_type = GetNodeInfoCommand

  def test_happy_path(self):
    """Successful invocation of `getNodeInfo`."""
    self.adapter.response = {
      'appName': 'IRI',
      'appVersion': '1.0.8.nu',
      'duration': 1,
      'jreAvailableProcessors': 4,
      'jreFreeMemory': 91707424,
      'jreMaxMemory': 1908932608,
      'jreTotalMemory': 122683392,
      'latestMilestoneIndex': 107,
      'latestSolidSubtangleMilestoneIndex': 107,
      'neighbors': 2,
      'packetsQueueSize': 0,
      'time': 1477037811737,
      'tips': 3,
      'transactionsToRequest': 0,

      'latestMilestone':
        'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
        'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',

      'latestSolidSubtangleMilestone':
        'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
        'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
    }

    self.assertCommandSuccess(
      expected_response = {
        'appName': 'IRI',
        'appVersion': '1.0.8.nu',
        'duration': 1,
        'jreAvailableProcessors': 4,
        'jreFreeMemory': 91707424,
        'jreMaxMemory': 1908932608,
        'jreTotalMemory': 122683392,
        'latestMilestoneIndex': 107,
        'latestSolidSubtangleMilestoneIndex': 107,
        'neighbors': 2,
        'packetsQueueSize': 0,
        'time': 1477037811737,
        'tips': 3,
        'transactionsToRequest': 0,

        'latestMilestone':
          TryteString(
            b'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
            b'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
          ),

        'latestSolidSubtangleMilestone':
          TryteString(
            b'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
            b'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999'
          ),
      }
    )
