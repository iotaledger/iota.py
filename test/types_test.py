# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota.types import Trit, Tryte


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


class TryteTestCase(TestCase):
  def test_comparison(self):
    """Testing equality and comparison of tryte values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_init_mixed_types(self):
    """
    As a convenience, you are allowed to initialize a Tryte using ints.
    """
    # Mixing Trits and ints is also OK.
    tryte = Tryte([Trit(1), 1, -1])

    self.assertEqual(tryte[0], Trit(1))
    self.assertEqual(tryte[1], Trit(1))

    # Well, shucks.
    self.assertNotEqual(tryte[2], Trit(-1))
    self.assertEqual(tryte[2].value, -1)

  # noinspection PyTypeChecker
  def test_error_init_wrong_type(self):
    """
    Attempting to initialize a tryte with something other than an array
      of trits.
    """
    with self.assertRaises(TypeError):
      Tryte(Trit(1))

    with self.assertRaises(TypeError):
      Tryte(['1', False, None])

  def test_error_init_not_enough_trits(self):
    """Attempting to initialize a tryte with less than 3 trits."""
    with self.assertRaises(ValueError):
      Tryte([])

    with self.assertRaises(ValueError):
      Tryte([Trit(0)])

    with self.assertRaises(ValueError):
      Tryte([Trit(0), Trit(0)])

  def test_init_with_padding(self):
    """Padding a tryte so that it has the correct number of trits."""
    tryte1 = Tryte([Trit(1)], pad=True)

    # Note that padding trits are applied first.
    self.assertEqual(tryte1[0].value, -1)
    self.assertEqual(tryte1[1].value, -1)
    self.assertEqual(tryte1[2].value, 1)

    tryte2 = Tryte([Trit(0), Trit(1)], pad=True)

    self.assertEqual(tryte2[0].value, -1)
    self.assertEqual(tryte2[1].value, 0)
    self.assertEqual(tryte2[2].value, 1)

  def test_error_init_too_many_trits(self):
    """Attempting to initialize a tryte with more than 3 trits."""
    with self.assertRaises(ValueError):
      Tryte([Trit(-1), Trit(-1), Trit(-1), Trit(-1)])
