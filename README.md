# ChatOperator - Hybrid Chatbot Orchestration System

> Automate chatbot operations across web-based chat platforms without APIs using AI-powered configuration and deterministic operations.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

ChatOperator is a **dual-module system** that enables automated chatbot responses across multiple web chat platforms that lack official APIs. It uses:

- **Module 1 (Analyzer)**: AI vision (Gemini) to generate configuration caches by analyzing web interfaces
- **Module 2 (Operator)**: Deterministic Selenium-based automation for fast, cost-effective daily operations

### Key Features

✅ **AI-Powered Configuration** - Uses Google Gemini Vision API to automatically detect chat interface elements
✅ **Self-Healing** - Detects selector failures and triggers automatic recalibration
✅ **Round-Robin Scheduling** - Efficiently manages multiple concurrent conversations
✅ **Cost-Optimized** - Separates expensive AI analysis from daily operations
✅ **Platform Agnostic** - Works with any web-based chat interface
✅ **Headless Operation** - Runs in background without UI (configurable)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MODULE 1: ANALYZER                   │
│  (Run once or when selectors break)                     │
├─────────────────────────────────────────────────────────┤
│  1. Selenium navigates to chat platform                 │
│  2. Captures screenshot + HTML DOM                      │
│  3. Gemini Vision API analyzes interface                │
│  4. Generates config cache (JSON) with CSS selectors    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    config.json cache
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   MODULE 2: OPERATOR                    │
│  (Runs continuously, uses cached config)                │
├─────────────────────────────────────────────────────────┤
│  1. Authenticates to platform (manual QR code support)  │
│  2. Polls for new messages/conversations                │
│  3. Reads conversation history                          │
│  4. Calls chatbot API for response                      │
│  5. Sends response through web interface                │
│  6. Round-robin to next conversation                    │
│  7. Repeat (with recalibration on selector failure)     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Chrome or Firefox browser

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd chatoperator

# Install dependencies with uv
uv sync

# Create .env file from example
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or your favorite editor
```

### Configuration

Edit `.env` with your credentials:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Chatbot API (or use echo mode for testing)
CHATBOT_API_URL=https://api.your-chatbot.com/v1/chat
CHATBOT_API_KEY=your_chatbot_api_key

# Browser settings
DEFAULT_BROWSER=chrome  # or firefox
HEADLESS_MODE=true      # false for visible browser (debugging)

# Logging
LOG_LEVEL=INFO
```

---

## 📖 Usage

### Step 1: Analyze a Chat Platform (Module 1)

Run the analyzer to generate a configuration cache for a chat platform:

```bash
# Basic usage
uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com"

# With custom wait time (for slow-loading pages)
uv run python scripts/analyze_platform.py "Telegram Web" "https://web.telegram.org" --wait 10

# With visible browser (for debugging)
uv run python scripts/analyze_platform.py "Discord" "https://discord.com/app" --no-headless
```

**What happens:**
1. Browser opens and navigates to the URL
2. Screenshot and HTML captured
3. Gemini Vision API analyzes the interface
4. CSS selectors extracted and saved to `src/cache/<platform_name>.json`

### Step 2: Validate Configuration

Check that the generated config is valid:

```bash
uv run python scripts/validate_config.py src/cache/whatsapp_web.json
```

### Step 3: Run the Operator (Module 2)

Start the automated chatbot operator:

```bash
# Basic usage
uv run python scripts/run_operator.py "WhatsApp Web"

# With longer manual login wait (e.g., for QR code scan)
uv run python scripts/run_operator.py "WhatsApp Web" --manual-wait 120
```

**What happens:**
1. Browser opens and navigates to the platform
2. Waits for authentication (manual QR code scan if needed)
3. Starts polling for new messages
4. Processes conversations in round-robin order
5. Sends chatbot responses automatically

**Press `Ctrl+C` to stop the operator gracefully.**

---

## 🧪 Testing

Run the test suite:

```bash
# All tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_models/test_platform_config.py -v

# With detailed output
uv run pytest tests/ -vv
```

### Code Quality

```bash
# Linting
uv run ruff check src/ tests/ scripts/ --fix

# Type checking
uv run mypy src/ tests/ scripts/
```

---

## 📁 Project Structure

```
chatoperator/
├── src/
│   ├── config/              # Settings and configuration
│   ├── models/              # Pydantic data models
│   ├── module1_analyzer/    # Module 1: Interface Analyzer
│   │   ├── analyzer.py      # Main orchestrator
│   │   ├── gemini_client.py # Gemini Vision API client
│   │   ├── selector_generator.py # Prompt templates
│   │   ├── screenshot_capturer.py
│   │   ├── dom_extractor.py
│   │   └── cache_writer.py
│   ├── module2_operator/    # Module 2: Chat Operator
│   │   ├── operator.py      # Main orchestrator
│   │   ├── authenticator.py
│   │   ├── conversation_reader.py
│   │   ├── message_sender.py
│   │   ├── chatbot_interface.py
│   │   ├── round_robin.py
│   │   ├── polling_loop.py
│   │   └── cache_loader.py
│   ├── selenium_utils/      # Selenium helpers
│   │   ├── driver_factory.py
│   │   ├── wait_helpers.py
│   │   └── element_helpers.py
│   ├── utils/               # Utilities
│   │   ├── logger.py
│   │   └── exceptions.py
│   └── cache/               # Configuration caches (*.json)
├── scripts/
│   ├── analyze_platform.py  # Module 1 CLI
│   ├── run_operator.py      # Module 2 CLI
│   └── validate_config.py   # Config validation
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
└── README.md
```

---

## ⚙️ Configuration Reference

### Cache File Format (`src/cache/<platform>.json`)

```json
{
  "platform_name": "WhatsApp Web",
  "url": "https://web.whatsapp.com",
  "last_updated": "2025-11-16T12:00:00",
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

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ Yes |
| `CHATBOT_API_URL` | Your chatbot API endpoint | - | No (echo mode) |
| `CHATBOT_API_KEY` | Your chatbot API key | - | No (echo mode) |
| `DEFAULT_BROWSER` | Browser to use (`chrome` or `firefox`) | `chrome` | No |
| `HEADLESS_MODE` | Run browser in headless mode | `true` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `POLL_INTERVAL` | Polling interval in seconds | `10` | No |

---

## 🔧 Troubleshooting

### Common Issues

**1. Selector Not Found Error**

```
SelectorNotFoundException: Could not find element after 3 attempts
```

**Solution:** Selectors may have changed. Re-run the analyzer:

```bash
uv run python scripts/analyze_platform.py "Platform Name" "URL"
```

**2. Authentication Failed**

```
AuthenticationFailedException: Failed to authenticate
```

**Solution:**
- Ensure you complete manual login (QR code scan) within the wait period
- Increase manual wait time: `--manual-wait 120`
- Run with visible browser to debug: `--no-headless`

**3. Gemini API Errors**

```
GeminiAPIException: Failed to analyze interface
```

**Solution:**
- Check `GEMINI_API_KEY` is set correctly
- Verify API quota hasn't been exceeded
- Check network connection

**4. Chatbot API Not Configured**

If `CHATBOT_API_URL` is not set, the system runs in **echo mode** (returns last message) for testing.

---

## 🛡️ Security Best Practices

1. **Never commit `.env` file** - Contains sensitive API keys
2. **Use environment variables** - Don't hardcode credentials
3. **Secure cache files** - May contain platform-specific data
4. **Review logs** - Don't log sensitive user data
5. **Run headless in production** - More secure and resource-efficient

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting (`uv run pytest && uv run ruff check`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI vision for interface analysis
- **Selenium** - Browser automation
- **Pydantic** - Data validation
- **UV** - Modern Python package management

---

## 📞 Support

For issues, questions, or feature requests:

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Documentation: See `/docs/requiremients.md` for detailed requirements

---

**Made with ❤️ by the ChatOperator Team**
