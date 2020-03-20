from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.get_node_info import GetNodeInfoCommand
from test import patch, MagicMock, async_test


class GetNodeInfoRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetNodeInfoCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_empty(self):
    """
    The incoming request is (correctly) empty.
    """
    request = {}

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        # All you had to do was nothing!  How did you screw that up?!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )


class GetNodeInfoResponseFilterTestCase(BaseFilterTestCase):
  filter_type = GetNodeInfoCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  def test_pass_happy_path(self):
    """
    The incoming response contains valid values.
    """
    response = {
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

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
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
          TransactionHash(
            b'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
            b'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
          ),

        'latestSolidSubtangleMilestone':
          TransactionHash(
            b'VBVEUQYE99LFWHDZRFKTGFHYGDFEAMAEBGUBTTJR'
            b'FKHCFBRTXFAJQ9XIUEZQCJOQTZNOOHKUQIKOY9999',
          ),
      },
    )


class GetNodeInfoCommandTestCase(TestCase):
  def setUp(self):
    super(GetNodeInfoCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.get_node_info.GetNodeInfoCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.get_node_info()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_wireup_async(self):
    """
    Verify that the command is wired up correctly. (async)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.get_node_info.GetNodeInfoCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.get_node_info()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )