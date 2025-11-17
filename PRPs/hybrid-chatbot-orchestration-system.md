# PRP: Hybrid Chatbot Orchestration System

**Feature**: Sistema de Orquestación de Chatbots Híbrido (Hybrid Chatbot Orchestration System)
**Version**: 1.0
**Date**: 2025-11-16
**Confidence Score**: 8/10

---

## Goal

Build a **Hybrid Chatbot Orchestration System** that automatically connects to and manages multiple third-party web chat interfaces **without APIs**. The system uses a two-module architecture:
- **Module 1 (Analyzer)**: Uses AI vision to generate configuration caches for chat platforms
- **Module 2 (Operator)**: Uses cached configurations for fast, deterministic daily operations

This enables automated, continuous chatbot responses across multiple platforms while minimizing AI costs and maximizing speed and reliability.

---

## Why

**Business Value:**
- Automate chatbot operations across multiple web-based chat platforms that lack APIs
- Reduce operational costs by separating expensive AI analysis from daily operations
- Enable scaling to handle multiple concurrent conversations efficiently
- Provide consistent chatbot responses across different platforms

**User Impact:**
- End users receive faster, more consistent chatbot responses
- System administrators can easily add new chat platforms without manual selector hunting
- Operations team gets reliable, self-healing automation

**Problems Solved:**
- Manual configuration of web automation selectors is error-prone and time-consuming
- Direct LLM integration for every operation is costly and slow
- Web platform UI changes break traditional hardcoded automation
- Managing multiple chat conversations requires intelligent orchestration

---

## What

### User-Visible Behavior

1. **Initial Setup**: System analyzes a chat platform's web interface once, generating a configuration cache
2. **Daily Operations**: System automatically:
   - Monitors multiple chat conversations
   - Reads conversation history
   - Generates appropriate chatbot responses
   - Sends responses through the web interface
   - Rotates between conversations using round-robin scheduling
3. **Self-Healing**: When selectors fail, system triggers recalibration automatically

### Technical Requirements

**From DRS Document** (see `/docs/requiremients.md`):
- Python-based dual-module architecture
- Selenium for browser automation
- Google Gemini Vision API for multimodal analysis
- JSON-based configuration caching
- Round-robin conversation scheduling
- Periodic polling for new messages
- Secure credential management
- Sub-10-second operation cycle per conversation

### Success Criteria

- [ ] Module 1 can analyze a chat interface and generate valid CSS/XPath selectors
- [ ] Module 2 can operate using cached configuration for at least 1 week without failures
- [ ] System handles authentication automatically
- [ ] Round-robin scheduling distributes attention across all active conversations
- [ ] Operation cycle (read → process → respond) completes in < 10 seconds
- [ ] System automatically triggers recalibration on selector failures
- [ ] Configuration cache is human-readable and can be manually edited if needed

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Core APIs and Libraries

- url: https://ai.google.dev/gemini-api/docs/image-understanding
  why: |
    Official Gemini Vision API documentation. Key sections:
    - Passing screenshots as inline data or via File API
    - Multimodal prompting with image + text
    - Base64 encoding for screenshots
    - Token calculation for images
  critical: |
    Gemini 2.5 Flash supports 258 tokens per image tile.
    For screenshots > 384px, images are tiled into 768x768 chunks.
    Use inline data for screenshots < 20MB, File API for larger.

- url: https://ai.google.dev/gemini-api/docs/document-processing
  why: |
    Shows how to combine visual + structural analysis
    Pattern for sending both screenshot and HTML to LLM
  critical: |
    Multimodal analysis (vision + DOM) provides best selector accuracy

- url: https://docs.astral.sh/uv/guides/projects/
  why: |
    Modern Python project structure using uv
    Dependency management with pyproject.toml
    Running commands with uv run
  critical: |
    Use uv for all dependency and environment management
    Follow standard Python package structure

- url: https://www.lambdatest.com/blog/selenium-best-practices-for-web-testing/
  why: |
    16 Selenium best practices including:
    - Explicit waits over implicit waits
    - Robust selector strategies (prefer CSS over XPath when possible)
    - Error handling patterns
  critical: |
    ALWAYS use WebDriverWait with explicit conditions
    Avoid hardcoded sleeps
    Use CSS selectors for simple queries, XPath for complex traversal

- url: https://realpython.com/modern-web-automation-with-python-and-selenium/
  why: |
    Modern Selenium patterns for Python
    Headless browser configuration
    Element interaction best practices

- url: https://www.browserstack.com/guide/find-element-in-selenium-with-python
  why: |
    Comprehensive guide to element location strategies
    When to use ID, CSS, XPath, etc.

# Project Structure Reference

- file: /docs/requiremients.md
  why: |
    Complete DRS (Documento de Requerimientos del Sistema)
    Contains all functional and non-functional requirements
    Defines the dual-module architecture
  critical: |
    This is the source of truth for all requirements
    Review sections RF-01 through RF-08 for functional requirements
    Review R-IA-01 through R-IA-04 for AI vision requirements
    Review RNF-01 through RNF-05 for non-functional requirements
```

### Current Codebase Tree

```bash
.
├── docs/
│   └── requiremients.md    # Complete system requirements (Spanish)
└── PRPs/
    └── hybrid-chatbot-orchestration-system.md  # This document
```

### Desired Codebase Tree with Responsibilities

```bash
.
├── .python-version                    # Python version (3.11+)
├── pyproject.toml                     # Project metadata and dependencies
├── uv.lock                            # Locked dependencies
├── README.md                          # Project documentation
├── .env.example                       # Example environment variables
├── .gitignore                         # Git ignore patterns
│
├── docs/
│   └── requiremients.md               # Requirements (existing)
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/                        # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py                # Environment variables and global config
│   │   └── schema.py                  # Pydantic models for config validation
│   │
│   ├── models/                        # Data models
│   │   ├── __init__.py
│   │   ├── platform_config.py         # PlatformConfig model (cache structure)
│   │   ├── conversation.py            # Conversation and Message models
│   │   └── selector.py                # Selector model (CSS/XPath)
│   │
│   ├── module1_analyzer/              # MODULE 1: Interface Analyzer
│   │   ├── __init__.py
│   │   ├── analyzer.py                # Main analyzer orchestrator
│   │   ├── screenshot_capturer.py     # Selenium screenshot capture
│   │   ├── dom_extractor.py           # HTML/DOM extraction
│   │   ├── gemini_client.py           # Gemini Vision API client
│   │   ├── selector_generator.py      # Prompts and selector extraction
│   │   └── cache_writer.py            # Write config.json cache
│   │
│   ├── module2_operator/              # MODULE 2: Orchestrator/Operator
│   │   ├── __init__.py
│   │   ├── operator.py                # Main operator orchestrator
│   │   ├── authenticator.py           # Handle login flows
│   │   ├── conversation_reader.py     # Read chat history
│   │   ├── message_sender.py          # Send messages
│   │   ├── round_robin.py             # Round-robin scheduler
│   │   ├── polling_loop.py            # Periodic polling logic
│   │   └── chatbot_interface.py       # Interface to external chatbot
│   │
│   ├── selenium_utils/                # Shared Selenium utilities
│   │   ├── __init__.py
│   │   ├── driver_factory.py          # WebDriver creation and configuration
│   │   ├── wait_helpers.py            # Common explicit wait patterns
│   │   └── element_helpers.py         # Safe element interaction wrappers
│   │
│   ├── cache/                         # Configuration cache storage
│   │   └── .gitkeep                   # (cache JSON files stored here)
│   │
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       ├── logger.py                  # Logging configuration
│       └── exceptions.py              # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_module1/
│   │   ├── test_analyzer.py
│   │   ├── test_gemini_client.py
│   │   └── test_selector_generation.py
│   ├── test_module2/
│   │   ├── test_operator.py
│   │   ├── test_round_robin.py
│   │   └── test_conversation_reader.py
│   └── test_utils/
│       └── test_exceptions.py
│
├── scripts/
│   ├── analyze_platform.py            # CLI: Run Module 1 on a platform
│   ├── run_operator.py                # CLI: Run Module 2 continuous operation
│   └── validate_config.py             # CLI: Validate a config cache file
│
└── PRPs/
    └── hybrid-chatbot-orchestration-system.md
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: Selenium Best Practices

# 1. ALWAYS use explicit waits, NEVER hardcoded sleeps
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ✅ CORRECT
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "button.send"))
)

# ❌ WRONG - brittle and slow
time.sleep(5)
element = driver.find_element(By.CSS_SELECTOR, "button.send")

# 2. Handle StaleElementReferenceException
# Web chat interfaces frequently update DOM, causing stale references
# Always re-query elements after DOM changes

# 3. Prefer CSS selectors over XPath for simple queries
# CSS: faster parsing, more readable
# XPath: use when you need complex traversal (parent, sibling, etc.)

# 4. Selenium requires chromedriver/geckodriver matching browser version
# Use webdriver-manager for automatic driver management

# CRITICAL: Gemini Vision API

# 1. Image size limits
# Inline data: Total request (image + prompt) < 20MB
# File API: Use for larger files or repeated use

# 2. Token calculation
# Each 768x768 tile = 258 tokens
# Budget accordingly when sending screenshots

# 3. Multimodal prompting pattern
from google import genai
from google.genai import types

# ✅ CORRECT: Send both screenshot AND HTML for best accuracy
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=screenshot_bytes, mime_type='image/png'),
        f"HTML:\n{html_content}",
        "Find the CSS selector for the send button..."
    ]
)

# 4. Rate limits: Gemini API has rate limits
# Implement exponential backoff for retries

# CRITICAL: Project Structure (UV)

# 1. Use uv for all dependency management
# uv add selenium google-genai pydantic
# uv run pytest
# uv run python scripts/analyze_platform.py

# 2. Store secrets in environment variables
# Use python-dotenv to load .env files
# NEVER commit .env to git

# 3. Configuration cache format (JSON)
{
  "platform_name": "WhatsApp Web",
  "url": "https://web.whatsapp.com",
  "last_updated": "2025-11-16T12:00:00Z",
  "selectors": {
    "input_field": "div[contenteditable='true'][data-tab='10']",
    "send_button": "button[aria-label='Send']",
    "message_bubble_user": "div.message-out",
    "message_bubble_bot": "div.message-in",
    "conversation_list": "div._2aBzC",
    "unread_indicator": "span.unread"
  },
  "wait_timeouts": {
    "page_load": 30,
    "element_visible": 10,
    "message_send": 5
  }
}
```

---

## Implementation Blueprint

### Data Models and Structure

```python
# src/models/platform_config.py
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Dict, Optional

class SelectorsModel(BaseModel):
    """CSS/XPath selectors for platform elements"""
    input_field: str = Field(..., description="Text input selector")
    send_button: str = Field(..., description="Send button selector")
    message_bubble_user: str = Field(..., description="User message bubble pattern")
    message_bubble_bot: Optional[str] = Field(None, description="Bot message bubble pattern")
    conversation_list: str = Field(..., description="List of conversations/chats")
    unread_indicator: str = Field(..., description="Unread message indicator")

class WaitTimeoutsModel(BaseModel):
    """Timeout configurations in seconds"""
    page_load: int = Field(default=30, ge=5, le=120)
    element_visible: int = Field(default=10, ge=2, le=60)
    message_send: int = Field(default=5, ge=1, le=30)

class PlatformConfig(BaseModel):
    """Configuration cache for a chat platform"""
    platform_name: str
    url: HttpUrl
    last_updated: datetime
    selectors: SelectorsModel
    wait_timeouts: WaitTimeoutsModel

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

# src/models/conversation.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Literal

class Message(BaseModel):
    """Single message in a conversation"""
    sender: Literal["user", "bot"]
    text: str
    timestamp: datetime

class Conversation(BaseModel):
    """A chat conversation"""
    conversation_id: str
    platform: str
    messages: List[Message]
    has_unread: bool
    last_message_time: datetime

# src/models/selector.py
from pydantic import BaseModel, validator
from typing import Literal

class Selector(BaseModel):
    """A CSS or XPath selector"""
    selector_type: Literal["css", "xpath"]
    value: str
    description: str

    @validator('value')
    def validate_selector(cls, v, values):
        """Basic validation of selector syntax"""
        if values.get('selector_type') == 'css' and '//' in v:
            raise ValueError("CSS selector should not contain XPath syntax")
        if values.get('selector_type') == 'xpath' and not v.startswith(('/', '(')):
            raise ValueError("XPath should start with / or (")
        return v
```

### List of Tasks (In Order)

```yaml
# ============================================================================
# PHASE 0: Project Initialization
# ============================================================================

Task 0.1: Initialize Python project with UV
  Action: CREATE
  Commands:
    - uv init --name chatoperator --lib
    - Create .python-version with "3.11"
    - Create pyproject.toml with dependencies
  Dependencies:
    - selenium
    - google-genai
    - pydantic
    - python-dotenv
    - webdriver-manager
    - pytest
    - pytest-asyncio
    - ruff
    - mypy
  Files:
    - pyproject.toml
    - .python-version
    - .env.example
    - .gitignore

Task 0.2: Create base project structure
  Action: CREATE
  Files:
    - src/__init__.py
    - src/config/__init__.py
    - src/models/__init__.py
    - src/selenium_utils/__init__.py
    - src/utils/__init__.py
    - tests/__init__.py
    - tests/conftest.py
    - scripts/ (directory)
    - src/cache/.gitkeep

# ============================================================================
# PHASE 1: Shared Infrastructure (Bottom-Up)
# ============================================================================

Task 1.1: Create configuration management
  Action: CREATE src/config/settings.py
  Purpose: Load environment variables and global configuration
  Pattern: Use pydantic-settings for env var validation
  Includes:
    - GEMINI_API_KEY
    - DEFAULT_BROWSER (chrome/firefox)
    - HEADLESS_MODE (bool)
    - LOG_LEVEL
    - CACHE_DIR path
  Test: test_config/test_settings.py

Task 1.2: Create data models
  Action: CREATE src/models/*.py
  Files:
    - platform_config.py (PlatformConfig, SelectorsModel, WaitTimeoutsModel)
    - conversation.py (Conversation, Message)
    - selector.py (Selector)
  Purpose: Type-safe data structures with Pydantic validation
  Test: test_models/test_platform_config.py, test_conversation.py

Task 1.3: Create logging utility
  Action: CREATE src/utils/logger.py
  Purpose: Centralized logging configuration
  Pattern:
    - Console handler for INFO+
    - File handler for DEBUG+
    - Structured JSON logs for production
  Test: Manual verification

Task 1.4: Create custom exceptions
  Action: CREATE src/utils/exceptions.py
  Purpose: Domain-specific exceptions
  Exceptions:
    - SelectorNotFoundException
    - AuthenticationFailedException
    - PlatformNotConfiguredException
    - RecalibrationRequiredException
  Test: test_utils/test_exceptions.py

Task 1.5: Create Selenium driver factory
  Action: CREATE src/selenium_utils/driver_factory.py
  Purpose: Centralized WebDriver creation with consistent configuration
  Features:
    - Support Chrome/Firefox
    - Headless mode support
    - User agent configuration
    - Window size configuration
    - Automatic driver management (webdriver-manager)
  Pattern:
    ```python
    def create_driver(headless: bool = True, browser: str = "chrome") -> WebDriver:
        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Use webdriver-manager for automatic driver download
            service = ChromeService(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
    ```
  Test: test_selenium_utils/test_driver_factory.py

Task 1.6: Create Selenium wait helpers
  Action: CREATE src/selenium_utils/wait_helpers.py
  Purpose: Reusable explicit wait patterns
  Functions:
    - wait_for_element(driver, selector, timeout=10)
    - wait_for_clickable(driver, selector, timeout=10)
    - wait_for_text_in_element(driver, selector, text, timeout=10)
    - wait_for_page_load(driver, timeout=30)
  Pattern: Wrap WebDriverWait with common EC conditions
  Test: test_selenium_utils/test_wait_helpers.py

Task 1.7: Create Selenium element helpers
  Action: CREATE src/selenium_utils/element_helpers.py
  Purpose: Safe element interaction with retry logic
  Functions:
    - safe_click(driver, selector, retries=3)
    - safe_send_keys(driver, selector, text, retries=3)
    - safe_get_text(driver, selector, retries=3)
    - safe_get_attribute(driver, selector, attribute, retries=3)
  Pattern: Handle StaleElementReferenceException with retries
  Test: test_selenium_utils/test_element_helpers.py

# ============================================================================
# PHASE 2: Module 1 - Interface Analyzer (AI-Powered Configuration)
# ============================================================================

Task 2.1: Create Gemini Vision API client
  Action: CREATE src/module1_analyzer/gemini_client.py
  Purpose: Wrapper for Google Gemini Vision API
  Features:
    - Initialize client with API key
    - Send screenshot + HTML for analysis
    - Parse JSON response with selectors
    - Rate limiting and retry logic
  Pattern:
    ```python
    from google import genai
    from google.genai import types

    class GeminiClient:
        def __init__(self, api_key: str):
            self.client = genai.Client(api_key=api_key)

        def analyze_interface(
            self,
            screenshot_bytes: bytes,
            html_content: str,
            platform_name: str
        ) -> Dict[str, str]:
            """Returns dict of selector_name -> selector_value"""
            prompt = self._build_analysis_prompt(platform_name)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=screenshot_bytes,
                        mime_type='image/png'
                    ),
                    f"HTML Structure:\n{html_content}",
                    prompt
                ]
            )
            return self._parse_selectors(response.text)
    ```
  Test: test_module1/test_gemini_client.py (mock API responses)

Task 2.2: Create selector generation prompts
  Action: CREATE src/module1_analyzer/selector_generator.py
  Purpose: Generate prompts for Gemini to extract selectors
  Features:
    - Build structured prompts for each selector type
    - Include examples of good CSS/XPath selectors
    - Request JSON output format
  Pattern:
    ```python
    SELECTOR_PROMPT_TEMPLATE = '''
    You are a web automation expert. Analyze this chat interface screenshot and HTML.

    Platform: {platform_name}

    Identify the following elements and provide the MOST ROBUST CSS selector for each:

    1. input_field: The text input where users type messages
    2. send_button: The button to send/submit messages
    3. message_bubble_user: Pattern to identify user's messages
    4. message_bubble_bot: Pattern to identify bot/received messages
    5. conversation_list: Container holding the list of conversations
    6. unread_indicator: Visual indicator for unread messages

    Requirements:
    - Prefer CSS selectors over XPath when possible
    - Use stable attributes (id, data-*, aria-*)
    - Avoid fragile selectors (nth-child, absolute positions)
    - Test selectors against the provided HTML

    Output Format (JSON):
    {{
      "input_field": "css_selector_here",
      "send_button": "css_selector_here",
      ...
    }}
    '''
    ```
  Test: test_module1/test_selector_generator.py

Task 2.3: Create screenshot capturer
  Action: CREATE src/module1_analyzer/screenshot_capturer.py
  Purpose: Capture full-page screenshots using Selenium
  Features:
    - Wait for page to fully load
    - Capture full viewport screenshot
    - Return PNG bytes
  Pattern:
    ```python
    def capture_screenshot(driver: WebDriver) -> bytes:
        # Wait for page load
        wait_for_page_load(driver, timeout=30)

        # Ensure window is maximized for consistent screenshots
        driver.maximize_window()

        # Small delay for dynamic content
        time.sleep(2)  # ONLY acceptable use of sleep in the codebase

        # Capture screenshot as PNG bytes
        screenshot_bytes = driver.get_screenshot_as_png()
        return screenshot_bytes
    ```
  Test: test_module1/test_screenshot_capturer.py

Task 2.4: Create DOM extractor
  Action: CREATE src/module1_analyzer/dom_extractor.py
  Purpose: Extract HTML/DOM structure from page
  Features:
    - Get page source HTML
    - Optional: Clean/minify HTML to reduce tokens
    - Focus on relevant sections (chat interface)
  Pattern:
    ```python
    def extract_dom(driver: WebDriver, focus_selector: str = "body") -> str:
        # Get full page source
        html = driver.page_source

        # Optional: Parse with BeautifulSoup and extract focused section
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the chat interface container (if known)
        chat_container = soup.select_one(focus_selector)
        if chat_container:
            return str(chat_container)

        return html
    ```
  Test: test_module1/test_dom_extractor.py

Task 2.5: Create cache writer
  Action: CREATE src/module1_analyzer/cache_writer.py
  Purpose: Write PlatformConfig to JSON cache file
  Features:
    - Validate config using Pydantic
    - Write formatted JSON to cache directory
    - Include timestamp
  Pattern:
    ```python
    def write_cache(config: PlatformConfig, cache_dir: Path):
        cache_file = cache_dir / f"{config.platform_name.lower().replace(' ', '_')}.json"

        # Validate
        config_dict = config.model_dump(mode='json')

        # Write pretty JSON
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Cache written to {cache_file}")
    ```
  Test: test_module1/test_cache_writer.py

Task 2.6: Create main analyzer orchestrator
  Action: CREATE src/module1_analyzer/analyzer.py
  Purpose: Orchestrate the entire analysis process
  Features:
    - Navigate to platform URL
    - Capture screenshot
    - Extract DOM
    - Call Gemini API
    - Generate PlatformConfig
    - Write cache
  Pattern:
    ```python
    class InterfaceAnalyzer:
        def __init__(self, gemini_api_key: str, cache_dir: Path):
            self.gemini_client = GeminiClient(gemini_api_key)
            self.cache_dir = cache_dir

        def analyze_platform(
            self,
            platform_name: str,
            url: str,
            wait_after_load: int = 5
        ) -> PlatformConfig:
            # Create driver
            driver = create_driver(headless=False)  # Visible for debugging

            try:
                # Navigate
                driver.get(url)
                time.sleep(wait_after_load)  # Wait for JS to load

                # Capture screenshot
                screenshot = capture_screenshot(driver)

                # Extract DOM
                html = extract_dom(driver)

                # Analyze with Gemini
                selectors_dict = self.gemini_client.analyze_interface(
                    screenshot, html, platform_name
                )

                # Build config
                config = PlatformConfig(
                    platform_name=platform_name,
                    url=url,
                    last_updated=datetime.now(UTC),
                    selectors=SelectorsModel(**selectors_dict),
                    wait_timeouts=WaitTimeoutsModel()  # Defaults
                )

                # Write cache
                write_cache(config, self.cache_dir)

                return config

            finally:
                driver.quit()
    ```
  Test: test_module1/test_analyzer.py (integration test with mock Gemini)

# ============================================================================
# PHASE 3: Module 2 - Operator (Deterministic Daily Operations)
# ============================================================================

Task 3.1: Create config cache loader
  Action: CREATE src/module2_operator/cache_loader.py
  Purpose: Load and validate cached PlatformConfig
  Features:
    - Read JSON from cache directory
    - Validate with Pydantic
    - Handle missing or invalid cache
  Pattern:
    ```python
    def load_cache(platform_name: str, cache_dir: Path) -> PlatformConfig:
        cache_file = cache_dir / f"{platform_name.lower().replace(' ', '_')}.json"

        if not cache_file.exists():
            raise PlatformNotConfiguredException(
                f"No cache found for {platform_name}. Run Module 1 first."
            )

        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return PlatformConfig(**data)
    ```
  Test: test_module2/test_cache_loader.py

Task 3.2: Create authenticator
  Action: CREATE src/module2_operator/authenticator.py
  Purpose: Handle login flows automatically
  Features:
    - Check if already logged in (cookie-based)
    - Perform login if needed
    - Wait for login success
    - Handle 2FA/QR codes (manual intervention required)
  Pattern:
    ```python
    class Authenticator:
        def __init__(self, driver: WebDriver, config: PlatformConfig):
            self.driver = driver
            self.config = config

        def ensure_authenticated(self, credentials: Optional[Dict] = None):
            # Navigate to platform
            self.driver.get(str(self.config.url))

            # Check if already logged in
            if self._is_logged_in():
                logger.info("Already authenticated")
                return

            # Handle platform-specific login
            if credentials:
                self._perform_login(credentials)
            else:
                # Wait for manual login (e.g., QR code scan)
                logger.warning("Manual login required. Waiting 60s...")
                time.sleep(60)

            if not self._is_logged_in():
                raise AuthenticationFailedException("Login failed or timed out")

        def _is_logged_in(self) -> bool:
            # Check for presence of main interface element
            try:
                wait_for_element(
                    self.driver,
                    self.config.selectors.conversation_list,
                    timeout=5
                )
                return True
            except TimeoutException:
                return False
    ```
  Test: test_module2/test_authenticator.py

Task 3.3: Create conversation reader
  Action: CREATE src/module2_operator/conversation_reader.py
  Purpose: Read chat history from active conversation
  Features:
    - Extract all message elements
    - Determine sender (user vs bot) based on bubble class
    - Extract message text
    - Build Conversation object
  Pattern:
    ```python
    class ConversationReader:
        def __init__(self, driver: WebDriver, config: PlatformConfig):
            self.driver = driver
            self.config = config

        def read_conversation(self, conversation_id: str) -> Conversation:
            messages = []

            # Find all message bubbles
            user_bubbles = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.config.selectors.message_bubble_user
            )
            bot_bubbles = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.config.selectors.message_bubble_bot or ""
            )

            # Combine and sort by position
            all_bubbles = []
            for bubble in user_bubbles:
                all_bubbles.append(("user", bubble))
            for bubble in bot_bubbles:
                all_bubbles.append(("bot", bubble))

            # Extract text
            for sender, bubble in all_bubbles:
                text = safe_get_text(self.driver, bubble)
                messages.append(Message(
                    sender=sender,
                    text=text,
                    timestamp=datetime.now(UTC)  # Simplified
                ))

            return Conversation(
                conversation_id=conversation_id,
                platform=self.config.platform_name,
                messages=messages,
                has_unread=False,
                last_message_time=messages[-1].timestamp if messages else datetime.now(UTC)
            )
    ```
  Test: test_module2/test_conversation_reader.py (with mock HTML)

Task 3.4: Create message sender
  Action: CREATE src/module2_operator/message_sender.py
  Purpose: Send messages through web interface
  Features:
    - Click input field
    - Type message text
    - Click send button
    - Wait for message to appear
    - Handle failures and retry
  Pattern:
    ```python
    class MessageSender:
        def __init__(self, driver: WebDriver, config: PlatformConfig):
            self.driver = driver
            self.config = config

        def send_message(self, text: str, retries: int = 3):
            for attempt in range(retries):
                try:
                    # Clear and type in input field
                    input_field = wait_for_element(
                        self.driver,
                        self.config.selectors.input_field,
                        timeout=self.config.wait_timeouts.element_visible
                    )
                    input_field.clear()
                    input_field.send_keys(text)

                    # Click send button
                    send_button = wait_for_clickable(
                        self.driver,
                        self.config.selectors.send_button,
                        timeout=self.config.wait_timeouts.element_visible
                    )
                    send_button.click()

                    # Wait briefly to confirm message sent
                    time.sleep(self.config.wait_timeouts.message_send)

                    logger.info(f"Message sent: {text[:50]}...")
                    return

                except (StaleElementReferenceException, TimeoutException) as e:
                    if attempt < retries - 1:
                        logger.warning(f"Send failed (attempt {attempt+1}), retrying...")
                        continue
                    else:
                        raise SelectorNotFoundException(
                            f"Failed to send message after {retries} attempts"
                        ) from e
    ```
  Test: test_module2/test_message_sender.py

Task 3.5: Create chatbot interface
  Action: CREATE src/module2_operator/chatbot_interface.py
  Purpose: Interface to external chatbot service
  Features:
    - Send conversation history
    - Receive chatbot response
    - Handle API errors
  Pattern:
    ```python
    class ChatbotInterface:
        """Interface to external chatbot API or service"""

        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def get_response(self, conversation: Conversation) -> str:
            """
            Send conversation history to chatbot and get response.

            This is a placeholder - implement based on your actual chatbot API.
            Could be OpenAI, Anthropic, custom LLM, etc.
            """
            # Build request payload
            messages = [
                {"role": msg.sender, "content": msg.text}
                for msg in conversation.messages
            ]

            # Call chatbot API (example)
            response = requests.post(
                self.api_url,
                json={"messages": messages, "conversation_id": conversation.conversation_id},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")
    ```
  Test: test_module2/test_chatbot_interface.py (mock API)

Task 3.6: Create round-robin scheduler
  Action: CREATE src/module2_operator/round_robin.py
  Purpose: Manage which conversation to attend next
  Features:
    - Track active conversation list
    - Rotate through conversations
    - Prioritize unread conversations
    - Skip empty/inactive conversations
  Pattern:
    ```python
    class RoundRobinScheduler:
        def __init__(self):
            self.conversation_queue = []
            self.current_index = 0

        def add_conversation(self, conversation_id: str):
            if conversation_id not in self.conversation_queue:
                self.conversation_queue.append(conversation_id)

        def remove_conversation(self, conversation_id: str):
            if conversation_id in self.conversation_queue:
                self.conversation_queue.remove(conversation_id)

        def get_next_conversation(self) -> Optional[str]:
            if not self.conversation_queue:
                return None

            # Round-robin: cycle through queue
            conversation_id = self.conversation_queue[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.conversation_queue)

            return conversation_id

        def prioritize_unread(self, unread_ids: List[str]):
            # Move unread conversations to front of queue
            for conv_id in unread_ids:
                if conv_id in self.conversation_queue:
                    self.conversation_queue.remove(conv_id)
                    self.conversation_queue.insert(0, conv_id)
    ```
  Test: test_module2/test_round_robin.py

Task 3.7: Create polling loop
  Action: CREATE src/module2_operator/polling_loop.py
  Purpose: Periodic polling for new messages/conversations
  Features:
    - Poll every X seconds (configurable)
    - Detect new conversations
    - Detect unread messages
    - Update scheduler
  Pattern:
    ```python
    class PollingLoop:
        def __init__(
            self,
            driver: WebDriver,
            config: PlatformConfig,
            scheduler: RoundRobinScheduler,
            poll_interval: int = 10
        ):
            self.driver = driver
            self.config = config
            self.scheduler = scheduler
            self.poll_interval = poll_interval

        def poll_for_updates(self) -> List[str]:
            """Returns list of conversation IDs with unread messages"""
            unread_conversations = []

            # Find all conversation elements
            conversation_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.config.selectors.conversation_list
            )

            for conv_elem in conversation_elements:
                # Check for unread indicator
                has_unread = self._has_unread_indicator(conv_elem)
                if has_unread:
                    conv_id = self._extract_conversation_id(conv_elem)
                    unread_conversations.append(conv_id)
                    self.scheduler.add_conversation(conv_id)

            return unread_conversations

        def _has_unread_indicator(self, conv_element) -> bool:
            try:
                conv_element.find_element(
                    By.CSS_SELECTOR,
                    self.config.selectors.unread_indicator
                )
                return True
            except NoSuchElementException:
                return False
    ```
  Test: test_module2/test_polling_loop.py

Task 3.8: Create main operator orchestrator
  Action: CREATE src/module2_operator/operator.py
  Purpose: Orchestrate the entire operation cycle
  Features:
    - Load cache
    - Authenticate
    - Start polling loop
    - Process conversations in round-robin
    - Handle selector failures → trigger recalibration
  Pattern:
    ```python
    class ChatOperator:
        def __init__(self, platform_name: str, cache_dir: Path):
            # Load config
            self.config = load_cache(platform_name, cache_dir)

            # Create driver
            self.driver = create_driver(headless=True)

            # Initialize components
            self.authenticator = Authenticator(self.driver, self.config)
            self.reader = ConversationReader(self.driver, self.config)
            self.sender = MessageSender(self.driver, self.config)
            self.scheduler = RoundRobinScheduler()
            self.poller = PollingLoop(self.driver, self.config, self.scheduler)
            self.chatbot = ChatbotInterface(
                api_url=os.getenv("CHATBOT_API_URL"),
                api_key=os.getenv("CHATBOT_API_KEY")
            )

        def run(self):
            """Main operation loop"""
            try:
                # Authenticate
                self.authenticator.ensure_authenticated()

                # Main loop
                while True:
                    # Poll for updates
                    unread_ids = self.poller.poll_for_updates()
                    if unread_ids:
                        self.scheduler.prioritize_unread(unread_ids)

                    # Get next conversation
                    conv_id = self.scheduler.get_next_conversation()
                    if not conv_id:
                        logger.info("No active conversations, sleeping...")
                        time.sleep(self.poller.poll_interval)
                        continue

                    # Process conversation
                    try:
                        self._process_conversation(conv_id)
                    except SelectorNotFoundException as e:
                        logger.error(f"Selector failed: {e}")
                        raise RecalibrationRequiredException(
                            f"Selectors outdated for {self.config.platform_name}"
                        ) from e

                    # Small delay before next conversation
                    time.sleep(2)

            finally:
                self.driver.quit()

        def _process_conversation(self, conversation_id: str):
            """Single conversation cycle: read → chatbot → send"""
            # Read conversation
            conversation = self.reader.read_conversation(conversation_id)

            # Get chatbot response
            response_text = self.chatbot.get_response(conversation)

            # Send response
            self.sender.send_message(response_text)

            logger.info(f"Processed conversation {conversation_id}")
    ```
  Test: test_module2/test_operator.py (integration test)

# ============================================================================
# PHASE 4: CLI Scripts and Entry Points
# ============================================================================

Task 4.1: Create Module 1 CLI script
  Action: CREATE scripts/analyze_platform.py
  Purpose: Command-line interface to run Module 1
  Features:
    - Accept platform name and URL as arguments
    - Run analyzer
    - Display results
  Pattern:
    ```python
    #!/usr/bin/env python3
    import argparse
    from pathlib import Path
    from src.module1_analyzer.analyzer import InterfaceAnalyzer
    from src.config.settings import settings

    def main():
        parser = argparse.ArgumentParser(
            description="Analyze a chat platform interface and generate config cache"
        )
        parser.add_argument("platform_name", help="Name of the chat platform")
        parser.add_argument("url", help="URL of the chat platform")
        parser.add_argument(
            "--wait",
            type=int,
            default=5,
            help="Seconds to wait after page load (default: 5)"
        )

        args = parser.parse_args()

        analyzer = InterfaceAnalyzer(
            gemini_api_key=settings.GEMINI_API_KEY,
            cache_dir=Path(settings.CACHE_DIR)
        )

        print(f"Analyzing {args.platform_name}...")
        config = analyzer.analyze_platform(
            platform_name=args.platform_name,
            url=args.url,
            wait_after_load=args.wait
        )

        print(f"✅ Analysis complete! Config saved to cache.")
        print(f"Platform: {config.platform_name}")
        print(f"Selectors found: {len(config.selectors.model_dump())}")

    if __name__ == "__main__":
        main()
    ```
  Usage: `uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com"`

Task 4.2: Create Module 2 CLI script
  Action: CREATE scripts/run_operator.py
  Purpose: Command-line interface to run Module 2
  Features:
    - Accept platform name as argument
    - Start operator in continuous mode
    - Handle graceful shutdown
  Pattern:
    ```python
    #!/usr/bin/env python3
    import argparse
    from pathlib import Path
    from src.module2_operator.operator import ChatOperator
    from src.config.settings import settings
    from src.utils.exceptions import RecalibrationRequiredException

    def main():
        parser = argparse.ArgumentParser(
            description="Run the chat operator for a configured platform"
        )
        parser.add_argument("platform_name", help="Name of the chat platform")

        args = parser.parse_args()

        try:
            operator = ChatOperator(
                platform_name=args.platform_name,
                cache_dir=Path(settings.CACHE_DIR)
            )

            print(f"Starting operator for {args.platform_name}...")
            operator.run()

        except RecalibrationRequiredException as e:
            print(f"❌ Recalibration required: {e}")
            print(f"Run: uv run python scripts/analyze_platform.py '{args.platform_name}' <URL>")
            return 1

        except KeyboardInterrupt:
            print("\n⏹️  Operator stopped by user")
            return 0

    if __name__ == "__main__":
        exit(main())
    ```
  Usage: `uv run python scripts/run_operator.py "WhatsApp Web"`

Task 4.3: Create config validation script
  Action: CREATE scripts/validate_config.py
  Purpose: Validate a cached config file
  Pattern:
    ```python
    #!/usr/bin/env python3
    import argparse
    import json
    from pathlib import Path
    from src.models.platform_config import PlatformConfig

    def main():
        parser = argparse.ArgumentParser(description="Validate a platform config cache")
        parser.add_argument("config_file", help="Path to config JSON file")

        args = parser.parse_args()

        # Load and validate
        with open(args.config_file, 'r') as f:
            data = json.load(f)

        try:
            config = PlatformConfig(**data)
            print(f"✅ Config is valid!")
            print(f"Platform: {config.platform_name}")
            print(f"URL: {config.url}")
            print(f"Last updated: {config.last_updated}")
            print(f"Selectors: {list(config.selectors.model_dump().keys())}")
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return 1

    if __name__ == "__main__":
        exit(main())
    ```

# ============================================================================
# PHASE 5: Testing and Documentation
# ============================================================================

Task 5.1: Create pytest fixtures
  Action: CREATE tests/conftest.py
  Purpose: Shared pytest fixtures
  Fixtures:
    - mock_driver: Mock WebDriver
    - sample_config: Sample PlatformConfig
    - mock_gemini_response: Mock Gemini API response

Task 5.2: Write unit tests for all modules
  Action: CREATE test files for each module
  Coverage targets:
    - 80%+ code coverage
    - All critical paths tested
    - Edge cases handled

Task 5.3: Create README.md
  Action: CREATE README.md
  Sections:
    - Project overview
    - Installation instructions
    - Quick start guide
    - Architecture diagram
    - Configuration reference
    - Troubleshooting

Task 5.4: Create .env.example
  Action: CREATE .env.example
  Contents:
    ```
    # Google Gemini API
    GEMINI_API_KEY=your_api_key_here

    # Browser Configuration
    DEFAULT_BROWSER=chrome
    HEADLESS_MODE=true

    # Chatbot API (configure based on your chatbot service)
    CHATBOT_API_URL=https://api.your-chatbot.com/v1/chat
    CHATBOT_API_KEY=your_chatbot_api_key

    # Logging
    LOG_LEVEL=INFO

    # Cache Directory
    CACHE_DIR=./src/cache
    ```
```

### Integration Points

```yaml
EXTERNAL_APIS:
  - name: Google Gemini Vision API
    url: https://ai.google.dev/gemini-api/docs
    auth: API key via environment variable
    rate_limits: Check Gemini API quotas

  - name: Chatbot Service (user-configurable)
    note: This is a placeholder - user must implement based on their chatbot

BROWSER:
  - WebDriver: Chrome or Firefox
  - Driver Manager: webdriver-manager (automatic driver downloads)

CONFIGURATION:
  - Environment variables via .env file
  - Pydantic validation for all configs
  - JSON cache files in src/cache/

DATABASE:
  - None required for MVP
  - Future: Store conversation history in SQLite/PostgreSQL
```

---

## Validation Loop

### Level 1: Syntax & Style

```bash
# FIRST: Fix line endings (CRITICAL per CLAUDE.md)
dos2unix src/**/*.py tests/**/*.py scripts/**/*.py

# Run linting and type checking
uv run ruff check src/ tests/ scripts/ --fix
uv run mypy src/ tests/ scripts/

# Expected: No errors
# If errors: Read output, fix issues, re-run
```

### Level 2: Unit Tests

```bash
# Run all unit tests
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Expected:
# - All tests pass
# - Coverage > 80%

# If failing:
# - Read test output carefully
# - Fix the underlying issue in src/
# - Do NOT mock away failures - fix the real problem
# - Re-run until green
```

### Level 3: Integration Tests

#### Test Module 1 (Analyzer)

```bash
# Requires: Valid GEMINI_API_KEY in .env

# Analyze a test platform (example: WhatsApp Web)
uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com" --wait 10

# Expected output:
# - Screenshot captured
# - Gemini API called successfully
# - Config cache written to src/cache/whatsapp_web.json
# - No exceptions

# Validate the generated config
uv run python scripts/validate_config.py src/cache/whatsapp_web.json

# Expected: ✅ Config is valid
```

#### Test Module 2 (Operator)

```bash
# Requires:
# - Valid config cache from Module 1
# - Valid CHATBOT_API_KEY in .env
# - Access to the chat platform

# Run operator (will require manual login for first time)
uv run python scripts/run_operator.py "WhatsApp Web"

# Expected behavior:
# 1. Browser opens (headless or visible based on config)
# 2. Navigates to WhatsApp Web
# 3. Waits for QR code scan (if not already logged in)
# 4. Starts polling for conversations
# 5. Processes conversations in round-robin
# 6. Sends chatbot responses

# Monitor logs for:
# - "Already authenticated" or successful login
# - "Polling for updates..."
# - "Processing conversation {id}"
# - "Message sent: ..."

# Test error handling:
# - Manually change a selector in cache to invalid value
# - Restart operator
# - Expected: RecalibrationRequiredException raised
```

### Level 4: End-to-End Test

```bash
# Full workflow test

# 1. Analyze a platform
uv run python scripts/analyze_platform.py "Test Platform" "https://test.example.com"

# 2. Validate config
uv run python scripts/validate_config.py src/cache/test_platform.json

# 3. Run operator
uv run python scripts/run_operator.py "Test Platform"

# 4. Send a test message through the web interface manually

# 5. Verify operator:
#    - Detects the message
#    - Reads conversation history
#    - Gets chatbot response
#    - Sends response back

# 6. Check logs for full cycle completion
```

---

## Final Validation Checklist

- [ ] All unit tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check src/ tests/ scripts/`
- [ ] No type errors: `uv run mypy src/ tests/ scripts/`
- [ ] All files use LF line endings: `file src/**/*.py` (no CRLF)
- [ ] Module 1 successfully analyzes a test platform
- [ ] Generated config passes validation
- [ ] Module 2 successfully authenticates
- [ ] Module 2 reads conversations correctly
- [ ] Module 2 sends messages successfully
- [ ] Round-robin scheduling works across multiple conversations
- [ ] Polling detects new messages
- [ ] Selector failures trigger RecalibrationRequiredException
- [ ] All environment variables documented in .env.example
- [ ] README.md provides clear setup instructions
- [ ] No hardcoded secrets in codebase

---

## Anti-Patterns to Avoid

### Selenium Anti-Patterns

- ❌ **Don't use hardcoded `time.sleep()`** except for initial page load stabilization
  - ✅ Use `WebDriverWait` with explicit conditions

- ❌ **Don't ignore StaleElementReferenceException**
  - ✅ Implement retry logic in element helpers

- ❌ **Don't use fragile selectors** (nth-child, absolute positions)
  - ✅ Prefer stable attributes: id, data-*, aria-*, class patterns

### Gemini API Anti-Patterns

- ❌ **Don't send screenshots without HTML context**
  - ✅ Always send both screenshot AND DOM for best accuracy

- ❌ **Don't ignore rate limits**
  - ✅ Implement exponential backoff and retry logic

- ❌ **Don't use Gemini for every operation**
  - ✅ Use Gemini only for initial analysis (Module 1)
  - ✅ Use cached config for daily operations (Module 2)

### Architecture Anti-Patterns

- ❌ **Don't mix Module 1 and Module 2 concerns**
  - ✅ Keep analyzer and operator completely separate

- ❌ **Don't skip validation on cached configs**
  - ✅ Always validate with Pydantic when loading cache

- ❌ **Don't handle all exceptions generically**
  - ✅ Use specific exception types for different failure modes

### Testing Anti-Patterns

- ❌ **Don't mock away real problems**
  - ✅ Fix the underlying issue

- ❌ **Don't skip integration tests**
  - ✅ Test the full workflow end-to-end

---

## Known Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Chat platform changes UI** | Selectors break, operator fails | Automatic recalibration detection + Module 1 re-run |
| **Gemini API rate limits** | Can't generate new configs | Implement exponential backoff, cache configs long-term |
| **Selenium driver version mismatch** | Browser automation fails | Use webdriver-manager for automatic driver updates |
| **Chatbot API downtime** | Can't generate responses | Implement retry logic, fallback responses |
| **2FA/Manual login required** | Can't automate authentication | Provide manual login mode, cookie persistence |
| **Large conversation history** | Slow to read, high token cost | Limit history to last N messages, implement pagination |

---

## Future Enhancements (Out of Scope for MVP)

- [ ] Multi-platform support (run multiple operators concurrently)
- [ ] Database storage for conversation history
- [ ] Admin dashboard for monitoring
- [ ] Automatic recovery from browser crashes
- [ ] Metrics and analytics (response times, success rates)
- [ ] Support for multimedia messages (images, files)
- [ ] Conversation priority based on user importance
- [ ] A/B testing different chatbot models

---

## References

- [DRS Document](/docs/requiremients.md) - Complete system requirements
- [Gemini Vision API Docs](https://ai.google.dev/gemini-api/docs/image-understanding)
- [Selenium Best Practices](https://www.lambdatest.com/blog/selenium-best-practices-for-web-testing/)
- [UV Project Guide](https://docs.astral.sh/uv/guides/projects/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**END OF PRP**
