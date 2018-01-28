# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address
from iota.flash import MAX_USES
from iota.flash.commands.multisig import get_last_branch, update_leaf_to_root, get_minimum_branch


class FlashUtilsTestCase(TestCase):

  def setUp(self):
    super(FlashUtilsTestCase, self).setUp()

    self.address_1 = {
      'address': Address(b'USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9USERONE9ADDRESS9U'),
      'children': [],
      'bundles': []
    }
    self.address_2 = {
      'address': Address(b'USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9USERTWO9ADDRESS9U'),
      'children': [],
      'bundles': []
    }
    self.address_3 = {
      'address': Address(b'USERTHR9ADDRESS9USERTHR9ADDRESS9USERTHR9ADDRESS9USERTHR9ADDRESS9USERTHR9ADDRESS9U'),
      'children': [],
      'bundles': []
    }
    self.address_4 = {
      'address': Address(b'USERFOU9ADDRESS9USERFOU9ADDRESS9USERFOU9ADDRESS9USERFOU9ADDRESS9USERFOU9ADDRESS9U'),
      'children': [],
      'bundles': []
    }

    # wire up test tree
    self.root_1 = self.address_1
    self.root_1['children'].append(self.address_2)
    self.address_2['children'].append(self.address_3)
    self.address_2['children'].append(self.address_4)

  def test_pass_get_last_branch_full_tree(self):
    """
    Tests if proper last branch is found in full tree
    """
    branch = get_last_branch(root=self.root_1)
    self.assertListEqual(branch, [self.address_1, self.address_2, self.address_4])

  def test_pass_get_last_branch_single_tree(self):
    """
    Tests if proper last branch is found in tree with one node
    """
    branch = get_last_branch(root=self.address_4)
    self.assertListEqual(branch, [self.address_4])

  def test_fail_get_last_branch_full_tree(self):
    """
    Tests if proper last branch is not found in full tree
    """
    branch = get_last_branch(root=self.address_2)
    self.assertNotEqual(branch, [self.address_1, self.address_2, self.address_4])

  def test_pass_get_minimum_branch_unused_tree(self):
    """
    Tests if proper minimum branch is found in unused tree
    """
    branch = get_minimum_branch(root=self.root_1)
    self.assertListEqual(branch, [self.address_1])

  def test_pass_get_minimum_branch_used_tree(self):
    """
    Tests if proper minimum branch is found in used tree
    """
    self.root_1['bundles'] = list(range(MAX_USES))  # fill with dummy data
    branch = get_minimum_branch(root=self.root_1)
    self.assertListEqual(branch, [self.address_1, self.address_2])

  def test_pass_update_leaf_to_root(self):
    """
    Tests if proper address is returned in full tree search
    """
    address, num_generate = update_leaf_to_root(root=self.root_1)
    self.assertEqual(address, self.address_1)
    self.assertEqual(num_generate, 0)
