from app.models.application import ApplicationContent
from app.models.message import Message


def generate_openai_clarification_system_message() -> str:
    return f"""Your task is to clarify the user's natural language instruction so that an AI agent can use your output to perform specific actions on the databases of applications. Currently, the user's instruction is not clear enough for the AI agent to understand which applications, tables, and HTTP methods to use. Your job is to ask for the necessary information that is missing."""

def generate_openai_clarification_user_message(
    applications: list[ApplicationContent], 
    message: str, 
    chat_history: list[Message]
) -> str:
    return f"""### Here are the applications that might be relevant to the user's instruction:

{[application.model_dump() for application in applications]}

### Here is the chat history:

{[message.model_dump() for message in chat_history]}

### Here is the user's current instruction:

{message}
"""

    