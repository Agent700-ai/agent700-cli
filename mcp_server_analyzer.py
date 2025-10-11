#!/usr/bin/env python3
"""
Agent700 MCP Server Analyzer

This script analyzes all MCP servers configured for an Agent700 agent,
showing their status, tools, and identifying potential issues like
function name length problems.

Usage:
    python mcp_server_analyzer.py [--agent-id AGENT_ID] [--show-disconnected]
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import argparse

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_configuration():
    """Load configuration from environment variables."""
    load_dotenv()
    
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    agent_uuid = os.getenv('AGENT_UUID')
    api_base_url = os.getenv('API_BASE_URL', 'https://api.agent700.ai')
    
    if not all([email, password, agent_uuid]):
        print(f"{Colors.FAIL}❌ Missing required environment variables{Colors.ENDC}")
        print("Required: EMAIL, PASSWORD, AGENT_UUID")
        print("Optional: API_BASE_URL (defaults to https://api.agent700.ai)")
        sys.exit(1)
    
    return email, password, agent_uuid, api_base_url

def authenticate(email, password, api_base_url):
    """Authenticate with Agent700 API."""
    print(f"{Colors.OKCYAN}🔐 Authenticating with Agent700...{Colors.ENDC}")
    
    login_url = f"{api_base_url}/api/auth/login"
    login_data = {'email': email, 'password': password}
    
    # Add device fingerprinting headers
    device_headers = get_device_fingerprint()
    headers = {
        'Content-Type': 'application/json',
        **device_headers
    }
    
    try:
        response = requests.post(login_url, json=login_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        access_token = data['accessToken']
        
        print(f"{Colors.OKGREEN}✅ Authentication successful!{Colors.ENDC}")
        print(f"   📧 Logged in as: {email}")
        if 'organization' in data:
            print(f"   🏢 Organization: {data['organization']}")
        
        return access_token
        
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}❌ Authentication failed: {e}{Colors.ENDC}")
        sys.exit(1)

def get_device_fingerprint():
    """Get device fingerprinting information for security headers."""
    try:
        screen_resolution = "1920x1080"
        import datetime
        now = datetime.datetime.now()
        utc_offset = now.astimezone().utcoffset()
        timezone_offset = int(utc_offset.total_seconds() / 60)
        return {
            'X-Screen-Resolution': screen_resolution,
            'X-Timezone-Offset': str(timezone_offset)
        }
    except Exception as e:
        print(f"Warning: Could not get device fingerprint: {e}")
        return {
            'X-Screen-Resolution': '1920x1080',
            'X-Timezone-Offset': '0'
        }

def get_agent_mcp_servers(access_token, agent_uuid, api_base_url):
    """Fetch all MCP servers for the agent."""
    print(f"{Colors.OKCYAN}🔍 Fetching MCP servers for agent...{Colors.ENDC}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    mcp_url = f'{api_base_url}/api/agents/{agent_uuid}/mcp/servers'
    
    try:
        response = requests.get(mcp_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get('success'):
            return data.get('servers', [])
        else:
            print(f"{Colors.FAIL}❌ Failed to fetch MCP servers: {data.get('error', 'Unknown error')}{Colors.ENDC}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}❌ Error fetching MCP servers: {e}{Colors.ENDC}")
        return []

def analyze_mcp_servers(servers, show_disconnected=False):
    """Analyze MCP servers and identify issues."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}📊 MCP Server Analysis{Colors.ENDC}")
    print("=" * 80)
    
    # Filter servers based on status
    if not show_disconnected:
        servers = [s for s in servers if s.get('status') == 'connected']
        print(f"{Colors.OKGREEN}✅ Showing only connected servers{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Showing all servers (including disconnected){Colors.ENDC}")
    
    if not servers:
        print(f"{Colors.WARNING}⚠️  No servers found{Colors.ENDC}")
        return
    
    # Statistics
    total_servers = len(servers)
    connected_servers = len([s for s in servers if s.get('status') == 'connected'])
    disconnected_servers = total_servers - connected_servers
    
    print(f"\n{Colors.BOLD}📈 Summary:{Colors.ENDC}")
    print(f"   • Total servers: {total_servers}")
    print(f"   • Connected: {connected_servers}")
    print(f"   • Disconnected: {disconnected_servers}")
    
    # Analyze each server
    long_function_names = []
    duplicate_servers = {}
    
    for i, server in enumerate(servers, 1):
        print(f"\n{Colors.BOLD}📡 Server {i}: {server.get('name', 'Unknown')}{Colors.ENDC}")
        print("-" * 60)
        
        # Basic info
        print(f"   ID: {server.get('id', 'N/A')}")
        print(f"   Status: {get_status_icon(server.get('status', 'unknown'))} {server.get('status', 'unknown')}")
        print(f"   Public: {'Yes' if server.get('public') else 'No'}")
        print(f"   Custom: {'Yes' if server.get('agent') else 'No'}")
        print(f"   Disabled: {'Yes' if server.get('disabled') else 'No'}")
        
        # Tools analysis
        tools = server.get('tools', [])
        resources = server.get('resources', [])
        
        print(f"   Tools: {len(tools)}")
        print(f"   Resources: {len(resources)}")
        
        if tools:
            print(f"\n   {Colors.BOLD}🔧 Tools:{Colors.ENDC}")
            for tool in tools:
                tool_name = tool.get('name', '')
                tool_desc = tool.get('description', 'No description')
                name_length = len(tool_name)
                
                # Check for long function names
                if name_length > 64:
                    long_function_names.append({
                        'server': server.get('name', 'Unknown'),
                        'tool': tool_name,
                        'length': name_length
                    })
                    print(f"     {Colors.FAIL}⚠️  {tool_name} ({name_length} chars) - EXCEEDS LIMIT!{Colors.ENDC}")
                elif name_length > 50:
                    print(f"     {Colors.WARNING}📏 {tool_name} ({name_length} chars) - Long name{Colors.ENDC}")
                else:
                    print(f"     ✅ {tool_name} ({name_length} chars)")
                
                # Show description if available
                if tool_desc and tool_desc != 'No description':
                    print(f"        └─ {tool_desc}")
        
        # Check for duplicate server names
        server_name = server.get('name', 'Unknown')
        if server_name in duplicate_servers:
            duplicate_servers[server_name].append(server.get('id', 'N/A'))
        else:
            duplicate_servers[server_name] = [server.get('id', 'N/A')]
    
    # Report issues
    print(f"\n{Colors.BOLD}{Colors.HEADER}🚨 Issues Found{Colors.ENDC}")
    print("=" * 80)
    
    if long_function_names:
        print(f"\n{Colors.FAIL}❌ Function Names Exceeding 64 Characters:{Colors.ENDC}")
        for issue in long_function_names:
            print(f"   • {issue['server']}: {issue['tool']} ({issue['length']} chars)")
    else:
        print(f"\n{Colors.OKGREEN}✅ No function names exceed 64 characters{Colors.ENDC}")
    
    # Check for duplicates
    duplicates = {name: ids for name, ids in duplicate_servers.items() if len(ids) > 1}
    if duplicates:
        print(f"\n{Colors.WARNING}⚠️  Duplicate Server Names:{Colors.ENDC}")
        for name, ids in duplicates.items():
            print(f"   • {name}: {len(ids)} instances")
            for server_id in ids:
                print(f"     └─ {server_id}")
    else:
        print(f"\n{Colors.OKGREEN}✅ No duplicate server names{Colors.ENDC}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}{Colors.HEADER}💡 Recommendations{Colors.ENDC}")
    print("=" * 80)
    
    if long_function_names:
        print(f"\n{Colors.WARNING}🔧 Fix Function Name Length Issues:{Colors.ENDC}")
        print("   1. Rename functions to be ≤ 64 characters")
        print("   2. Use abbreviations or shorter names")
        print("   3. Consider using function aliases")
    
    if duplicates:
        print(f"\n{Colors.WARNING}🔧 Fix Duplicate Servers:{Colors.ENDC}")
        print("   1. Remove duplicate servers")
        print("   2. Rename servers to be unique")
        print("   3. Keep only the most recent/working version")
    
    if disconnected_servers > 0:
        print(f"\n{Colors.WARNING}🔧 Clean Up Disconnected Servers:{Colors.ENDC}")
        print("   1. Remove or restart disconnected servers")
        print("   2. Check server configurations")
        print("   3. Verify server connectivity")

def get_status_icon(status):
    """Get status icon for display."""
    icons = {
        'connected': f'{Colors.OKGREEN}✅{Colors.ENDC}',
        'disconnected': f'{Colors.FAIL}❌{Colors.ENDC}',
        'error': f'{Colors.FAIL}⚠️{Colors.ENDC}',
        'connecting': f'{Colors.WARNING}🔄{Colors.ENDC}'
    }
    return icons.get(status, '❓')

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze Agent700 MCP servers')
    parser.add_argument('--agent-id', help='Agent UUID (overrides .env)')
    parser.add_argument('--show-disconnected', action='store_true', 
                       help='Show disconnected servers')
    parser.add_argument('--api-url', help='API base URL (overrides .env)')
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.HEADER}Agent700 MCP Server Analyzer{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Analyzing MCP server configuration and identifying issues{Colors.ENDC}")
    print()
    
    # Load configuration
    email, password, agent_uuid, api_base_url = load_configuration()
    
    # Override with command line arguments
    if args.agent_id:
        agent_uuid = args.agent_id
    if args.api_url:
        api_base_url = args.api_url
    
    print(f"{Colors.OKCYAN}🔧 Configuration:{Colors.ENDC}")
    print(f"   • API URL: {api_base_url}")
    print(f"   • Agent ID: {agent_uuid}")
    print(f"   • Show Disconnected: {'Yes' if args.show_disconnected else 'No'}")
    print()
    
    # Authenticate
    access_token = authenticate(email, password, api_base_url)
    
    # Get MCP servers
    servers = get_agent_mcp_servers(access_token, agent_uuid, api_base_url)
    
    if not servers:
        print(f"{Colors.WARNING}⚠️  No MCP servers found for this agent{Colors.ENDC}")
        return
    
    # Analyze servers
    analyze_mcp_servers(servers, args.show_disconnected)
    
    print(f"\n{Colors.OKGREEN}✅ Analysis complete!{Colors.ENDC}")
    print(f"{Colors.OKCYAN}💡 Use --show-disconnected to see all servers{Colors.ENDC}")

if __name__ == "__main__":
    main()
