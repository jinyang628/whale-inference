from app.models.inference.create import CreateMessage


def generate_openai_application_system_message() -> str:
    return f"""Your task is create an application based on the user's description. You need to generate the database tables necessary to support the CRUD operations, and provide a description of the general tasks which the application supports. The user might follow up with additional requirements that you will need to incorporate into your design. You may ask users a clarification question to get a better understanding of the application requirements if necessary. Do not include the id column in your response.
"""

def generate_openai_application_user_message(
    message: str, 
    chat_history: list[CreateMessage]
) -> str:
    return f"""### Here is the chat history:

{[message.model_dump() for message in chat_history]}

### Here is the user's current instruction:

{message}
"""