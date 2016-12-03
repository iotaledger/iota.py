# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase

from iota.commands.add_neighbors import AddNeighborsRequestFilter
from iota.filters import NodeUri


class AddNeighborsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = AddNeighborsRequestFilter

  def test_pass_happy_path(self):
    """The incoming request is valid."""
    self.assertFilterPasses({
      'uris': [
        'udp://node1.iotatoken.com',
        'http://localhost:14265/',
      ],
    })

  def test_fail_neighbors_wrong_type(self):
    """`neighbors` is not an array."""
    self.assertFilterErrors(
      {
        # Nope; it's gotta be an array, even if you only want to add
        #   a single neighbor.
        'uris': 'http://localhost:8080/'
      },

      {
        'uris': [f.Type.CODE_WRONG_TYPE]
      },

      self.skip_value_check,
    )

  def test_neighbors_empty(self):
    """`neighbors` is an array, but it's empty."""
    self.assertFilterErrors(
      {
        # Insert "Forever Alone" meme here.
        'uris': [],
      },

      {
        'uris': [f.Required.CODE_EMPTY],
      },

      self.skip_value_check,
    )

  def test_neighbors_contents_invalid(self):
    """
    `neighbors` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        # When I said it has to be an array before, I meant an array of
        #   strings!
        'uris': [
          '',
          False,
          None,
          b'http://localhost:8080/',
          'not a valid uri',


          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          'udp://localhost',

          2130706433,
        ],
      },

      {
        'uris.0':  [f.Required.CODE_EMPTY],
        'uris.1':  [f.Type.CODE_WRONG_TYPE],
        'uris.2':  [f.Required.CODE_EMPTY],
        'uris.3':  [f.Type.CODE_WRONG_TYPE],
        'uris.4':  [NodeUri.CODE_NOT_NODE_URI],
        'uris.6':  [f.Type.CODE_WRONG_TYPE],
      },

      self.skip_value_check,
    )
