# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota.types import Trit


class TritTestCase(TestCase):
  def test_comparison(self):
    """Testing equality and comparison of trit values."""
    on      = Trit(1)
    off     = Trit(0)
    unknown = Trit(-1)

    self.assertTrue(on == on)
    self.assertFalse(on != on)
    self.assertTrue(on <= on)
    self.assertFalse(on < on)
    self.assertTrue(on >= on)
    self.assertFalse(on > on)

    self.assertTrue(off == off)
    self.assertFalse(off != off)
    self.assertTrue(off <= off)
    self.assertFalse(off < off)
    self.assertTrue(off >= off)
    self.assertFalse(off > off)

    # `unknown` behaves similarly to NaN.
    # :see: https://en.wikipedia.org/wiki/IEEE_754
    self.assertFalse(unknown == unknown)
    self.assertTrue(unknown != unknown)
    self.assertFalse(unknown <= unknown)
    self.assertFalse(unknown < unknown)
    self.assertFalse(unknown >= unknown)
    self.assertFalse(unknown > unknown)

    self.assertFalse(on == off)
    self.assertTrue(on != off)
    self.assertFalse(on <= off)
    self.assertFalse(on < off)
    self.assertTrue(on > off)
    self.assertTrue(on >= off)

    self.assertFalse(off == on)
    self.assertTrue(off != on)
    self.assertTrue(off <= on)
    self.assertTrue(off < on)
    self.assertFalse(off >= on)
    self.assertFalse(off > on)

    self.assertFalse(on == unknown)
    self.assertTrue(on != unknown)
    self.assertFalse(on < unknown)
    self.assertFalse(on <= unknown)
    self.assertFalse(on > unknown)
    self.assertFalse(on >= unknown)

    self.assertFalse(off == unknown)
    self.assertTrue(off != unknown)
    self.assertFalse(off < unknown)
    self.assertFalse(off <= unknown)
    self.assertFalse(off > unknown)
    self.assertFalse(off >= unknown)

    self.assertTrue(on is on)
    self.assertTrue(unknown is unknown)

    self.assertFalse(on is off)
    self.assertFalse(on is Trit(1))
    self.assertFalse(unknown is Trit(-1))

    # Identity comparison also works for non-Trits.
    self.assertFalse(on is 1)
    self.assertFalse(unknown is None)

  def test_error_invalid_value(self):
    """Attempting to initialize a trit with an invalid value."""
    with self.assertRaises(ValueError):
      Trit(2)

    with self.assertRaises(ValueError):
      Trit(-2)

  # noinspection PyTypeChecker
  def test_error_invalid_type(self):
    """Trits may only be initialized using ints."""
    with self.assertRaises(TypeError):
      Trit(1.0)

    with self.assertRaises(TypeError):
      # This is not allowed because it is ambiguous; did you mean
      #   `Trit(0)` or `Trit(ord('0'))`?
      Trit('0')

    with self.assertRaises(TypeError):
      # Technically, booleans are ints, but we still don't allow them
      #   because Trits and booleans mean very different things.
      Trit(False)

    with self.assertRaises(TypeError):
      # It's too easy to accidentally pass a null to the initializer.
      #   For safety, this also is not allowed.
      Trit(None)

  # noinspection PyTypeChecker
  def test_error_invalid_comparison(self):
    """Trits can only be compared to other trits."""
    with self.assertRaises(TypeError):
      Trit(0) == 0

    with self.assertRaises(TypeError):
      Trit(1) != {}

    with self.assertRaises(TypeError):
      Trit(0) <= 0

    with self.assertRaises(TypeError):
      Trit(1) >= '0'

    with self.assertRaises(TypeError):
      Trit(-1) < 1

    with self.assertRaises(TypeError):
      Trit(-1) > False
