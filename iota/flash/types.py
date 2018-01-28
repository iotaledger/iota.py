# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List

from iota import Bundle
from iota.crypto.types import Seed, Digest


class FlashUser:
  """
  Object representing a user withing a Flash channel
  """

  def __init__(self, user_index, seed, index, security, depth, flash):
    # type: (FlashUser, int, Seed, int, int, int, FlashState) -> None
    self.user_index = user_index  # type: int
    self.seed = seed  # type: Seed
    self.index = index  # type: int
    self.security = security  # type: int
    self.depth = depth  # type: int
    self.flash = flash  # type: FlashState
    self.bundles = []  # type: List[Bundle]
    self.partial_digests = []  # type: List[Digest]


class FlashState:
  """
  Object storing information of the current state of the channel
  """

  def __init__(self, signers_count, balance, deposit):
    # type: (FlashState, int, int, list) -> None
    self.signers_count = signers_count  # type: int
    self.balane = balance  # type: int
    self.deposit = deposit  # type: List[int]
    self.outputs = {}  # type: dict  # TODO: refine this type
    self.transfers = []  # type: list  # TODO: refine this type
    self.remainder_address = None  # type: dict
    self.deposit_address = None  # type: dict
    self.settlement_addresses = None  # type: dict
    self.root = None  # type: dict
