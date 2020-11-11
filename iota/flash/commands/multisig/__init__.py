from typing import List

from iota.flash import MAX_USES


def get_last_branch(root):
  # type: (dict) -> List[dict]
  """
  Searches for last used branch in tree and returns list of node beginning with
  root node.

  :param root: root of tree
  :return list of nodes in last used branch beginning with root node
  """
  multisigs = []
  node = root
  while node:
    multisigs.append(node)
    node = node['children'][-1] if node['children'] else None
  return multisigs


def get_minimum_branch(root):
  # type: (dict) -> List[dict]
  """
  Searches for minimum branch in tree, which stores transactions

  :param root: root of tree
  :return list of nodes storing transactions
  """
  multisigs = []
  node = root
  while node:
    multisigs.append(node)
    if len(node['children']) and len(node['bundles']) == MAX_USES:
      node = node['children'][-1]
    else:
      node = None
  return multisigs


def update_leaf_to_root(root):
  # type: (dict) -> (dict, int)
  """
  Searches tree for node in branch that can be used and number of addresses that
  needs to be generated
  :param root:
  :returns: tuple (multisig_address, num_to_ generate)
  :rtype: (dict, int)
  """
  multisigs = get_last_branch(root)

  # get the first one that does not pass all the way down
  for i in range(len(multisigs) - 1):
    transactions = multisigs[i]['bundles']
    if not any([t.value > 0 and t.address == multisigs[i + 1]['address'] for t in transactions]):
      return multisigs[i], 0

  # TODO: TEST this section
  # get the first from the bottom that is used less than MAX_USES times
  num_generate = 0
  for i in reversed(range(len(multisigs))):
    if len(multisigs[i]['bundles']) != MAX_USES:
      break
    num_generate += 1
  return multisigs[i], num_generate
