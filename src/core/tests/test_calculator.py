"""
Test the calculator service
"""

from django.test import TestCase
import core.calculator as calc


class TestCalculator(TestCase):
    """
    Test the calculator module
    """

    def test_add(self):
        """
        Test the add function
        """
        self.assertEqual(calc.add(3, 4), 7)
