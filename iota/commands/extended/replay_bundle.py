# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand, RequestFilter

__all__ = [
  'ReplayBundleCommand',
]


class ReplayBundleCommand(FilterCommand):
  """
  Executes ``replayBundle`` extended API command.

  See :py:meth:`iota.api.Iota.replay_bundle` for more information.
  """
  command = 'replayBundle'

  def get_request_filter(self):
    return ReplayBundleRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class ReplayBundleRequestFilter(RequestFilter):
  def __init__(self):
    super(ReplayBundleRequestFilter, self).__init__(
      {
      },

      allow_missing_keys = {
      },
    )
