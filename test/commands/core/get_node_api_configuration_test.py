from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core import GetNodeAPIConfigurationCommand
from test import patch, MagicMock, async_test


class GetNodeAPIConfigurationRequestFilterTestCase(BaseFilterTestCase):
    filter_type = \
        GetNodeAPIConfigurationCommand(MockAdapter()).get_request_filter
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


class GetNodeAPIConfigurationCommandTestCase(TestCase):
    def setUp(self):
        super(GetNodeAPIConfigurationCommandTestCase, self).setUp()

        self.adapter = MockAdapter()

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.get_node_api_configuration.GetNodeAPIConfigurationCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = Iota(self.adapter)

            response = api.get_node_api_configuration()

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
        with patch('iota.commands.core.get_node_api_configuration.GetNodeAPIConfigurationCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = AsyncIota(self.adapter)

            response = await api.get_node_api_configuration()

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )