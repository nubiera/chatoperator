"""Selector generation prompts for Gemini Vision API."""

SELECTOR_PROMPT_TEMPLATE = '''You are a web automation expert analyzing a chat interface.

Platform: {platform_name}

Analyze the provided screenshot and HTML structure to identify UI elements for automation.

**Required Elements** (provide the MOST ROBUST CSS selector for each):

1. **input_field**: The text input field where users type their messages
   - Look for contenteditable divs or textarea elements
   - Prefer selectors with stable attributes like data-*, id, or aria-*

2. **send_button**: The button to send/submit messages
   - Usually has text like "Send", "Enviar", or an icon (plane, arrow)
   - Prefer aria-label or stable class patterns

3. **message_bubble_user**: Pattern to identify USER's sent messages
   - Look for message containers with outgoing/sent indicators
   - Usually aligned right or have specific classes like "message-out"

4. **message_bubble_bot**: Pattern to identify RECEIVED messages (from other users/bots)
   - Look for incoming message containers
   - Usually aligned left or have classes like "message-in"
   - Set to null if cannot distinguish from user messages

5. **conversation_list**: Container holding the list of conversations/chats
   - The sidebar or panel showing all chat threads
   - Should contain multiple conversation items

6. **unread_indicator**: Visual indicator for unread/new messages
   - Badges, dots, or highlights showing unread count
   - Often uses classes like "unread", "badge", or contains numbers

**Selector Requirements:**
- Prefer CSS selectors over XPath when possible
- Use stable attributes: id, data-*, aria-*, name
- Avoid fragile selectors: nth-child, absolute positions, dynamic IDs
- Test selectors match the provided HTML structure
- Be as specific as needed to avoid false matches

**Output Format** (JSON only, no markdown):
{{
  "input_field": "css_selector_here",
  "send_button": "css_selector_here",
  "message_bubble_user": "css_selector_here",
  "message_bubble_bot": "css_selector_here_or_null",
  "conversation_list": "css_selector_here",
  "unread_indicator": "css_selector_here"
}}

**Important**:
- Return ONLY valid JSON, no code blocks or markdown
- Use double quotes for strings
- Ensure all selectors are non-empty strings except message_bubble_bot which can be null
- Validate selectors against the provided HTML'''


def build_analysis_prompt(platform_name: str) -> str:
    """
    Build the analysis prompt for Gemini.

    Args:
        platform_name: Name of the chat platform

    Returns:
        Formatted prompt string
    """
    return SELECTOR_PROMPT_TEMPLATE.format(platform_name=platform_name)
