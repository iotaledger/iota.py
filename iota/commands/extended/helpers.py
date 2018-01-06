class Helpers(object):
  """
  Adds additional helper functions that aren't part of the core or extended
  API.
  """

  def __init__(self, api):
    self.api = api

  def is_promotable(self, tail):
    # type: (TransactionHash) -> bool
    """
    Determines if a tail transaction is promotable.

    :param tail:
      Transaction hash. Must be a tail transaction.
    """
    return self.api.check_consistency(tails=[tail])['state']
