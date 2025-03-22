# Chat History CLI Options

This document lists all available options for the Chat History command-line interface.

## Basic Usage

```bash
python -m cli.chat_history_query [options]
```

## All Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--thread` | Thread ID for this conversation | "default" (will generate UUID) |
| `--model` | LLM model to use | gpt-3.5-turbo |
| `--temperature` | Temperature setting for the LLM | 0.7 |
| `--language` | Language to respond in | English |
| `--system_message` | System message to use in the conversations | "You are a helpful assistant." |
| `--message` | Single message to send (for non-interactive mode) | None |
| `--streaming` | Enable streaming responses | False |
| `--clear_history` | Clear the thread history before starting | False |

## Examples

### Start an Interactive Chat Session

```bash
python -m cli.chat_history_query
```

### Start a Chat with Custom Thread ID

```bash
python -m cli.chat_history_query --thread my-conversation-123
```

### Use a Different Model and Temperature

```bash
python -m cli.chat_history_query --model gpt-4 --temperature 0.9
```

### Set a Custom System Message

```bash
python -m cli.chat_history_query --system_message "You are a helpful coding assistant that specializes in Python."
```

### Chat in a Different Language

```bash
python -m cli.chat_history_query --language Spanish
```

### Enable Streaming Responses

```bash
python -m cli.chat_history_query --streaming
```

### Send a Single Message (Non-Interactive Mode)

```bash
python -m cli.chat_history_query --message "What is the capital of France?"
```

### Clear History Before Starting

```bash
python -m cli.chat_history_query --thread existing-thread-id --clear_history
```

### Combine Multiple Options

```bash
python -m cli.chat_history_query --thread project-abc --model gpt-4 --temperature 0.8 --system_message "You are a helpful data science assistant." --streaming
```

## Interactive Commands

During an interactive chat session, you can use these special commands:

| Command | Description |
|---------|-------------|
| `history` | Display the conversation history |
| `clear` | Clear the conversation history |
| `exit` or `quit` | End the conversation |

## Multithreading Support

The Chat History CLI supports multiple concurrent conversation threads through the `--thread` parameter. Each thread maintains its own conversation history in the database, allowing you to:

1. Resume conversations later
2. Maintain separate contexts for different topics
3. Run multiple parallel conversations

Example of switching between threads:

```bash
# Start or continue conversation in thread "work-project"
python -m cli.chat_history_query --thread work-project

# Start or continue conversation in thread "personal-assistant"
python -m cli.chat_history_query --thread personal-assistant
```

## Implementation Details

The Chat History CLI uses a PostgreSQL database to store conversation messages. The connection string is read from the `POSTGRES_URI` environment variable by default. 