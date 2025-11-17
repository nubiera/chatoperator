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


ARCHIVE_SELECTOR_EXTENSION = '''

**Additional Archive Elements** (for conversation downloading):

7. **conversation_item**: Individual conversation/match item in the list
   - Clickable items representing each chat in the conversation list
   - Should be specific enough to select one conversation at a time

8. **profile_name**: User/match name displayed in the conversation
   - The name of the person you're chatting with
   - Usually in header or profile section

9. **profile_picture**: Profile picture element or URL
   - Main profile photo selector
   - Should point to img element or element with background-image

10. **profile_bio**: User bio/description text (optional)
    - About section or bio text
    - Set to null if not available

11. **profile_age**: Age display (optional)
    - User's age if shown
    - Set to null if not available

12. **profile_distance**: Distance display (optional)
    - Distance indicator (e.g., "2 miles away")
    - Set to null if not available

13. **message_timestamp**: Timestamp for each message (optional)
    - Time/date indicator for messages
    - Set to null if not consistently available

14. **message_container**: Container holding all messages in a conversation
    - The scrollable area containing message history
    - Parent element of all message bubbles

15. **scroll_container**: Scrollable container for loading history
    - Element that needs to be scrolled to load older messages
    - Often the same as message_container

16. **all_profile_pictures**: Selector for all profile photos in gallery (optional)
    - For platforms with multiple profile photos
    - Set to null if only one profile picture

**Updated Output Format**:
{{
  "selectors": {{
    "input_field": "css_selector_here",
    "send_button": "css_selector_here",
    "message_bubble_user": "css_selector_here",
    "message_bubble_bot": "css_selector_here_or_null",
    "conversation_list": "css_selector_here",
    "unread_indicator": "css_selector_here"
  }},
  "archive_selectors": {{
    "conversation_item": "css_selector_here",
    "profile_name": "css_selector_here",
    "profile_picture": "css_selector_here",
    "profile_bio": "css_selector_here_or_null",
    "profile_age": "css_selector_here_or_null",
    "profile_distance": "css_selector_here_or_null",
    "message_timestamp": "css_selector_here_or_null",
    "message_container": "css_selector_here",
    "scroll_container": "css_selector_here",
    "all_profile_pictures": "css_selector_here_or_null"
  }}
}}'''


def build_analysis_prompt(platform_name: str, include_archive: bool = False) -> str:
    """
    Build the analysis prompt for Gemini.

    Args:
        platform_name: Name of the chat platform
        include_archive: Whether to include archive selector extraction

    Returns:
        Formatted prompt string
    """
    base_prompt = SELECTOR_PROMPT_TEMPLATE.format(platform_name=platform_name)

    if include_archive:
        # Replace the output format section with archive-enabled version
        base_prompt = base_prompt.replace(
            '**Output Format** (JSON only, no markdown):',
            '**Output Format** (JSON only, no markdown) - WITH ARCHIVE SELECTORS:'
        )
        # Remove the old output format and add the new one
        base_prompt = base_prompt.split('**Output Format**')[0] + ARCHIVE_SELECTOR_EXTENSION

    return base_prompt
