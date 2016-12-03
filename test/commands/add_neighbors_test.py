# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterError
from iota.commands.add_neighbors import AddNeighborsCommand
from test.commands import BaseFilterCommandTestCase


class AddNeighborsCommandTestCase(BaseFilterCommandTestCase):
  command_type = AddNeighborsCommand

  def test_happy_path(self):
    """Successful invocation of `addNeighbors`."""
    expected_response = {
      'addedNeighbors': 0,
      'duration': 2,
    }

    self.adapter.response = expected_response

    neighbors = ['udp://node1.iotatoken.com:14265/', 'http://localhost:14265/']

    self.assertCommandSuccess(
      expected_response = expected_response,

      request = {
        'uris': neighbors,
      },
    )

  def test_uris_error_invalid(self):
    """Attempting to call `addNeighbors`, but `uris` is invalid."""
    with self.assertRaises(FilterError):
      # It's gotta be an array.
      self.command(uris='http://localhost:8080/')

    with self.assertRaises(FilterError):
      # I meant an array of strings!
      self.command(uris=[42, 'http://localhost:8080/'])

    with self.assertRaises(FilterError):
      # Insert "Forever Alone" meme here.
      self.command(uris=[])
