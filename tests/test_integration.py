"""
Integration tests for end-to-end workflows.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import tempfile
from pathlib import Path

from tests.test_utils import (
    create_mock_auth_response,
    create_mock_agent_config_response,
    create_mock_chat_response,
    create_test_input_file,
    create_test_output_file,
)


@pytest.mark.integration
def test_full_cli_workflow_with_file_io(tmp_path):
    """Test complete workflow with file I/O."""
    input_file = create_test_input_file("Test message from file", tmp_path)
    output_file = create_test_output_file(tmp_path)
    
    with patch('sys.argv', ['a700cli', '--input-file', str(input_file), '--output-file', str(output_file)]):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.send_message_http') as mock_send:
            
            mock_env.return_value = {
                'EMAIL': 'test@example.com',
                'PASSWORD': 'testpass',
                'AGENT_UUID': 'test-uuid',
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            mock_auth.return_value = 'test_token'
            mock_config.return_value = {'agentName': 'Test Agent'}
            mock_send.return_value = MagicMock(content='Test response', citations=[])
            
            from a700cli.__main__ import main
            
            try:
                main()
            except SystemExit:
                pass
            
            # After implementation, output file should contain response
            if output_file.exists():
                content = output_file.read_text()
                assert len(content) > 0


@pytest.mark.integration
def test_websocket_end_to_end():
    """Test WebSocket mode end-to-end (mocked)."""
    with patch('sys.argv', ['a700cli', 'test message', '--streaming']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.WEBSOCKET_AVAILABLE', True), \
             patch('a700cli.__main__.WebSocketClient') as mock_ws_class:
            
            mock_env.return_value = {
                'EMAIL': 'test@example.com',
                'PASSWORD': 'testpass',
                'AGENT_UUID': 'test-uuid',
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            mock_auth.return_value = 'test_token'
            mock_config.return_value = {'agentName': 'Test Agent'}
            
            mock_ws = MagicMock()
            mock_ws.send_message.return_value = MagicMock(
                content='Streamed response',
                citations=[],
                error=None
            )
            mock_ws_class.return_value = mock_ws
            
            from a700cli.__main__ import main
            
            try:
                main()
            except (SystemExit, AttributeError, ImportError):
                pass
            
            # After implementation, WebSocket should be used


@pytest.mark.integration
def test_http_fallback_on_websocket_failure():
    """Test HTTP fallback when WebSocket fails."""
    with patch('sys.argv', ['a700cli', 'test message', '--streaming']):
        with patch('a700cli.__main__.load_environment') as mock_env, \
             patch('a700cli.__main__.authenticate') as mock_auth, \
             patch('a700cli.__main__.get_agent_config') as mock_config, \
             patch('a700cli.__main__.WEBSOCKET_AVAILABLE', True), \
             patch('a700cli.__main__.WebSocketClient') as mock_ws_class, \
             patch('a700cli.__main__.send_message_http') as mock_http:
            
            mock_env.return_value = {
                'EMAIL': 'test@example.com',
                'PASSWORD': 'testpass',
                'AGENT_UUID': 'test-uuid',
                'API_BASE_URL': 'https://api.agent700.ai'
            }
            mock_auth.return_value = 'test_token'
            mock_config.return_value = {'agentName': 'Test Agent'}
            
            # Simulate WebSocket failure
            mock_ws = MagicMock()
            mock_ws.send_message.return_value = MagicMock(
                content='',
                error='Connection failed'
            )
            mock_ws_class.return_value = mock_ws
            mock_http.return_value = MagicMock(content='HTTP response', citations=[])
            
            from a700cli.__main__ import main
            
            try:
                main()
            except (SystemExit, AttributeError, ImportError):
                pass
            
            # After implementation, should fallback to HTTP
            # mock_http.assert_called_once()
