# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from six import string_types, text_type
from typing import Generator, Sequence

from iota.api import BaseCommand


class AddNeighborsCommand(BaseCommand):
  """
  Executes `addNeighbors` command.

  :see: iota.IotaApi.add_neighbors
  """
  command = 'addNeighbors'

  def _prepare_request(self, request):
    # Required parameters.
    uris = request['uris']

    if isinstance(uris, Generator):
      # :see: https://youtrack.jetbrains.com/issue/PY-20709
      # noinspection PyTypeChecker
      uris = list(uris)

    if isinstance(uris, string_types) or not isinstance(uris, Sequence):
      raise TypeError(
        'uris has wrong type (expected Sequence, actual {type}).'.format(
          type = type(uris).__name__,
        ),
      )

    if not uris:
      raise ValueError('uris must not be empty.')

    for i, u in enumerate(uris):
      if not isinstance(u, string_types):
        raise TypeError(
          'uris[{i}] has wrong type '
          '(expected {expected}, actual {type}).'.format(
            i         = i,
            expected  = text_type.__name__,
            type      = type(u).__name__,
          ),
        )

  def _prepare_response(self, response):
    pass
