#!/usr/bin/env python3
"""
Enhanced Agent700 API Command-Line Interface

A sophisticated CLI tool for interacting with Agent700 agents with rich visual output,
enhanced MCP support, and workflow integration features.

Usage:
    python enhanced_run_agent.py "Your message here" [OPTIONS]

Requirements:
    - Create a .env file with your credentials (see .env.example)
    - Install dependencies: pip install -r requirements.txt
"""

import os
import sys
import json
import textwrap
import threading
import time
import logging
import re
import uuid
from datetime import datetime
import requests
from dotenv import load_dotenv
import platform
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin
import hashlib
from pathlib import Path
import pickle
import base64
from datetime import timedelta
import signal
import readline

# Enhanced console output support
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    Console = None
    RICH_AVAILABLE = False

# WebSocket support
try:
    import socketio
    WEBSOCKET_AVAILABLE = True
except ImportError:
    socketio = None
    WEBSOCKET_AVAILABLE = False


@dataclass
class ChatMessage:
    """Individual chat message structure matching frontend."""
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    type: str = 'message'  # 'message', 'error', 'loading', etc.
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ChatResponse:
    """Structured response data from Agent700 API."""
    content: str = ""
    citations: List[str] = None
    mcp_results: List[Dict] = None
    finish_reason: str = None
    usage: Dict = None
    error: str = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.mcp_results is None:
            self.mcp_results = []


class EnhancedColors:
    """Enhanced color codes and styling for better visual output."""
    # Standard colors
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    # Status indicators
    SUCCESS = f'{GREEN}✓{RESET}'
    ERROR = f'{RED}✗{RESET}'
    WARNING = f'{YELLOW}⚠{RESET}'
    INFO = f'{CYAN}ℹ{RESET}'
    LOADING = f'{BLUE}⟳{RESET}'
    MCP = f'{MAGENTA}🔧{RESET}'
    
    @classmethod
    def supports_color(cls) -> bool:
        """Check if terminal supports color output."""
        return (
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
            os.getenv('TERM', '').lower() not in ('dumb', '') and
            platform.system() != 'Windows' or os.getenv('ANSICON')
        )


class RichConsoleManager:
    """Manages rich console output with fallbacks."""
    
    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()
        else:
            self.console = None
            self.colors = EnhancedColors()
    
    def print(self, text: str, style: str = None, **kwargs):
        """Print with rich formatting or fallback to colored text."""
        if self.use_rich and self.console:
            self.console.print(text, style=style, **kwargs)
        else:
            # Fallback to colored console output
            if style:
                color_map = {
                    'green': self.colors.GREEN,
                    'red': self.colors.RED,
                    'yellow': self.colors.YELLOW,
                    'blue': self.colors.BLUE,
                    'cyan': self.colors.CYAN,
                    'bold': self.colors.BOLD,
                    'dim': self.colors.DIM
                }
                color = color_map.get(style, '')
                print(f"{color}{text}{self.colors.RESET}")
            else:
                print(text)
    
    def print_panel(self, content: str, title: str = None, style: str = "blue"):
        """Print content in a panel with fallback."""
        if self.use_rich and self.console:
            panel = Panel(content, title=title, border_style=style)
            self.console.print(panel)
        else:
            # Fallback panel rendering
            border = "=" * 60
            if title:
                print(f"{self.colors.BLUE}{border}{self.colors.RESET}")
                print(f"{self.colors.BOLD}{title}{self.colors.RESET}")
                print(f"{self.colors.BLUE}{border}{self.colors.RESET}")
            print(content)
            if title:
                print(f"{self.colors.BLUE}{border}{self.colors.RESET}")
    
    def print_table(self, data: List[Dict], title: str = None):
        """Print data as a formatted table."""
        if not data:
            return
        
        if self.use_rich and self.console:
            table = Table(title=title, show_header=True, header_style="bold magenta")
            
            # Add columns
            headers = list(data[0].keys())
            for header in headers:
                table.add_column(header.replace('_', ' ').title(), style="cyan")
            
            # Add rows
            for row in data[:10]:  # Limit to first 10 rows
                values = [str(row.get(col, '')) for col in headers]
                table.add_row(*values)
            
            self.console.print(table)
            
            if len(data) > 10:
                self.console.print(f"[dim]... and {len(data) - 10} more rows[/dim]")
        else:
            # Fallback table rendering
            if title:
                print(f"\n{self.colors.BOLD}{title}{self.colors.RESET}")
            
            if data:
                headers = list(data[0].keys())
                # Print headers
                header_row = " | ".join(h.replace('_', ' ').title() for h in headers)
                print(f"{self.colors.CYAN}{header_row}{self.colors.RESET}")
                print("-" * len(header_row))
                
                # Print data rows (limit to 10)
                for row in data[:10]:
                    values = [str(row.get(col, ''))[:20] for col in headers]  # Limit column width
                    print(" | ".join(values))
                
                if len(data) > 10:
                    print(f"{self.colors.DIM}... and {len(data) - 10} more rows{self.colors.RESET}")


@dataclass
class SessionData:
    """Session data structure for persistent authentication."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None
    user_email: str = ""
    organization: str = ""
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """Check if the session is expired."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expiry
        except:
            return True
    
    def is_near_expiry(self, minutes: int = 5) -> bool:
        """Check if session expires within specified minutes."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            near_expiry = expiry - timedelta(minutes=minutes)
            return datetime.now() > near_expiry
        except:
            return True


class SessionManager:
    """Enhanced session management with token persistence and automatic refresh."""
    
    def __init__(self, email: str, console: RichConsoleManager, logger: logging.Logger):
        self.email = email
        self.console = console
        self.logger = logger
        self.session_file = Path(f".agent700_session_{self._hash_email(email)}.dat")
        self.session_timeout_hours = 24  # Default session timeout
    
    def _hash_email(self, email: str) -> str:
        """Create a short hash of email for filename."""
        return hashlib.md5(email.encode()).hexdigest()[:12]
    
    def _encrypt_session_data(self, data: SessionData) -> str:
        """Simple obfuscation of session data (not cryptographically secure)."""
        try:
            # Convert to JSON and encode
            json_data = json.dumps({
                'access_token': data.access_token,
                'refresh_token': data.refresh_token,
                'expires_at': data.expires_at,
                'user_email': data.user_email,
                'organization': data.organization,
                'created_at': data.created_at
            })
            
            # Simple base64 encoding (not secure, just obfuscation)
            encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
            return encoded_data
        except Exception as e:
            self.logger.error(f"Failed to encode session data: {e}")
            return ""
    
    def _decrypt_session_data(self, encrypted_data: str) -> Optional[SessionData]:
        """Decode session data."""
        try:
            # Decode from base64
            json_data = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
            data = json.loads(json_data)
            
            return SessionData(
                access_token=data.get('access_token', ''),
                refresh_token=data.get('refresh_token'),
                expires_at=data.get('expires_at'),
                user_email=data.get('user_email', ''),
                organization=data.get('organization', ''),
                created_at=data.get('created_at')
            )
        except Exception as e:
            self.logger.error(f"Failed to decode session data: {e}")
            return None
    
    def save_session(self, session_data: SessionData) -> bool:
        """Save session data securely."""
        try:
            encrypted_data = self._encrypt_session_data(session_data)
            if encrypted_data:
                with open(self.session_file, 'w') as f:
                    f.write(encrypted_data)
                return True
        except Exception as e:
            self.console.print(f"Warning: Could not save session: {e}", style="yellow")
        return False
    
    def load_session(self) -> Optional[SessionData]:
        """Load existing session data."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    encrypted_data = f.read().strip()
                    return self._decrypt_session_data(encrypted_data)
        except Exception as e:
            self.logger.debug(f"Could not load session: {e}")
        return None
    
    def clear_session(self):
        """Clear stored session."""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            self.console.print("✓ Session cleared", style="green")
        except Exception as e:
            self.console.print(f"Warning: Could not clear session: {e}", style="yellow")
    
    def get_valid_token(self, password: str, api_base_url: str, force_refresh: bool = False) -> str:
        """Get a valid access token, refreshing if necessary."""
        
        # Try to load existing session
        session = self.load_session()
        
        if session and not force_refresh:
            # Check if token is still valid
            if not session.is_expired():
                if session.is_near_expiry():
                    self.console.print("🔄 Token expires soon, refreshing...", style="yellow")
                    # Try to refresh token
                    refreshed_token = self._refresh_token(session, api_base_url)
                    if refreshed_token:
                        return refreshed_token
                    else:
                        self.console.print("⚠ Token refresh failed, re-authenticating...", style="yellow")
                else:
                    self.console.print("✓ Using cached session", style="green")
                    return session.access_token
            else:
                self.console.print("⚠ Session expired, re-authenticating...", style="yellow")
        
        # Authenticate fresh
        return self._authenticate_fresh(password, api_base_url)
    
    def _refresh_token(self, session: SessionData, api_base_url: str) -> Optional[str]:
        """Attempt to refresh the access token."""
        if not session.refresh_token:
            return None
        
        # Ensure proper API URL format
        if not api_base_url.endswith('/api'):
            if api_base_url.endswith('/'):
                api_base_url = api_base_url + 'api'
            else:
                api_base_url = api_base_url + '/api'
        
        refresh_url = f"{api_base_url}/auth/refresh"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session.refresh_token}',
            **get_enhanced_device_fingerprint()
        }
        
        try:
            response = requests.post(refresh_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('accessToken')
                
                if new_token:
                    # Update session with new token
                    session.access_token = new_token
                    if data.get('refreshToken'):
                        session.refresh_token = data.get('refreshToken')
                    
                    # Calculate new expiry (assume 1 hour if not provided)
                    if data.get('expiresIn'):
                        expiry_seconds = data.get('expiresIn')
                        session.expires_at = (datetime.now() + timedelta(seconds=expiry_seconds)).isoformat()
                    else:
                        session.expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
                    
                    # Save refreshed session
                    self.save_session(session)
                    return new_token
            
        except Exception as e:
            self.logger.debug(f"Token refresh failed: {e}")
        
        return None
    
    def _authenticate_fresh(self, password: str, api_base_url: str) -> str:
        """Perform fresh authentication and save session."""
        
        # Ensure proper API URL format
        if not api_base_url.endswith('/api'):
            if api_base_url.endswith('/'):
                api_base_url = api_base_url + 'api'
            else:
                api_base_url = api_base_url + '/api'
        
        login_url = f"{api_base_url}/auth/login"
        
        login_data = {
            "email": self.email,
            "password": password
        }
        
        headers = {
            'Content-Type': 'application/json',
            **get_enhanced_device_fingerprint()
        }
        
        try:
            self.console.print("🔐 Authenticating with Agent700...", style="blue")
            
            response = requests.post(login_url, json=login_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('accessToken')
                
                if access_token:
                    self.console.print("✅ Authentication successful!", style="green bold")
                    
                    # Create session data
                    session = SessionData(
                        access_token=access_token,
                        refresh_token=data.get('refreshToken'),
                        user_email=data.get('email', self.email),
                        organization=data.get('defaultOrganization', {}).get('name', '')
                    )
                    
                    # Calculate expiry (assume 1 hour if not provided)
                    if data.get('expiresIn'):
                        expiry_seconds = data.get('expiresIn')
                        session.expires_at = (datetime.now() + timedelta(seconds=expiry_seconds)).isoformat()
                    else:
                        session.expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
                    
                    # Save session
                    self.save_session(session)
                    
                    # Display login info
                    if session.user_email:
                        self.console.print(f"   📧 Logged in as: {session.user_email}", style="dim")
                    if session.organization:
                        self.console.print(f"   🏢 Organization: {session.organization}", style="dim")
                    
                    return access_token
                else:
                    self.logger.error("No access token in response")
                    self.console.print("❌ No access token received from server", style="red")
                    sys.exit(1)
            else:
                format_enhanced_error("auth_failed", response.status_code, response.text, console=self.console)
                sys.exit(1)
                
        except requests.exceptions.RequestException as e:
            format_enhanced_error("network_auth", exception=e, console=self.console)
            sys.exit(1)
    
    def get_session_info(self) -> str:
        """Get session information for display."""
        session = self.load_session()
        if not session:
            return "No active session"
        
        try:
            created = datetime.fromisoformat(session.created_at)
            age = datetime.now() - created
            
            status = "Active"
            if session.is_expired():
                status = "Expired"
            elif session.is_near_expiry():
                status = "Expires soon"
            
            return f"Session: {status} | Age: {age.days}d {age.seconds//3600}h | User: {session.user_email}"
        except:
            return "Session: Unknown status"


class ConversationManager:
    """Manages conversation history and context like the frontend."""
    
    def __init__(self, agent_uuid: str, console: RichConsoleManager):
        self.agent_uuid = agent_uuid
        self.console = console
        self.history_file = Path(f".agent700_conversation_{self._hash_agent_id(agent_uuid)}.json")
        self.max_characters = 300000  # Match frontend 300K character limit
    
    def _hash_agent_id(self, agent_id: str) -> str:
        """Create a short hash of agent ID for filename."""
        return hashlib.md5(agent_id.encode()).hexdigest()[:8]
    
    def load_conversation_history(self) -> List[ChatMessage]:
        """Load conversation history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = []
                    for msg_data in data.get('messages', []):
                        messages.append(ChatMessage(**msg_data))
                    return messages
            return []
        except Exception as e:
            self.console.print(f"Warning: Could not load conversation history: {e}", style="yellow")
            return []
    
    def save_conversation_history(self, messages: List[ChatMessage]):
        """Save conversation history to file."""
        try:
            data = {
                'agent_uuid': self.agent_uuid,
                'last_updated': datetime.now().isoformat(),
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'content': msg.content,
                        'type': msg.type,
                        'timestamp': msg.timestamp
                    }
                    for msg in messages
                ]
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"Warning: Could not save conversation history: {e}", style="yellow")
    
    def add_message(self, role: str, content: str, msg_type: str = 'message') -> ChatMessage:
        """Add a new message to conversation history."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            type=msg_type
        )
        
        # Load existing history, add new message, save
        history = self.load_conversation_history()
        history.append(message)
        self.save_conversation_history(history)
        
        return message
    
    def clear_history(self):
        """Clear conversation history."""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            self.console.print("✓ Conversation history cleared", style="green")
        except Exception as e:
            self.console.print(f"Warning: Could not clear history: {e}", style="yellow")
    
    def get_context_info(self) -> str:
        """Get conversation context information."""
        history = self.load_conversation_history()
        if not history:
            return "No conversation history"
        
        total_chars = sum(len(msg.content) for msg in history)
        user_msgs = len([m for m in history if m.role == 'user'])
        assistant_msgs = len([m for m in history if m.role == 'assistant'])
        
        return f"Messages: {len(history)} (👤{user_msgs} 🤖{assistant_msgs}) | Characters: {total_chars:,}"
    
    def build_full_chat_history(self, new_message: str, agent_config: Dict) -> List[Dict]:
        """Build full chat history matching frontend logic."""
        # Load existing conversation
        history = self.load_conversation_history()
        
        # Add system prompt if available (matching frontend)
        messages = []
        if agent_config.get('masterPrompt'):
            messages.append({
                'role': 'system',
                'content': agent_config['masterPrompt']
            })
        
        # Convert history to API format and apply character limit
        total_chars = 0
        limited_history = []
        
        # Process messages from newest to oldest to stay within character limit
        for message in reversed(history):
            msg_content = message.content
            msg_length = len(msg_content)
            
            if total_chars + msg_length < self.max_characters:
                limited_history.insert(0, {
                    'role': message.role,
                    'content': msg_content
                })
                total_chars += msg_length
            else:
                break
        
        # Add limited history to messages
        messages.extend(limited_history)
        
        # Add new user message
        messages.append({
            'role': 'user',
            'content': new_message
        })
        
        # Ensure first message is system if no system prompt was added
        if messages and messages[0]['role'] != 'system':
            messages.insert(0, {'role': 'system', 'content': ''})
        
        return messages


def setup_enhanced_logging(verbose: bool = False) -> logging.Logger:
    """Setup enhanced logging with structured output."""
    log_level = logging.DEBUG if verbose else logging.WARNING
    
    logger = logging.getLogger('agent700_enhanced')
    logger.setLevel(log_level)
    logger.handlers.clear()
    
    # Console handler with custom formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_enhanced_device_fingerprint() -> Dict[str, str]:
    """Get enhanced device fingerprinting information."""
    try:
        import datetime
        now = datetime.datetime.now()
        utc_offset = now.astimezone().utcoffset()
        timezone_offset = int(utc_offset.total_seconds() / 60) if utc_offset else 0
        
        fingerprint = {
            'X-Screen-Resolution': '1920x1080',
            'X-Timezone-Offset': str(timezone_offset),
            'X-User-Agent': f'Agent700-CLI/2.0 ({platform.system()} {platform.release()})',
            'X-Client-Type': 'enhanced-cli'
        }
        
        return fingerprint
    except Exception:
        return {
            'X-Screen-Resolution': '1920x1080',
            'X-Timezone-Offset': '0',
            'X-User-Agent': 'Agent700-CLI/2.0',
            'X-Client-Type': 'enhanced-cli'
        }


def get_user_input_safe(prompt: str, hide_input: bool = False) -> str:
    """Get user input with proper handling for interactive mode."""
    try:
        if hide_input:
            import getpass
            return getpass.getpass(prompt).strip()
        else:
            return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n🛑 Exiting...")
        sys.exit(0)

def load_enhanced_configuration() -> Tuple[str, str, str, str]:
    """Load and validate configuration with interactive prompts for missing values."""
    load_dotenv()
    
    config = {
        'EMAIL': os.getenv('EMAIL'),
        'PASSWORD': os.getenv('PASSWORD'),
        'AGENT_UUID': os.getenv('AGENT_UUID'),
        'API_BASE_URL': os.getenv('API_BASE_URL', 'https://api.agent700.ai')
    }
    
    console = RichConsoleManager()
    
    # Check if we need to prompt for credentials
    missing_vars = [k for k, v in config.items() if not v]
    
    if missing_vars:
        console.print("🔐 Agent700 Authentication Setup", style="blue bold")
        console.print("Some configuration is missing. Let's set it up interactively.", style="yellow")
        print()
        
        # Prompt for missing credentials
        if not config['EMAIL']:
            config['EMAIL'] = get_user_input_safe("📧 Email: ")
            if not config['EMAIL']:
                console.print("❌ Email is required", style="red")
        sys.exit(1)
    
        if not config['PASSWORD']:
            config['PASSWORD'] = get_user_input_safe("🔒 Password: ", hide_input=True)
            if not config['PASSWORD']:
                console.print("❌ Password is required", style="red")
                sys.exit(1)
        
        if not config['AGENT_UUID']:
            # We'll get the agent UUID after authentication
            config['AGENT_UUID'] = None
    
    return config['EMAIL'], config['PASSWORD'], config['AGENT_UUID'], config['API_BASE_URL']

def get_agent_uuid_interactive(access_token: str, api_base_url: str, console: RichConsoleManager) -> str:
    """Get agent UUID interactively after authentication."""
    
    # First, try to get a list of available agents
    try:
        agents_url = f"{api_base_url}/agents"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(agents_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data.get('agents', []) or agents_data.get('data', [])
            
            if agents:
                console.print("🤖 Available Agents:", style="green bold")
        print()
                
                for i, agent in enumerate(agents, 1):
                    name = agent.get('name', 'Unnamed Agent')
                    uuid = agent.get('id') or agent.get('uuid')
                    description = agent.get('description', 'No description')
                    
                    console.print(f"{i}. {name}", style="cyan bold")
                    console.print(f"   ID: {uuid}", style="dim")
                    console.print(f"   Description: {description}", style="dim")
        print()
                
                # Prompt for selection
                while True:
                    try:
                        choice = get_user_input_safe("Select agent (number) or enter UUID: ")
                        
                        if not choice:
                            console.print("❌ Agent selection is required", style="red")
                            continue
                        
                        # Check if it's a number (selection from list)
                        if choice.isdigit():
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(agents):
                                selected_agent = agents[choice_num - 1]
                                agent_uuid = selected_agent.get('id') or selected_agent.get('uuid')
                                console.print(f"✅ Selected: {selected_agent.get('name', 'Unnamed Agent')}", style="green")
                                return agent_uuid
        else:
                                console.print(f"❌ Please enter a number between 1 and {len(agents)}", style="red")
                                continue
                        else:
                            # Assume it's a UUID
                            console.print(f"✅ Using provided UUID: {choice}", style="green")
                            return choice
                            
                    except ValueError:
                        console.print("❌ Please enter a valid number or UUID", style="red")
                        continue
            else:
                console.print("⚠️ No agents found in your account", style="yellow")
        else:
            console.print("⚠️ Could not fetch agent list, you'll need to provide the UUID manually", style="yellow")
    
    except Exception as e:
        console.print(f"⚠️ Could not fetch agent list: {e}", style="yellow")
    
    # Fallback: prompt for UUID directly
    console.print("Please provide the Agent UUID manually:", style="blue")
    while True:
        agent_uuid = get_user_input_safe("🤖 Agent UUID: ")
        if agent_uuid:
            return agent_uuid
        console.print("❌ Agent UUID is required", style="red")

def save_config_to_env(email: str, password: str, agent_uuid: str, api_base_url: str):
    """Save configuration to .env file for future use."""
    env_content = f"""# Agent700 CLI Configuration
EMAIL={email}
PASSWORD={password}
AGENT_UUID={agent_uuid}
API_BASE_URL={api_base_url}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        return True
    except Exception:
        return False


def format_enhanced_error(error_type: str, status_code: int = None, 
                         response_text: str = None, exception: Exception = None, 
                         console: RichConsoleManager = None) -> None:
    """Format enhanced error messages with better UX."""
    
    if not console:
        console = RichConsoleManager()
    
    error_messages = {
        "auth_failed": {
            "title": "🔐 Authentication Failed",
            "401": "Invalid email or password. Please check your credentials.",
            "429": "Too many login attempts. Please wait before trying again.",
            "default": f"Authentication failed (Status: {status_code})"
        },
        "network_auth": {
            "title": "🌐 Network Error During Authentication",
            "message": f"Could not connect to Agent700 servers: {exception}",
            "tips": [
                "Check your internet connection",
                "Verify the API_BASE_URL in your .env file",
                "Try again in a few moments"
            ]
        },
        "chat_failed": {
            "title": "💬 Message Processing Failed",
            "402": "Payment required. Your account may have insufficient credits.",
            "403": "Access denied. You may not have permission to use this agent.",
            "404": "Agent not found. Please verify your AGENT_UUID.",
            "429": "Rate limit exceeded. Please wait before sending another message.",
            "default": f"Chat request failed (Status: {status_code})"
        },
        "network_chat": {
            "title": "🌐 Network Error During Chat",
            "message": f"Could not send message to agent: {exception}",
            "tips": [
                "Check network connectivity",
                "Server may be experiencing high load",
                "Try again in a moment"
            ]
        }
    }
    
    error_info = error_messages.get(error_type, {"title": "❌ Unknown Error"})
    
    console.print(error_info["title"], style="red bold")
    
    if status_code and str(status_code) in error_info:
        console.print(error_info[str(status_code)], style="yellow")
    elif "message" in error_info:
        console.print(error_info["message"], style="yellow")
    elif "default" in error_info:
        console.print(error_info["default"], style="yellow")
    
    if "tips" in error_info:
        console.print("\n💡 Troubleshooting tips:", style="cyan bold")
        for tip in error_info["tips"]:
            console.print(f"  • {tip}", style="dim")
    
    if response_text and len(response_text) < 500:
        console.print(f"\nServer response: {response_text}", style="dim")


def get_enhanced_agent_config(access_token: str, agent_uuid: str, api_base_url: str, 
                             console: RichConsoleManager, logger: logging.Logger) -> Dict:
    """Fetch agent configuration with enhanced error handling."""
    
    # Ensure proper API URL format
    if not api_base_url.endswith('/api'):
        if api_base_url.endswith('/'):
            api_base_url = api_base_url + 'api'
        else:
            api_base_url = api_base_url + '/api'
    
    agent_url = f"{api_base_url}/agents/{agent_uuid}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        **get_enhanced_device_fingerprint()
    }
    
    try:
        console.print("🔍 Fetching agent configuration...", style="blue")
        response = requests.get(agent_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            agent_data = response.json()
            revisions = agent_data.get('revisions', [])
            
            if revisions:
                latest_revision = max(revisions, key=lambda x: x.get('id', 0))
                
                config = {
                    'agentRevisionId': latest_revision.get('id'),
                    'enableMcp': latest_revision.get('enableMcp', False),
                    'mcpServerNames': latest_revision.get('mcpServerNames', []),
                    'model': latest_revision.get('model', 'gpt-4o'),
                    'temperature': latest_revision.get('temperature', 0.7),
                    'maxTokens': latest_revision.get('maxTokens', 4000),
                    'agentName': latest_revision.get('name', 'Unknown Agent'),
                    'masterPrompt': latest_revision.get('masterPrompt', ''),  # Add master prompt like frontend
                    'imageDimensions': latest_revision.get('imageDimensions', '1024x1024'),
                    'topP': latest_revision.get('topP', 1.0),
                    'scrubPii': latest_revision.get('scrubPii', False),
                    'piiThreshold': latest_revision.get('piiThreshold', 0.5)
                }
                
                # Display agent info
                console.print(f"✓ Agent: {config['agentName']}", style="green")
                console.print(f"✓ Model: {config['model']}", style="green")
                if config['enableMcp'] and config['mcpServerNames']:
                    console.print(f"✓ MCP Tools: {', '.join(config['mcpServerNames'])}", style="green")
                else:
                    console.print("⚠ MCP Tools: Disabled", style="yellow")
                
                return config
            else:
                logger.error("No revisions found in agent data")
        else:
            logger.error(f"Failed to fetch agent config: {response.status_code}")
            format_enhanced_error("chat_failed", response.status_code, response.text, console=console)
            
    except Exception as e:
        logger.error(f"Exception while fetching agent config: {e}")
        format_enhanced_error("network_chat", exception=e, console=console)
    
    # Fallback configuration
    return {
        'agentRevisionId': None,
        'enableMcp': False,
        'mcpServerNames': [],
        'model': 'gpt-4o',
        'temperature': 0.7,
        'maxTokens': 4000,
        'agentName': 'Unknown Agent',
        'masterPrompt': '',
        'imageDimensions': '1024x1024',
        'topP': 1.0,
        'scrubPii': False,
        'piiThreshold': 0.5
    }


def enhanced_authenticate(email: str, password: str, api_base_url: str, 
                         console: RichConsoleManager, logger: logging.Logger) -> str:
    """Enhanced authentication with better UX."""
    
    # Ensure proper API URL format
    if not api_base_url.endswith('/api'):
        if api_base_url.endswith('/'):
            api_base_url = api_base_url + 'api'
        else:
            api_base_url = api_base_url + '/api'
    
    login_url = f"{api_base_url}/auth/login"
    
    login_data = {
        "email": email,
        "password": password
    }
    
        headers = {
            'Content-Type': 'application/json',
        **get_enhanced_device_fingerprint()
        }
    
    try:
        console.print("🔐 Authenticating with Agent700...", style="blue")
        
        response = requests.post(login_url, json=login_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('accessToken')
            
            if access_token:
                console.print("✅ Authentication successful!", style="green bold")
                
                if 'email' in data:
                    console.print(f"   📧 Logged in as: {data['email']}", style="dim")
                if data.get('defaultOrganization', {}).get('name'):
                    console.print(f"   🏢 Organization: {data['defaultOrganization']['name']}", style="dim")
                
                return access_token
            else:
                logger.error("No access token in response")
                console.print("❌ No access token received from server", style="red")
                sys.exit(1)
        else:
            format_enhanced_error("auth_failed", response.status_code, response.text, console=console)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        format_enhanced_error("network_auth", exception=e, console=console)
        sys.exit(1)


def parse_enhanced_citations(content: str) -> Tuple[str, List[str]]:
    """Enhanced citation parsing matching web UI behavior."""
    citation_pattern = r'<!--citations>(.*?)<!--citations>'
    match = re.search(citation_pattern, content)
    
    citations = []
    clean_content = content
    
    if match:
        raw_citations = match.group(1)
        citations = [c.strip() for c in raw_citations.split(',') if c.strip()]
        clean_content = re.sub(citation_pattern, '', content).strip()
        
        # Convert [1], [2] references to links in content
        for i, citation in enumerate(citations, 1):
            link_pattern = f"\\[{i}\\]"
            clean_content = re.sub(link_pattern, f"[{i}]({citation})", clean_content)
    
    return clean_content, citations


def format_enhanced_response(response_data: ChatResponse, user_message: str, 
                           console: RichConsoleManager, output_format: str = "rich") -> None:
    """Format the response with rich visual output."""
    
    if output_format == "json":
        # JSON output for workflow consumption
        output = {
            "user_message": user_message,
            "agent_response": response_data.content,
            "citations": response_data.citations,
            "mcp_results": response_data.mcp_results,
            "finish_reason": response_data.finish_reason,
            "usage": response_data.usage,
            "timestamp": datetime.now().isoformat(),
            "success": not bool(response_data.error)
        }
        print(json.dumps(output, indent=2))
        return
    
    if output_format == "plain":
        # Plain text output
        print(f"User: {user_message}")
        print(f"Agent: {response_data.content}")
        if response_data.citations:
            print(f"Citations: {', '.join(response_data.citations)}")
        return
    
    # Rich output (default)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    console.print_panel(
        f"🤖 Agent700 Conversation\n📅 {timestamp}",
        title="Agent Response",
        style="blue"
    )
    
    # User message
    console.print("👤 Your Message:", style="bold cyan")
    wrapped_message = textwrap.fill(user_message, width=75, initial_indent="  ", subsequent_indent="  ")
    console.print(wrapped_message, style="blue")
    print()
    
    # Handle errors
    if response_data.error:
        console.print("❌ Agent Error:", style="red bold")
        console.print(f"  {response_data.error}", style="red")
        return
    
    # Agent response
    console.print("🤖 Agent Response:", style="bold green")
    
    # Parse citations from content
    clean_content, parsed_citations = parse_enhanced_citations(response_data.content)
    if parsed_citations:
        response_data.citations.extend(parsed_citations)
    
    # Format content with markdown if available
    if console.use_rich:
        try:
            # Try to render as markdown
            md = Markdown(clean_content)
            console.console.print(md)
        except:
            # Fallback to plain text
            wrapped_response = textwrap.fill(clean_content, width=75, initial_indent="  ", subsequent_indent="  ")
            console.print(wrapped_response, style="green")
        else:
            wrapped_response = textwrap.fill(clean_content, width=75, initial_indent="  ", subsequent_indent="  ")
            console.print(wrapped_response, style="green")
    
    print()
    
    # Citations
    if response_data.citations:
        console.print("📚 Citations:", style="bold yellow")
        for i, citation in enumerate(response_data.citations, 1):
            console.print(f"  [{i}] {citation}", style="yellow")
        print()
    
    # MCP Results
    if response_data.mcp_results:
        console.print("🔧 MCP Tool Results:", style="bold magenta")
        for i, result in enumerate(response_data.mcp_results, 1):
            if isinstance(result, dict):
                console.print(f"  Tool {i}:", style="magenta")
                for key, value in result.items():
                    if key != 'raw':
                        console.print(f"    • {key}: {value}", style="dim")
        else:
                console.print(f"  • Result {i}: {result}", style="dim")
        print()
    
    # Usage information
    if response_data.usage:
        console.print("📊 Token Usage:", style="bold cyan")
        usage = response_data.usage
        console.print(f"  • Prompt tokens: {usage.get('prompt_tokens', 'N/A')}", style="dim")
        console.print(f"  • Completion tokens: {usage.get('completion_tokens', 'N/A')}", style="dim")
        console.print(f"  • Total tokens: {usage.get('total_tokens', 'N/A')}", style="dim")
        print()
    
    # Finish reason
    if response_data.finish_reason:
        reason_style = "green" if response_data.finish_reason == 'stop' else "yellow"
        console.print(f"🏁 Status: {response_data.finish_reason}", style=f"bold {reason_style}")


class EnhancedAgent700Client:
    """Enhanced WebSocket client with rich features."""
    
    def __init__(self, api_base_url: str, access_token: str, console: RichConsoleManager, logger: logging.Logger):
            self.api_base_url = api_base_url
        self.access_token = access_token
        self.console = console
        self.logger = logger
        
        # Ensure proper WebSocket URL
        if not api_base_url.endswith('/api'):
            if api_base_url.endswith('/'):
                self.api_base_url = api_base_url + 'api'
            else:
                self.api_base_url = api_base_url + '/api'
        
        # Initialize WebSocket client
        if socketio is None:
            raise ImportError("python-socketio not available")
            
        self.sio = socketio.Client(
            logger=False,  # Disable socketio logging to reduce noise
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1
        )
        
        # Response tracking
        self.response_complete = False
        self.full_response = ""
        self.mcp_results = []
        self.citations = []
        self.finish_reason = None
        self.usage_info = {}
        self.error_occurred = False
        self.error_message = ""
        
        # Progress tracking
        self.progress = None
        self.task_id = None
        
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup enhanced WebSocket event handlers."""
        
        @self.sio.event
        def connect():
            self.console.print("🔌 Connected to streaming endpoint", style="green")
            if self.progress:
                self.progress.update(self.task_id, description="[green]Connected - waiting for response...")
        
        @self.sio.event
        def connect_error(data):
            self.logger.error(f"Connection error: {data}")
            self.error_occurred = True
            self.error_message = f"Connection failed: {data}"
        
        @self.sio.event
        def disconnect():
            self.console.print("🔌 Disconnected from streaming endpoint", style="yellow")
        
        @self.sio.on('chat_message_response')
        def on_chat_response(data):
            """Handle streaming chat responses with enhanced processing."""
            content = data.get('content', '')
            finish_reason = data.get('finish_reason')
            citations = data.get('citations')
            usage = data.get('usage')
            
            if content:
                self.full_response += content
                # Update progress with content preview
                if self.progress and self.task_id:
                    preview = content[:50] + "..." if len(content) > 50 else content
                    self.progress.update(self.task_id, description=f"[green]Receiving: {preview}")
                else:
                    # Real-time streaming output
                    print(content, end='', flush=True)
            
            if citations:
                self.citations.extend(citations)
            
            if usage:
                self.usage_info.update(usage)
            
            if finish_reason:
                self.finish_reason = finish_reason
                if finish_reason == 'stop':
                    self.response_complete = True
                    if self.progress:
                        self.progress.update(self.task_id, description="[green]Response complete ✓")
                elif finish_reason == 'tool_calls':
                    if self.progress:
                        self.progress.update(self.task_id, description="[blue]🔧 MCP tools executing...")
                    else:
                        self.console.print("\n🔧 MCP tools are executing...", style="blue")
        
        @self.sio.on('mcp_tool_complete_in_content')
        def on_mcp_tool_complete(data):
            """Handle MCP tool results with enhanced parsing."""
            try:
            result_block = data.get('result_block', [])
            
                # Enhanced MCP result parsing with multiple strategies
                parsed_result = None
                if isinstance(result_block, list) and len(result_block) > 1:
                    try:
                        parsed_result = json.loads(result_block[1])
                    except (json.JSONDecodeError, IndexError):
                        parsed_result = {'raw': result_block}
                elif isinstance(result_block, str):
                    try:
                        parsed_result = json.loads(result_block)
                    except json.JSONDecodeError:
                        parsed_result = {'raw': result_block}
                else:
                    parsed_result = {'raw': result_block}
                
                self.mcp_results.append(parsed_result)
                
                if self.progress:
                    self.progress.update(self.task_id, description=f"[magenta]🔧 MCP tool completed ({len(self.mcp_results)} results)")
                else:
                    self.console.print("🛠️ MCP tool completed", style="magenta")
                
            except Exception as e:
                self.logger.error(f"Failed to parse MCP result: {e}")
                self.mcp_results.append({'error': str(e), 'raw': data})
        
        @self.sio.on('data_table')
        def on_data_table(data):
            """Handle data table results."""
            self.console.print("📊 Data table received", style="cyan")
            self.mcp_results.append({'type': 'data_table', 'content': data})
        
        @self.sio.on('scrubbed_message')
        def on_scrubbed_message(data):
            """Handle PII scrubbing notifications."""
            self.console.print(f"🔒 PII scrubbed: {data}", style="yellow")
        
        @self.sio.on('error')
        def on_error(data):
            """Handle WebSocket errors with enhanced reporting."""
            self.logger.error(f"WebSocket error: {data}")
            self.error_occurred = True
            
            if isinstance(data, dict):
                error_code = data.get('code')
                error_message = data.get('error', str(data))
                
                if error_code == 401:
                    self.error_message = "Authentication failed - token invalid or expired"
                elif error_code == 400 and 'not publically shared' in error_message.lower():
                    self.error_message = "Agent access error - check agent permissions"
                else:
                    self.error_message = f"WebSocket error: {error_message}"
            else:
                self.error_message = f"WebSocket error: {str(data)}"
    
    def send_message(self, agent_uuid: str, user_message: str, agent_config: Dict, 
                    conversation_manager: ConversationManager, timeout: int = 300, use_progress: bool = True) -> ChatResponse:
        """Send message via enhanced WebSocket with rich feedback."""
        
        # Reset state
        self.response_complete = False
        self.full_response = ""
        self.mcp_results = []
        self.citations = []
        self.finish_reason = None
        self.usage_info = {}
        self.error_occurred = False
        self.error_message = ""
        
        try:
            # Setup progress tracking if requested
            if use_progress and self.console.use_rich:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                ) as progress:
                    self.progress = progress
                    self.task_id = progress.add_task("Connecting...", total=None)
                    return self._send_message_with_progress(agent_uuid, user_message, agent_config, timeout, conversation_manager)
            else:
                return self._send_message_simple(agent_uuid, user_message, agent_config, timeout, conversation_manager)
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return ChatResponse(error=str(e))
    
    def _send_message_with_progress(self, agent_uuid: str, user_message: str, 
                                  agent_config: Dict, timeout: int, 
                                  conversation_manager: ConversationManager) -> ChatResponse:
        """Send message with progress bar using full conversation context."""
        
        # Connect to WebSocket
        try:
            self.progress.update(self.task_id, description="[blue]Connecting to Agent700...")
            
            device_headers = get_enhanced_device_fingerprint()
                connection_headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    **device_headers
                }
                
            # Use the correct streaming endpoint
            stream_url = f"{self.api_base_url}/stream-chat"
                self.sio.connect(
                stream_url,
                    headers=connection_headers,
                    transports=['websocket', 'polling'],
                    wait_timeout=10
                )
            
        except Exception as e:
            self.progress.update(self.task_id, description=f"[red]Connection failed: {str(e)}")
            return ChatResponse(error=f"Connection failed: {e}")
        
            if not self.sio.connected:
            return ChatResponse(error="Failed to connect to WebSocket endpoint")
            
        # Build full conversation history like frontend
        full_messages = conversation_manager.build_full_chat_history(user_message, agent_config)
        
        # Prepare payload matching frontend exactly
            payload = {
                "agentId": agent_uuid,
            "Authorization": f"Bearer {self.access_token}",
            "messages": full_messages,
            "streamResponses": True,
            # Add ALL agent parameters like frontend
            "masterPrompt": agent_config.get('masterPrompt', ''),
            "imageDimensions": agent_config.get('imageDimensions', '1024x1024'),
            "model": agent_config.get('model', 'gpt-4o'),
            "temperature": agent_config.get('temperature', 0.7),
            "topP": agent_config.get('topP', 1.0),
            "maxTokens": agent_config.get('maxTokens', 4000),
            "scrubPii": agent_config.get('scrubPii', False),
            "piiThreshold": agent_config.get('piiThreshold', 0.5)
        }
        
        # Add agent configuration
        if agent_config.get('agentRevisionId'):
            payload["revisionId"] = agent_config['agentRevisionId']
        
        if agent_config.get('enableMcp') and agent_config.get('mcpServerNames'):
                payload.update({
                    "enableMcp": True,
                    "mcpServerNames": agent_config['mcpServerNames']
                })
        
        # Send message
        self.progress.update(self.task_id, description="[blue]Sending message with conversation context...")
        self.sio.emit('send_chat_message', payload)
        
        # Wait for response
        start_time = time.time()
        while not self.response_complete and not self.error_occurred and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        # Disconnect
        self.sio.disconnect()
        
        # Save user message to conversation
        conversation_manager.add_message('user', user_message)
        
        # Return response and save assistant message
        if self.error_occurred:
            return ChatResponse(error=self.error_message)
        
        if not self.response_complete:
            return ChatResponse(error="Response timed out")
        
        # Save assistant response to conversation
        if self.full_response:
            conversation_manager.add_message('assistant', self.full_response)
        
        return ChatResponse(
            content=self.full_response,
            citations=self.citations,
            mcp_results=self.mcp_results,
            finish_reason=self.finish_reason,
            usage=self.usage_info
        )
    
    def _send_message_simple(self, agent_uuid: str, user_message: str, 
                           agent_config: Dict, timeout: int, conversation_manager: ConversationManager) -> ChatResponse:
        """Send message without progress bar using full conversation context."""
        
        try:
            self.console.print("🔌 Connecting to streaming endpoint...", style="blue")
            
            device_headers = get_enhanced_device_fingerprint()
            connection_headers = {
                'Authorization': f'Bearer {self.access_token}',
                **device_headers
            }
            
            # Use the correct streaming endpoint
            stream_url = f"{self.api_base_url}/stream-chat"
            self.sio.connect(
                stream_url,
                headers=connection_headers,
                transports=['websocket', 'polling'],
                wait_timeout=10
            )
            
        except Exception as e:
            return ChatResponse(error=f"Connection failed: {e}")
        
        if not self.sio.connected:
            return ChatResponse(error="Failed to connect to WebSocket endpoint")
        
        # Build full conversation history like frontend
        full_messages = conversation_manager.build_full_chat_history(user_message, agent_config)
        
        # Prepare payload matching frontend exactly
        payload = {
            "agentId": agent_uuid,
            "Authorization": f"Bearer {self.access_token}",
            "messages": full_messages,
            "streamResponses": True,
            # Add ALL agent parameters like frontend
            "masterPrompt": agent_config.get('masterPrompt', ''),
            "imageDimensions": agent_config.get('imageDimensions', '1024x1024'),
            "model": agent_config.get('model', 'gpt-4o'),
            "temperature": agent_config.get('temperature', 0.7),
            "topP": agent_config.get('topP', 1.0),
            "maxTokens": agent_config.get('maxTokens', 4000),
            "scrubPii": agent_config.get('scrubPii', False),
            "piiThreshold": agent_config.get('piiThreshold', 0.5)
        }
        
        # Add agent configuration
        if agent_config.get('agentRevisionId'):
                payload["revisionId"] = agent_config['agentRevisionId']
            
        if agent_config.get('enableMcp') and agent_config.get('mcpServerNames'):
            payload.update({
                "enableMcp": True,
                "mcpServerNames": agent_config['mcpServerNames']
            })
        
        # Send message
        self.console.print("💬 Sending message with conversation context...", style="blue")
        self.console.print("🤖 Agent Response:", style="bold green")
            print("-" * 50)
        
            self.sio.emit('send_chat_message', payload)
            
        # Wait for response with simple feedback
            start_time = time.time()
        while not self.response_complete and not self.error_occurred and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
        print()  # New line after streaming
            
        # Disconnect
            self.sio.disconnect()
            
        # Save conversation
        conversation_manager.add_message('user', user_message)
        if self.full_response:
            conversation_manager.add_message('assistant', self.full_response)
        
        # Return response
        if self.error_occurred:
            return ChatResponse(error=self.error_message)
        
        if not self.response_complete:
            return ChatResponse(error="Response timed out")
        
        return ChatResponse(
            content=self.full_response,
            citations=self.citations,
            mcp_results=self.mcp_results,
            finish_reason=self.finish_reason,
            usage=self.usage_info
        )


def send_message_http(access_token: str, agent_uuid: str, user_message: str, 
                     api_base_url: str, agent_config: Dict, console: RichConsoleManager, 
                     logger: logging.Logger, timeout: int = 300) -> ChatResponse:
    """Send message using HTTP mode with enhanced error handling."""
    
    # Ensure proper API URL format
    if not api_base_url.endswith('/api'):
        if api_base_url.endswith('/'):
            api_base_url = api_base_url + 'api'
        else:
            api_base_url = api_base_url + '/api'
    
    chat_url = f"{api_base_url}/chat"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        **get_enhanced_device_fingerprint()
    }
    
    # Build payload
    payload = {
        "agentId": agent_uuid,
        "messages": [{"role": "user", "content": user_message}],
        "streamResponses": False
    }
    
    # Add agent configuration
    if agent_config.get('agentRevisionId'):
        payload["revisionId"] = agent_config['agentRevisionId']
    
    if agent_config.get('enableMcp') and agent_config.get('mcpServerNames'):
        payload.update({
            "enableMcp": True,
            "mcpServerNames": agent_config['mcpServerNames']
        })
    
    try:
        console.print("💬 Sending message via HTTP...", style="blue")
        response = requests.post(chat_url, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return ChatResponse(
                content=data.get('response', ''),
                citations=data.get('citations', []),
                usage=data.get('usage', {}),
                finish_reason='stop'
            )
        else:
            format_enhanced_error("chat_failed", response.status_code, response.text, console=console)
            return ChatResponse(error=f"HTTP request failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        format_enhanced_error("network_chat", exception=e, console=console)
        return ChatResponse(error=f"Network error: {e}")


# Global variables for interactive mode
interactive_mode = False
exit_requested = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully in interactive mode."""
    global exit_requested
    if interactive_mode:
        print("\n\n🛑 Exiting conversation... (Press Ctrl+C again to force exit)")
        exit_requested = True
    else:
        print("\n🛑 Exiting...")
        sys.exit(0)

def get_user_input(prompt="You: "):
    """Get user input with proper handling for interactive mode."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return None
    
def run_interactive_conversation(access_token: str, agent_uuid: str, api_base_url: str, 
                               agent_config: Dict, conversation_manager: ConversationManager,
                               console: RichConsoleManager, logger: logging.Logger, 
                               use_streaming: bool = True, timeout: int = 300):
    """Run interactive conversation mode with back-and-forth messaging."""
    global interactive_mode, exit_requested
    
    interactive_mode = True
    exit_requested = False
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    if not console.quiet:
        console.print_panel(
            "🤖 Interactive Agent700 Chat Mode\n\n"
            "Commands:\n"
            "  /exit, /quit, /q    - Exit conversation\n"
            "  /clear             - Clear conversation history\n"
            "  /context           - Show conversation context\n"
            "  /help              - Show this help\n\n"
            "Press Ctrl+C to exit gracefully\n"
            "Type your message and press Enter to send",
            title="Interactive Chat",
            style="green"
        )
    
    while not exit_requested:
        try:
            # Get user input
            user_input = get_user_input("\n👤 You: ")
            
            if user_input is None:  # Ctrl+C or EOF
                break
                
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() in ['/exit', '/quit', '/q']:
                if not console.quiet:
                    console.print("👋 Goodbye!", style="green")
                break
                
            elif user_input.lower() == '/clear':
                conversation_manager.clear_history()
                if not console.quiet:
                    console.print("✓ Conversation history cleared", style="green")
                continue
                
            elif user_input.lower() == '/context':
                context_info = conversation_manager.get_context_info()
                if not console.quiet:
                    console.print_panel(context_info, title="Conversation Context", style="cyan")
                else:
                    print(context_info)
                continue
                
            elif user_input.lower() == '/help':
                if not console.quiet:
                    console.print_panel(
                        "Available commands:\n"
                        "  /exit, /quit, /q    - Exit conversation\n"
                        "  /clear             - Clear conversation history\n"
                        "  /context           - Show conversation context\n"
                        "  /help              - Show this help\n\n"
                        "Press Ctrl+C to exit gracefully",
                        title="Help",
                        style="blue"
                    )
                continue
            
            # Send message to agent
            if not console.quiet:
                console.print("🤖 Agent: ", style="blue", end="")
            
            response_data = None
            
            if use_streaming and WEBSOCKET_AVAILABLE:
                try:
                    client = EnhancedAgent700Client(api_base_url, access_token, console, logger)
                    response_data = client.send_message(agent_uuid, user_input, agent_config, conversation_manager, timeout, False)
                    
                    # If streaming failed, fallback to HTTP
                    if response_data.error and "Connection failed" in response_data.error:
                        if not console.quiet:
                            console.print("🔄 WebSocket failed, falling back to HTTP...", style="yellow")
                        response_data = send_message_http_with_context(access_token, agent_uuid, user_input, api_base_url, 
                                                                       agent_config, conversation_manager, console, logger, timeout)
                except Exception as e:
                    if not console.quiet:
                        console.print(f"🔄 Streaming error, falling back to HTTP: {e}", style="yellow")
                    response_data = send_message_http_with_context(access_token, agent_uuid, user_input, api_base_url, 
                                                                  agent_config, conversation_manager, console, logger, timeout)
            else:
                response_data = send_message_http_with_context(access_token, agent_uuid, user_input, api_base_url, 
                                                              agent_config, conversation_manager, console, logger, timeout)
            
            # Display response
            if response_data and not response_data.error:
                if console.quiet:
                    print(response_data.content)
    else:
                    # Simple response display for interactive mode
                    console.print(response_data.content, style="white")
                    
                    # Show citations if any
                    if response_data.citations:
                        console.print(f"\n📚 Sources: {', '.join(response_data.citations)}", style="dim")
            else:
                if not console.quiet:
                    console.print("❌ Failed to get response from agent", style="red")
                if response_data and response_data.error:
                    console.print(f"Error: {response_data.error}", style="red")
                    
        except KeyboardInterrupt:
            # Handle Ctrl+C during processing
            break
        except Exception as e:
            if not console.quiet:
                console.print(f"❌ Error: {e}", style="red")
            continue
    
    interactive_mode = False

def main():
    """Enhanced main function with session management, conversation continuity, and workflow features."""
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Configuration flags
    use_streaming = "--streaming" in args
    verbose_logging = "--verbose" in args or "-v" in args
    output_format = "rich"  # Default
    use_progress = True
    timeout = 300
    quiet_mode = False
    clear_history = "--clear-history" in args
    show_context = "--show-context" in args
    clear_session = "--clear-session" in args
    show_session = "--show-session" in args
    force_auth = "--force-auth" in args
    interactive_mode = "--interactive" in args or "-i" in args
    
    # Parse output format
    for arg in args:
        if arg.startswith('--output='):
            output_format = arg.split('=', 1)[1]
        elif arg.startswith('--timeout='):
            try:
                timeout = int(arg.split('=', 1)[1])
            except ValueError:
                timeout = 300
        elif arg == '--quiet':
            quiet_mode = True
            use_progress = False
        elif arg == '--no-rich':
            output_format = "plain"
    
    # Remove flags from message
    message_args = [arg for arg in args if not arg.startswith('--') and not arg.startswith('-')]
    
    # Setup console and logging
    console = RichConsoleManager(use_rich=(output_format == "rich" and not quiet_mode))
    logger = setup_enhanced_logging(verbose_logging)
    
    # Load configuration
    try:
        email, password, agent_uuid, api_base_url = load_enhanced_configuration()
    except SystemExit:
        sys.exit(1)
    
    # Initialize session and conversation managers
    session_manager = SessionManager(email, console, logger)
    conversation_manager = ConversationManager(agent_uuid, console)
    
    # Handle special session commands
    if clear_session:
        session_manager.clear_session()
        if not quiet_mode:
            console.print("✓ Session cleared", style="green")
        sys.exit(0)
    
    if show_session:
        session_info = session_manager.get_session_info()
        if not quiet_mode:
            console.print_panel(
                session_info,
                title="Session Status",
                style="cyan"
            )
        else:
            print(session_info)
        sys.exit(0)
    
    # Handle conversation commands
    if clear_history:
        conversation_manager.clear_history()
        if not quiet_mode:
            console.print("✓ Conversation history cleared", style="green")
        sys.exit(0)
    
    if show_context:
        context_info = conversation_manager.get_context_info()
        if not quiet_mode:
            console.print_panel(
                context_info,
                title="Conversation Context",
                style="cyan"
            )
    else:
            print(context_info)
        sys.exit(0)
    
    # Handle interactive mode
    if interactive_mode:
        if len(message_args) > 0:
            # Interactive mode with initial message
            user_message = message_args[0]
        else:
            # Interactive mode without initial message
            user_message = None
    else:
        # Require message for normal operation
        if len(message_args) < 1:
            if not quiet_mode:
                console = RichConsoleManager()
                console.print_panel(
                    "python run_agent.py \"Your message\" [OPTIONS]\n\n"
                    "Communication Options:\n"
                    "  --streaming       Use WebSocket streaming (recommended)\n"
                    "  --interactive, -i Start interactive conversation mode\n"
                    "  --output=FORMAT   Output format: rich, json, plain\n"
                    "  --timeout=SECS    Timeout in seconds (default: 300)\n"
                    "  --quiet           Minimal output for workflows\n"
                    "  --no-rich         Disable rich formatting\n\n"
                    "Session Management:\n"
                    "  --force-auth      Force fresh authentication\n"
                    "  --clear-session   Clear stored session\n"
                    "  --show-session    Show session status\n\n"
                    "Conversation Management:\n"
                    "  --clear-history   Clear conversation history\n"
                    "  --show-context    Show conversation context\n\n"
                    "Debug Options:\n"
                    "  --verbose, -v     Enable verbose logging\n\n"
                    "Examples:\n"
                    "  python run_agent.py \"Hello\" --streaming\n"
                    "  python run_agent.py --interactive\n"
                    "  python run_agent.py \"Analyze data\" --output=json\n"
                    "  python run_agent.py \"Quick query\" --quiet\n"
                    "  python run_agent.py --clear-history\n"
                    "  python run_agent.py --show-context\n"
                    "  python run_agent.py --show-session\n"
                    "  python run_agent.py --clear-session",
                    title="Agent700 CLI v2.0",
                    style="blue"
                )
            sys.exit(1)
        
        user_message = message_args[0]
    
    # Show configuration and context if not in quiet mode
    if not quiet_mode:
        context_info = conversation_manager.get_context_info()
        session_info = session_manager.get_session_info()
        console.print_panel(
            f"API URL: {api_base_url}\n"
            f"Email: {email}\n"
            f"Agent ID: {agent_uuid}\n"
            f"Mode: {'Streaming' if use_streaming else 'HTTP'}\n"
            f"Output: {output_format}\n"
            f"Timeout: {timeout}s\n"
            f"Session: {session_info}\n"
            f"Context: {context_info}",
            title="Configuration",
            style="cyan"
        )
    
    # Enhanced authentication with session management
    try:
        access_token = session_manager.get_valid_token(password, api_base_url, force_auth)
    except SystemExit:
        sys.exit(1)
    
    # If agent UUID is not provided, get it interactively
    if not agent_uuid:
        agent_uuid = get_agent_uuid_interactive(access_token, api_base_url, console)
        
        # Ask if user wants to save configuration
        if not quiet_mode:
            save_config = get_user_input_safe("💾 Save this configuration to .env file? (y/N): ")
            if save_config.lower() in ['y', 'yes']:
                if save_config_to_env(email, password, agent_uuid, api_base_url):
                    console.print("✅ Configuration saved to .env file", style="green")
                else:
                    console.print("⚠️ Could not save configuration to .env file", style="yellow")
    
    # Get agent configuration
    agent_config = get_enhanced_agent_config(access_token, agent_uuid, api_base_url, console, logger)
    
    # Handle interactive mode
    if interactive_mode:
        run_interactive_conversation(access_token, agent_uuid, api_base_url, agent_config, 
                                   conversation_manager, console, logger, use_streaming, timeout)
        sys.exit(0)
    
    # Send message with enhanced session and conversation continuity
    response_data = None
    
    if use_streaming and WEBSOCKET_AVAILABLE:
        try:
            client = EnhancedAgent700Client(api_base_url, access_token, console, logger)
            response_data = client.send_message(agent_uuid, user_message, agent_config, conversation_manager, timeout, use_progress)
            
            # If streaming failed, fallback to HTTP
            if response_data.error and "Connection failed" in response_data.error:
                if not quiet_mode:
                    console.print("🔄 WebSocket failed, falling back to HTTP...", style="yellow")
                response_data = send_message_http_with_context(access_token, agent_uuid, user_message, api_base_url, 
                                                               agent_config, conversation_manager, console, logger, timeout)
        except Exception as e:
            if not quiet_mode:
                console.print(f"🔄 Streaming error, falling back to HTTP: {e}", style="yellow")
            response_data = send_message_http_with_context(access_token, agent_uuid, user_message, api_base_url, 
                                                          agent_config, conversation_manager, console, logger, timeout)
    else:
        if not quiet_mode and not WEBSOCKET_AVAILABLE:
            console.print("⚠ WebSocket not available, using HTTP mode", style="yellow")
        response_data = send_message_http_with_context(access_token, agent_uuid, user_message, api_base_url, 
                                                      agent_config, conversation_manager, console, logger, timeout)
    
    # Format and display response
    if response_data:
        if quiet_mode and not response_data.error:
            # Quiet mode: just print the response content
            print(response_data.content)
    else:
            format_enhanced_response(response_data, user_message, console, output_format)
        
        # Set exit code for workflow integration
        if response_data.error:
            sys.exit(1)  # Error occurred
        else:
            sys.exit(0)  # Success
    else:
        if not quiet_mode:
            console.print("❌ Failed to get response from agent", style="red")
        sys.exit(1)


def send_message_http_with_context(access_token: str, agent_uuid: str, user_message: str, 
                                   api_base_url: str, agent_config: Dict, conversation_manager: ConversationManager,
                                   console: RichConsoleManager, logger: logging.Logger, timeout: int = 300) -> ChatResponse:
    """Send message using HTTP mode with full conversation context."""
    
    # Ensure proper API URL format
    if not api_base_url.endswith('/api'):
        if api_base_url.endswith('/'):
            api_base_url = api_base_url + 'api'
        else:
            api_base_url = api_base_url + '/api'
    
    chat_url = f"{api_base_url}/chat"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        **get_enhanced_device_fingerprint()
    }
    
    # Build full conversation history like frontend
    full_messages = conversation_manager.build_full_chat_history(user_message, agent_config)
    
    # Build payload matching frontend exactly
    payload = {
        "agentId": agent_uuid,
        "messages": full_messages,
        "streamResponses": False,
        # Add ALL agent parameters like frontend
        "masterPrompt": agent_config.get('masterPrompt', ''),
        "imageDimensions": agent_config.get('imageDimensions', '1024x1024'),
        "model": agent_config.get('model', 'gpt-4o'),
        "temperature": agent_config.get('temperature', 0.7),
        "topP": agent_config.get('topP', 1.0),
        "maxTokens": agent_config.get('maxTokens', 4000),
        "scrubPii": agent_config.get('scrubPii', False),
        "piiThreshold": agent_config.get('piiThreshold', 0.5)
    }
    
    # Add agent configuration
    if agent_config.get('agentRevisionId'):
        payload["revisionId"] = agent_config['agentRevisionId']
    
    if agent_config.get('enableMcp') and agent_config.get('mcpServerNames'):
        payload.update({
            "enableMcp": True,
            "mcpServerNames": agent_config['mcpServerNames']
        })
    
    try:
        console.print("💬 Sending message with conversation context via HTTP...", style="blue")
        response = requests.post(chat_url, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save conversation
            conversation_manager.add_message('user', user_message)
            response_content = data.get('response', '')
            if response_content:
                conversation_manager.add_message('assistant', response_content)
            
            return ChatResponse(
                content=response_content,
                citations=data.get('citations', []),
                usage=data.get('usage', {}),
                finish_reason='stop'
            )
        else:
            format_enhanced_error("chat_failed", response.status_code, response.text, console=console)
            return ChatResponse(error=f"HTTP request failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        format_enhanced_error("network_chat", exception=e, console=console)
        return ChatResponse(error=f"Network error: {e}")


if __name__ == "__main__":
    main()
