from unittest import TestCase

from iota import trits_from_int


class TritsFromIntTestCase(TestCase):
  """
  Explicit unit tests for :py:func:`trits_from_int`.

  Note that this function is used internally by many different classes
  and functions, so we still have good coverage even though this
  particular test case has limited scope.
  """
  def test_zero(self):
    """
    Zero is represented as ``[0]`` by default.

    https://github.com/iotaledger/iota.py/issues/49
    """
    self.assertEqual(trits_from_int(0), [0])

  def test_zero_unpadded(self):
    """
    Converting zero to trits, without padding.
    """
    self.assertEqual(trits_from_int(0, pad=None), [])


