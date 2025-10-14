# A700cli - Enhanced Agent700 CLI

A sophisticated command-line interface for interacting with Agent700 agents with rich visual output, enhanced MCP support, session management, conversation history, and comprehensive workflow integration features.

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
- Conversation history management with JSON-based storage
- Enhanced device fingerprinting for security
- Automatic session recovery and validation
- Pickle-based session persistence for reliability

### 🚀 Workflow Integration
- Multiple output formats (rich, JSON, plain text)
- Proper exit codes for workflow automation
- Quiet mode for minimal output
- File I/O support for batch processing
- Stdin/stdout integration for piping
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
   curl -O https://your-repo/A700cli.py
   curl -O https://your-repo/requirements.txt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your setup method**:
   ```bash
   # Option A: Interactive setup (recommended)
   python A700cli.py --interactive
   
   # Option B: Manual .env configuration
   cp .env.example .env
   # Edit .env with your credentials
   ```

## 📁 Local Development Files

The following files are automatically generated during local development and are ignored by git:

- **`.agent700_conversation.json`** - Stores conversation history and context
- **`.agent700_session.dat`** - Contains session data and authentication tokens  
- **`.env`** - Environment variables for authentication (auto-generated)

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
python A700cli.py --interactive
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

The Agent700 CLI supports two primary usage modes:

### 🔄 Interactive Mode
For back-and-forth conversations with persistent context:
```bash
python A700cli.py --interactive
```

### ⚡ Non-Interactive Mode  
For single commands, automation, and workflow integration:
```bash
python A700cli.py "Your message here"
```

## 🆕 Enhanced Features in A700cli.py

### 📁 File I/O Support
```bash
# Read message from file
python A700cli.py --input-file prompt.txt

# Read from stdin
echo "Your message" | python A700cli.py

# Write response to file
python A700cli.py "Generate report" --output-file report.txt
```

### 🔇 Quiet Mode for Scripting
```bash
# Minimal output for automation
python A700cli.py "Quick query" --quiet

# Perfect for piping
result=$(python A700cli.py "Process data" --quiet)
```

### 🤖 Interactive Agent Selection
```bash
# Automatically lists and lets you select agents
python A700cli.py --interactive
```

### 💬 Enhanced Interactive Commands
- `/exit`, `/quit`, `/q` - Exit conversation
- `/clear` - Clear conversation history
- `/context` - Show conversation context
- `/help` - Show available commands

## 🚀 Non-Interactive Mode Usage

### Basic Single Message
```bash
python A700cli.py "Your message here"
```

### File Input/Output
```bash
# Read from file
python A700cli.py --input-file prompt.txt

# Write to file
python A700cli.py "Generate report" --output-file report.txt

# Read from stdin
echo "Your message" | python A700cli.py
```

### Quiet Mode for Automation
```bash
# Minimal output for scripts
python A700cli.py "Quick query" --quiet

# Perfect for piping
result=$(python A700cli.py "Process data" --quiet)
```

## 💬 Interactive Mode Usage

### Interactive Conversation Mode
```bash
python A700cli.py --interactive
```

## 🎯 Non-Interactive Mode Use Cases

### Automation & Scripting
Perfect for automated workflows, CI/CD pipelines, and batch processing:

```bash
# Automated report generation
python A700cli.py "Generate weekly sales report" --output-file report.txt

# Batch data processing
python A700cli.py "Process customer feedback data" --quiet

# Status checks in monitoring systems
python A700cli.py "Check system health" --quiet
```

### API Integration
Ideal for integrating with other systems and applications:

```bash
# REST API integration
response=$(python A700cli.py "Analyze user behavior" --quiet)
echo "$response"

# Webhook processing
python A700cli.py "Process webhook data: $payload" --output-file result.txt

# Microservice communication
python A700cli.py "Validate transaction data" --quiet
```

### Data Processing Workflows
Excellent for data analysis and processing pipelines:

```bash
# Data analysis with MCP tools
python A700cli.py "Analyze dataset: $file_path" --input-file data.txt

# Report generation
python A700cli.py "Generate insights from Q4 data" --output-file insights.txt

# Data validation
python A700cli.py "Validate data integrity" --quiet
```

### System Administration
Great for system monitoring and administrative tasks:

```bash
# System diagnostics
python A700cli.py "Check server performance metrics" --quiet

# Log analysis
python A700cli.py "Analyze error logs for patterns" --input-file logs.txt

# Automated alerts
python A700cli.py "Generate system status report" --output-file status.txt --quiet
```

### Development & Testing
Perfect for development workflows and testing:

```bash
# Code analysis
python A700cli.py "Review code quality for: $file" --input-file code.py --output-file analysis.txt

# Test generation
python A700cli.py "Generate unit tests for: $function" --output-file tests.py

# Documentation generation
python A700cli.py "Create API documentation" --output-file docs.md
```

### Business Process Automation
Ideal for business workflow automation:

```bash
# Customer service automation
python A700cli.py "Process customer inquiry: $ticket" --output-file response.txt

# Content generation
python A700cli.py "Generate marketing content for: $campaign" --output-file content.txt

# Compliance checking
python A700cli.py "Check compliance requirements" --quiet
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `message` | Message to send (positional argument) | None |
| `--interactive, -i` | Start interactive conversation mode | Single message mode |
| `--input-file, -f` | Read message from file (use `-` for stdin) | None |
| `--output-file, -o` | Write response to file | None |
| `--quiet, -q` | Minimal output for workflows | Verbose output |
| `--help-auth` | Show authentication environment variables | None |

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

Perfect for automated workflows and CI/CD pipelines using non-interactive mode:

### Exit Codes
- **0**: Success
- **1**: Error (authentication, network, agent error)

### Workflow Examples

#### Basic Automation Script
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

#### CI/CD Pipeline Integration
```bash
#!/bin/bash
# GitHub Actions / Jenkins example

# Generate deployment report
python run_agent.py "Generate deployment report for $BRANCH" \
    --output=json \
    --timeout=300 \
    --quiet > deployment_report.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Deployment report generated successfully"
    # Process the JSON response
    cat deployment_report.json | jq '.agent_response'
else
    echo "❌ Failed to generate deployment report"
    exit 1
fi
```

#### Monitoring & Alerting
```bash
#!/bin/bash
# System monitoring example

# Check system health
health_status=$(python run_agent.py "Check system health metrics" \
    --output=plain \
    --timeout=30 \
    --quiet)

if [ $? -eq 0 ]; then
    echo "System Status: $health_status"
else
    # Send alert
    python run_agent.py "Generate system alert notification" \
        --output=json \
        --quiet | jq '.agent_response' | mail -s "System Alert" admin@company.com
fi
```

#### Data Processing Pipeline
```bash
#!/bin/bash
# Data processing workflow

# Process incoming data
python run_agent.py "Process data file: $INPUT_FILE" \
    --streaming \
    --output=json \
    --timeout=600 > processed_data.json

# Validate results
validation_result=$(python run_agent.py "Validate processed data" \
    --output=plain \
    --quiet)

if [ $? -eq 0 ]; then
    echo "✅ Data processing completed: $validation_result"
    # Move to next stage
    mv processed_data.json /output/
else
    echo "❌ Data validation failed: $validation_result"
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

### 🔄 Interactive Mode Examples

#### Interactive Conversation
```bash
# Start interactive chat
python A700cli.py --interactive
```

### ⚡ Non-Interactive Mode Examples

#### Basic Single Message
```bash
python A700cli.py "Hello, how can you help me today?"
```

#### File Input/Output
```bash
# Read from file
python A700cli.py --input-file prompt.txt

# Write to file
python A700cli.py "Generate report" --output-file report.txt

# Read from stdin
echo "Your message" | python A700cli.py
```

#### Quiet Automation
```bash
result=$(python A700cli.py "Quick status check" --quiet)
echo "Status: $result"
```

#### Batch Processing
```bash
# Process multiple items
for item in $ITEMS; do
    python A700cli.py "Process item: $item" --quiet
done
```

#### Content Generation
```bash
# Generate documentation
python A700cli.py "Create API documentation for: $endpoint" \
    --output-file docs.md
```

## 🔄 Migration from Original Script

### Key Differences in A700cli.py
1. **Enhanced CLI Interface**: Proper argparse-based command-line parsing
2. **File I/O Support**: Read from files, write to files, stdin/stdout integration
3. **Interactive Agent Selection**: Automatic agent discovery and selection
4. **Session Management**: Persistent sessions with pickle-based storage
5. **Conversation History**: JSON-based conversation tracking
6. **Quiet Mode**: Perfect for automation and scripting
7. **Rich Console Support**: Beautiful terminal output with fallback

### Migration Steps
1. Install new dependencies: `pip install -r requirements.txt`
2. Update your scripts to use `A700cli.py` instead of `run_agent.py`
3. Use new command-line options (`--input-file`, `--output-file`, `--quiet`)
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
python A700cli.py "test"

# Test different modes
python A700cli.py "test" --quiet
python A700cli.py "test" --input-file test.txt
python A700cli.py "test" --output-file result.txt

# Test interactive mode
python A700cli.py --interactive
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
