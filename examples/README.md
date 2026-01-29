# A700cli Examples

Copy-paste CLI examples to get started quickly.

## Basic Usage

### Send a single message

```bash
a700cli "Hello, how can you help me today?"
```

### Start interactive chat

```bash
a700cli --interactive
```

### Read message from a file

```bash
a700cli --input-file prompt.txt
```

### Save response to a file

```bash
a700cli "Generate a summary" --output-file summary.txt
```

### Quiet mode for scripts (response only, no status messages)

```bash
a700cli "What is 2+2?" --quiet
```

### Pipe input from stdin

```bash
echo "Explain this error" | a700cli --quiet
```

### Use WebSocket streaming for real-time responses

```bash
a700cli "Tell me a story" --streaming
```

## Automation Examples

### Process a file and save output

```bash
a700cli --input-file data.txt --output-file result.txt --quiet
```

### Capture response in a variable (bash)

```bash
response=$(a700cli "Quick status check" --quiet)
echo "Agent said: $response"
```

### List available agents

```bash
a700cli --list-agents
```

### Search agents by name

```bash
a700cli --list-agents --search "code"
```

## Need Help?

- Run `a700cli --help` for all options
- Email hello@agent700.ai for support
- Docs: https://agent700.ai/docs
