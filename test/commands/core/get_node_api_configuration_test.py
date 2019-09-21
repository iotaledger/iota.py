# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota
from iota.adapter import MockAdapter
from iota.commands.core import GetNodeAPIConfigurationCommand


class GetNodeAPIConfigurationRequestFilterTestCase(BaseFilterTestCase):
    filter_type = \
        GetNodeAPIConfigurationCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def test_pass_empty(self):
        """
        The incoming response is (correctly) empty.
        """
        request = {}

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_fail_unexpected_parameters(self):
        """
        The incoming response contains unexpected parameters.
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


class GetNodeAPIConfigurationFilterTestCase(BaseFilterTestCase):
    filter_type = \
        GetNodeAPIConfigurationCommand(MockAdapter()).get_response_filter
    skip_value_check = True

    # noinspection SpellCheckingInspection
    def test_pass_happy_path(self):
        """
        The incoming response contains valid values.
        """
        response = {
            'maxFindTransactions': 100000,
            'maxRequestsList': 1000,
            'maxGetTrytes': 10000,
            'maxBodyLength': 1000000,
            'testNet': False,
            'milestoneStartIndex': 1050000,
        }

        filter_ = self._filter(response)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,
            {
                'maxFindTransactions': 100000,
                'maxRequestsList': 1000,
                'maxGetTrytes': 10000,
                'maxBodyLength': 1000000,
                'testNet': False,
                'milestoneStartIndex': 1050000,
            }
        )


class GetNodeAPIConfigurationCommandTestCase(TestCase):
    def setUp(self):
        super(GetNodeAPIConfigurationCommandTestCase, self).setUp()

        self.adapter = MockAdapter()

    def test_wireup(self):
        """
        Verify that the command is wired up correctly.
        """
        self.assertIsInstance(
            Iota(self.adapter).getNodeAPIConfiguration,
            GetNodeAPIConfigurationCommand,
        )
