# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota
from iota.adapter import MockAdapter
from iota.commands.core.remove_neighbors import RemoveNeighborsCommand
from iota.filters import NodeUri


class RemoveNeighborsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = RemoveNeighborsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_valid_request(self):
    """
    The incoming request is valid.
    """
    request = {
      'uris': [
        'udp://node1.iotatoken.com',
        'udp://localhost:14265/',
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_fail_empty(self):
    """
    The incoming request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'uris': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'uris': ['udp://localhost'],

        # I've never seen that before in my life, officer.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_neighbors_null(self):
    """
    ``uris`` is null.
    """
    self.assertFilterErrors(
      {
        'uris': None,
      },

      {
        'uris': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_uris_wrong_type(self):
    """
    ``uris`` is not an array.
    """
    self.assertFilterErrors(
      {
        # Nope; it's gotta be an array, even if you only want to add
        # a single neighbor.
        'uris': 'udp://localhost:8080/'
      },

      {
        'uris': [f.Type.CODE_WRONG_TYPE]
      },
    )

  def test_fail_uris_empty(self):
    """
    ``uris`` is an array, but it's empty.
    """
    self.assertFilterErrors(
      {
        # Insert "Forever Alone" meme here.
        'uris': [],
      },

      {
        'uris': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_uris_contents_invalid(self):
    """
    ``uris`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        # When I said it has to be an array before, I meant an array of
        # strings!
        'uris': [
          '',
          False,
          None,
          b'udp://localhost:8080/',
          'not a valid uri',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          'udp://localhost',

          # Only UDP URIs are allowed.
          'http://localhost:14265',

          2130706433,
        ],
      },

      {
        'uris.0':  [f.Required.CODE_EMPTY],
        'uris.1':  [f.Type.CODE_WRONG_TYPE],
        'uris.2':  [f.Required.CODE_EMPTY],
        'uris.3':  [f.Type.CODE_WRONG_TYPE],
        'uris.4':  [NodeUri.CODE_NOT_NODE_URI],
        'uris.6':  [NodeUri.CODE_NOT_NODE_URI],
        'uris.7':  [f.Type.CODE_WRONG_TYPE],
      },
    )


class RemoveNeighborsCommandTestCase(TestCase):
  def setUp(self):
    super(RemoveNeighborsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).removeNeighbors,
      RemoveNeighborsCommand,
    )
