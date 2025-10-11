#!/usr/bin/env python3
"""
AppleScript MCP Server for A700cli

This module provides AppleScript integration for local macOS automation,
allowing the Agent700 to interact with applications, files, and system settings.
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class AppleScriptResult:
    """Result from AppleScript execution."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0

class AppleScriptMCP:
    """AppleScript MCP server for local macOS automation."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.supported_apps = {
            'finder': 'Finder',
            'safari': 'Safari',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'vscode': 'Visual Studio Code',
            'xcode': 'Xcode',
            'terminal': 'Terminal',
            'mail': 'Mail',
            'calendar': 'Calendar',
            'notes': 'Notes',
            'reminders': 'Reminders',
            'contacts': 'Contacts',
            'messages': 'Messages',
            'facetime': 'FaceTime',
            'photos': 'Photos',
            'music': 'Music',
            'spotify': 'Spotify',
            'itunes': 'iTunes',
            'preview': 'Preview',
            'textedit': 'TextEdit',
            'pages': 'Pages',
            'numbers': 'Numbers',
            'keynote': 'Keynote'
        }
    
    def execute_applescript(self, script: str, timeout: int = 30) -> AppleScriptResult:
        """Execute AppleScript with error handling and timeout."""
        import time
        start_time = time.time()
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
                f.write(script)
                script_path = f.name
            
            try:
                # Execute AppleScript
                result = subprocess.run(
                    ['osascript', script_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    return AppleScriptResult(
                        success=True,
                        output=result.stdout.strip(),
                        execution_time=execution_time
                    )
                else:
                    return AppleScriptResult(
                        success=False,
                        output=result.stdout.strip(),
                        error=result.stderr.strip(),
                        execution_time=execution_time
                    )
                    
            finally:
                # Clean up temporary file
                os.unlink(script_path)
                
        except subprocess.TimeoutExpired:
            return AppleScriptResult(
                success=False,
                output="",
                error=f"AppleScript execution timed out after {timeout} seconds",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return AppleScriptResult(
                success=False,
                output="",
                error=f"AppleScript execution failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def get_app_info(self, app_name: str) -> Dict[str, Any]:
        """Get information about a running application."""
        script = f'''
        tell application "System Events"
            try
                set appProcess to first process whose name is "{app_name}"
                set appInfo to {{}}
                set appInfo to appInfo & {{"name": name of appProcess}}
                set appInfo to appInfo & {{"pid": unix id of appProcess}}
                set appInfo to appInfo & {{"frontmost": frontmost of appProcess}}
                return appInfo as string
            on error
                return "{{"error": "Application not found"}}"
            end try
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return {"error": "Failed to parse application info", "raw": result.output}
        else:
            return {"error": result.error}
    
    def list_running_apps(self) -> List[Dict[str, Any]]:
        """Get list of currently running applications."""
        script = '''
        tell application "System Events"
            set appList to {}
            repeat with appProcess in (every process)
                set appInfo to {name:name of appProcess, pid:unix id of appProcess, frontmost:frontmost of appProcess}
                set end of appList to appInfo
            end repeat
            return appList as string
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return [{"error": "Failed to parse app list", "raw": result.output}]
        else:
            return [{"error": result.error}]
    
    def open_application(self, app_name: str) -> AppleScriptResult:
        """Open an application."""
        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''
        return self.execute_applescript(script)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file or folder."""
        script = f'''
        set filePath to POSIX file "{file_path}"
        tell application "System Events"
            try
                set fileInfo to {{}}
                set fileInfo to fileInfo & {{"name": name of filePath}}
                set fileInfo to fileInfo & {{"path": POSIX path of filePath}}
                set fileInfo to fileInfo & {{"exists": exists filePath}}
                if exists filePath then
                    set fileInfo to fileInfo & {{"size": size of filePath}}
                    set fileInfo to fileInfo & {{"kind": kind of filePath}}
                    set fileInfo to fileInfo & {{"created": creation date of filePath}}
                    set fileInfo to fileInfo & {{"modified": modification date of filePath}}
                end if
                return fileInfo as string
            on error errMsg
                return "{{"error": errMsg}}"
            end try
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return {"error": "Failed to parse file info", "raw": result.output}
        else:
            return {"error": result.error}
    
    def list_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        """List contents of a folder."""
        script = f'''
        set folderPath to POSIX file "{folder_path}"
        tell application "System Events"
            try
                set folderContents to {{}}
                repeat with item in (every item of folder folderPath)
                    set itemInfo to {{name:name of item, kind:kind of item, size:size of item}}
                    set end of folderContents to itemInfo
                end repeat
                return folderContents as string
            on error errMsg
                return "{{"error": errMsg}}"
            end try
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return [{"error": "Failed to parse folder contents", "raw": result.output}]
        else:
            return [{"error": result.error}]
    
    def open_file(self, file_path: str, app_name: Optional[str] = None) -> AppleScriptResult:
        """Open a file with specified application or default."""
        if app_name:
            script = f'''
            tell application "{app_name}"
                open POSIX file "{file_path}"
                activate
            end tell
            '''
        else:
            script = f'''
            tell application "Finder"
                open POSIX file "{file_path}"
            end tell
            '''
        return self.execute_applescript(script)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        script = '''
        tell application "System Events"
            set systemInfo to {}
            set systemInfo to systemInfo & {computer_name:computer name}
            set systemInfo to systemInfo & {user_name:name of current user}
            set systemInfo to systemInfo & {os_version:system version}
            return systemInfo as string
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return {"error": "Failed to parse system info", "raw": result.output}
        else:
            return {"error": result.error}
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content."""
        script = '''
        return the clipboard
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            return result.output
        else:
            return f"Error getting clipboard: {result.error}"
    
    def set_clipboard_content(self, content: str) -> AppleScriptResult:
        """Set clipboard content."""
        # Escape content for AppleScript
        escaped_content = content.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
        script = f'''
        set the clipboard to "{escaped_content}"
        '''
        return self.execute_applescript(script)
    
    def take_screenshot(self, file_path: str) -> AppleScriptResult:
        """Take a screenshot and save to specified path."""
        script = f'''
        tell application "System Events"
            set screenshotPath to POSIX file "{file_path}"
            do shell script "screencapture " & quoted form of POSIX path of screenshotPath
        end tell
        '''
        return self.execute_applescript(script)
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """Get notification settings for applications."""
        script = '''
        tell application "System Events"
            set notificationInfo to {}
            -- This would require more complex AppleScript to access System Preferences
            -- For now, return basic info
            return "{"message": "Notification settings require System Preferences access"}"
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return {"error": "Failed to parse notification settings", "raw": result.output}
        else:
            return {"error": result.error}
    
    def execute_custom_script(self, script: str) -> AppleScriptResult:
        """Execute custom AppleScript."""
        return self.execute_applescript(script)
    
    def get_notes(self, folder_name: str = None) -> List[Dict[str, Any]]:
        """Get notes from the Notes app."""
        if folder_name:
            script = f'''
            tell application "Notes"
                set notesList to {{}}
                repeat with noteItem in notes of folder "{folder_name}"
                    set noteInfo to {{name:name of noteItem, body:body of noteItem, creation_date:creation date of noteItem, modification_date:modification date of noteItem}}
                    set end of notesList to noteInfo
                end repeat
                return notesList as string
            end tell
            '''
        else:
            script = '''
            tell application "Notes"
                set notesList to {}
                repeat with noteItem in notes
                    set noteInfo to {name:name of noteItem, body:body of noteItem, creation_date:creation date of noteItem, modification_date:modification date of noteItem}
                    set end of notesList to noteInfo
                end repeat
                return notesList as string
            end tell
            '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return [{"error": "Failed to parse notes", "raw": result.output}]
        else:
            return [{"error": result.error}]
    
    def create_note(self, note_title: str, note_content: str, folder_name: str = None) -> AppleScriptResult:
        """Create a new note in the Notes app."""
        if folder_name:
            script = f'''
            tell application "Notes"
                set newNote to make new note at folder "{folder_name}" with properties {{name:"{note_title}", body:"{note_content}"}}
                return "Note created successfully"
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                set newNote to make new note with properties {{name:"{note_title}", body:"{note_content}"}}
                return "Note created successfully"
            end tell
            '''
        return self.execute_applescript(script)
    
    def search_notes(self, search_term: str) -> List[Dict[str, Any]]:
        """Search notes for a specific term."""
        script = f'''
        tell application "Notes"
            set matchingNotes to {{}}
            repeat with noteItem in notes
                if "{search_term}" is in name of noteItem or "{search_term}" is in body of noteItem then
                    set noteInfo to {{name:name of noteItem, body:body of noteItem, creation_date:creation date of noteItem, modification_date:modification date of noteItem}}
                    set end of matchingNotes to noteInfo
                end if
            end repeat
            return matchingNotes as string
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return [{"error": "Failed to parse search results", "raw": result.output}]
        else:
            return [{"error": result.error}]
    
    def get_note_folders(self) -> List[Dict[str, Any]]:
        """Get list of note folders."""
        script = '''
        tell application "Notes"
            set foldersList to {}
            repeat with folderItem in folders
                set folderInfo to {name:name of folderItem, note_count:count of notes of folderItem}
                set end of foldersList to folderInfo
            end repeat
            return foldersList as string
        end tell
        '''
        
        result = self.execute_applescript(script)
        if result.success:
            try:
                return json.loads(result.output)
            except json.JSONDecodeError:
                return [{"error": "Failed to parse folders", "raw": result.output}]
        else:
            return [{"error": result.error}]

# MCP Tool Functions
def applescript_get_app_info(app_name: str) -> Dict[str, Any]:
    """MCP tool: Get information about a running application."""
    mcp = AppleScriptMCP()
    return mcp.get_app_info(app_name)

def applescript_list_running_apps() -> List[Dict[str, Any]]:
    """MCP tool: List currently running applications."""
    mcp = AppleScriptMCP()
    return mcp.list_running_apps()

def applescript_open_application(app_name: str) -> Dict[str, Any]:
    """MCP tool: Open an application."""
    mcp = AppleScriptMCP()
    result = mcp.open_application(app_name)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_get_file_info(file_path: str) -> Dict[str, Any]:
    """MCP tool: Get information about a file or folder."""
    mcp = AppleScriptMCP()
    return mcp.get_file_info(file_path)

def applescript_list_folder_contents(folder_path: str) -> List[Dict[str, Any]]:
    """MCP tool: List contents of a folder."""
    mcp = AppleScriptMCP()
    return mcp.list_folder_contents(folder_path)

def applescript_open_file(file_path: str, app_name: str = None) -> Dict[str, Any]:
    """MCP tool: Open a file with specified application."""
    mcp = AppleScriptMCP()
    result = mcp.open_file(file_path, app_name)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_get_system_info() -> Dict[str, Any]:
    """MCP tool: Get system information."""
    mcp = AppleScriptMCP()
    return mcp.get_system_info()

def applescript_get_clipboard() -> str:
    """MCP tool: Get current clipboard content."""
    mcp = AppleScriptMCP()
    return mcp.get_clipboard_content()

def applescript_set_clipboard(content: str) -> Dict[str, Any]:
    """MCP tool: Set clipboard content."""
    mcp = AppleScriptMCP()
    result = mcp.set_clipboard_content(content)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_take_screenshot(file_path: str) -> Dict[str, Any]:
    """MCP tool: Take a screenshot."""
    mcp = AppleScriptMCP()
    result = mcp.take_screenshot(file_path)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_execute_custom(script: str) -> Dict[str, Any]:
    """MCP tool: Execute custom AppleScript."""
    mcp = AppleScriptMCP()
    result = mcp.execute_custom_script(script)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_get_notes(folder_name: str = None) -> List[Dict[str, Any]]:
    """MCP tool: Get notes from the Notes app."""
    mcp = AppleScriptMCP()
    return mcp.get_notes(folder_name)

def applescript_create_note(note_title: str, note_content: str, folder_name: str = None) -> Dict[str, Any]:
    """MCP tool: Create a new note in the Notes app."""
    mcp = AppleScriptMCP()
    result = mcp.create_note(note_title, note_content, folder_name)
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time
    }

def applescript_search_notes(search_term: str) -> List[Dict[str, Any]]:
    """MCP tool: Search notes for a specific term."""
    mcp = AppleScriptMCP()
    return mcp.search_notes(search_term)

def applescript_get_note_folders() -> List[Dict[str, Any]]:
    """MCP tool: Get list of note folders."""
    mcp = AppleScriptMCP()
    return mcp.get_note_folders()

# MCP Tool Registry
APPLESCRIPT_MCP_TOOLS = {
    "applescript_get_app_info": {
        "description": "Get information about a running application",
        "parameters": {
            "app_name": {"type": "string", "description": "Name of the application"}
        }
    },
    "applescript_list_running_apps": {
        "description": "List currently running applications",
        "parameters": {}
    },
    "applescript_open_application": {
        "description": "Open an application",
        "parameters": {
            "app_name": {"type": "string", "description": "Name of the application to open"}
        }
    },
    "applescript_get_file_info": {
        "description": "Get information about a file or folder",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file or folder"}
        }
    },
    "applescript_list_folder_contents": {
        "description": "List contents of a folder",
        "parameters": {
            "folder_path": {"type": "string", "description": "Path to the folder"}
        }
    },
    "applescript_open_file": {
        "description": "Open a file with specified application",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file"},
            "app_name": {"type": "string", "description": "Name of the application to open with (optional)"}
        }
    },
    "applescript_get_system_info": {
        "description": "Get system information",
        "parameters": {}
    },
    "applescript_get_clipboard": {
        "description": "Get current clipboard content",
        "parameters": {}
    },
    "applescript_set_clipboard": {
        "description": "Set clipboard content",
        "parameters": {
            "content": {"type": "string", "description": "Content to set in clipboard"}
        }
    },
    "applescript_take_screenshot": {
        "description": "Take a screenshot",
        "parameters": {
            "file_path": {"type": "string", "description": "Path where to save the screenshot"}
        }
    },
    "applescript_execute_custom": {
        "description": "Execute custom AppleScript",
        "parameters": {
            "script": {"type": "string", "description": "AppleScript code to execute"}
        }
    },
    "applescript_get_notes": {
        "description": "Get notes from the Notes app",
        "parameters": {
            "folder_name": {"type": "string", "description": "Name of the folder to get notes from (optional)"}
        }
    },
    "applescript_create_note": {
        "description": "Create a new note in the Notes app",
        "parameters": {
            "note_title": {"type": "string", "description": "Title of the note"},
            "note_content": {"type": "string", "description": "Content of the note"},
            "folder_name": {"type": "string", "description": "Name of the folder to create note in (optional)"}
        }
    },
    "applescript_search_notes": {
        "description": "Search notes for a specific term",
        "parameters": {
            "search_term": {"type": "string", "description": "Term to search for in note titles and content"}
        }
    },
    "applescript_get_note_folders": {
        "description": "Get list of note folders",
        "parameters": {}
    }
}

if __name__ == "__main__":
    # Test the AppleScript MCP
    mcp = AppleScriptMCP()
    
    print("🍎 AppleScript MCP Test")
    print("=" * 40)
    
    # Test system info
    print("📊 System Info:")
    system_info = mcp.get_system_info()
    print(json.dumps(system_info, indent=2))
    
    # Test running apps
    print("\n📱 Running Apps:")
    apps = mcp.list_running_apps()
    for app in apps[:5]:  # Show first 5
        print(f"  • {app.get('name', 'Unknown')} (PID: {app.get('pid', 'N/A')})")
    
    # Test clipboard
    print("\n📋 Clipboard:")
    clipboard = mcp.get_clipboard_content()
    print(f"  Content: {clipboard[:100]}{'...' if len(clipboard) > 100 else ''}")
