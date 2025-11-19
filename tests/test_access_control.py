#!/usr/bin/env python3
"""
Test suite for Access Control functionality
Tests the group ID filtering feature
"""

import os
import sys
import unittest
import configparser
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import ConfigLoader


class TestAccessControl(unittest.TestCase):
    """Test cases for access control functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset the singleton instance before each test
        ConfigLoader._instance = None
        ConfigLoader._config = None

    def test_get_allowed_group_ids_empty(self):
        """Test that empty allowed_group_ids returns empty list"""
        with patch.object(ConfigLoader, 'get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.get.return_value = ''
            mock_config.return_value = mock_cfg
            
            result = ConfigLoader.get_allowed_group_ids()
            self.assertEqual(result, [])

    def test_get_allowed_group_ids_single(self):
        """Test parsing single group ID"""
        with patch.object(ConfigLoader, 'get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.get.return_value = '-1001234567890'
            mock_config.return_value = mock_cfg
            
            result = ConfigLoader.get_allowed_group_ids()
            self.assertEqual(result, [-1001234567890])

    def test_get_allowed_group_ids_multiple(self):
        """Test parsing multiple group IDs"""
        with patch.object(ConfigLoader, 'get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.get.return_value = '-1001234567890, -1009876543210, 123456'
            mock_config.return_value = mock_cfg
            
            result = ConfigLoader.get_allowed_group_ids()
            self.assertEqual(result, [-1001234567890, -1009876543210, 123456])

    def test_get_allowed_group_ids_with_whitespace(self):
        """Test parsing group IDs with extra whitespace"""
        with patch.object(ConfigLoader, 'get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.get.return_value = '  -1001234567890  ,  -1009876543210  '
            mock_config.return_value = mock_cfg
            
            result = ConfigLoader.get_allowed_group_ids()
            self.assertEqual(result, [-1001234567890, -1009876543210])

    def test_get_allowed_group_ids_invalid(self):
        """Test handling invalid group IDs"""
        with patch.object(ConfigLoader, 'get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.get.return_value = 'invalid, not-a-number'
            mock_config.return_value = mock_cfg
            
            result = ConfigLoader.get_allowed_group_ids()
            self.assertEqual(result, [])

    def test_is_group_allowed_no_restrictions(self):
        """Test that all groups are allowed when no restrictions are configured"""
        with patch.object(ConfigLoader, 'get_allowed_group_ids', return_value=[]):
            self.assertTrue(ConfigLoader.is_group_allowed(-1001234567890))
            self.assertTrue(ConfigLoader.is_group_allowed(123456))
            self.assertTrue(ConfigLoader.is_group_allowed(-999))

    def test_is_group_allowed_with_restrictions_allowed(self):
        """Test that allowed group IDs pass the check"""
        allowed_ids = [-1001234567890, -1009876543210]
        with patch.object(ConfigLoader, 'get_allowed_group_ids', return_value=allowed_ids):
            self.assertTrue(ConfigLoader.is_group_allowed(-1001234567890))
            self.assertTrue(ConfigLoader.is_group_allowed(-1009876543210))

    def test_is_group_allowed_with_restrictions_denied(self):
        """Test that non-allowed group IDs are denied"""
        allowed_ids = [-1001234567890, -1009876543210]
        with patch.object(ConfigLoader, 'get_allowed_group_ids', return_value=allowed_ids):
            self.assertFalse(ConfigLoader.is_group_allowed(-999))
            self.assertFalse(ConfigLoader.is_group_allowed(123456))
            self.assertFalse(ConfigLoader.is_group_allowed(-1111111111111))

    def test_is_group_allowed_positive_ids(self):
        """Test that positive IDs (private chats) work correctly"""
        allowed_ids = [123456, 789012]
        with patch.object(ConfigLoader, 'get_allowed_group_ids', return_value=allowed_ids):
            self.assertTrue(ConfigLoader.is_group_allowed(123456))
            self.assertTrue(ConfigLoader.is_group_allowed(789012))
            self.assertFalse(ConfigLoader.is_group_allowed(999999))


if __name__ == '__main__':
    unittest.main()
