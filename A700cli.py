#!/usr/bin/env python3
"""
A700cli - Enhanced Agent700 CLI with Interactive Configuration
"""

import os
import sys
import json
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import requests
from dotenv import load_dotenv
import platform
import hashlib
from pathlib import Path
import pickle
from datetime import datetime

# Enhanced console output support
try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def __init__(self): pass
        def print(self, *args, **kwargs): print(*args)
        def print_panel(self, text, title="", style=""): 
            print(f"\n{'='*50}")
            if title: print(f"{title}")
            print(f"{'='*50}")
            print(text)
            print(f"{'='*50}\n")

@dataclass
class AgentResponse:
    content: str
    citations: List[str] = None
    error: str = None

class SessionManager:
    def __init__(self):
        self.session_file = Path(".agent700_session.dat")
        self.session_data = self.load_session()
    
    def load_session(self) -> Dict[str, Any]:
        if self.session_file.exists():
            try:
                with open(self.session_file, 'rb') as f:
                    return pickle.load(f)
            except: pass
        return {}
    
    def save_session(self, data: Dict[str, Any]):
        self.session_data.update(data)
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.session_data, f)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")

class ConversationManager:
    def __init__(self):
        self.conversation_file = Path(".agent700_conversation.json")
        self.conversation_history = self.load_conversation()
    
    def load_conversation(self) -> List[Dict[str, Any]]:
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r') as f:
                    return json.load(f)
            except: pass
        return []
    
    def save_conversation(self):
        try:
            with open(self.conversation_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")
    
    def add_user_message(self, message: str):
        self.conversation_history.append({
            "role": "user", "content": message, "timestamp": datetime.now().isoformat()
        })
        self.save_conversation()
    
    def add_agent_message(self, message: str):
        self.conversation_history.append({
            "role": "agent", "content": message, "timestamp": datetime.now().isoformat()
        })
        self.save_conversation()
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        return self.conversation_history[-10:]

def load_environment() -> Dict[str, str]:
    load_dotenv()
    return {
        "API_BASE_URL": os.getenv("API_BASE_URL", "https://api.agent700.ai"),
        "EMAIL": os.getenv("EMAIL"), "PASSWORD": os.getenv("PASSWORD"),
        "AGENT_UUID": os.getenv("AGENT_UUID")
    }

def get_device_fingerprint() -> str:
    system_info = {
        "platform": platform.system(), "platform_release": platform.release(),
        "architecture": platform.machine(), "python_version": platform.python_version()
    }
    fingerprint_data = json.dumps(system_info, sort_keys=True)
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

def authenticate(email: str, password: str, api_base_url: str, console) -> Optional[str]:
    auth_url = f"{api_base_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json", "User-Agent": "A700cli/1.0.0",
        "X-Device-Fingerprint": get_device_fingerprint()
    }
    payload = {"email": email, "password": password}
    
    try:
        console.print("🔐 Authenticating...", style="blue")
        response = requests.post(auth_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("accessToken")
            if access_token:
                console.print("✅ Authentication successful", style="green")
                return access_token
        console.print(f"❌ Authentication failed: {response.status_code}", style="red")
        return None
    except Exception as e:
        console.print(f"❌ Authentication error: {e}", style="red")
        return None

def get_agent_config(access_token: str, agent_uuid: str, api_base_url: str, console) -> Dict[str, Any]:
    agent_url = f"{api_base_url}/api/agents/{agent_uuid}"
    headers = {
        "Authorization": f"Bearer {access_token}", "Content-Type": "application/json",
        "User-Agent": "A700cli/1.0.0", "X-Device-Fingerprint": get_device_fingerprint()
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
                    'agentName': latest_revision.get('name', 'Unknown Agent'),
                    'masterPrompt': latest_revision.get('masterPrompt', ''),
                    'temperature': latest_revision.get('temperature', 0.7),
                    'maxTokens': latest_revision.get('maxTokens', 4000),
                    'imageDimensions': latest_revision.get('imageDimensions', '1024x1024'),
                    'topP': latest_revision.get('topP', 1.0),
                    'scrubPii': latest_revision.get('scrubPii', False),
                    'piiThreshold': latest_revision.get('piiThreshold', 0.5)
                }
                console.print(f"✓ Agent: {config['agentName']}", style="green")
                return config
        console.print(f"❌ Failed to get agent config: {response.status_code}", style="red")
        return {}
    except Exception as e:
        console.print(f"❌ Error getting agent config: {e}", style="red")
        return {}

def get_agent_uuid_interactive(access_token: str, api_base_url: str, console) -> str:
    """Get agent UUID interactively."""
    agents_url = f"{api_base_url}/api/agents"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "A700cli/1.0.0"
    }
    
    try:
        console.print("🔍 Fetching available agents...", style="blue")
        response = requests.get(agents_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data.get('agents', [])
            
            if agents:
                console.print(f"\n📋 Available Agents ({len(agents)}):", style="blue")
                for i, agent in enumerate(agents, 1):
                    console.print(f"  {i}. {agent.get('name', 'Unknown')} ({agent.get('uuid', 'No UUID')})", style="white")
                
                while True:
                    try:
                        choice = input(f"\nSelect agent (1-{len(agents)}): ").strip()
                        if choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(agents):
                                selected_agent = agents[idx]
                                console.print(f"✅ Selected: {selected_agent.get('name', 'Unknown')}", style="green")
                                return selected_agent.get('uuid', '')
                        console.print("❌ Invalid selection. Please try again.", style="red")
                    except KeyboardInterrupt:
                        console.print("\n👋 Goodbye!", style="green")
                        sys.exit(0)
            else:
                console.print("❌ No agents found", style="red")
                return ""
        else:
            console.print(f"❌ Failed to get agents: {response.status_code}", style="red")
            return ""
            
    except Exception as e:
        console.print(f"❌ Error getting agents: {e}", style="red")
        return ""

def send_message_http(access_token: str, agent_uuid: str, user_message: str, 
                     api_base_url: str, agent_config: Dict[str, Any], 
                     conversation_manager: ConversationManager, console, timeout: int = 300) -> AgentResponse:
    chat_url = f"{api_base_url}/api/chat"
    headers = {
        "Authorization": f"Bearer {access_token}", "Content-Type": "application/json",
        "User-Agent": "A700cli/1.0.0", "X-Device-Fingerprint": get_device_fingerprint()
    }
    
    # Start with a fresh message (no conversation history for now)
    messages = [{
        "role": "user",
        "content": user_message
    }]
    
    # Messages prepared for API
    
    # Build simple payload like original run_agent.py
    payload = {
        "agentId": agent_uuid,
        "messages": messages,
        "streamResponses": False
    }
    
    try:
        console.print("💬 Sending with conversation context", style="blue", end="")
        
        # Start animated dots
        dots_running = True
        def animate_dots():
            while dots_running:
                print(".", end="", flush=True)
                time.sleep(0.5)
        
        dots_thread = threading.Thread(target=animate_dots, daemon=True)
        dots_thread.start()
        
        response = requests.post(chat_url, json=payload, headers=headers, timeout=timeout)
        dots_running = False
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for API errors first
            if data.get('error'):
                return AgentResponse(content="", error=f"API Error: {data.get('error')}")
            
            # Try different possible response structures
            content = data.get('content') or data.get('message') or data.get('response')
            if not content and 'messages' in data:
                # Check if response is in messages array
                messages = data.get('messages', [])
                if messages:
                    last_message = messages[-1]
                    content = last_message.get('content', '')
            
            if content:
                conversation_manager.add_user_message(user_message)
                conversation_manager.add_agent_message(content)
                
                return AgentResponse(
                    content=content,
                    citations=data.get('citations', [])
                )
            else:
                return AgentResponse(content="", error=f"No content found in response: {data}")
        else:
            return AgentResponse(content="", error=f"HTTP {response.status_code}: {response.text}")
    except Exception as e:
        return AgentResponse(content="", error=str(e))

def main():
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print("A700cli - Enhanced Agent700 CLI with Interactive Configuration")
        print("Usage: python A700cli --interactive    Start interactive chat")
        print("       python A700cli \"Your message\"   Send single message")
        sys.exit(0)
    
    console = Console()
    session_manager = SessionManager()
    conversation_manager = ConversationManager()
    
    env = load_environment()
    api_base_url = env.get("API_BASE_URL", "https://api.agent700.ai")
    
    email = env.get("EMAIL")
    password = env.get("PASSWORD")
    agent_uuid = env.get("AGENT_UUID")
    
    if not email:
        email = input("📧 Email: ").strip()
        if not email:
            console.print("❌ Email is required", style="red")
            sys.exit(1)
    
    if not password or password == 'your_password_here':
        try:
            import getpass
            password = getpass.getpass("🔐 Password: ")
        except (EOFError, KeyboardInterrupt):
            # Fallback to regular input if getpass fails
            password = input("🔐 Password: ")
        if not password:
            console.print("❌ Password is required", style="red")
            sys.exit(1)
    
    access_token = authenticate(email, password, api_base_url, console)
    if not access_token:
        console.print("❌ Authentication failed", style="red")
        sys.exit(1)
    
    session_manager.save_session({
        "access_token": access_token, "email": email,
        "saved_at": datetime.now().isoformat()
    })
    
    if not agent_uuid:
        console.print("🔍 No agent UUID found. Let's select an agent...", style="blue")
        agent_uuid = get_agent_uuid_interactive(access_token, api_base_url, console)
        if not agent_uuid:
            console.print("❌ No agent selected", style="red")
            sys.exit(1)
        
        # Save to .env file
        try:
            env_content = f"API_BASE_URL={api_base_url}\nEMAIL={email}\nPASSWORD={password}\nAGENT_UUID={agent_uuid}\n"
            with open(".env", "w") as f:
                f.write(env_content)
            console.print("✅ Configuration saved to .env file", style="green")
        except Exception as e:
            console.print("⚠️ Could not save configuration to .env file", style="yellow")
    
    agent_config = get_agent_config(access_token, agent_uuid, api_base_url, console)
    
    # Agent configuration loaded
    
    interactive_mode = "--interactive" in args or "-i" in args or "-interactive" in args
    
    if interactive_mode:
        from rich.panel import Panel
        console.print(Panel(
            "Interactive Agent700 Chat\n\nCommands: /exit, /quit, /q, /clear, /context, /help",
            title="Interactive Chat", style="green"
        ))
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['/exit', '/quit', '/q']:
                    console.print("👋 Goodbye!", style="green")
                    break
                elif user_input.lower() == '/clear':
                    conversation_manager.conversation_history = []
                    console.print("🧹 Conversation history cleared", style="yellow")
                    continue
                
                if not user_input: continue
                
                conversation_manager.add_user_message(user_input)
                console.print("🤖 Agent: ", style="blue", end="")
                
                response_data = send_message_http(access_token, agent_uuid, user_input, 
                                                api_base_url, agent_config, conversation_manager, console)
                
                if response_data and not response_data.error:
                    console.print(response_data.content, style="white")
                    if response_data.citations:
                        console.print(f"\n📚 Sources: {', '.join(response_data.citations)}", style="dim")
                else:
                    console.print("❌ Failed to get response from agent", style="red")
                    if response_data and response_data.error:
                        console.print(f"Error: {response_data.error}", style="red")
                        
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!", style="green")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")
    else:
        if len(args) == 0:
            console.print("❌ No message provided", style="red")
            console.print("Usage: python A700cli \"Your message here\"", style="yellow")
            console.print("       python A700cli --interactive", style="yellow")
            sys.exit(1)
        
        user_message = args[0]
        console.print(f"👤 You: {user_message}", style="white")
        
        response_data = send_message_http(access_token, agent_uuid, user_message, 
                                        api_base_url, agent_config, conversation_manager, console)
        
        if response_data and not response_data.error:
            console.print(f"🤖 Agent: {response_data.content}", style="white")
            if response_data.citations:
                console.print(f"\n📚 Sources: {', '.join(response_data.citations)}", style="dim")
        else:
            console.print("❌ Failed to get response from agent", style="red")
            if response_data and response_data.error:
                console.print(f"Error: {response_data.error}", style="red")

if __name__ == "__main__":
    main()