# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota
from iota.adapter import MockAdapter
from iota.commands.core import GetNodeAPIConfigurationCommand
from test import patch, MagicMock


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
        Verify that the command is wired up correctly.

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.get_node_api_configuration.GetNodeAPIConfigurationCommand.__call__',
                MagicMock(return_value='You found me!')
                ) as mocked_command:

            api = Iota(self.adapter)

            # Don't need to call with proper args here.
            response = api.get_node_api_configuration()

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )
