# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase
from iota.commands.core.interrupt_attaching_to_tangle import \
  InterruptAttachingToTangleCommand
from test import MockAdapter


class InterruptAttachingToTangleRequestFilterTestCase(BaseFilterTestCase):
  filter_type =\
    InterruptAttachingToTangleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_empty(self):
    filter_ = self._filter({})

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, {})

  def test_fail_unexpected_parameters(self):
    """The request contains unexpected parameters."""
    self.assertFilterErrors(
      {
        # You're tearing me apart Lisa!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )
