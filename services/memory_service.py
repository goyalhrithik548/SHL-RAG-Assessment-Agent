"""
Purpose:
This file rebuilds conversation memory from the messages sent by the frontend.

Workflow:
1. Read each message from the request.
2. Convert it into a simple "Role: text" line.
3. Join the lines into one history string for the router and retriever.

Why this exists:
The app is stateless. Keeping memory reconstruction in one small function makes
that design clear and easy to debug.
"""


def build_memory(messages):
    """
    Convert chat messages into plain text history.

    This mirrors the original app.py formatting exactly.
    """
    history_lines = []

    for message in messages:
        role = message.role.capitalize()

        history_lines.append(
            f"{role}: {message.content}",
        )

    return "\n".join(history_lines)
