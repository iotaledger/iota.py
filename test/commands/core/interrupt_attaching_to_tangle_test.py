from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.interrupt_attaching_to_tangle import \
  InterruptAttachingToTangleCommand
from test import patch, MagicMock, async_test


class InterruptAttachingToTangleRequestFilterTestCase(BaseFilterTestCase):
  filter_type =\
    InterruptAttachingToTangleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_empty(self):
    filter_ = self._filter({})

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, {})

  def test_fail_unexpected_parameters(self):
    """
    The request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        # You're tearing me apart Lisa!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )


class InterruptAttachingToTangleCommandTestCase(TestCase):
  def setUp(self):
    super(InterruptAttachingToTangleCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.interrupt_attaching_to_tangle.InterruptAttachingToTangleCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.interrupt_attaching_to_tangle()

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
    with patch('iota.commands.core.interrupt_attaching_to_tangle.InterruptAttachingToTangleCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.interrupt_attaching_to_tangle()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )