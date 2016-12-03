# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from pprint import pformat
from typing import Optional
from unittest import TestCase

from iota.commands import FilterCommand, FilterError
from test import MockAdapter


class BaseCommandTestCase(TestCase):
  command_type = None

  def setUp(self):
    super(BaseCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = self.command_type(self.adapter) # type: FilterCommand

  def assertCommandSuccess(self, expected_response, request=None):
    # type: (dict, Optional[dict]) -> None
    """
    Sends the command to the adapter and expects a successful result.
    """
    request   = request or {} # type: dict
    response  = self.command(**request)

    self.assertDictEqual(response, expected_response)


class BaseFilterCommandTestCase(BaseCommandTestCase):
  def assertCommandSuccess(self, expected_response, request=None):
    # type: (dict, Optional[dict]) -> None
    """
    Sends the command to the adapter and expects a successful result.
    """
    try:
      super(BaseFilterCommandTestCase, self)\
        .assertCommandSuccess(expected_response, request)
    except FilterError as e:
      self.fail('{exc}\n\n{errors}'.format(
        exc     = e,
        errors  = pformat(e.context['filter_errors']),
      ))
