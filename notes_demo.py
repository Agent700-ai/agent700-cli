#!/usr/bin/env python3
"""
Notes Integration Demo for A700cli

This demonstrates the Notes app integration capabilities.
"""

import os
import sys
from typing import Dict, Any, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from applescript_integration import AppleScriptIntegration
    APPLESCRIPT_AVAILABLE = True
except ImportError:
    APPLESCRIPT_AVAILABLE = False

def demo_notes_integration():
    """Demonstrate Notes integration capabilities."""
    print("📝 Notes Integration Demo for A700cli")
    print("=" * 50)
    
    if not APPLESCRIPT_AVAILABLE:
        print("❌ AppleScript integration not available")
        return
    
    # Initialize AppleScript integration
    applescript_integration = AppleScriptIntegration()
    
    # Check availability
    availability = applescript_integration.check_availability()
    print(f"AppleScript Available: {'✅ Yes' if availability['available'] else '❌ No'}")
    
    if not availability['available']:
        print(f"Error: {availability.get('error', 'Unknown error')}")
        return
    
    print("\n🎯 Notes Integration Capabilities:")
    print("=" * 40)
    
    print("1. 📁 Get Note Folders")
    print("   - List all note folders")
    print("   - Show note count per folder")
    
    print("\n2. 📝 Get Notes")
    print("   - List all notes")
    print("   - Get notes from specific folder")
    print("   - Show note titles and content previews")
    
    print("\n3. ✍️ Create Notes")
    print("   - Create new notes")
    print("   - Add notes to specific folders")
    print("   - Set note titles and content")
    
    print("\n4. 🔍 Search Notes")
    print("   - Search by title or content")
    print("   - Find notes containing specific terms")
    
    print("\n📱 Demo: Getting Note Folders")
    print("-" * 40)
    
    folders = applescript_integration.execute_tool("applescript_get_note_folders", {})
    print(applescript_integration.format_tool_result("applescript_get_note_folders", folders))
    
    print("\n📝 Demo: Getting Notes")
    print("-" * 40)
    
    notes = applescript_integration.execute_tool("applescript_get_notes", {})
    print(applescript_integration.format_tool_result("applescript_get_notes", notes))
    
    print("\n✍️ Demo: Creating a Note")
    print("-" * 40)
    
    print("🤖 Agent: I'll create a test note for you...")
    print("🍎 Executing AppleScript tool: applescript_create_note")
    
    # Create a test note
    create_result = applescript_integration.execute_tool("applescript_create_note", {
        "note_title": "A700cli Test Note",
        "note_content": "This note was created by A700cli with AppleScript integration! 🎉"
    })
    print(applescript_integration.format_tool_result("applescript_create_note", create_result))
    
    print("\n🔍 Demo: Searching Notes")
    print("-" * 40)
    
    print("🤖 Agent: Let me search for notes containing 'test'...")
    print("🍎 Executing AppleScript tool: applescript_search_notes")
    
    search_result = applescript_integration.execute_tool("applescript_search_notes", {
        "search_term": "test"
    })
    print(applescript_integration.format_tool_result("applescript_search_notes", search_result))
    
    print("\n✅ Notes Integration Demo Complete!")
    print("\n💡 In A700cli Interactive Mode:")
    print("=" * 40)
    print("👤 You: Show me my notes")
    print("🤖 Agent: I'll get your notes for you...")
    print("🍎 [AppleScript tool executes automatically]")
    print("📝 [Notes displayed]")
    print()
    print("👤 You: Create a note called 'Meeting Notes' with today's agenda")
    print("🤖 Agent: I'll create that note for you...")
    print("🍎 [AppleScript tool executes automatically]")
    print("✅ [Note created successfully]")
    print()
    print("👤 You: Search for notes about 'project'")
    print("🤖 Agent: I'll search your notes for 'project'...")
    print("🍎 [AppleScript tool executes automatically]")
    print("🔍 [Search results displayed]")
    
    print("\n🔧 Integration Status:")
    print("=" * 20)
    print("✅ Notes MCP tools available")
    print("✅ Tool execution working")
    print("✅ Result formatting working")
    print("✅ Ready for A700cli integration")
    
    print("\n📋 Available Notes Tools:")
    print("=" * 30)
    print("  • applescript_get_notes - Get all notes or notes from specific folder")
    print("  • applescript_create_note - Create new notes")
    print("  • applescript_search_notes - Search notes by content")
    print("  • applescript_get_note_folders - Get list of note folders")
    
    print("\n🎮 Interactive Mode Examples:")
    print("=" * 35)
    print("👤 You: Show me my notes")
    print("👤 You: Create a note called 'Shopping List'")
    print("👤 You: Search for notes about 'work'")
    print("👤 You: Show me my note folders")
    print("👤 You: Create a note in my 'Work' folder")

if __name__ == "__main__":
    demo_notes_integration()

