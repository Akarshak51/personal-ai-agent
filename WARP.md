# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Start Commands

### Development Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes testing, linting, docs)
pip install -r requirements-dev.txt

# Set up pre-commit hooks (if using)
pre-commit install
```

### Configuration
```bash
# Copy example configuration
cp config/config.example.json config/config.json

# Edit configuration with your settings (API keys, preferences, etc.)
# Key sections: integrations (OpenAI/Anthropic), memory, nlp, security
```

### Running the Agent
```bash
# Basic run
python src/main.py

# Interactive mode
python src/main.py --interactive

# Debug mode
python src/main.py --debug

# Custom config
python src/main.py --config path/to/custom/config.json
```

### Testing and Quality
```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## Architecture Overview

### Core Components Architecture
The agent follows a modular architecture with clear separation of concerns:

- **Agent Core** (`src/agent/personal_agent.py`): Main orchestrator handling conversation flow and response generation
- **Memory System** (`src/memory/memory_manager.py`): Dual-layer memory (SQLite for long-term, in-memory for short-term)
- **NLP Processor** (`src/nlp/processor.py`): Intent recognition, entity extraction, sentiment analysis
- **Configuration** (`src/utils/config.py`): Centralized config management with defaults and validation
- **Response Formatter** (`src/utils/response_formatter.py`): Output formatting and presentation

### Data Flow
1. User input → NLP Processor (intent/entity extraction)
2. Memory Manager retrieves relevant context
3. Agent Core generates response based on intent + context
4. Response Formatter formats output
5. Interaction stored in Memory Manager

### Memory Architecture
- **Short-term**: In-memory dict for session data
- **Long-term**: SQLite database with tables:
  - `interactions`: User inputs and agent responses with metadata
  - `user_context`: Persistent user-specific context data
- **Retention**: Configurable cleanup of old memories
- **Context Retrieval**: Intelligent context selection based on recency and relevance

### Intent System
Rule-based intent recognition with patterns for:
- `greeting`: Hello, good morning, etc.
- `question`: What/how/why questions, queries with ?
- `task`: Help requests, assistance, creation tasks  
- `personal`: Questions about the agent itself
- `general`: Fallback for unmatched inputs

## Configuration Structure

The `config/config.json` file controls all agent behavior:

- **agent**: Name, version, personality settings (style, tone, verbosity)
- **nlp**: Language, sentiment analysis, intent recognition settings
- **memory**: Storage location, retention policies, context length
- **integrations**: External APIs (OpenAI, Anthropic, web search)
- **security**: Content filtering, rate limiting, file access controls
- **server**: Web interface settings (FastAPI)
- **features**: Enable/disable voice, GUI, learning mode

## Key Integration Points

### External AI Models
- OpenAI GPT models via `integrations.openai`
- Anthropic Claude models via `integrations.anthropic`
- Local/basic NLP as fallback

### Storage Systems
- SQLite for persistent memory (default)
- Configurable database types via `integrations.database`
- File-based configuration storage

### API Surface
- CLI interface (main entry point)
- Web interface capability (FastAPI server)
- Programmatic interface via `PersonalAgent` class

## Development Guidelines

### Adding New Intents
1. Add regex patterns to `NLPProcessor.intent_patterns`
2. Implement handler method in `PersonalAgent._handle_{intent_name}`
3. Update intent routing in `PersonalAgent._generate_response`

### Memory Extensions
- Use `MemoryManager.add_to_short_term_memory` for session data
- Use `MemoryManager.store_user_context` for persistent user data
- Implement custom retrieval logic in `get_relevant_context`

### Configuration Changes
- Update `config.example.json` with new options
- Add defaults in `config.py.apply_defaults`
- Use `get_config_value` for nested config access

### Response Customization
- Modify personality via `agent.personality` config
- Extend `ResponseFormatter` for custom output formats
- Implement context-aware responses using memory data

## Important Notes

- API keys go in `config/config.json`, never hardcode them
- Memory cleanup runs based on `memory_retention_days` setting
- Security features include content filtering and rate limiting
- The agent supports both CLI and web interfaces
- All interactions are logged and stored for context
- Configuration falls back to example config if main config missing