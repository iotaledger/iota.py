# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import convert_value_to_standard_unit


class ConvertValueToStandardUnitTestCase(TestCase):
  def test_convert_to_smaller_unit(self):
    """
    Converting to smaller unit.
    """
    self.assertEqual(convert_value_to_standard_unit('1.618 Mi', 'i'), 1618000)

  def test_convert_to_bigger_unit(self):
    """
    Converting to bigger unit.
    """
    self.assertEqual(convert_value_to_standard_unit('42 i', 'Ki'), 0.042)

  def test_convert_to_same_size_unit(self):
    """
    Converting to unit of same size.
    """
    self.assertEqual(
      convert_value_to_standard_unit('299792458 Mi', 'Mi'),
      299792458,
    )

  def test_convert_from_invalid_symbol(self):
    """
    Attempting conversion from value suffixed with invalid symbol.
    """
    with self.assertRaises(ValueError):
      convert_value_to_standard_unit('3.141592 Xi', 'Pi')

  def test_convert_to_invalid_symbol(self):
    """
    Attempting conversion to invalid symbol.
    """
    with self.assertRaises(ValueError):
      convert_value_to_standard_unit('3.141592 Pi', 'Xi')

  def test_convert_type_list(self):
    """
    Attempting to convert invalid type: list.
    """
    with self.assertRaises(ValueError):
      # noinspection PyTypeChecker
      convert_value_to_standard_unit(['3.141592', 'Pi'], 'Gi')

  def test_convert_type_float(self):
    """
    Attempting to convert invalid type: float.
    """
    with self.assertRaises(ValueError):
      # noinspection PyTypeChecker
      convert_value_to_standard_unit(3.141592, 'Pi')

  def test_convert_value_no_space(self):
    """
    Attempting to convert value missing a space separating amount and suffix.
    """
    with self.assertRaises(ValueError):
      convert_value_to_standard_unit('3.141592Pi', 'Gi')

  def test_convert_fractional_iotas(self):
    """
    Converting from/to fractional iotas.
    """
    self.assertEqual(convert_value_to_standard_unit('1.6182 Ki', 'i'), 1618.2)

  def test_convert_negative_values(self):
    """
    Converting negative values.
    """
    self.assertEqual(convert_value_to_standard_unit('-1.618 Ki', 'i'), -1618)

  def test_convert_wrong_case_symbol(self):
    """
    Attempting to convert value containing suffix specified with wrong case.
    """
    with self.assertRaises(ValueError):
      convert_value_to_standard_unit('3.141592 pI', 'Gi')
