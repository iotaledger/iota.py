# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase

from iota.filters import NodeUri


class NodeUriTestCase(BaseFilterTestCase):
  filter_type = NodeUri

  def test_pass_none(self):
    """
    ``None`` always passes this filter.

    Use ``Required | NodeUri`` to reject null values.
    """
    self.assertFilterPasses(None)

  def test_pass_uri(self):
    """The incoming value is a valid URI."""
    self.assertFilterPasses('udp://localhost:14265/node')

  def test_fail_not_a_uri(self):
    """The incoming value is not a URI."""
    self.assertFilterErrors(
      'not a valid uri',
      [NodeUri.CODE_INVALID],
    )

  def test_fail_bytes(self):
    """
    To ensure consistent behavior in Python 2 and 3, bytes are not
      accepted.
    """
    self.assertFilterErrors(
      b'udp://localhost:14265/node',
      [f.Type.CODE_WRONG_TYPE],
    )

  def test_fail_wrong_type(self):
    """The incoming value is not a string."""
    self.assertFilterErrors(
      # Use ``FilterRepeater(NodeUri)`` to validate a sequence of URIs.
      ['udp://localhost:14265/node'],
      [f.Type.CODE_WRONG_TYPE],
    )
