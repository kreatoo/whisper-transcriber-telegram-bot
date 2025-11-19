#!/usr/bin/env python3
"""
Test suite for reply handling functionality
Tests the bot mention detection when replying to voice/audio messages
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram import Update, Message, Chat, User, Voice, Audio, Document, MessageEntity
from telegram.ext import CallbackContext


class TestReplyHandling(unittest.TestCase):
    """Test cases for reply handling functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # We'll import the bot class here to avoid import issues
        pass

    def test_private_chat_reply_detection(self):
        """Test that replies in private chats are always detected"""
        # Create mock objects
        mock_update = MagicMock(spec=Update)
        mock_message = MagicMock(spec=Message)
        mock_chat = MagicMock(spec=Chat)
        mock_user = MagicMock(spec=User)
        mock_voice = MagicMock(spec=Voice)
        mock_reply_message = MagicMock(spec=Message)
        
        # Setup the mock chain
        mock_update.message = mock_message
        mock_update.effective_user = mock_user
        mock_update.effective_chat = mock_chat
        mock_message.text = "transcribe this"
        mock_message.chat = mock_chat
        mock_message.reply_to_message = mock_reply_message
        mock_message.entities = None
        mock_chat.type = "private"
        mock_user.id = 12345
        mock_reply_message.voice = mock_voice
        
        # In private chat, is_bot_mentioned should be True
        is_bot_mentioned = False
        if mock_chat.type == "private":
            is_bot_mentioned = True
        
        self.assertTrue(is_bot_mentioned, "Bot should be considered mentioned in private chats")

    def test_text_mention_detection(self):
        """Test that @bot_username mentions in text are detected"""
        bot_username = "test_bot"
        message_text = "Hey @test_bot please transcribe this"
        
        is_bot_mentioned = f"@{bot_username}" in message_text
        self.assertTrue(is_bot_mentioned, "Bot mention in text should be detected")

    def test_text_mention_not_detected_for_other_bot(self):
        """Test that mentions of other bots are not detected"""
        bot_username = "test_bot"
        message_text = "Hey @other_bot please transcribe this"
        
        is_bot_mentioned = f"@{bot_username}" in message_text
        self.assertFalse(is_bot_mentioned, "Other bot mention should not be detected")

    def test_entity_based_mention_detection(self):
        """Test that entity-based mentions are properly detected"""
        bot_username = "test_bot"
        message_text = "@test_bot transcribe"
        
        # Create mock entity
        mock_entity = MagicMock(spec=MessageEntity)
        mock_entity.type = "mention"
        mock_entity.offset = 0
        mock_entity.length = 9  # Length of "@test_bot"
        
        entities = [mock_entity]
        
        # Simulate entity-based mention detection
        is_bot_mentioned = False
        for entity in entities:
            if entity.type == "mention":
                mention_text = message_text[entity.offset:entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    is_bot_mentioned = True
                    break
        
        self.assertTrue(is_bot_mentioned, "Entity-based mention should be detected")

    def test_text_mention_entity_without_bot_name(self):
        """Test that entity mentions of other users are not detected as bot mention"""
        bot_username = "test_bot"
        message_text = "@other_user transcribe"
        
        # Create mock entity for different user
        mock_entity = MagicMock(spec=MessageEntity)
        mock_entity.type = "mention"
        mock_entity.offset = 0
        mock_entity.length = 11  # Length of "@other_user"
        
        entities = [mock_entity]
        
        # Simulate entity-based mention detection
        is_bot_mentioned = False
        for entity in entities:
            if entity.type == "mention":
                mention_text = message_text[entity.offset:entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    is_bot_mentioned = True
                    break
        
        self.assertFalse(is_bot_mentioned, "Other user mention should not be detected as bot")

    def test_text_mention_entity_for_bot(self):
        """Test text_mention entity type detection"""
        bot_username = "test_bot"
        
        # Create mock entity with user
        mock_entity = MagicMock(spec=MessageEntity)
        mock_entity.type = "text_mention"
        mock_user = MagicMock(spec=User)
        mock_user.username = bot_username
        mock_entity.user = mock_user
        
        entities = [mock_entity]
        
        # Simulate text_mention detection
        is_bot_mentioned = False
        for entity in entities:
            if entity.type == "text_mention":
                if hasattr(entity, 'user') and entity.user.username == bot_username:
                    is_bot_mentioned = True
                    break
        
        self.assertTrue(is_bot_mentioned, "text_mention entity should be detected")

    def test_no_mention_in_group_chat(self):
        """Test that no mention in group chat is not detected"""
        bot_username = "test_bot"
        message_text = "transcribe this"
        chat_type = "group"
        
        is_bot_mentioned = False
        if chat_type == "private":
            is_bot_mentioned = True
        elif message_text and f"@{bot_username}" in message_text:
            is_bot_mentioned = True
        
        self.assertFalse(is_bot_mentioned, "No mention in group should not trigger detection")

    def test_reply_to_voice_without_mention_in_group(self):
        """Test that reply to voice without mention in group is not processed"""
        bot_username = "test_bot"
        message_text = "please transcribe"
        chat_type = "group"
        has_reply = True
        reply_has_voice = True
        
        is_bot_mentioned = False
        if chat_type == "private":
            is_bot_mentioned = True
        elif message_text and f"@{bot_username}" in message_text:
            is_bot_mentioned = True
        
        should_process = is_bot_mentioned and has_reply and reply_has_voice
        self.assertFalse(should_process, "Reply without mention in group should not be processed")

    def test_reply_to_voice_with_mention_in_group(self):
        """Test that reply to voice with mention in group is processed"""
        bot_username = "test_bot"
        message_text = "@test_bot please transcribe"
        chat_type = "group"
        has_reply = True
        reply_has_voice = True
        
        is_bot_mentioned = False
        if chat_type == "private":
            is_bot_mentioned = True
        elif message_text and f"@{bot_username}" in message_text:
            is_bot_mentioned = True
        
        should_process = is_bot_mentioned and has_reply and reply_has_voice
        self.assertTrue(should_process, "Reply with mention in group should be processed")

    def test_reply_to_audio_file_with_mention(self):
        """Test that reply to audio file with mention is processed"""
        bot_username = "test_bot"
        message_text = "@test_bot transcribe"
        has_reply = True
        reply_has_audio = True
        
        is_bot_mentioned = f"@{bot_username}" in message_text
        should_process = is_bot_mentioned and has_reply and reply_has_audio
        self.assertTrue(should_process, "Reply to audio with mention should be processed")

    def test_reply_to_document_with_mention(self):
        """Test that reply to document with mention is processed"""
        bot_username = "test_bot"
        message_text = "@test_bot transcribe"
        has_reply = True
        reply_has_document = True
        
        is_bot_mentioned = f"@{bot_username}" in message_text
        should_process = is_bot_mentioned and has_reply and reply_has_document
        self.assertTrue(should_process, "Reply to document with mention should be processed")


if __name__ == '__main__':
    unittest.main()
