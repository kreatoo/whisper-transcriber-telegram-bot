#!/usr/bin/env python3
"""
Integration test demonstrating the access control feature.
This script shows how the bot would behave with different configurations.
"""

import os
import sys
import configparser

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_loader import ConfigLoader


def test_scenario(description, allowed_ids_config, test_chat_ids):
    """Test a scenario with specific configuration"""
    print(f"\n{'='*70}")
    print(f"Scenario: {description}")
    print(f"{'='*70}")
    print(f"Configuration: allowed_group_ids = {allowed_ids_config}")
    print()
    
    # Mock the config
    from unittest.mock import patch, MagicMock
    
    with patch.object(ConfigLoader, 'get_config') as mock_config:
        mock_cfg = MagicMock()
        mock_cfg.get.return_value = allowed_ids_config
        mock_config.return_value = mock_cfg
        
        # Get the parsed allowed IDs
        allowed_ids = ConfigLoader.get_allowed_group_ids()
        if allowed_ids:
            print(f"Parsed allowed IDs: {allowed_ids}")
        else:
            print("No restrictions (all chats allowed)")
        print()
        
        # Test each chat ID
        for chat_id, description in test_chat_ids:
            is_allowed = ConfigLoader.is_group_allowed(chat_id)
            status = "✅ ALLOWED" if is_allowed else "❌ DENIED"
            print(f"  Chat ID {chat_id:15} ({description:20}): {status}")


def main():
    """Run integration tests"""
    print("\n" + "="*70)
    print("ACCESS CONTROL FEATURE - INTEGRATION TEST")
    print("="*70)
    
    # Scenario 1: No restrictions (default behavior)
    test_scenario(
        "No restrictions configured (default)",
        "",
        [
            (-1001234567890, "Public Group A"),
            (-1009876543210, "Public Group B"),
            (123456789, "Private Chat"),
            (-999999999, "Public Group C"),
        ]
    )
    
    # Scenario 2: Restrict to specific groups
    test_scenario(
        "Restricted to two specific groups",
        "-1001234567890, -1009876543210",
        [
            (-1001234567890, "Allowed Group 1"),
            (-1009876543210, "Allowed Group 2"),
            (123456789, "Private Chat"),
            (-999999999, "Unauthorized Group"),
        ]
    )
    
    # Scenario 3: Restrict to single private chat
    test_scenario(
        "Restricted to single private chat",
        "123456789",
        [
            (123456789, "Allowed Private Chat"),
            (987654321, "Other Private Chat"),
            (-1001234567890, "Public Group"),
        ]
    )
    
    # Scenario 4: Mix of private and group chats
    test_scenario(
        "Mix of private chat and group",
        "123456789, -1001234567890",
        [
            (123456789, "Allowed Private Chat"),
            (-1001234567890, "Allowed Group"),
            (987654321, "Unauthorized Private"),
            (-999999999, "Unauthorized Group"),
        ]
    )
    
    print("\n" + "="*70)
    print("CONFIGURATION EXAMPLES")
    print("="*70)
    print("""
To configure access control, edit config/config.ini:

[AccessControl]
# Allow all (no restrictions) - DEFAULT
allowed_group_ids = 

# Restrict to specific groups only
allowed_group_ids = -1001234567890, -1009876543210

# Restrict to private chat only
allowed_group_ids = 123456789

# Mix of private chats and groups
allowed_group_ids = 123456789, 987654321, -1001234567890

Note: Group IDs typically start with a minus sign (-)
To find your group ID:
1. Add the bot to the group
2. Send a message
3. Check the bot logs for chat_id
""")
    
    print("="*70)
    print()


if __name__ == '__main__':
    main()
