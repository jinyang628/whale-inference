from app.models.application import ApplicationContent
from app.models.message import Message


def generate_openai_selection_system_message() -> str:    
    return f"""Your task is to interpret the user's natural language instruction and select the relevant (application, table name, HTTP method) groupings so that an ORM can use your output to perform specific actions on the databases of applications.

Follow these guidelines:
    1. The user's instruction might be related to multiple applications and you need to decide which subset of applications the user's instruction is related to.
    2. For each application, you need to determine the subset of tables which the user's instruction is related to.
    3. For each table, you need to determine the appropriate HTTP methods to use given the user's instructions.  
    4. The chat history is given to provide more context, but you only have to generate the relevant groupings based on the user's current instruction. 
"""

def generate_openai_selection_user_message(
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
