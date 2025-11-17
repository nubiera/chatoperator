# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ChatOperator** is a hybrid chatbot orchestration system that automates chatbot operations across web-based chat platforms that lack official APIs. It uses a **dual-module architecture** to separate expensive AI analysis from deterministic daily operations.

### Core Architecture: Two Independent Modules

#### Module 1: Interface Analyzer (`src/module1_analyzer/`)
**Purpose**: One-time AI-powered configuration generation
**Entry point**: `scripts/analyze_platform.py`
**Key technology**: Google Gemini Vision API + Selenium

**Flow**:
1. Navigate to chat platform URL with Selenium
2. Capture screenshot (PNG bytes) + HTML/DOM structure
3. Send both to Gemini Vision API with structured prompt
4. Parse JSON response containing CSS/XPath selectors
5. Write validated config to `src/cache/<platform_name>.json`

**Critical components**:
- `analyzer.py`: Main orchestrator that coordinates the entire flow
- `gemini_client.py`: Multimodal API client (screenshot + HTML → selectors)
- `selector_generator.py`: Prompt engineering for selector extraction
- `cache_writer.py`: Pydantic-validated JSON config persistence

#### Module 2: Chat Operator (`src/module2_operator/`)
**Purpose**: Continuous deterministic chat automation
**Entry point**: `scripts/run_operator.py`
**Key technology**: Selenium + cached configs (no AI calls)

**Flow**:
1. Load cached config from Module 1
2. Authenticate (supports manual QR code login)
3. **Main loop** (runs indefinitely):
   - Poll for unread messages/conversations
   - Use round-robin scheduler to select next conversation
   - Read conversation history via cached selectors
   - Call chatbot API for response
   - Send response through web interface
   - Catch `SelectorNotFoundException` → raise `RecalibrationRequiredException`

**Critical components**:
- `operator.py`: Main orchestrator with infinite loop and exception handling
- `round_robin.py`: Fair conversation scheduling with unread prioritization
- `authenticator.py`: Platform login (manual QR code support)
- `conversation_reader.py`: Extract messages from DOM using cached selectors
- `message_sender.py`: Type and send messages with retry logic
- `chatbot_interface.py`: External chatbot API integration (has "echo mode" fallback)

### Shared Infrastructure

#### Configuration (`src/config/settings.py`)
Uses `pydantic-settings` to load from `.env`:
- `GEMINI_API_KEY`: Required for Module 1
- `CHATBOT_API_URL` / `CHATBOT_API_KEY`: Optional (echo mode if not set)
- `DEFAULT_BROWSER`: chrome or firefox
- `HEADLESS_MODE`: true/false
- `POLL_INTERVAL`: Seconds between polling cycles

#### Selenium Utilities (`src/selenium_utils/`)
**CRITICAL**: Never use `time.sleep()` except for initial page load stabilization
- `driver_factory.py`: Creates WebDriver with anti-detection measures
- `wait_helpers.py`: Explicit wait patterns (WebDriverWait with EC conditions)
- `element_helpers.py`: Safe element interaction with `StaleElementReferenceException` retry logic

**Pattern**: Always use explicit waits, never hardcoded sleeps
```python
# ✅ CORRECT
element = wait_for_element(driver, selector, timeout=10)
element.click()

# ❌ WRONG
time.sleep(5)
element = driver.find_element(By.CSS_SELECTOR, selector)
```

#### Data Models (`src/models/`)
All config/data validated with Pydantic v2:
- `PlatformConfig`: Complete platform configuration schema
  - `SelectorsModel`: CSS/XPath selectors for UI elements
  - `WaitTimeoutsModel`: Timeout configurations
- `Conversation` / `Message`: Chat history representation
- `Selector`: Individual selector with type (css/xpath) validation

#### Exception Hierarchy (`src/utils/exceptions.py`)
```
ChatOperatorException (base)
├── SelectorNotFoundException → Triggers recalibration
├── RecalibrationRequiredException → User must run Module 1 again
├── PlatformNotConfiguredException → No cache found
├── AuthenticationFailedException → Login failed
├── GeminiAPIException → Module 1 AI failure
└── ChatbotAPIException → Module 2 chatbot failure
```

## Development Commands

### Environment Setup
```bash
# Install all dependencies (including dev tools)
uv sync --extra dev

# Install without dev dependencies
uv sync
```

### Running the System

#### Analyze a Platform (Module 1)
```bash
# Basic: Analyze with default settings
uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com"

# Advanced: Custom wait time + visible browser for debugging
uv run python scripts/analyze_platform.py "Discord" "https://discord.com/app" --wait 10 --no-headless

# With focused DOM extraction
uv run python scripts/analyze_platform.py "Telegram" "https://web.telegram.org" --focus "div.main-container"
```

#### Validate Generated Config
```bash
# Check config is valid and view selectors
uv run python scripts/validate_config.py src/cache/whatsapp_web.json

# Verbose mode: Show full JSON
uv run python scripts/validate_config.py src/cache/whatsapp_web.json --verbose
```

#### Run Operator (Module 2)
```bash
# Basic: Run with default 60s manual login wait
uv run python scripts/run_operator.py "WhatsApp Web"

# Extended wait for QR code scan (120s)
uv run python scripts/run_operator.py "WhatsApp Web" --manual-wait 120
```

### Testing

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_models/test_platform_config.py -v

# Run specific test class/method
uv run pytest tests/test_models/test_platform_config.py::TestSelectorsModel::test_valid_selectors -v

# Run tests without coverage (faster)
uv run pytest tests/ -v

# Generate HTML coverage report
uv run pytest tests/ --cov=src --cov-report=html
# View: open htmlcov/index.html
```

### Code Quality

```bash
# Linting (auto-fix enabled)
uv run ruff check src/ tests/ scripts/ --fix

# Linting (check only, no fixes)
uv run ruff check src/ tests/ scripts/

# Type checking (ignores missing imports for Selenium/Gemini)
uv run mypy src/ --ignore-missing-imports

# Type checking (strict mode)
uv run mypy src/
```

### Line Endings (CRITICAL)
All files MUST use Unix (LF) line endings per CLAUDE.md requirements:
```bash
# Fix line endings after creating/editing files
dos2unix <filename>

# Bulk fix
dos2unix src/**/*.py tests/**/*.py scripts/**/*.py
```

## Key Architectural Patterns

### 1. Self-Healing via Recalibration
When Module 2 encounters selector failures:
```python
# In operator.py main loop
try:
    self._process_conversation(conv_id)
except SelectorNotFoundException as e:
    raise RecalibrationRequiredException(
        f"Run Module 1 to recalibrate: "
        f"uv run python scripts/analyze_platform.py '{platform}' {url}"
    )
```
This prompts the user to re-run Module 1 to regenerate selectors.

### 2. Round-Robin Conversation Scheduling
`RoundRobinScheduler` maintains a circular queue:
- `add_conversation()`: Add newly detected conversations
- `get_next_conversation()`: Get next in rotation (circular index)
- `prioritize_unread()`: Move unread conversations to front
- Ensures fair attention distribution across all active chats

### 3. Retry Logic with Stale Element Handling
All Selenium interactions retry on `StaleElementReferenceException`:
```python
for attempt in range(retries):
    try:
        element = wait_for_element(driver, selector)
        element.click()
        return
    except StaleElementReferenceException:
        if attempt < retries - 1:
            continue
        raise SelectorNotFoundException(...)
```

### 4. Gemini Vision Multimodal Pattern
Module 1 sends both visual and structural information:
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        Part.from_bytes(screenshot_bytes, mime_type="image/png"),
        f"HTML:\n{html_content}",
        prompt  # Structured prompt for selector extraction
    ]
)
```
This gives Gemini both semantic context (vision) and structural context (HTML).

### 5. Configuration Cache Schema
Generated configs in `src/cache/` follow strict Pydantic schema:
```json
{
  "platform_name": "Platform Name",
  "url": "https://...",
  "last_updated": "ISO8601 timestamp",
  "selectors": {
    "input_field": "CSS selector",
    "send_button": "CSS selector",
    "message_bubble_user": "CSS selector",
    "message_bubble_bot": "CSS selector or null",
    "conversation_list": "CSS selector",
    "unread_indicator": "CSS selector"
  },
  "wait_timeouts": {
    "page_load": 30,
    "element_visible": 10,
    "message_send": 5
  }
}
```

## Important Implementation Details

### Module 1: Gemini Vision Integration
- **Rate limits**: Free tier = 15 RPM, 1500 requests/day
- **Token calculation**: 258 tokens per 768x768 tile
- **HTML truncation**: Max 50,000 chars to avoid token overflow
- **Response parsing**: Handles both raw JSON and markdown-wrapped JSON from Gemini
- **Selector validation**: Pydantic validates all selectors before caching

### Module 2: Continuous Operation
- **Infinite loop**: Runs until Ctrl+C or exception
- **Polling interval**: Configurable via `POLL_INTERVAL` env var (default: 10s)
- **Conversation limit**: Reads max 50 messages per conversation to prevent token overflow
- **Echo mode**: Chatbot interface falls back to echo mode if API not configured
- **Graceful shutdown**: Catches `KeyboardInterrupt` and cleans up WebDriver

### Selenium Best Practices (Enforced Throughout)
1. **Always use explicit waits**: `wait_for_element()`, `wait_for_clickable()`
2. **Never hardcode sleeps**: Exception for initial page load (2-5s)
3. **Retry stale elements**: All element helpers retry 3 times by default
4. **Anti-detection measures**: User agent, disable automation flags, CDP commands
5. **Headless mode**: Production should run headless; debugging uses visible browser

### Chatbot Integration
The `ChatbotInterface` is designed to be swapped out:
- Default: Echo mode (returns last message) for testing
- Custom: Implement `get_response(conversation: Conversation) -> str`
- Example integrations: OpenAI, Anthropic, custom LLM endpoints
- Request format: Send full conversation history as context

## Testing Strategy

### Current Coverage
- **Model tests**: Pydantic validation and serialization
- **Fixtures**: Mock drivers, sample configs, temporary cache directories
- **Coverage**: 2% (mostly models tested; integration tests needed)

### Adding Tests
1. **Unit tests**: Test individual functions in isolation
2. **Integration tests**: Test module orchestrators with mocked external APIs
3. **E2E tests**: Would require actual chat platforms (not automated yet)

### Test Fixtures Available (in `tests/conftest.py`)
- `mock_driver`: Mock Selenium WebDriver
- `sample_config`: Valid PlatformConfig instance
- `sample_selectors`: Valid SelectorsModel instance
- `mock_gemini_response`: JSON response from Gemini API
- `temp_cache_dir`: Temporary directory for cache testing
- `sample_cache_file`: Pre-created cache file for testing

## Common Workflows

### Adding a New Chat Platform
1. Run Module 1 analyzer: `uv run python scripts/analyze_platform.py "Platform" "URL"`
2. Validate config: `uv run python scripts/validate_config.py src/cache/platform.json`
3. Test operator: `uv run python scripts/run_operator.py "Platform" --manual-wait 120`
4. Monitor logs for selector errors
5. If selectors fail, re-run Module 1 (recalibration)

### Debugging Selector Issues
1. Run with visible browser: `--no-headless`
2. Increase wait times: `--wait 10`
3. Check logs for `SelectorNotFoundException`
4. Manually inspect generated cache file
5. Optionally edit cache manually and validate
6. Re-run Module 1 if needed

### Extending Chatbot Integration
1. Create new class implementing `get_response(conversation: Conversation) -> str`
2. Initialize in `operator.py` instead of default `ChatbotInterface()`
3. Set `CHATBOT_API_URL` and `CHATBOT_API_KEY` in `.env`
4. Test with echo mode first, then switch to real API

## Critical Files Reference

- **System entry points**: `scripts/{analyze_platform,run_operator,validate_config}.py`
- **Module 1 orchestrator**: `src/module1_analyzer/analyzer.py`
- **Module 2 orchestrator**: `src/module2_operator/operator.py`
- **Configuration**: `src/config/settings.py` (loads from `.env`)
- **Cache schema**: `src/models/platform_config.py`
- **Selenium patterns**: `src/selenium_utils/wait_helpers.py`
- **Exception handling**: `src/utils/exceptions.py`
- **Requirements documentation**: `docs/requiremients.md` (Spanish, detailed DRS)

## Environment Variables

Required:
- `GEMINI_API_KEY`: Get from https://aistudio.google.com/apikey

Optional (with defaults):
- `CHATBOT_API_URL`: Custom chatbot endpoint (defaults to echo mode)
- `CHATBOT_API_KEY`: Custom chatbot auth (defaults to echo mode)
- `DEFAULT_BROWSER`: `chrome` or `firefox` (default: `chrome`)
- `HEADLESS_MODE`: `true` or `false` (default: `true`)
- `LOG_LEVEL`: `DEBUG|INFO|WARNING|ERROR` (default: `INFO`)
- `CACHE_DIR`: Cache directory path (default: `./src/cache`)
- `POLL_INTERVAL`: Polling seconds (default: `10`)
