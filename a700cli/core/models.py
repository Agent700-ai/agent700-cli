"""
Data models for a700cli.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class ToolCall:
    """Parsed tool call from a <tool_use> block."""
    server: str
    tool: str
    arguments: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from Agent700 API."""
    content: str
    citations: List[str] = None
    error: str = None
    mcp_results: List[Dict] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.mcp_results is None:
            self.mcp_results = []
