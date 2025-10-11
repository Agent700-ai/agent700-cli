# Agent700 CLI Tool

A sophisticated command-line interface for interacting with Agent700 agents with rich visual output, enhanced MCP support, session management, and workflow integration features.

## ✨ Key Features

### 🎨 Rich Visual Output
- Beautiful colored console output with progress indicators
- Markdown rendering in terminal
- Formatted tables for structured data
- Visual MCP tool execution feedback
- Citation display with source information
- Enhanced error formatting with troubleshooting tips

### 🔧 Enhanced MCP Integration
- Robust MCP tool result parsing with fallback strategies
- Better error handling and reporting
- Visual feedback during tool execution
- Support for complex MCP result structures
- Comprehensive MCP debugging with verbose logging

### 💾 Session Management
- Persistent session storage with automatic token refresh
- Conversation history management
- Enhanced device fingerprinting for security
- Automatic session recovery and validation

### 🚀 Workflow Integration
- Multiple output formats (rich, JSON, plain text)
- Proper exit codes for workflow automation
- Quiet mode for minimal output
- Configurable timeouts and retry logic
- Test pattern execution for systematic testing

### 🛡️ Enhanced Reliability
- Better WebSocket connection handling with automatic fallback
- Comprehensive error messages with troubleshooting tips
- Enhanced device fingerprinting for security
- Robust authentication with detailed feedback
- Graceful error recovery and fallback mechanisms

## 🚀 Installation

1. **Clone or download the script**:
   ```bash
   # Download the script files
   curl -O https://your-repo/run_agent.py
   curl -O https://your-repo/A700cli  # Enhanced version
   curl -O https://your-repo/requirements.txt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your setup method**:
   ```bash
   # Option A: Interactive setup (recommended)
   python A700cli --interactive
   
   # Option B: Manual .env configuration
   cp .env.example .env
   # Edit .env with your credentials
   ```

## 📁 Local Development Files

The following files are automatically generated during local development and are ignored by git:

- **`.agent700_conversation.json`** - Stores conversation history and context
- **`.agent700_session.dat`** - Contains session data and authentication tokens  
- **`.agent700_session_*.dat`** - Additional session files with unique identifiers

These files:
- ✅ **Should be ignored by git** (already in `.gitignore`)
- ✅ **Contain sensitive data** (authentication tokens, session info)
- ✅ **Are user-specific** (different for each developer)
- ✅ **Are automatically generated** when using the CLI
- ✅ **Should not be committed** to the repository

**Note**: These files are created automatically when you first run the CLI and will persist your session and conversation history locally.

## 📋 Configuration

### Automatic Configuration (Recommended)

The CLI will automatically prompt for missing credentials and agent selection:

```bash
python run_agent.py --interactive
```

The tool will:
1. **Prompt for login credentials** if not found in `.env`
2. **Authenticate with Agent700** and show your account info
3. **List available agents** for you to choose from
4. **Save configuration** to `.env` file for future use

### Interactive Setup Features

- **🔐 Secure Login**: Password input is hidden for security
- **🤖 Agent Discovery**: Automatically fetches and displays your available agents
- **📋 Easy Selection**: Choose agents by number or enter UUID directly
- **💾 Configuration Saving**: Automatically saves credentials to `.env` file
- **🔄 Session Management**: Maintains authentication across conversations

### Manual Configuration

Alternatively, create a `.env` file with your Agent700 credentials:

```env
EMAIL=your-email@company.com
PASSWORD=your_secure_password
AGENT_UUID=your-agent-uuid-here
API_BASE_URL=https://api.agent700.ai  # Optional, defaults to production
```

## 💬 Usage

### Basic Usage
```bash
python run_agent.py "Your message here"
```

### Rich Output Mode (Default)
```bash
python run_agent.py "Analyze this data for me" --streaming
```

### Workflow Integration (JSON Output)
```bash
python run_agent.py "Process this request" --output=json --timeout=120
```

### Quiet Mode for Scripting
```bash
python run_agent.py "Quick query" --quiet
```

### Test Pattern Execution
```bash
python run_agent.py --test-patterns
```

### Interactive Conversation Mode
```bash
python run_agent.py --interactive
```

### Verbose MCP Debugging
```bash
python run_agent.py "Debug MCP tools" --verbose
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--streaming` | Use WebSocket streaming (recommended) | HTTP mode |
| `--output=FORMAT` | Output format: `rich`, `json`, `plain` | `rich` |
| `--timeout=SECS` | Request timeout in seconds | `300` |
| `--quiet` | Minimal output for workflows | Verbose output |
| `--no-rich` | Disable rich formatting | Rich enabled |
| `--verbose, -v` | Enable detailed MCP logging | Warning level |
| `--test-patterns` | Run predefined test message patterns | Normal mode |
| `--interactive, -i` | Start interactive conversation mode | Single message mode |

## 📊 Output Formats

### Rich Output (Default)
Beautiful console output with:
- Colored panels and sections
- Markdown rendering
- Progress indicators
- Citation cards
- MCP tool result formatting

### JSON Output
Structured data perfect for workflows:
```json
{
  "user_message": "Your query",
  "agent_response": "Agent's response",
  "citations": ["source1", "source2"],
  "mcp_results": [{"tool": "result"}],
  "finish_reason": "stop",
  "timestamp": "2023-10-10T19:15:00",
  "success": true
}
```

### Plain Text Output
Simple text format:
```
User: Your message
Agent: Response content
Citations: source1, source2
```

## 💬 Interactive Conversation Mode

### Features
- **Back-and-forth messaging** with persistent conversation context
- **Graceful Ctrl+C exit** with proper signal handling
- **Special commands** for conversation management
- **Session persistence** across messages
- **Rich console output** with progress indicators

### Interactive Commands
| Command | Description |
|---------|-------------|
| `/exit`, `/quit`, `/q` | Exit conversation gracefully |
| `/clear` | Clear conversation history |
| `/context` | Show conversation context |
| `/help` | Show available commands |

### Usage Examples
```bash
# Start interactive conversation
python run_agent.py --interactive

# Interactive with streaming
python run_agent.py --interactive --streaming

# Interactive with verbose logging
python run_agent.py --interactive --verbose
```

### Interactive Mode Features
- **Conversation History**: Maintains context across all messages
- **Session Management**: Automatic token refresh and validation
- **Error Recovery**: Graceful handling of connection issues
- **Rich Output**: Beautiful formatting with progress indicators
- **MCP Integration**: Full MCP tool support in interactive mode

## 🔐 Interactive Setup Process

### First-Time Setup
When you run the CLI without a `.env` file, it will guide you through setup:

```bash
python run_agent.py --interactive
```

**Step 1: Authentication**
```
🔐 Agent700 Authentication Setup
Some configuration is missing. Let's set it up interactively.

📧 Email: your-email@company.com
🔒 Password: [hidden input]
```

**Step 2: Agent Selection**
```
🤖 Available Agents:

1. Customer Support Agent
   ID: 123e4567-e89b-12d3-a456-426614174000
   Description: Handles customer inquiries and support tickets

2. Data Analysis Agent
   ID: 987fcdeb-51a2-43d1-b789-123456789abc
   Description: Analyzes data and generates insights

Select agent (number) or enter UUID: 1
✅ Selected: Customer Support Agent
```

**Step 3: Save Configuration**
```
💾 Save this configuration to .env file? (y/N): y
✅ Configuration saved to .env file
```

### Agent Discovery
The CLI automatically:
- **Fetches your available agents** from Agent700
- **Shows agent names and descriptions** for easy selection
- **Allows selection by number** or direct UUID entry
- **Validates agent access** before proceeding

## 🔗 WebSocket vs HTTP Modes

### WebSocket Streaming Mode (Recommended)
- **Real-time response streaming**
- **Progress indicators**  
- **Live MCP tool execution feedback**
- **Automatic fallback to HTTP on failure**

```bash
python run_agent.py "Stream this response" --streaming
```

### HTTP Mode
- **Simple request-response**
- **Better for automation**
- **More reliable for network issues**

```bash
python run_agent.py "Process this" # HTTP mode (default)
```

## 🛠️ MCP Tool Support

The enhanced script provides superior MCP integration with comprehensive debugging:

### Features
- **Automatic MCP server detection** from agent configuration
- **Real-time tool execution feedback** with progress indicators
- **Enhanced result parsing** with multiple fallback strategies
- **Visual tool result formatting** in rich output mode
- **Error handling** for malformed tool responses
- **Comprehensive MCP debugging** with verbose logging
- **Test pattern execution** for systematic MCP testing

### MCP Tool Execution Flow
1. **Agent Configuration**: Fetches MCP settings from agent
2. **Tool Detection**: Shows which MCP tools are available
3. **Execution Feedback**: Visual indicators during tool runs
4. **Result Processing**: Structured display of tool outputs
5. **Error Recovery**: Graceful handling of tool failures
6. **Debug Logging**: Detailed MCP execution logs with `--verbose`

### MCP Debugging
```bash
# Enable verbose MCP logging
python run_agent.py "Use MCP tools" --verbose

# Test MCP patterns systematically
python run_agent.py --test-patterns

# Debug specific MCP issues
python run_agent.py "Search for information" --verbose --streaming
```

## 🔄 Workflow Integration

Perfect for automated workflows and CI/CD pipelines:

### Exit Codes
- **0**: Success
- **1**: Error (authentication, network, agent error)

### Workflow Example
```bash
#!/bin/bash
# Workflow script example

response=$(python run_agent.py "Analyze deployment" --output=json --quiet)
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Agent response successful"
    echo "$response" | jq '.agent_response'
else
    echo "Agent request failed"
    exit 1
fi
```

### Docker Integration
```dockerfile
FROM python:3.9-slim

COPY run_agent.py requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt

# Copy environment file
COPY .env /app/

ENTRYPOINT ["python", "run_agent.py"]
```

## 🎯 Use Cases

### Development & Testing
```bash
# Test agent responses with rich output
python run_agent.py "Test query" --streaming --verbose

# Debug MCP tool execution
python run_agent.py "Use search tool" --output=json --verbose

# Run systematic test patterns
python run_agent.py --test-patterns
```

### Automation & CI/CD
```bash
# Automated report generation
python run_agent.py "Generate weekly report" --output=json --timeout=600

# Quiet mode for scripts
python run_agent.py "Process data batch" --quiet
```

### Data Analysis Workflows
```bash
# Process with MCP tools and get structured output
python run_agent.py "Analyze this dataset" --streaming --output=json
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Test with HTTP mode if WebSocket fails
python run_agent.py "test" --no-streaming --verbose
```

#### Authentication Issues
```bash
# Verify credentials with verbose logging
python run_agent.py "test" --verbose
```

#### MCP Tool Problems
```bash
# Check agent MCP configuration
python run_agent.py "test" --verbose --streaming
```

### Error Messages
The enhanced script provides detailed error messages with:
- **Root cause identification**
- **Troubleshooting suggestions**
- **Configuration guidance**
- **Network diagnostics**

## 💾 Session Management

### Persistent Sessions
- **Automatic session storage** in `~/.agent700/session.json`
- **Token refresh** with automatic retry logic
- **Session validation** before each request
- **Graceful session recovery** on token expiration

### Conversation History
- **Chat history storage** in `~/.agent700/conversations/`
- **Conversation context** maintained across sessions
- **Automatic conversation management** with cleanup
- **Rich conversation display** with timestamps and formatting

### Session Features
```bash
# Sessions are automatically managed
python run_agent.py "Continue our conversation"  # Uses existing session

# Force new session
rm ~/.agent700/session.json
python run_agent.py "Start fresh conversation"
```

## 🔒 Security Features

### Enhanced Authentication
- **Device fingerprinting** for improved security
- **Token validation** with detailed error reporting
- **Session management** with automatic retry logic
- **Enhanced device fingerprinting** with system information

### Privacy Protection
- **Credential protection** in logs
- **Secure token storage** recommendations
- **Network security** best practices
- **Session encryption** for sensitive data

## 🚀 Performance Features

### Optimizations
- **Connection pooling** for WebSocket connections
- **Automatic fallback** from streaming to HTTP
- **Timeout management** for different operation types
- **Memory-efficient** response processing

### Monitoring
- **Real-time progress tracking**
- **Performance metrics** in verbose mode
- **Connection status monitoring**
- **Resource usage optimization**

## 📝 Examples

### Basic Chat
```bash
python run_agent.py "Hello, how can you help me today?"
```

### Data Analysis
```bash
python run_agent.py "Analyze the sales data and provide insights" --streaming
```

### MCP Tool Usage
```bash
python run_agent.py "Search for recent news about AI" --streaming --verbose
```

### Workflow Integration
```bash
python run_agent.py "Generate report for Q4 2023" --output=json --timeout=300
```

### Quiet Automation
```bash
result=$(python run_agent.py "Quick status check" --quiet)
echo "Status: $result"
```

### Test Pattern Execution
```bash
python run_agent.py --test-patterns
```

### Interactive Conversation
```bash
# Start interactive chat
python run_agent.py --interactive

# Interactive with streaming
python run_agent.py --interactive --streaming

# Interactive with verbose logging
python run_agent.py --interactive --verbose
```

## 🔄 Migration from Original Script

### Differences
1. **Rich Output**: Enhanced visual formatting
2. **Better Error Handling**: More informative error messages  
3. **MCP Integration**: Improved tool result processing
4. **Workflow Features**: JSON output, exit codes, quiet mode
5. **Connection Management**: Better WebSocket handling

### Migration Steps
1. Install new dependencies: `pip install -r requirements.txt`
2. Update your scripts to use new command-line options
3. Optionally upgrade to rich output mode
4. Test with your existing .env configuration

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd agent700-enhanced-cli
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### Testing
```bash
# Run basic tests
python run_agent.py "test" --verbose

# Test different modes
python run_agent.py "test" --output=json
python run_agent.py "test" --quiet
python run_agent.py "test" --streaming

# Run systematic test patterns
python run_agent.py --test-patterns
```

## 📄 License

This enhanced script maintains the same license as the original Agent700 CLI tool.

## 🔗 Related Resources

- [Agent700 Documentation](https://docs.agent700.ai)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io)
- [Rich Python Library](https://rich.readthedocs.io)
- [WebSocket Documentation](https://python-socketio.readthedocs.io)

---

**Happy chatting with your enhanced Agent700 CLI! 🚀**
