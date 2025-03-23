# Agent Query CLI Options

This document lists all available options for the Agent query command-line interface.

## Basic Usage

```bash
python -m cli.agent_query [options]
```

## Examples

### Example 1: REACT Agent with Calculator Tool

```bash
python -m cli.agent_query \
  --agent_type react \
  --tools calculator \
  --message "What is the square root of 144 plus the cube of 3?" \
  --streaming
```

### Example 2: REACT Agent with Weather Tool

```bash
python -m cli.agent_query \
  --agent_type react \
  --tools weather \
  --message "What's the weather like in San Francisco today?"
```

### Example 3: Conversational Agent with Multiple Tools

```bash
python -m cli.agent_query \
  --agent_type conversational \
  --tools search \
  --message "I'm planning a trip to Paris next week. What should I pack, considering weather?" \
  --system_message "You are a helpful travel assistant that gives concise advice."
```

### Example 4: Continuing a Conversation (Memory Demo)

First create a thread and ask a question:
```bash
THREAD_ID=$(python -m cli.agent_query \
  --agent_type react \
  --tools calculator,search \
  --message "My name is Alex and I'm planning to invest $1000 with a 5% annual return. How much will I have after 10 years?" \
  | grep "Thread ID:" | awk '{print $3}')
```

Follow-up question using the same thread:
```bash
python -m cli.agent_query \
  --thread $THREAD_ID \
  --agent_type react \
  --tools calculator,search \
  --message "What if I increased my investment to $1500 instead?" \
  --streaming
```
