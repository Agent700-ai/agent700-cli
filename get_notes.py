#!/usr/bin/env python3
"""
Simple script to get notes using AppleScript
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from applescript_integration import AppleScriptIntegration
    integration = AppleScriptIntegration()
    
    print("📝 Getting your notes...")
    result = integration.execute_tool("applescript_get_notes", {})
    print(integration.format_tool_result("applescript_get_notes", result))
    
except ImportError:
    print("❌ AppleScript integration not available")
except Exception as e:
    print(f"❌ Error: {e}")

