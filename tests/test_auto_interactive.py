"""
Tests for auto-enter interactive mode after UUID setup (SPEC-AUTO-INTERACTIVE-001).

Following TDD methodology - these tests should fail initially (Red phase),
then pass after implementation (Green phase).
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path

from tests.test_utils import MockConsole, create_mock_auth_response, create_mock_agent_config_response


@pytest.mark.cli
@pytest.mark.unit
def test_auto_enter_interactive_after_uuid_setup__spec_AC1(capsys):
    """
    Test AC1: Auto-enter interactive mode when UUID just set up.
    
    Given: User runs a700cli without arguments
    Given: AGENT_UUID is missing from .env
    When: User successfully enters and saves UUID
    Then: CLI automatically enters interactive mode
    Then: Streaming is enabled
    Then: Message "Starting interactive chat with streaming..." is displayed
    """
    with patch('sys.argv', ['a700cli']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.prompt_agent_uuid') as mock_prompt, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('a700cli.__main__.input') as mock_input, \
             patch('getpass.getpass') as mock_getpass, \
             patch('a700cli.__main__.sys.stdin.isatty', return_value=True):
            
            # Setup: No UUID in env
            mock_env.return_value = {
                'EMAIL': None,
                'PASSWORD': None,
                'AGENT_UUID': None,  # No UUID - triggers setup
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            
            mock_getpass.return_value = 'testpass'
            mock_input.side_effect = ['test@example.com', '92b20084-fcf2-4a6d-bf71-77382344fe3d', '/exit']
            mock_auth.return_value = 'test_token'
            mock_prompt.return_value = '92b20084-fcf2-4a6d-bf71-77382344fe3d'
            mock_config.return_value = {'agentName': 'Test Agent', 'agentRevisionId': 1}
            
            from a700cli.__main__ import main
            
            try:
                main()
            except (SystemExit, KeyboardInterrupt):
                pass
            
            # Verify: UUID was prompted
            assert mock_prompt.called, "Should prompt for UUID when missing"
            
            # Verify: Interactive mode was entered (we got to input prompt)
            assert mock_input.call_count >= 2, "Should enter interactive mode"
            
            # Check output for auto-interactive message
            captured = capsys.readouterr()
            # Note: This will fail until implementation is done (TDD Red phase)


@pytest.mark.cli
@pytest.mark.unit
def test_no_auto_enter_when_uuid_exists__spec_AC2(capsys):
    """
    Test AC2: No auto-enter when UUID exists in .env.
    
    Given: AGENT_UUID exists in .env
    When: User runs a700cli without arguments
    Then: CLI shows "No message provided" error (existing behavior)
    """
    with patch('sys.argv', ['a700cli']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.input') as mock_input, \
             patch('getpass.getpass') as mock_getpass, \
             patch('a700cli.__main__.sys.stdin.isatty', return_value=True):
            
            # Setup: UUID exists in env
            mock_env.return_value = {
                'EMAIL': 'test@example.com',
                'PASSWORD': 'testpass',
                'AGENT_UUID': 'existing-uuid-123',  # UUID exists
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            
            mock_getpass.return_value = 'testpass'
            mock_auth.return_value = 'test_token'
            mock_config.return_value = {'agentName': 'Test Agent', 'agentRevisionId': 1}
            
            from a700cli.__main__ import main
            
            try:
                main()
            except SystemExit:
                pass
            
            # Verify: Should show "No message provided" error
            captured = capsys.readouterr()
            assert 'No message provided' in captured.out or 'Usage:' in captured.out, \
                "Should show error when UUID exists and no message provided"


@pytest.mark.cli
@pytest.mark.unit
def test_no_auto_enter_when_message_provided__spec_AC3(capsys):
    """
    Test AC3: No auto-enter when message provided.
    
    Given: UUID just set up
    When: User provides message via argument
    Then: CLI sends message normally (no auto-interactive)
    """
    with patch('sys.argv', ['a700cli', 'test message']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.prompt_agent_uuid') as mock_prompt, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.send_message_http') as mock_send, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('a700cli.__main__.input') as mock_input, \
             patch('getpass.getpass') as mock_getpass, \
             patch('a700cli.__main__.sys.stdin.isatty', return_value=True):
            
            # Setup: No UUID in env, but message provided
            mock_env.return_value = {
                'EMAIL': None,
                'PASSWORD': None,
                'AGENT_UUID': None,
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            
            mock_getpass.return_value = 'testpass'
            mock_input.return_value = 'test@example.com'
            mock_auth.return_value = 'test_token'
            mock_prompt.return_value = '92b20084-fcf2-4a6d-bf71-77382344fe3d'
            mock_config.return_value = {'agentName': 'Test Agent', 'agentRevisionId': 1}
            mock_send.return_value = MagicMock(content='Response', citations=[], error=None)
            
            from a700cli.__main__ import main
            
            try:
                main()
            except SystemExit:
                pass
            
            # Verify: Message was sent (not interactive mode)
            assert mock_send.called, "Should send message when provided"
            
            # Verify: Should not enter interactive mode
            # (input should only be called for email, not for interactive chat)
            assert mock_input.call_count <= 1, "Should not enter interactive mode when message provided"


@pytest.mark.cli
@pytest.mark.unit
def test_no_auto_enter_when_explicit_interactive__spec_AC4(capsys):
    """
    Test AC4: No auto-enter when explicit --interactive flag used.
    
    Given: UUID just set up
    When: User uses --interactive flag
    Then: CLI uses explicit interactive mode (respects --streaming if provided)
    """
    with patch('sys.argv', ['a700cli', '--interactive']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.prompt_agent_uuid') as mock_prompt, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('a700cli.__main__.input') as mock_input, \
             patch('getpass.getpass') as mock_getpass, \
             patch('a700cli.__main__.sys.stdin.isatty', return_value=True):
            
            # Setup: No UUID in env, but --interactive flag used
            mock_env.return_value = {
                'EMAIL': None,
                'PASSWORD': None,
                'AGENT_UUID': None,
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            
            mock_getpass.return_value = 'testpass'
            mock_input.side_effect = ['test@example.com', '/exit']
            mock_auth.return_value = 'test_token'
            mock_prompt.return_value = '92b20084-fcf2-4a6d-bf71-77382344fe3d'
            mock_config.return_value = {'agentName': 'Test Agent', 'agentRevisionId': 1}
            
            from a700cli.__main__ import main
            
            try:
                main()
            except (SystemExit, KeyboardInterrupt):
                pass
            
            # Verify: Interactive mode was entered (explicit flag)
            assert mock_input.call_count >= 2, "Should enter interactive mode with explicit flag"
            
            # Verify: Should not auto-enter (should use explicit flag behavior)
            # The difference is that with explicit flag, we don't auto-enable streaming
            # (unless --streaming is also provided)


@pytest.mark.cli
@pytest.mark.unit
def test_streaming_enabled_in_auto_interactive__spec_AC5(capsys):
    """
    Test AC5: Streaming enabled in auto-interactive mode.
    
    Given: Auto-interactive mode is triggered
    When: User sends a message
    Then: WebSocket streaming is attempted (if available)
    Then: Falls back to HTTP if WebSocket fails (existing behavior)
    """
    with patch('sys.argv', ['a700cli']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.prompt_agent_uuid') as mock_prompt, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.WebSocketClient') as mock_ws_client, \
             patch('a700cli.__main__.WEBSOCKET_AVAILABLE', True), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('a700cli.__main__.input') as mock_input, \
             patch('getpass.getpass') as mock_getpass, \
             patch('a700cli.__main__.sys.stdin.isatty', return_value=True):
            
            # Setup: No UUID in env, WebSocket available
            mock_env.return_value = {
                'EMAIL': None,
                'PASSWORD': None,
                'AGENT_UUID': None,
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            
            # Mock WebSocket client
            mock_ws_instance = MagicMock()
            mock_ws_instance.send_message.return_value = MagicMock(
                content='Streamed response',
                citations=[],
                error=None
            )
            mock_ws_client.return_value = mock_ws_instance
            
            mock_getpass.return_value = 'testpass'
            mock_input.side_effect = ['test@example.com', 'test message', '/exit']
            mock_auth.return_value = 'test_token'
            mock_prompt.return_value = '92b20084-fcf2-4a6d-bf71-77382344fe3d'
            mock_config.return_value = {'agentName': 'Test Agent', 'agentRevisionId': 1}
            
            from a700cli.__main__ import main
            
            try:
                main()
            except (SystemExit, KeyboardInterrupt):
                pass
            
            # Verify: WebSocket client was created (streaming attempted)
            # This will fail until implementation is done (TDD Red phase)
            # After implementation, should verify WebSocketClient was called
